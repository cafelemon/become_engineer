<div class="be-tutor-mount" data-tutor-lesson="python-core-01" aria-hidden="true"></div>

<section id="overview-types" class="be-page-hero be-lesson-hero" data-learning-context="overview-types" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 核心 · 第一课 · 把接口说清楚</span>

# 类型提示、接口与静态检查认知

## 程序还没运行，检查器先发现了一处错误

~~~python
def calculate_progress(target_hours: float, completed_hours: float) -> float:
    return completed_hours / target_hours


calculate_progress("10", 7.5)
~~~

Python 解释器会等到除法发生时才报错；mypy 可以在运行前指出：第一个参数承诺是 <code>float</code>，这里却传入了 <code>str</code>。

~~~text
Argument 1 to "calculate_progress" has incompatible type "str"; expected "float"
~~~

类型提示不会把 Python 变成另一门语言。它更像写给调用者和检查器的一份接口说明：这里需要什么、会返回什么、哪些值可能缺失。

<div class="be-page-actions" markdown="1">
[先分清三层检查](#concept-three-checks){ .md-button .md-button--primary }
[运行类型契约例子](#reproduce-type-contracts){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 核心 · 1 / 5</strong></div>
  <div><span>前置</span><strong>Python 起步、JSON、异常和 unittest</strong></div>
  <div><span>完成后留下</span><strong>严格类型检查、JSON 校验和报告器接口清单</strong></div>
</div>

## 开始前

- 能运行多文件 Python 程序和 `unittest`。
- 知道外部 JSON 可能缺字段、写错类型或根本不是合法 JSON。
- 已完成 CS 起步，能把“数据怎样表示”和“接口允许哪些操作”分开考虑。
- 本课不要求先学 C++；以后并行学习时，再比较两种语言的检查时机。

<section id="concept-three-checks" data-learning-context="concept-three-checks" data-context-type="concept" markdown="1">

## 静态检查、运行时校验和测试各管一段

先看学习记录从文件走到报告的路径：

~~~mermaid
flowchart LR
    A["JSON 文件"] --> B["json.loads"]
    B --> C["object：先不相信结构"]
    C --> D["isinstance 与业务规则"]
    D --> E["StudyRecord"]
    E --> F["统计与报告"]
    M["mypy --strict"] -.检查代码接口.-> C
    M -.检查代码接口.-> E
    M -.检查代码接口.-> F
    T["unittest"] -.运行真实场景.-> D
    T -.运行真实场景.-> F
~~~

| 工具 | 擅长发现 | 不能替你证明 |
| --- | --- | --- |
| 类型提示与 mypy | 错参数、错返回值、漏字段、未处理的 `None` | 文件里的真实 JSON 一定正确 |
| 运行时校验 | 本次输入的结构、类型和业务范围 | 其他代码路径以后不会回归 |
| 自动化测试 | 固定场景的输出、异常和副作用 | 没覆盖的所有输入都正确 |

三层不能互相替代。mypy 通过不等于数据可信，测试通过也不等于接口表达清楚。

</section>

<section id="concept-annotations" data-learning-context="concept-annotations" data-context-type="concept" markdown="1">

## 注解不是门卫

这段代码虽然标了 <code>float</code>，运行时仍会把字符串原样传进去：

~~~python
def echo_hours(hours: float) -> float:
    return hours


result = echo_hours("five")
print(result, type(result))
~~~

直接运行会打印：

~~~text
five <class 'str'>
~~~

mypy 会报告调用和返回契约不一致，但 Python 解释器通常不会根据函数注解自动拦截调用。若输入来自用户、文件或网络，仍要在运行时检查。

类型提示的价值在于把预期写进代码，让编辑器、检查器、评审者和未来的你更早看见冲突，而不是替代所有防御代码。

</section>

<section id="example-common-types" data-learning-context="example-common-types" data-context-type="example" markdown="1">

## 先写出真实可能性

常见容器可以直接标出元素类型：

~~~python
course_names: list[str] = ["Python", "CS"]
hours_by_course: dict[str, float] = {"Python": 8.0, "CS": 6.0}
unique_tags: set[str] = {"语言", "工程"}
point: tuple[float, float] = (3.0, 4.0)
history: tuple[str, ...] = ("起步", "类型", "工程化")
~~~

<code>tuple[float, float]</code> 表示恰好两个位置；<code>tuple[str, ...]</code> 表示任意长度、每项都是字符串。

可能找不到时，把 <code>None</code> 写出来：

~~~python
def find_course(name: str) -> str | None:
    if name.casefold() == "python":
        return "Python"
    return None


course = find_course("python")
if course is not None:
    print(course.upper())
~~~

调用者看到 <code>str | None</code> 就知道必须处理缺失情况，不必等到某次 <code>None.upper()</code> 才发现。

复杂类型反复出现时，可以在 Python 3.11 中使用 <code>TypeAlias</code>：

~~~python
from typing import TypeAlias

ProgressRow: TypeAlias = tuple[str, float, str]
~~~

别名改善可读性，但不会创建新的运行时类。

</section>

<section id="concept-typeddict-sequence" data-learning-context="concept-typeddict-sequence" data-context-type="concept" markdown="1">

## 固定字典用 TypedDict，只读输入用 Sequence

学习记录仍是普通字典，但键名固定：

~~~python
from typing import TypedDict


class StudyRecord(TypedDict):
    course_name: str
    target_hours: float
    completed_hours: float
    tags: list[str]
~~~

mypy 能检查源码里看得见的构造位置：

~~~python
record: StudyRecord = {
    "course_name": "Python 核心",
    "target_hours": 10.0,
    "completed_hours": 4.0,
    # 漏了 tags，静态检查会报告错误
}
~~~

但运行时 <code>type(record)</code> 仍然是 <code>dict</code>。<code>TypedDict</code> 不会自动检查 <code>json.loads()</code> 的返回值。

如果函数只需要读取一组记录，不要把接口写死为 <code>list</code>：

~~~python
from collections.abc import Sequence


def total_completed(records: Sequence[StudyRecord]) -> float:
    return sum(record["completed_hours"] for record in records)
~~~

列表和元组都能满足这个接口。<code>Sequence</code> 表达“需要长度、索引和遍历”，并不声称对象在运行时绝对不可变。

</section>

<section id="concept-object-any-cast" data-learning-context="concept-object-any-cast" data-context-type="concept" markdown="1">

## object 会逼你检查，Any 会让检查器让路

<code>object</code> 表示“现在还不知道是什么”。使用前必须缩小类型：

~~~python
def normalize_name(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("course_name 必须是字符串")
    return value.strip()
~~~

<code>Any</code> 则会让大部分静态检查退出：

~~~python
from typing import Any


def unsafe_name(value: Any) -> str:
    return value.strip().method_that_does_not_exist()
~~~

这段明显可疑的调用也可能一路传播。动态库边界有时不得不用 <code>Any</code>，但应尽快把它收窄，不能用来让错误列表变成零。

<code>cast()</code> 只告诉检查器“请把它当作某类型”，不会转换或验证值：

~~~python
from typing import cast

value: object = 42
name = cast(str, value)
print(name.upper())  # 运行时仍然失败
~~~

同样，<code># type: ignore</code> 只是压住诊断。先问清接口是否写错、边界是否缺校验，再考虑极少数检查器确实无法推导的情况。

</section>

<section id="reproduce-type-contracts" data-learning-context="reproduce-type-contracts" data-context-type="reproduce" markdown="1">

## 从 object 收窄成可信记录

完整例子模拟 <code>json.loads()</code> 之后的未知对象，逐层检查，再构造 <code>StudyRecord</code>：

~~~python
--8<-- "examples/python-core/type_contracts.py"
~~~

先运行静态检查：

~~~bash
.venv/bin/python -m mypy --strict site-src/examples/python-core/type_contracts.py
~~~

再运行程序：

~~~bash
python site-src/examples/python-core/type_contracts.py
~~~

你应该看到：

~~~text
course=Python 核心
progress=40.0%
total_completed=10.0
tuple_input=6.0
~~~

严格检查证明代码接口前后一致；程序输出证明这组运行时数据通过校验并得到预期结果。两份结果缺一不可。

</section>

<section id="troubleshoot-mypy-json" data-learning-context="troubleshoot-mypy-json" data-context-type="troubleshoot" markdown="1">

## 让两种错误各自出现一次

第一种错误写在源码里：

~~~python
def progress_label(progress: float) -> str:
    return progress
~~~

mypy 应指出函数承诺返回 <code>str</code>，实际返回 <code>float</code>，并以非零状态结束。阅读诊断时别只看“失败”，至少找出文件、行号、错误类别、期望类型和实际类型。

第二种错误来自运行数据：

~~~python
raw: object = {
    "course_name": "Python 核心",
    "target_hours": "ten",
    "completed_hours": 4.0,
    "tags": ["python"],
}
~~~

这段变量故意标成 <code>object</code>，静态检查无法也不该猜测 JSON 内部一定正确。<code>validate_record(raw)</code> 必须在运行时拒绝字符串形式的目标小时。

修复源码错误后重跑 mypy；修复输入错误后重跑程序与测试。不要用 <code>Any</code>、<code>cast()</code> 或忽略注释把两类问题盖住。

</section>

<section id="modify-type-contract" data-learning-context="modify-type-contract" data-context-type="modify" markdown="1">

## 增加一条可选备注

给独立例子增加：

~~~python
weekly_note: str | None
~~~

这不是只改 <code>TypedDict</code> 一行。你还需要同步：

1. 运行时校验：字段缺失时是否允许，存在时是否必须为字符串。
2. 构造位置：每条 <code>StudyRecord</code> 都要满足新契约。
3. 输出行为：有备注时显示，没有时保持原报告不变。
4. 测试：至少覆盖字符串、<code>None</code> 和错误数字三种输入。

完成后让 mypy、正常运行和错误输入测试都通过。若只是把字段标成 <code>Any</code>，这次练习就没有解决问题。

</section>

<section id="project-reporter-types" data-learning-context="project-reporter-types" data-context-type="project" markdown="1">

## 给报告器画一张接口清单

仓库里的双语言学习进度报告器已经继续演进到数据类、生成器、上下文管理、CLI 和配置版本。本课**不要把当前项目倒退回 TypedDict**；独立例子代表类型化阶段的历史快照，正式项目只做回归和接口审计。

从当前 Python 项目选择四个公开边界，写下：

| 边界 | 输入 | 输出 | 谁负责运行时校验 | 是否修改输入 |
| --- | --- | --- | --- | --- |
| `summarize()` | `Iterable[StudyRecord]` | `StudySummary` | 调用前的数据入口 | 否 |
| `build_report()` | `Iterable[StudyRecord]` | `str` | 已接收可信对象 | 否 |
| `write_audit_snapshot()` | 记录与 `Path` | `bool` | 文件系统操作 | 否 |
| `main()` | CLI 参数 | 退出码 | CLI 和配置边界 | 否 |

然后运行项目当前的严格检查和全部测试，确认本课的接口理解没有破坏最终版本：

~~~bash
cd exercises/programming-languages/study-progress-reporters/python
../../../../.venv/bin/python -m mypy --strict .
../../../../.venv/bin/python -m unittest discover -s tests -v
~~~

路径以仓库根目录的虚拟环境为例；如果你在项目内另建环境，使用那个环境里的 Python。

</section>

<section id="deepen-structural-types" data-learning-context="deepen-structural-types" data-context-type="deepen" markdown="1">

## 类型应该表达需要的能力

把参数写成 <code>list[StudyRecord]</code> 往往只是照着当前调用者抄类型。更好的问题是：函数真正需要什么？

- 只遍历一次：后续会学习 <code>Iterable</code>。
- 需要多次遍历、长度和下标：<code>Sequence</code> 更准确。
- 需要修改列表：才要求 <code>list</code> 或更具体的可变接口。
- 只需要某个方法：后续会使用 <code>Protocol</code> 描述结构化能力。

越宽泛的接口不一定越好，越具体也不一定越安全。合适的接口应该刚好表达实现真正依赖的能力，同时让不必要的调用无法发生。

类型检查也有边界：它不能证明除数不为零、小时数一定非负、路径一定存在或报告百分比一定算对。这些仍属于业务规则与运行测试。

</section>

<section id="career-type-evidence" data-learning-context="career-type-evidence" data-context-type="career" markdown="1">

## “加了类型提示”还不算完整成果

项目表达时，比“我给 Python 代码加了注解”更有价值的是说明你解决了哪类接口问题：

> 我把外部 JSON 先收进 `object` 边界，经过字段和业务规则校验后才构造内部类型；模块接口使用 `Sequence`、`Iterable` 和明确返回类型，通过 mypy 严格模式、运行测试和错误输入测试分别验证静态契约与真实行为。类型化前后主报告保持一致。

若被追问“mypy 通过后为什么还要校验 JSON”，可以直接回答：静态检查分析的是代码里的类型关系，不会替我检查某次运行读到的外部内容；外部数据必须在信任边界执行运行时校验。

这里不要夸大成“消灭了所有类型错误”。更准确的说法是：缩小了动态数据传播范围，让一部分接口冲突提前暴露，并保留了运行时和测试层的防线。

</section>

## 完成检查

- [ ] 我能解释类型提示、mypy、运行时校验和 unittest 的分工。
- [ ] 我亲自证明过函数注解不会自动拦截错误参数。
- [ ] 我能写出容器、`X | None` 和 `TypeAlias` 的准确例子。
- [ ] 我知道 `TypedDict` 在运行时仍是普通字典。
- [ ] 我能说明何时用 `Sequence`，而不是把所有输入都写成 `list`。
- [ ] 我能区分 `object`、`Any` 和 `cast()`，没有用它们掩盖错误。
- [ ] 我运行了严格 mypy 检查和类型契约例子。
- [ ] 我分别复现了一次静态错误和一次坏 JSON 运行错误。
- [ ] 我增加了可选备注，并同步校验、构造、输出和测试。
- [ ] 我为当前报告器写下接口清单，并确认最终项目回归通过。

## 来源与版本

- 适用版本：Python 3.11 及以上；mypy 2.2.0 严格模式。
- 核查日期：2026-07-17。
- 事实来源：[Python `typing` 文档](https://docs.python.org/3.11/library/typing.html)用于类型提示、`TypedDict`、`TypeAlias`、`Any`、`cast()`和运行时边界；[Python `collections.abc`](https://docs.python.org/3.11/library/collections.abc.html)用于 `Sequence` 等容器接口；[mypy 类型提示速查](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)与[严格配置](https://mypy.readthedocs.io/en/stable/config_file.html)用于静态检查行为和命令。
- 代码验证：仓库脚本运行严格 mypy、正常记录、元组输入、坏字段、缺字段、布尔数字拒绝、输入不变和静态错误退出码；不联网。

## 下一步

进入[可维护函数接口、协议与模块边界](02-maintainable-function-interfaces-protocols-modules.md)，把单个类型标注扩展成模块之间可替换、可测试的公开接口。

[进入下一课](02-maintainable-function-interfaces-protocols-modules.md){ .md-button .md-button--primary }
