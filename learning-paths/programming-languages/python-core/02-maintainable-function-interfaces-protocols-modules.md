<div class="be-tutor-mount" data-tutor-lesson="python-core-02" aria-hidden="true"></div>

<section id="overview-interface" class="be-page-hero be-lesson-hero" data-learning-context="overview-interface" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 核心 · 第二课 · 让边界可以替换</span>

# 可维护函数接口、协议与模块边界

## 同一份报告，换一个出口

程序正常运行时把报告打印到终端；测试时把同一段文字放进列表。分析和格式化代码不必知道结果最终去了哪里。

~~~text
终端输出：接口学习报告 / 总完成：6.0 小时
内存输出：['接口学习报告\n总完成：6.0 小时']
~~~

这节课不追求更多模块，而是让每个模块只知道自己真正需要知道的事：业务计算返回数据，报告函数返回文字，入口选择具体输出方式。

<div class="be-page-actions" markdown="1">
[先看依赖方向](#concept-dependency-direction){ .md-button .md-button--primary }
[运行可替换输出](#reproduce-replace-writer){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 核心 · 2 / 5</strong></div>
  <div><span>前置</span><strong>类型契约、函数、模块、mypy 与 unittest</strong></div>
  <div><span>完成后留下</span><strong>可替换输出、依赖图和接口失败记录</strong></div>
</div>

## 开始前

- 已完成上一课，能区分静态检查、运行时校验和测试。
- 能读懂函数参数、返回值、`Sequence` 和 `TypedDict`。
- 知道 Python 模块就是可以导入的 `.py` 文件。
- 本课继续使用学习进度报告器，不要求 C++ 前置。

<section id="concept-signature" data-learning-context="concept-signature" data-context-type="concept" markdown="1">

## 签名要让调用者看懂意图

两个相邻数字即使类型相同，也可能很容易传反：

~~~python
def summarize(
    completed_hours: float,
    target_hours: float,
    *,
    progress_limit: float = 1.0,
) -> float:
    return min(completed_hours / target_hours, progress_limit)
~~~

星号后面的参数只能按名称传入：

~~~python
summarize(7.5, 10.0, progress_limit=1.0)
~~~

<code>progress_limit=1.0</code> 在调用位置一眼就能看出含义；若只写第三个位置参数 <code>1.0</code>，读者还要回头找定义。

Python 签名中常见三类参数：

| 位置 | 调用方式 | 适合 |
| --- | --- | --- |
| `/` 之前 | 只能按位置 | 参数名不属于公开契约的回调 |
| `/` 与 `*` 之间 | 位置或关键字 | 普通常用参数 |
| `*` 之后 | 只能按关键字 | 布尔开关、限制、输出端等需要说出名字的选项 |

规则不是越多越好。只在调用容易含糊、或参数角色必须明确时使用位置专用与关键字专用约束。

</section>

<section id="troubleshoot-default-value" data-learning-context="troubleshoot-default-value" data-context-type="troubleshoot" markdown="1">

## 默认列表为什么记住了上一次调用

先故意写一次有问题的版本：

~~~python
def remember_course(course: str, history: list[str] = []) -> list[str]:
    history.append(course)
    return history


print(remember_course("Python"))
print(remember_course("CS"))
~~~

第二次会得到 <code>['Python', 'CS']</code>。默认列表在函数定义时创建一次，省略参数的多次调用会共享它。

如果想让每次调用都有新列表，用 <code>None</code> 作为哨兵：

~~~python
def remember_course(
    course: str,
    history: list[str] | None = None,
) -> list[str]:
    current = [] if history is None else history
    current.append(course)
    return current
~~~

有意缓存时可以共享状态，但必须清楚写出并测试。普通函数不要让默认参数悄悄变成跨调用全局变量。

</section>

<section id="concept-data-flow" data-learning-context="concept-data-flow" data-context-type="concept" markdown="1">

## 返回值让数据流看得见

下面的函数把结果藏在全局变量里：

~~~python
latest_report = ""


def build_latest_report() -> None:
    global latest_report
    latest_report = "学习报告"
~~~

调用者只看签名，不知道真正结果在哪里；测试还会受执行顺序影响。更清楚的写法是返回结果：

~~~python
def build_report() -> str:
    return "学习报告"
~~~

需要打印、写文件或发送网络请求时，再由边界代码处理这个字符串。核心函数越少依赖终端、文件和全局状态，就越容易单独测试，也越容易复用。

</section>

<section id="concept-protocol" data-learning-context="concept-protocol" data-context-type="concept" markdown="1">

## Protocol 只描述“能做什么”

简单回调可以使用 <code>Callable[[str], None]</code>。当这个角色会长期出现在项目中，给它一个名字更容易读：

~~~python
from typing import Protocol


class ReportWriter(Protocol):
    def __call__(self, report: str, /) -> None:
        ...
~~~

普通函数不需要继承协议，只要签名兼容即可：

~~~python
def print_report(text: str, /) -> None:
    print(text)


writer: ReportWriter = print_report
~~~

mypy 按结构判断这个函数能否接收一个字符串并返回 <code>None</code>。这种方式叫结构化子类型。

<code>Protocol</code> 默认不会自动在运行时校验对象。它解决的是静态接口表达，不是权限、安全或外部输入验证。

</section>

<section id="concept-dependency-direction" data-learning-context="concept-dependency-direction" data-context-type="concept" markdown="1">

## 具体选择留在入口，业务代码只依赖协议

~~~mermaid
flowchart LR
    CLI["cli：入口与组装"] --> APP["application：组织流程"]
    CLI --> PRINT["print_writer：终端输出"]
    APP --> ANALYSIS["analysis：统计"]
    APP --> REPORT["reporting：生成文本"]
    APP --> PORT["ports：ReportWriter"]
    PRINT -.结构兼容.-> PORT
~~~

- 入口知道今天要从哪里读、写到哪里。
- 应用流程只知道有一个 <code>ReportWriter</code>，不导入具体终端函数。
- 分析和报告模块不认识终端、文件或测试列表。
- 测试传入内存 writer，即可观察输出而不捕获标准输出。

如果 <code>analysis.py</code> 反向导入 <code>cli.py</code> 的打印函数，很容易形成循环导入，也让业务计算被具体运行方式绑住。依赖箭头应从入口指向核心，而不是核心回头寻找入口。

</section>

<section id="example-module-public" data-learning-context="example-module-public" data-context-type="example" markdown="1">

## 下划线和 __all__ 是公开约定，不是门锁

模块可以用前导下划线表达内部实现：

~~~python
def _calculate_progress(...) -> float:
    ...
~~~

也可以用 <code>__all__</code> 列出希望公开的名字：

~~~python
__all__ = ["summarize_records"]
~~~

它们帮助读者、文档工具和 <code>from module import *</code> 理解公开接口，但无法阻止别人显式导入内部名称。Python 模块里的命名约定不是认证授权系统。

课程代码不使用 <code>import *</code>。<code>__all__</code> 在这里主要是一张公共 API 清单；真正的文件权限、账号权限和服务授权属于另一层问题。

</section>

<section id="reproduce-replace-writer" data-learning-context="reproduce-replace-writer" data-context-type="reproduce" markdown="1">

## 用两个 writer 跑同一段流程

完整例子包含关键字专用参数、结构化协议、返回值和内存输出：

~~~python
--8<-- "examples/python-core/interfaces_protocols.py"
~~~

先检查，再运行：

~~~bash
.venv/bin/python -m mypy --strict site-src/examples/python-core/interfaces_protocols.py
python site-src/examples/python-core/interfaces_protocols.py
~~~

你应该看到：

~~~text
terminal:
接口学习报告
总完成：6.0 小时
memory_count=1
memory_matches=True
fresh_defaults=True
~~~

终端 writer 和内存 writer 接收的是同一段报告；<code>run_report()</code> 还返回文本，让调用者可以继续处理。

</section>

<section id="troubleshoot-interface" data-learning-context="troubleshoot-interface" data-context-type="troubleshoot" markdown="1">

## 三种错误发生在不同阶段

**位置参数违反签名：**

~~~python
run_report(records, remember)
~~~

<code>writer</code> 位于星号之后，mypy 和运行时都会拒绝这个位置参数。正确调用是 <code>writer=remember</code>。

**回调不满足协议：**

~~~python
def wrong_writer(report: bytes, /) -> int:
    return len(report)
~~~

它接收 <code>bytes</code>、返回 <code>int</code>，与 <code>ReportWriter</code> 不兼容。mypy 应在组装位置指出问题。

**循环导入：**

~~~text
cli -> application -> analysis -> cli
~~~

Python 可能提示“partially initialized module”，也可能暴露尚未创建的名称。恢复方式不是随意移动一行 import，而是重新画依赖图：核心模块不应导入入口里的具体实现；把稳定接口移到更内层的模块，由入口完成组装。

</section>

<section id="modify-new-writer" data-learning-context="modify-new-writer" data-context-type="modify" markdown="1">

## 增加一份带前缀的输出

写一个新的兼容函数：

~~~python
def prefixed_writer(report: str, /) -> None:
    print("[学习记录]")
    print(report)
~~~

不修改 <code>build_report()</code> 和 <code>run_report()</code>，只在组装处替换 writer。然后再写一个内存版本，把前缀和报告一起保存到列表，确认：

1. 两个 writer 都通过 mypy 协议检查。
2. 报告正文一字不变。
3. 前缀只属于输出边界，没有渗入业务函数。
4. 原始记录没有被修改。

如果为了加前缀而给分析函数增加 <code>print()</code>，说明边界放错了位置。

</section>

<section id="project-reporter-interface" data-learning-context="project-reporter-interface" data-context-type="project" markdown="1">

## 审阅当前报告器的依赖箭头

当前双语言学习进度报告器已经有 <code>analysis.py</code>、<code>reporting.py</code>、<code>resources.py</code>、<code>cli.py</code> 等模块。不要为了复现课程重新拆一套正式代码，先完成一份依赖审阅：

- `models` 不导入业务或 CLI。
- `analysis` 只依赖模型与标准库。
- `reporting` 依赖分析结果和模型，不导入 CLI。
- `cli` 负责读取参数、选择输出和返回退出码。
- 测试可以直接调用核心函数，不需要启动完整命令行。

运行当前项目的 mypy 和全部测试，记录公开报告仍然一致。然后只在测试中写一个内存 writer 原型，验证“输出方式可替换”这个设计，不修改现有 CLI 的公开行为。

这节课给项目增加的不是更多文件，而是一张能解释的依赖图和一次可替换边界验证。下一课会继续把输入从固定序列扩展到一次性迭代器。

</section>

<section id="deepen-interface-size" data-learning-context="deepen-interface-size" data-context-type="deepen" markdown="1">

## 接口越抽象，不一定越好

如果只传一个简单回调，<code>Callable[[str], None]</code> 已经够用；若“报告输出”是长期业务角色，需要位置参数约束、重载或更多方法，命名 <code>Protocol</code> 才值得。

同样，参数类型也应按真实操作选择：

- 单次遍历：<code>Iterable</code>。
- 需要长度和索引：<code>Sequence</code>。
- 必须原地修改：明确可变接口或具体容器。

不要为每个函数都造协议，也不要为了看起来“架构化”把一个小程序拆成十几个只含一行的模块。边界的价值来自变化隔离和测试便利，而不是目录数量。

</section>

<section id="career-interface-evidence" data-learning-context="career-interface-evidence" data-context-type="career" markdown="1">

## 用一次替换证明设计，而不是只画图

项目介绍可以这样组织：

> 报告统计与文本生成保持纯函数，应用流程只依赖一个 `ReportWriter` 协议；CLI 负责组装终端输出，测试传入内存 writer。替换输出方式不修改核心分析，mypy 验证回调签名，单元测试证明报告正文和输入只读契约保持不变。

如果被追问“为什么不用直接 print”，回答应落到变化和测试：直接打印会把业务结果与终端副作用绑在一起；返回字符串并把 writer 放在边界后，核心可以单独测试，输出也能替换。

同时说明克制：这个项目只有一个输出方法时，<code>Callable</code> 也能完成；使用命名协议是为了让业务角色和后续扩展更清楚，不是为了堆设计模式。

</section>

## 完成检查

- [ ] 我能用 `/` 与 `*` 解释三类参数调用方式。
- [ ] 我复现并修复了可变默认列表共享状态。
- [ ] 我能说明为什么核心计算优先返回值，而不是修改全局变量或直接打印。
- [ ] 我知道简单 `Callable` 与命名 `Protocol` 各自适合什么情况。
- [ ] 我用终端和内存 writer 跑过同一份报告流程。
- [ ] 我分别观察了位置参数、错误回调和循环导入的失败阶段。
- [ ] 我知道前导下划线与 `__all__` 不是权限控制。
- [ ] 我增加了新 writer，没有修改报告正文和分析函数。
- [ ] 我为当前报告器画出入口、应用、分析、报告和输出的依赖方向。
- [ ] 我能用代码替换、mypy 和测试证明接口设计，而不只展示架构图。

## 来源与版本

- 适用版本：Python 3.11 及以上；mypy 2.2.0 严格模式。
- 核查日期：2026-07-17。
- 事实来源：[Python 函数定义](https://docs.python.org/3.11/reference/compound_stmts.html#function-definitions)用于参数种类与默认值求值；[Python `typing.Protocol`](https://docs.python.org/3.11/library/typing.html#typing.Protocol)用于结构化接口；[Python 导入系统](https://docs.python.org/3.11/reference/import.html)用于模块加载和循环导入边界；[Python `__all__`](https://docs.python.org/3.11/tutorial/modules.html#importing-from-a-package)用于公开名称约定。
- 代码验证：仓库脚本运行严格 mypy、终端与内存 writer、关键字专用参数、可变默认值修复、错误协议非零退出，以及正式报告器 mypy、测试和依赖方向检查；不联网。

## 下一步

进入[容器协议、迭代器与生成器](03-iterables-iterators-generators.md)，比较可重复遍历的序列与只能向前消费一次的迭代器。

[进入下一课](03-iterables-iterators-generators.md){ .md-button .md-button--primary }
