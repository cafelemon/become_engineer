<div class="be-tutor-mount" data-tutor-lesson="python-core-04" aria-hidden="true"></div>

<section id="overview-object" class="be-page-hero be-lesson-hero" data-learning-context="overview-object" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 核心 · 第四课 · 让数据拥有自己的行为</span>

# Python 数据模型、数据类与上下文管理

## 同一条记录，哪种写法更像它本来的样子

~~~python
print(record["course_name"])
print(record.course_name)
print(record.progress)
~~~

字典能保存字段；对象还能说明这些字段之间怎样计算、怎样修改、怎样复制。最后一行的 `progress` 不是额外保存的数据，而是对象根据计划和完成小时算出的结果。

这节课还会把记录写进审计文件。文件只在 `with` 代码块里打开，离开时由 Python 负责关闭。

<div class="be-page-actions" markdown="1">
[看看数据类替你写了什么](#concept-dataclass){ .md-button .md-button--primary }
[运行完整小例子](#reproduce-record-audit){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 核心 · 4 / 5</strong></div>
  <div><span>前置</span><strong>类型提示、函数接口、迭代器、文件与异常</strong></div>
  <div><span>完成后留下</span><strong>有行为的学习记录、隔离的副本与审计文件</strong></div>
</div>

## 开始前

- 能读懂带类型标注的类和函数。
- 知道 `Iterable` 可能是列表，也可能是只能消费一次的生成器。
- 能用 `unittest` 检查正常路径和失败路径。
- 本课只用 Python 3.11 标准库；不要求先学 C++ 对象或 RAII。

<section id="concept-object-boundary" data-learning-context="concept-object-boundary" data-context-type="concept" markdown="1">

## 字典描述形状，对象还可以承担行为

上一课使用 `TypedDict` 描述学习记录：

~~~python
class StudyRecordDict(TypedDict):
    course_name: str
    target_hours: float
    completed_hours: float
    tags: list[str]
~~~

它告诉 mypy 有哪些键，但运行时仍是普通字典。计算进度、更新小时和复制标签的代码只能散落在外部函数中。

数据类把同一组字段变成实例：

~~~python
record = StudyRecord("Python 起步", 10.0, 7.5, ["python"])
print(record.course_name)
record.add_completed_hours(2.5)
~~~

这不是说“所有函数都应该塞进类”。只依赖一条记录、并且能用记录自己的字段讲清楚的行为，才适合放回对象。跨多条记录的排序、汇总和报告生成仍留在独立模块。

</section>

<section id="concept-dataclass" data-learning-context="concept-dataclass" data-context-type="concept" markdown="1">

## 数据类替你补齐重复代码

~~~python
from dataclasses import dataclass, field


@dataclass
class StudyRecord:
    course_name: str
    target_hours: float
    completed_hours: float
    tags: list[str] = field(default_factory=list)
~~~

`@dataclass` 会根据字段生成常用的初始化、显示和相等比较方法：

~~~python
first = StudyRecord("Python", 10.0, 7.5)
second = StudyRecord("Python", 10.0, 7.5)

print(first)
print(first == second)  # True
~~~

它仍然是普通 Python 类。字段后的类型标注供静态工具检查，不会自动拒绝来自 JSON 或网络的错误值；外部输入仍要在进入对象之前验证。

</section>

<section id="example-properties-methods" data-learning-context="example-properties-methods" data-context-type="example" markdown="1">

## 进度是属性，增加小时是动作

进度和状态都能从当前字段算出，不必再保存一份可能过期的值：

~~~python
@property
def progress(self) -> float:
    if self.target_hours <= 0.0:
        return 0.0
    raw = self.completed_hours / self.target_hours
    return min(max(raw, 0.0), 1.0)

@property
def status(self) -> str:
    return "已完成" if self.completed_hours >= self.target_hours else "进行中"
~~~

`record.progress` 看起来像字段，读取时却会重新计算。它不是缓存。

修改已经完成的小时数是一项动作，用方法表达更清楚：

~~~python
def add_completed_hours(self, additional_hours: float) -> None:
    if additional_hours < 0.0:
        raise ValueError("增加的小时数不能为负数")
    self.completed_hours += additional_hours
~~~

这里增加了负数检查，因为方法不该让记录从 7.5 小时倒退到 5 小时。若业务真的需要撤销记录，应给它单独命名，而不是偷偷复用“增加”。

</section>

<section id="troubleshoot-mutable-default" data-learning-context="troubleshoot-mutable-default" data-context-type="troubleshoot" markdown="1">

## 空列表为什么不能直接写在字段后面

故意试一次错的：

~~~python
@dataclass
class BadRecord:
    tags: list[str] = []
~~~

Python 3.11 会在定义数据类时拒绝这个写法，并提示使用 `default_factory`。原因是列表会被复用，多条记录可能拿到同一个对象。

~~~python
tags: list[str] = field(default_factory=list)
~~~

`default_factory=list` 会在每次创建实例时调用一次 `list()`：

~~~python
first = StudyRecord("Python", 10.0, 7.5)
second = StudyRecord("C++", 12.0, 12.0)
first.tags.append("基础")

assert second.tags == []
~~~

这里检查的是两个对象是否互不影响，不需要拿内存地址截图来证明。

</section>

<section id="concept-copy-boundary" data-learning-context="concept-copy-boundary" data-context-type="concept" markdown="1">

## 复制对象时，里面的列表也要单独处理

`dataclasses.replace()` 会新建一层对象，但不会自动深复制里面的列表：

~~~python
from dataclasses import replace


def clone(self) -> StudyRecord:
    return replace(self, tags=list(self.tags))
~~~

如果只写 `replace(self)`，原记录和副本仍指向同一个 `tags`。显式复制列表以后，下面的检查才会通过：

~~~python
original = StudyRecord("Python", 10.0, 7.5, ["基础"])
copied = original.clone()
copied.tags.append("重点")

assert original.tags == ["基础"]
~~~

这只是针对当前模型的一层复制。以后字段里再出现字典或嵌套对象，要重新决定哪些内容共享、哪些内容隔离，不能把 `replace()` 当成通用深复制。

</section>

<section id="concept-with-protocol" data-learning-context="concept-with-protocol" data-context-type="concept" markdown="1">

## with 把打开和关闭放在同一个范围里

~~~python
with output_path.open("w", encoding="utf-8") as output:
    output.write("学习审计快照\n")
    output.write("Python 起步\t10\t7.5\n")
~~~

`with` 进入代码块时取得文件对象，离开代码块时执行退出逻辑。正常写完会关闭；块内抛出异常也会先走退出流程，再决定异常是否继续传播。

~~~mermaid
flowchart LR
    A["调用 open()"] --> B["进入 with，得到 output"]
    B --> C["在代码块内写入"]
    C --> D{"正常结束或发生异常"}
    D --> E["退出 with，关闭文件"]
    E --> F["继续后续代码或传播异常"]
~~~

上下文管理负责资源何时释放；它不会替业务决定“写失败以后返回什么”。本课的审计函数捕获 `OSError` 并返回 `False`，这是接口约定，不是 `with` 自动完成的事。

</section>

<section id="reproduce-record-audit" data-learning-context="reproduce-record-audit" data-context-type="reproduce" markdown="1">

## 跑一遍对象和文件的完整过程

~~~python
--8<-- "examples/python-core/dataclasses_contexts.py"
~~~

~~~bash
.venv/bin/python -m mypy --strict site-src/examples/python-core/dataclasses_contexts.py
python site-src/examples/python-core/dataclasses_contexts.py
~~~

你应该看到：

~~~text
before=75.0% 进行中
after=100.0% 已完成
original_tags=['基础']
copied_tags=['基础', '重点']
audit_ok=True
audit_closed=True
missing_parent=False
~~~

`original_tags` 和 `copied_tags` 不同，说明副本的列表已经隔离；`audit_closed=True` 说明离开 `with` 后文件确实关闭；缺失父目录稳定走失败分支。

</section>

<section id="troubleshoot-audit-failure" data-learning-context="troubleshoot-audit-failure" data-context-type="troubleshoot" markdown="1">

## 文件没有生成，先看路径和返回值

审计函数只处理预期的文件系统错误：

~~~python
def write_audit_snapshot(
    records: Iterable[StudyRecord], output_path: Path
) -> bool:
    snapshot = [record.clone() for record in records]
    try:
        with output_path.open("w", encoding="utf-8") as output:
            ...
    except OSError:
        return False
    return True
~~~

用临时目录分别测试：

- `root / "audit.txt"`：父目录存在，文件应写成。
- `root / "missing" / "audit.txt"`：不要创建 `missing`，函数应返回 `False`。

不要依赖“把目录权限改坏”做测试，不同系统和用户权限会让结果漂移。也不要捕获所有 `Exception`，那会把拼写错误、类型错误等程序缺陷一起藏起来。

</section>

<section id="modify-remaining-progress" data-learning-context="modify-remaining-progress" data-context-type="modify" markdown="1">

## 增加“还差多少”

给 `StudyRecord` 增加一个只读属性：

~~~python
@property
def remaining_progress(self) -> float:
    ...
~~~

先写四组检查，再补实现：

| 计划小时 | 完成小时 | 应得到 |
| ---: | ---: | ---: |
| 10 | 7.5 | `0.25` |
| 10 | 10 | `0.0` |
| 10 | 12 | `0.0` |
| 0 | 0 | `1.0` 或项目另行说明的明确约定 |

前三组不应出现负数。零计划怎样解释没有唯一答案，但你的代码、测试和页面说明必须一致。完成后再给审计快照增加状态列，确认主报告文本没有跟着改变。

</section>

<section id="project-reporter-objects" data-learning-context="project-reporter-objects" data-context-type="project" markdown="1">

## 回到学习进度报告器

当前正式项目已经使用 `StudyRecord` 和 `StudySummary` 数据类，并有 30 项测试。检查这条关系：

~~~text
外部数据
  -> 在输入边界验证并创建 StudyRecord
  -> 对象提供 progress / status / clone / add_completed_hours
  -> analysis.py 负责多记录汇总和筛选
  -> reporting.py 保持公开报告文字
~~~

项目的审计写入还比本课小例子多走了一步：它先取得临时路径，写完后再替换正式文件。这是下一课的自定义上下文管理器内容。此处只需找到内层 `with pending_path.open(...)`，说明文件对象仍然怎样被关闭；不要为了配合本课而把项目退回直接覆盖正式文件的旧版本。

在项目目录运行：

~~~bash
python -m mypy --strict .
PYTHONPATH=src python -m unittest discover -s tests -v
python main.py
~~~

确认 30 项测试通过，主报告仍以“学习进度报告”开头，总体进度保持 `87.1%`，审计成功和缺失父目录失败都有测试。

</section>

<section id="deepen-data-model" data-learning-context="deepen-data-model" data-context-type="deepen" markdown="1">

## dataclass 没有替你设计对象

数据类减少了样板代码，却不会回答这些问题：

- 哪些字段可以修改，哪些应只读。
- 两个对象相等到底意味着什么。
- 复制时哪些嵌套值共享，哪些隔离。
- 外部数据在哪里验证。
- 一个行为属于单条记录，还是跨记录服务。

对象设计的重点仍是职责和约束。`frozen=True`、`slots=True`、自定义 `__post_init__()` 和手写上下文管理协议都有适用场景，但不应在没有问题需要解决时一次堆进来。

</section>

<section id="career-object-evidence" data-learning-context="career-object-evidence" data-context-type="career" markdown="1">

## 讲对象化时，别只说“代码更优雅”

更有说服力的项目表达是：

> 我把报告器的记录从类型化字典迁移成数据类。单记录的进度、状态、复制和修改由对象负责，跨记录汇总仍留在分析模块。测试覆盖了可变默认值隔离、克隆列表隔离、零计划边界、审计写入成功和缺失父目录失败；迁移前后公开报告保持一致。

这段话能让人追问设计、失败路径和验证方法。只说“使用了 dataclass 和 with”只能列出技术名词，不能说明你解决了什么。

</section>

## 完成检查

- [ ] 我能说明 `TypedDict` 与数据类各自提供什么。
- [ ] 我知道 `@dataclass` 生成哪些常用方法，也知道它不负责运行时输入验证。
- [ ] 我把只依赖单条记录的进度和状态放回对象，没有把所有函数都搬进去。
- [ ] 我用两个实例证明 `default_factory` 不共享列表。
- [ ] 我修改副本的标签后，原对象保持不变。
- [ ] 我能解释 `with` 负责资源释放，`try/except` 负责接口的错误约定。
- [ ] 我跑过独立例子，并看到成功写入、文件关闭和缺失父目录失败。
- [ ] 我完成了 `remaining_progress` 及边界测试。
- [ ] 我没有把当前正式项目退回旧版本，30 项测试仍然通过。

## 来源与版本

- 适用版本：Python 3.11 及以上；mypy 2.2.0 严格模式。
- 核查日期：2026-07-17。
- 事实来源：[Python `dataclasses`](https://docs.python.org/3.11/library/dataclasses.html)用于生成方法、`field()`、`replace()` 和可变默认值；[Python 数据模型](https://docs.python.org/3.11/reference/datamodel.html)用于类、实例、属性和上下文管理协议；[Python `with` 语句](https://docs.python.org/3.11/reference/compound_stmts.html#the-with-statement)用于进入、退出和异常传播顺序；[`contextlib`](https://docs.python.org/3.11/library/contextlib.html)只用于说明下一课的扩展方向。
- 代码验证：仓库脚本覆盖数据类相等与显示、属性和方法、可变默认值隔离、克隆隔离、审计成功、文件关闭、缺失父目录失败、严格 mypy 和正式项目 30 项测试；不联网。

## 下一步

进入[装饰器、闭包与自定义上下文管理器](05-decorators-closures-custom-context-managers.md)，给函数加上可组合的调用追踪，并把“先写临时文件，成功后再替换”封装成清楚的资源边界。
