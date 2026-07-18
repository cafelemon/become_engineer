<div class="be-tutor-mount" data-tutor-lesson="python-core-05" aria-hidden="true"></div>

<section id="overview-safe-boundary" class="be-page-hero be-lesson-hero" data-learning-context="overview-safe-boundary" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 核心 · 第五课 · 给函数加一道不打扰业务的边界</span>

# Python 装饰器、闭包与自定义上下文管理器

## 写到一半失败，旧文件为什么还在

~~~text
写入前：已发布内容
块内失败：RuntimeError
写入后：已发布内容
临时文件：不存在
~~~

程序没有直接碰正式文件，而是先写旁边的临时文件。只有整个代码块正常结束，临时文件才会替换正式文件；中途失败就清理。

同一个项目还可以给某次函数调用加上“开始、完成、失败”事件，却不改原函数的参数、返回值和主报告。

<div class="be-page-actions" markdown="1">
[先看函数怎样被包装](#concept-function-object){ .md-button .md-button--primary }
[运行追踪与分阶段写入](#reproduce-trace-stage){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 核心 · 5 / 5</strong></div>
  <div><span>前置</span><strong>函数、作用域、生成器、异常、with 和类型提示</strong></div>
  <div><span>完成后留下</span><strong>可选调用追踪与失败不破坏旧文件的审计导出</strong></div>
</div>

## 开始前

- 能把函数传给另一个函数，并读懂嵌套函数。
- 知道生成器在 `yield` 处暂停，异常会继续传播。
- 已经用过文件对象自带的 `with`。
- 本课只使用 Python 3.11 标准库，不引入日志框架。

<section id="concept-function-object" data-learning-context="concept-function-object" data-context-type="concept" markdown="1">

## 装饰器之前，先看普通函数包装

Python 中，函数本身也是值：

~~~python
from collections.abc import Callable


def announce(function: Callable[[], str]) -> Callable[[], str]:
    def wrapper() -> str:
        return "开始 -> " + function()

    return wrapper


def finish() -> str:
    return "完成"


traced_finish = announce(finish)
print(traced_finish())
~~~

`announce()` 接收原函数，返回一个新函数。`@announce` 只是把这种重新绑定写得更紧凑：

~~~python
@announce
def finish() -> str:
    return "完成"
~~~

可以近似读成 `finish = announce(finish)`。装饰发生在解释器执行函数定义时；真正的 `wrapper()` 函数体仍要等调用时才运行。

</section>

<section id="concept-closure" data-learning-context="concept-closure" data-context-type="concept" markdown="1">

## 外层函数结束了，内层函数仍记得配置

~~~python
def trace_calls(event_sink: EventSink) -> Decorator:
    def decorate(function: Callable[P, R]) -> Callable[P, R]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            event_sink(f"开始:{function.__name__}")
            return function(*args, **kwargs)
        return wrapper
    return decorate
~~~

`trace_calls(events.append)` 早已返回，但之后调用包装函数时，`wrapper` 仍能找到 `event_sink` 和 `function`。这两个来自外层作用域的名称被闭包保留下来。

每个调用者都能传自己的事件去向，不需要模块级全局列表：

~~~python
first_events: list[str] = []
second_events: list[str] = []

first_trace = trace_calls(first_events.append)
second_trace = trace_calls(second_events.append)
~~~

闭包不是“把所有变量复制一份”。它保存的是对自由变量的关联；若捕获的是可变对象，后续修改仍然可见。

</section>

<section id="concept-decorator-contract" data-learning-context="concept-decorator-contract" data-context-type="concept" markdown="1">

## 包装以后，调用方式不能变宽成一团雾

~~~python
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
~~~

`ParamSpec` 代表原函数的整组位置参数和关键字参数；`TypeVar` 把原返回类型连接到包装函数：

~~~python
def decorate(function: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        result = function(*args, **kwargs)
        return result
    return wrapper
~~~

若写成 `Callable[..., object]`，mypy 只能知道“它大概能被调用”，却很难继续检查参数名和返回类型。类型变量有用的前提是实现确实原样转发 `args`、`kwargs` 和结果。

</section>

<section id="example-wraps-metadata" data-learning-context="example-wraps-metadata" data-context-type="example" markdown="1">

## wraps 把原函数的名字和说明带回来

新建的包装函数默认叫 `wrapper`，文档也来自包装器。加上：

~~~python
from functools import wraps


@wraps(function)
def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
    ...
~~~

再检查：

~~~python
assert traced.__name__ == original.__name__
assert traced.__doc__ == original.__doc__
assert traced.__wrapped__ is original
~~~

`wraps` 处理运行时元数据；`ParamSpec` 和 `TypeVar` 服务静态类型检查。两边都需要，但它们都不会自动保证业务结果正确。

</section>

<section id="troubleshoot-exception" data-learning-context="troubleshoot-exception" data-context-type="troubleshoot" markdown="1">

## 记录失败以后，原异常还要继续走

~~~python
try:
    result = function(*args, **kwargs)
except Exception as error:
    event_sink(f"失败:{function.__name__}:{type(error).__name__}")
    raise
~~~

追踪器可以观察异常类型，但不能把失败悄悄变成 `None`。测试要同时证明事件出现、原异常继续传播：

~~~python
with self.assertRaisesRegex(ValueError, "审计数据无效"):
    fail_export()

assert events == [
    "开始:fail_export",
    "失败:fail_export:ValueError",
]
~~~

这里捕获 `Exception` 是为了记录所有普通业务异常，紧接着使用裸 `raise` 原样传播；它和上一课“捕获 `OSError` 并转换成 `False`”的目的不同。

</section>

<section id="concept-contextmanager" data-learning-context="concept-contextmanager" data-context-type="concept" markdown="1">

## yield 的前后，正好对应进入和退出

~~~python
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def staged_output_path(output_path: Path) -> Iterator[Path]:
    pending_path = output_path.with_name(f".{output_path.name}.tmp")
    try:
        yield pending_path
        pending_path.replace(output_path)
    finally:
        pending_path.unlink(missing_ok=True)
~~~

~~~mermaid
flowchart TD
    A["进入：算出同目录临时路径"] --> B["yield：调用者写临时文件"]
    B --> C{"代码块正常结束吗"}
    C -->|是| D["replace：发布正式文件"]
    C -->|否| E["跳过发布，异常继续传播"]
    D --> F["finally：清理临时路径"]
    E --> F
~~~

`@contextmanager` 把只 `yield` 一次的生成器函数适配成上下文管理器。块内异常会回到 `yield` 位置；这里没有捕获它，所以跳过 `replace()`，执行 `finally` 后继续抛给调用者。

</section>

<section id="example-staged-write" data-learning-context="example-staged-write" data-context-type="example" markdown="1">

## 正式路径只在最后一刻被替换

~~~python
with staged_output_path(output_path) as pending_path:
    with pending_path.open("w", encoding="utf-8") as output:
        output.write("学习审计快照\n")
~~~

这两个 `with` 各管一件事：

- 内层文件上下文保证临时文件关闭。
- 外层自定义上下文决定正常结束后发布，失败后清理。

临时文件放在目标同一目录，避免跨文件系统移动带来的额外不确定性。这个做法适合单文件发布，但不是数据库事务，也不能同时原子提交多份文件。

</section>

<section id="reproduce-trace-stage" data-learning-context="reproduce-trace-stage" data-context-type="reproduce" markdown="1">

## 亲手看见成功事件和失败清理

~~~python
--8<-- "examples/python-core/decorators_contextmanagers.py"
~~~

~~~bash
.venv/bin/python -m mypy --strict site-src/examples/python-core/decorators_contextmanagers.py
python site-src/examples/python-core/decorators_contextmanagers.py
~~~

你应该看到：

~~~text
result=完成。
events=['开始:join_text', '完成:join_text']
name=join_text
failure=ValueError
failure_events=['开始:fail_export', '失败:fail_export:ValueError']
published=新审计内容
preserved=旧审计内容
pending_exists=False
~~~

最后两行最重要：块内失败后旧内容仍在，临时文件已经清理。

</section>

<section id="modify-publish-check" data-learning-context="modify-publish-check" data-context-type="modify" markdown="1">

## 发布前检查第一行

在 `yield pending_path` 之后、`replace()` 之前增加检查：临时文件第一行必须是“学习审计快照”。不符合就抛出 `ValueError`。

先写三组测试：

1. 正确标题可以替换旧文件。
2. 错误标题保留旧文件，并清理临时文件。
3. 空文件同样拒绝发布。

不要在上下文管理器里解析整份业务数据；这次只加一个发布前的最小不变量。若以后校验规则变复杂，应把验证函数独立出来，再由上下文管理器调用。

</section>

<section id="troubleshoot-staged-file" data-learning-context="troubleshoot-staged-file" data-context-type="troubleshoot" markdown="1">

## 临时文件还在，或者旧文件被覆盖了

按执行顺序检查：

| 现象 | 常见原因 | 修复位置 |
| --- | --- | --- |
| 块内失败后旧文件变了 | 代码块写的是正式路径 | 只打开 `pending_path` |
| 失败后留下 `.tmp` | 清理不在 `finally` | 把 `unlink(missing_ok=True)` 放进退出清理 |
| 失败仍发布新文件 | `replace()` 放在 `yield` 前或异常被吞掉 | 只在正常返回后执行替换 |
| 多次调用互相覆盖临时文件 | 固定临时名不支持并发 | 当前单进程课程先写清限制，后续再设计唯一临时名 |

不要把单进程测试通过说成已经解决并发发布。当前实现有意保持简单，适合学习和本项目的串行 CLI。

</section>

<section id="project-reporter-boundaries" data-learning-context="project-reporter-boundaries" data-context-type="project" markdown="1">

## 回到学习进度报告器

项目里两项能力都是可选边界，不侵入报告核心：

~~~text
调用者显式组合 trace_calls(events.append)(write_audit_snapshot)
    -> 记录开始 / 完成 / 失败
    -> 原参数、返回值和异常不变

write_audit_snapshot()
    -> staged_output_path() 给出临时路径
    -> 文件 with 写入并关闭
    -> 正常退出后替换正式文件
~~~

追踪器没有永久装饰 `build_report()`，事件也不写标准输出。这样 30 项测试、Python/C++ 主报告和 CLI 契约都不受影响。

~~~bash
python -m mypy --strict .
PYTHONPATH=src python -m unittest discover -s tests -v
python main.py
~~~

重点检查成功事件、失败事件、元数据、异常传播、首次写入、覆盖旧文件、块内失败保留旧文件和临时文件清理。

</section>

<section id="deepen-wrapper-choice" data-learning-context="deepen-wrapper-choice" data-context-type="deepen" markdown="1">

## 不是什么都要用装饰器

装饰器适合多个函数共享、并且不改变核心业务语义的调用边界，例如追踪、权限或重试。若只有一个调用点，显式函数调用可能更容易读；若资源有清楚的进入和退出范围，`with` 比隐式装饰更直观。

继续深化时还会遇到：

- 多层装饰器的应用顺序。
- 同步与异步函数的不同包装方式。
- `ContextDecorator`、类式 `__enter__` / `__exit__`。
- 多资源动态管理的 `ExitStack`。

这些能力等到真实问题出现再引入。本课先保证单层包装和单文件发布能被完整测试。

</section>

<section id="career-boundary-evidence" data-learning-context="career-boundary-evidence" data-context-type="career" markdown="1">

## 讲装饰器时，说清楚它没有改变什么

项目表达可以是：

> 我实现了一个 `ParamSpec` 与 `TypeVar` 保持调用契约的追踪装饰器，事件写入调用者提供的 sink；失败事件记录异常类型，但原异常继续传播。审计导出使用生成器式上下文管理器先写同目录临时文件，正常退出才替换正式文件。测试证明块内失败后旧文件不变、临时文件清理，主报告和公开函数签名保持稳定。

这比“我会写装饰器”更能说明你理解抽象边界、失败语义和回归验证。

</section>

## 完成检查

- [ ] 我能把 `@decorator` 还原成普通函数传递和重新绑定。
- [ ] 我能说明装饰发生在定义时，包装函数体执行在调用时。
- [ ] 我知道闭包怎样保留事件去向和原函数。
- [ ] 我能区分 `ParamSpec`、`TypeVar` 与 `wraps` 各自解决的问题。
- [ ] 我证明包装函数保留参数、返回值、名称、文档和 `__wrapped__`。
- [ ] 我记录失败事件后继续传播原异常。
- [ ] 我能沿着 `yield` 前后解释进入、发布和清理。
- [ ] 我跑过独立例子，并观察旧文件保护和临时文件清理。
- [ ] 我完成发布前首行检查及三组测试。
- [ ] 我运行正式项目 30 项测试，主报告没有追踪事件。

## 来源与版本

- 适用版本：Python 3.11 及以上；mypy 2.2.0 严格模式。
- 核查日期：2026-07-17。
- 事实来源：[Python 函数定义](https://docs.python.org/3.11/reference/compound_stmts.html#function-definitions)用于装饰器求值与应用；[`functools.wraps`](https://docs.python.org/3.11/library/functools.html#functools.wraps)用于包装函数元数据；[`typing.ParamSpec`](https://docs.python.org/3.11/library/typing.html#typing.ParamSpec)用于参数转发类型关系；[`contextlib.contextmanager`](https://docs.python.org/3.11/library/contextlib.html#contextlib.contextmanager)用于生成器式上下文管理器；[上下文管理器类型](https://docs.python.org/3.11/library/stdtypes.html#context-manager-types)用于进入、退出与异常传播。
- 代码验证：仓库脚本覆盖函数对象、定义时装饰、闭包隔离、参数与返回类型、元数据、成功与失败事件、异常传播、首次发布、旧文件保护、临时文件清理、严格 mypy 和正式项目 30 项测试；不联网。

## 下一步

进入[包结构、可安装入口与 CLI](06-package-structure-installable-cli.md)，把多模块报告器安装成命令行工具，并检查从源码、模块入口和控制台脚本启动时是否得到同一行为。
