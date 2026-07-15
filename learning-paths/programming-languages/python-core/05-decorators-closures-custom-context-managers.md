# Python 装饰器、闭包与自定义上下文管理器

<div class="be-tutor-mount" data-tutor-lesson="python-core-05" aria-hidden="true"></div>

> **任务先行：** 给双语言学习进度报告器增加一个可选的调用追踪器，并把审计导出升级为“先写临时文件，成功后再发布”。先观察事件和文件，再解释函数对象、闭包、装饰器与上下文管理协议。

## 任务路线

<div class="be-task-route" role="list" aria-label="本课五步任务"><span role="listitem">1 基线</span><span role="listitem">2 包装</span><span role="listitem">3 类型</span><span role="listitem">4 失败实验</span><span role="listitem">5 分阶段提交</span></div>

<section id="step-1" class="be-task-step" data-step-id="step-1" markdown="1">

## 第一步：运行对象与审计基线

运行 mypy、unittest 和报告器，确认上一课的对象方法、审计成功/失败路径和主报告契约。**可观察结果：** 从上一课提交开始应有 13 项测试；完成本课后的仓库版本有 16 项测试，报告总体进度仍为 `87.1%`。

</section>

<section id="step-2" class="be-task-step" data-step-id="step-2" markdown="1">

## 第二步：把函数包装过程改写成装饰器

先把函数传给包装函数并接收新函数，再用 `@trace_calls(events.append)` 表达同一过程。**主动修改：** 用追踪器包装 `write_audit_snapshot()`，观察开始和完成事件，但不把事件写进主报告。

</section>

<section id="step-3" class="be-task-step" data-step-id="step-3" markdown="1">

## 第三步：让闭包保持配置，让类型和元数据保持原样

使用闭包保存 `event_sink`，用 `ParamSpec` 与 `TypeVar` 转发原函数签名和返回类型，并用 `functools.wraps` 保留名称、文档与 `__wrapped__`。**成功标准：** mypy strict 通过，包装后的函数仍接受原参数并返回原类型。

</section>

<section id="step-4" class="be-task-step" data-step-id="step-4" markdown="1">

## 第四步：观察元数据丢失与异常传播

在临时实验中移除 `@wraps(function)`，观察函数名变成 `wrapper`；再让被包装函数抛出 `ValueError`。**恢复标准：** 名称和文档恢复，事件记录失败类型，原异常继续传播而不是被吞掉。

</section>

<section id="step-5" class="be-task-step" data-step-id="step-5" markdown="1">

## 第五步：用自定义上下文管理器分阶段发布审计文件

实现 `staged_output_path()`：块内只写同目录临时文件，正常退出后替换正式文件，失败时清理临时文件。**迁移验收：** 在不改变两个公开函数签名和主报告文本的前提下，独立增加一种可追踪事件或一种发布前校验。

</section>

上一课已经会使用文件自带的 `with`。本课继续回答两个工程问题：怎样给不同函数复用同一段调用边界，以及怎样把“进入、执行、成功提交、失败清理”封装成自己的上下文管理器。

## 课程信息

| 项目 | 内容 |
| --- | --- |
| 适合人群 | 已完成 Python 数据类与原生文件上下文管理，需要理解函数包装和自定义资源边界的学习者 |
| 前置知识 | 函数、作用域、类型提示、生成器、异常、数据类、`with`、mypy、unittest |
| 可观察产出 | 类型安全调用追踪器、分阶段审计文件发布、异常与清理回归测试 |
| 环境 | Python 3.11 及以上，仅使用标准库；mypy strict 与 unittest |
| 阶段作品 | [双语言学习进度报告器](../../../exercises/programming-languages/study-progress-reporters/README.md) |
| 事实核查 | Python 3.11.15 官方文档，2026-07-15 核查 |

## 学习目标

完成本节后，你应该能够：

- 说明函数为什么可以被传递、返回和重新绑定，以及 `@decorator` 在定义时完成了什么。
- 用闭包保存装饰器配置，不依赖全局可变状态。
- 用 `ParamSpec`、`TypeVar` 和 `wraps` 保持调用契约与函数元数据。
- 设计不会吞掉异常、不会改变业务返回值的边界装饰器。
- 用 `@contextmanager` 把进入、提交与失败清理组织为可复用资源边界。
- 判断装饰器、显式函数调用和显式 `with` 各自适合的范围。

## 第一步：保存上一课的可回归基线

从阶段作品的 Python 目录执行：

```bash
python -m mypy --strict .
python -m unittest discover -s tests -v
python main.py
```

如果你从上一课的提交开始，应先看到 13 项测试通过。当前仓库包含本课完成代码，因此会看到 16 项测试。无论从哪个状态开始，主报告都必须保持：

```text
学习进度报告
总计划：35.0 小时
总完成：30.5 小时
总体进度：87.1%
```

审计导出仍保持公开接口：

```python
def write_audit_snapshot(
    records: Iterable[StudyRecord], output_path: Path
) -> bool:
    ...
```

本课不能把追踪事件打印到标准输出，也不能把返回值改成事件对象。装饰器和上下文管理器只增强边界，不接管原来的业务契约。

## 第二步：先看函数包装，再使用装饰语法

Python 函数是对象。函数名可以指向函数对象，函数对象可以作为参数传入，也可以作为返回值返回：

```python
from collections.abc import Callable


def announce(function: Callable[[], str]) -> Callable[[], str]:
    def wrapper() -> str:
        return "开始 -> " + function()

    return wrapper


def finish() -> str:
    return "完成"


traced_finish = announce(finish)
assert traced_finish() == "开始 -> 完成"
```

装饰语法表达的是同一类重新绑定：

```python
@announce
def finish() -> str:
    return "完成"
```

可以近似理解为：

```python
def finish() -> str:
    return "完成"


finish = announce(finish)
```

装饰器表达式在函数定义执行时求值，不是等第一次调用函数才创建包装器。真正的 `wrapper()` 函数体仍在每次调用时执行。

本课不永久装饰报告器函数，而是在需要观察的调用点显式组合：

```python
events: list[str] = []
traced_writer = trace_calls(events.append)(write_audit_snapshot)
success = traced_writer(sample_records(), audit_path)

assert success
assert events == [
    "开始:write_audit_snapshot",
    "完成:write_audit_snapshot",
]
```

这样主程序没有全局事件列表，也不会因为导入模块就自动启用追踪。

## 第三步：用闭包、ParamSpec 和 wraps 保持契约

新建 `instrumentation.py`：

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeAlias, TypeVar


P = ParamSpec("P")
R = TypeVar("R")
EventSink: TypeAlias = Callable[[str], None]


def trace_calls(
    event_sink: EventSink,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Return a decorator that records deterministic call events."""

    def decorate(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            event_sink(f"开始:{function.__name__}")
            try:
                result = function(*args, **kwargs)
            except Exception as error:
                event_sink(
                    f"失败:{function.__name__}:{type(error).__name__}"
                )
                raise
            event_sink(f"完成:{function.__name__}")
            return result

        return wrapper

    return decorate
```

从外向内读这段代码：

1. `trace_calls()` 接收事件去向，返回真正的装饰器。
2. `decorate()` 接收被包装函数，返回 `wrapper()`。
3. `wrapper()` 调用原函数，并保持其返回值或异常。
4. 内层函数仍能读取 `event_sink` 和 `function`，这两个自由变量形成闭包。

`ParamSpec` 表示原函数的整组参数，`TypeVar` 表示返回类型。因此传入 `Callable[P, R]`，仍然返回 `Callable[P, R]`。这比 `Callable[..., object]` 更能帮助 mypy 检查调用者有没有传错参数。

`@wraps(function)` 会复制名称、限定名、注解和文档等元数据，并提供指向原函数的 `__wrapped__`。它不会替你保证业务逻辑正确，参数与返回值仍要由 `wrapper()` 原样转发。

主动修改与验收：

```python
events: list[str] = []


@trace_calls(events.append)
def join_text(left: str, right: str = "!") -> str:
    """Join two pieces of text."""
    return left + right


assert join_text("完成", right="。") == "完成。"
assert join_text.__name__ == "join_text"
assert join_text.__doc__ == "Join two pieces of text."
assert events == ["开始:join_text", "完成:join_text"]
```

## 第四步：安全观察元数据丢失和异常传播

### 失败实验一：临时移除 wraps

只在临时分支或练习文件中移除这一行：

```python
@wraps(function)
```

重新运行元数据测试，应看到名称断言失败：

```text
AssertionError: 'wrapper' != 'join_text'
```

恢复 `@wraps(function)` 后，名称、文档和 `__wrapped__` 测试重新通过。

### 失败实验二：原函数抛出异常

```python
events: list[str] = []


@trace_calls(events.append)
def fail_export() -> None:
    raise ValueError("审计数据无效")
```

测试必须同时证明两件事：记录失败事件，并继续抛出原异常。

```python
with self.assertRaisesRegex(ValueError, "审计数据无效"):
    fail_export()

self.assertEqual(
    events,
    ["开始:fail_export", "失败:fail_export:ValueError"],
)
```

如果包装器捕获异常后只记录、不 `raise`，调用者会误以为任务成功。边界代码可以观察失败，但不能未经明确协议就把失败变成成功。

## 第五步：用 contextmanager 分阶段提交文件

直接写正式文件时，进程或写入错误可能留下不完整内容。新建 `resources.py`，让块内先写同目录临时文件：

```python
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def staged_output_path(output_path: Path) -> Iterator[Path]:
    """Yield a sibling temporary path and replace the final file on success."""

    pending_path = output_path.with_name(f".{output_path.name}.tmp")
    try:
        yield pending_path
        pending_path.replace(output_path)
    finally:
        pending_path.unlink(missing_ok=True)
```

`@contextmanager` 把一个只产生一次值的生成器函数适配成上下文管理器：

- `yield` 之前对应进入阶段。
- `yield` 的值绑定到 `as` 后面的名称。
- 正常离开代码块后继续执行 `yield` 后的提交代码。
- 块内抛出异常时，异常会在 `yield` 位置重新进入生成器；`finally` 仍然清理临时文件。

报告器只改变内部写入路径，公开接口不变：

```python
def write_audit_snapshot(
    records: Iterable[StudyRecord], output_path: Path
) -> bool:
    snapshot = [record.clone() for record in records]
    try:
        with staged_output_path(output_path) as pending_path:
            with pending_path.open("w", encoding="utf-8") as output:
                output.write("学习审计快照\n")
                for record in snapshot:
                    output.write(
                        f"{record.course_name}\t{record.target_hours:g}\t"
                        f"{record.completed_hours:g}\n"
                    )
    except OSError:
        return False
    return True
```

失败测试先准备一份已经发布的内容，再在块内写入临时内容并主动抛错：

```python
output_path.write_text("已发布内容\n", encoding="utf-8")
pending_path = output_path.with_name(f".{output_path.name}.tmp")

with self.assertRaisesRegex(RuntimeError, "模拟块内失败"):
    with staged_output_path(output_path) as staged_path:
        staged_path.write_text("未完成内容\n", encoding="utf-8")
        raise RuntimeError("模拟块内失败")

assert output_path.read_text(encoding="utf-8") == "已发布内容\n"
assert not pending_path.exists()
```

这里的“成功后替换”改善了当前单文件场景，但不是数据库事务：它不同时提交多个文件，也不承诺跨文件系统原子性。临时文件必须与目标位于同一目录，且目标目录仍要具备写权限。

### 迁移验收

独立完成下面任意一项，不直接复制完整答案：

1. 为 `trace_calls()` 增加一种不包含参数值的确定性事件，同时保持原返回类型。
2. 在提交临时文件前验证第一行必须是“学习审计快照”，验证失败时保留旧文件。
3. 为分阶段发布增加自定义临时文件后缀，但不能使用全局状态，也不能改变 `write_audit_snapshot()` 签名。

完成后运行 16 项 unittest、mypy strict、Python/C++ 应用对照和审计文件测试。

## AI 协作任务

可以让 AI 提供装饰器类型标注和资源清理候选，但必须人工检查：

- 是否使用 `Any` 或 `Callable[..., object]` 掩盖了原函数签名。
- 是否忘记返回原函数结果、忘记转发关键字参数或忘记使用 `wraps`。
- 是否捕获异常后静默返回，改变了调用者看到的成功/失败语义。
- 是否在块内成功前覆盖正式文件，或在失败后留下临时文件。
- 是否把事件写入全局列表或标准输出，破坏测试隔离和主报告契约。

可复用提示：

```text
请为 Python 3.11 设计一个类型安全的调用追踪装饰器工厂和一个生成器式
上下文管理器。装饰器必须用 ParamSpec、TypeVar 和 wraps 保留原调用契约，
事件写入调用者提供的 sink；上下文管理器必须先写同目录临时文件，成功后
替换目标，失败时清理并继续传播异常。不要使用 Any、全局状态或第三方库。
```

## 常见错误与排查

| 现象 | 可能原因 | 检查与修复 |
| --- | --- | --- |
| 包装后的函数不能接收关键字参数 | 没有转发 `**kwargs` | 使用 `P.args`、`P.kwargs` 并原样调用原函数 |
| mypy 把包装结果推断成宽泛可调用对象 | 使用了 `Callable[..., object]` | 用 `ParamSpec` 和返回值 `TypeVar` 连接输入与输出 |
| 函数名显示为 `wrapper` | 缺少 `@wraps(function)` | 恢复 wraps 并检查名称、文档和 `__wrapped__` |
| 失败事件出现但测试没有抛错 | 包装器吞掉异常 | 记录后使用裸 `raise` 继续传播原异常 |
| 审计失败后旧文件被破坏 | 直接写正式路径或提前替换 | 块内只写临时路径，正常退出后再 `replace()` |
| 目录中残留 `.tmp` 文件 | 清理不在 `finally` 中 | 将 `unlink(missing_ok=True)` 放到退出清理阶段 |

## 完成证据

- mypy strict 对 8 个 Python 源文件无问题，16 项及以上 unittest 全部通过。
- 装饰器保持位置参数、关键字参数、返回值、名称、文档和原函数引用。
- 成功事件顺序确定；失败事件包含异常类型，原异常继续传播。
- 审计首次写入和覆盖旧文件成功，缺失父目录返回 `False`。
- 块内失败后旧文件不变、临时文件被清理。
- Python 与 C++ 主报告逐字一致，标准输出中没有追踪事件。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [函数定义](https://docs.python.org/3.11/reference/compound_stmts.html#function-definitions) | 装饰器求值、应用顺序和函数对象绑定 | Python 3.11.15，2026-07-15 核查 |
| [functools.wraps](https://docs.python.org/3.11/library/functools.html#functools.wraps) | 包装函数元数据与 `__wrapped__` | Python 3.11.15，2026-07-15 核查 |
| [typing.ParamSpec](https://docs.python.org/3.11/library/typing.html#typing.ParamSpec) | 装饰器参数转发的静态类型关系 | Python 3.11.15，2026-07-15 核查 |
| [contextlib.contextmanager](https://docs.python.org/3.11/library/contextlib.html#contextlib.contextmanager) | 生成器式上下文管理器与异常回到 `yield` | Python 3.11.15，2026-07-15 核查 |
| [上下文管理器类型](https://docs.python.org/3.11/library/stdtypes.html#context-manager-types) | `__enter__`、`__exit__`、异常传播和抑制边界 | Python 3.11.15，2026-07-15 核查 |

本地素材库中的装饰器笔记只用于识别闭包、装饰时机和参数转发等新手易错点；课程定义、类型方案和上下文语义均以以上官方资料与实际测试为准，原始素材不进入公开站点。

## 下一步

Python 核心语言的函数、对象、迭代和资源边界已经形成一条连续成果线。下一节进入 **包结构、CLI、配置与日志**，把当前多模块报告器组织为可以从命令行稳定运行、诊断和发布的最小工程；本节不提前引入 `ContextDecorator`、`ExitStack`、异步装饰器或 `asynccontextmanager`。
