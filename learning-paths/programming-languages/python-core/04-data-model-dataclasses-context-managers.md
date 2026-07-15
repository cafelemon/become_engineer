# Python 数据模型、数据类与上下文管理

<div class="be-tutor-mount" data-tutor-lesson="python-core-04" aria-hidden="true"></div>

> **任务先行：** 把双语言学习进度报告器从“字典里装字段”升级为“对象自己表达状态和行为”，再用 `with` 写出审计快照。先看到报告与文件，再解释数据类、对象方法和上下文管理协议。

## 任务路线

<div class="be-task-route" role="list" aria-label="本课五步任务"><span role="listitem">1 基线</span><span role="listitem">2 数据类</span><span role="listitem">3 方法</span><span role="listitem">4 失败实验</span><span role="listitem">5 with</span></div>

<section id="step-1" class="be-task-step" data-step-id="step-1" markdown="1">

## 第一步：运行字典模型基线

运行 mypy、unittest 和报告器，确认已有 `TypedDict` 版本的类型检查、13 类行为和标准输出。**可观察结果：** 报告仍以“学习进度报告”开头，总体进度为 `87.1%`。

</section>

<section id="step-2" class="be-task-step" data-step-id="step-2" markdown="1">

## 第二步：把记录迁移为数据类对象

使用 `@dataclass` 定义 `StudyRecord` 和 `StudySummary`，把 `record["course_name"]` 改为 `record.course_name`。**成功标准：** 构造、汇总、排序、筛选与报告测试全部通过，公开报告一字不变。

</section>

<section id="step-3" class="be-task-step" data-step-id="step-3" markdown="1">

## 第三步：让对象提供进度、状态、复制和修改行为

为 `StudyRecord` 增加 `progress`、`status`、`clone()` 和 `add_completed_hours()`。主动把 Python 起步从 `7.5` 小时更新到 `10.0` 小时。**成功标准：** 原对象状态变为“已完成”，复制对象的标签修改不会污染原对象。

</section>

<section id="step-4" class="be-task-step" data-step-id="step-4" markdown="1">

## 第四步：触发可变默认值失败并修复

临时把 `tags` 写成共享列表默认值，观察数据类在类定义阶段拒绝这个危险默认值；恢复 `field(default_factory=list)`。**验收：** 两个新建对象拥有不同标签列表，不通过垃圾回收或偶然运行结果判断正确性。

</section>

<section id="step-5" class="be-task-step" data-step-id="step-5" markdown="1">

## 第五步：用 with 导出审计快照并迁移验收

实现 `write_audit_snapshot()`，用 `with output_path.open(...)` 管理文件。验证成功文件和缺失父目录两条路径。**迁移任务：** 独立增加审计状态列或一种对象方法，同时保持 Python/C++ 主报告逐字一致。

</section>

上一节 C++ 课程用引用、非拥有指针和 `std::ofstream` 建立了对象与资源边界。Python 不要求学习者机械翻译 C++ 写法：本节用数据类表达对象，用普通引用语义调用方法，并用 `with` 管理文件资源。

## 课程信息

| 项目 | 内容 |
| --- | --- |
| 适合人群 | 已完成 Python 迭代器课程与 C++ RAII 课程，需要从结构化字典进入对象设计的学习者 |
| 前置知识 | `TypedDict`、类型提示、函数、模块、迭代器、文件与异常、mypy、unittest |
| 可观察产出 | 数据类报告器、对象方法测试、审计快照文件和稳定的双语言主报告 |
| 环境 | Python 3.11 及以上，仅使用标准库；mypy strict 与 unittest |
| 阶段作品 | [双语言学习进度报告器](../../../exercises/programming-languages/study-progress-reporters/README.md) |
| 事实核查 | Python 3.11.15 官方文档，2026-07-15 核查 |

## 学习目标

完成本节后，你应该能够：

- 说明类、实例、属性和方法在当前报告器中的具体作用。
- 使用 `@dataclass` 生成初始化、显示和相等比较所需的基础行为。
- 使用 `field(default_factory=list)` 避免多个实例共享可变默认值。
- 把属于记录自身的进度、状态、复制和更新行为放回对象。
- 用 `with` 管理文件的进入与退出，并区分资源释放和错误处理。
- 审阅 AI 是否引入共享列表、浅复制污染、吞掉异常或改变报告契约。

## 第一步：保存可回归的字典模型基线

从阶段作品的 Python 目录执行：

```bash
python -m mypy --strict .
python -m unittest discover -s tests -v
python main.py
```

迁移前后的核心证据都应包含下面这段输出：

```text
学习进度报告
总计划：35.0 小时
总完成：30.5 小时
总体进度：87.1%
```

原来的 `TypedDict` 只为字典访问提供静态形状：

```python
class StudyRecord(TypedDict):
    course_name: str
    target_hours: float
    completed_hours: float
    tags: list[str]
```

运行时仍然是普通字典，字段读取使用 `record["course_name"]`。数据类迁移的目标不是减少几个括号，而是让“记录是什么、能做什么、如何复制”集中在一个对象边界里。

## 第二步：用数据类建立对象边界

在 `models.py` 中定义记录：

```python
from __future__ import annotations

from dataclasses import dataclass, field, replace


@dataclass
class StudyRecord:
    course_name: str
    target_hours: float
    completed_hours: float
    tags: list[str] = field(default_factory=list)
```

`@dataclass` 会根据类型标注生成常用初始化、显示和相等比较行为。它仍然是普通 Python 类；类型标注不会自动验证网络或 JSON 输入，也不会自动让可变字段变成不可变。

样例数据从字典字面量变成显式实例：

```python
def sample_records() -> list[StudyRecord]:
    return [
        StudyRecord("Python 起步", 10.0, 7.5, ["python", "基础"]),
        StudyRecord("C++ 核心", 12.0, 12.0, ["cpp", "基础"]),
        StudyRecord("算法练习", 8.0, 4.0, ["算法", "基础", "基础"]),
        StudyRecord("工程复盘", 5.0, 7.0, ["工程", "复盘"]),
    ]
```

汇总结果也可以是数据类：

```python
@dataclass
class StudySummary:
    total_target_hours: float
    total_completed_hours: float
    status_counts: dict[str, int]
    unique_tags: set[str]
```

迁移时逐类替换访问方式：

| 字典模型 | 数据类对象 |
| --- | --- |
| `record["course_name"]` | `record.course_name` |
| `summary["status_counts"]` | `summary.status_counts` |
| 字典字面量 | `StudyRecord(...)` |
| 手工复制所有键 | 对象的 `clone()` |

不要一次删除所有旧访问再猜哪里遗漏。每迁移一个模块就运行 mypy；它会把仍在下标访问对象的位置列出来。

## 第三步：把与记录相关的行为放回对象

进度和状态直接依赖记录字段，放在对象上能让调用者只表达意图：

```python
@property
def progress(self) -> float:
    if self.target_hours <= 0.0:
        return 0.0
    raw_progress = self.completed_hours / self.target_hours
    return min(max(raw_progress, 0.0), 1.0)

@property
def status(self) -> str:
    return "已完成" if self.completed_hours >= self.target_hours else "进行中"
```

`property` 让只读计算仍通过 `record.progress` 访问。它不是缓存：每次读取都会根据当前字段重新计算。

对象修改方法表达“修改这一条已存在的记录”：

```python
def add_completed_hours(self, additional_hours: float) -> None:
    self.completed_hours += additional_hours
```

主动修改与验收：

```python
record = StudyRecord("Python 起步", 10.0, 7.5)
assert record.progress == 0.75
assert record.status == "进行中"

record.add_completed_hours(2.5)
assert record.completed_hours == 10.0
assert record.status == "已完成"
```

筛选函数承诺返回独立记录，因此只复制对象外壳不够；`tags` 列表也要复制：

```python
def clone(self) -> StudyRecord:
    return replace(self, tags=list(self.tags))
```

这是一层针对当前模型的复制。未来若字段里再放入字典或嵌套对象，需要重新审查复制边界，不能把 `replace()` 当作通用深复制。

## 第四步：安全观察可变默认值失败

下面的类定义是失败实验，只在临时文件或交互环境中运行：

```python
from dataclasses import dataclass


@dataclass
class BadRecord:
    tags: list[str] = []
```

Python 3.11 的数据类会拒绝这个可变默认值并提示使用 `default_factory`。即使在非数据类代码中绕过了检查，共享列表也会让一个实例的修改出现在另一个实例里。

恢复安全写法：

```python
from dataclasses import dataclass, field


@dataclass
class StudyRecord:
    course_name: str
    target_hours: float
    completed_hours: float
    tags: list[str] = field(default_factory=list)
```

测试必须观察两个实例：

```python
first = StudyRecord("Python", 10.0, 7.5)
second = StudyRecord("C++", 12.0, 12.0)
first.tags.append("基础")
assert second.tags == []
```

`default_factory` 每次构造实例都会调用一次 `list`，所以两个对象得到不同列表。这个结论由对象行为测试证明，不依赖内存地址截图。

## 第五步：用 with 管理审计文件

与 C++ 课程保持同一审计格式：标题后每行包含课程名、计划小时和完成小时。接口接受任何 `Iterable[StudyRecord]` 和明确的 `Path`：

```python
from collections.abc import Iterable
from pathlib import Path


def write_audit_snapshot(
    records: Iterable[StudyRecord], output_path: Path
) -> bool:
    snapshot = [record.clone() for record in records]
    try:
        with output_path.open("w", encoding="utf-8") as output:
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

`with` 会调用上下文管理器的进入和退出协议。文件离开代码块时关闭，即使块内发生异常也会执行退出逻辑；`try/except OSError` 仍然负责把打开或写入失败转换为本课程约定的 `False`。

成功路径使用临时目录验证真实内容：

```python
with TemporaryDirectory() as directory:
    audit_path = Path(directory) / "audit.txt"
    assert write_audit_snapshot(sample_records(), audit_path)
    assert "Python 起步\t10\t7.5" in audit_path.read_text(encoding="utf-8")
```

失败路径不能先创建父目录：

```python
with TemporaryDirectory() as directory:
    missing_path = Path(directory) / "missing" / "audit.txt"
    assert not write_audit_snapshot(sample_records(), missing_path)
```

本函数返回布尔值是为了与 C++ 阶段作品保持简单对照。真实应用通常还需要记录具体路径和错误原因；不要在更复杂系统中无条件吞掉所有 `OSError`。

### 迁移验收

独立完成下面任意一项：

1. 为审计快照增加状态列，并让 Python 与 C++ 审计格式保持一致。
2. 为 `StudyRecord` 增加一个不突破 `0.0` 到 `1.0` 的剩余进度属性及边界测试。
3. 让调用者在导出失败时打印明确路径，但主报告标准输出仍保持原契约。

完成后依次运行 mypy、unittest、Python 应用和 C++ 应用，并比较两份主报告。

## AI 协作任务

可以让 AI 提供字典到数据类的迁移清单和测试候选，但必须人工检查：

- 是否把所有下标访问迁移为对象属性，而没有用 `Any` 绕过 mypy。
- 是否给 `tags` 使用了 `default_factory`，复制时是否复制了列表。
- 是否把所有函数机械搬成方法，造成对象职责膨胀。
- 是否在 `with` 之外继续使用已关闭文件。
- 是否过宽捕获 `Exception`，或改变双语言主报告文本。

可复用提示：

```text
请把一个包含 course_name、target_hours、completed_hours 和 tags 的 TypedDict
迁移为 Python 3.11 dataclass。必须保留现有报告字符串和 Iterable 输入能力，
tags 不能在实例间共享；请列出需要修改的访问点、测试和失败风险，不要使用 Any 或 ignore。
```

## 常见错误与排查

| 现象 | 可能原因 | 检查与修复 |
| --- | --- | --- |
| mypy 提示对象不可下标 | 仍在使用 `record["..."]` | 改为属性访问，并检查汇总对象也已迁移 |
| 两条记录意外共享标签 | 使用了共享可变默认值 | 改为 `field(default_factory=list)` 并测试两个实例 |
| 筛选后修改影响原输入 | `clone()` 只复制对象外壳 | 使用 `replace(self, tags=list(self.tags))` |
| 审计文件为空或未生成 | 路径错误、父目录不存在或写入失败 | 检查布尔返回值和具体路径，覆盖成功/失败测试 |
| 主报告与 C++ 不一致 | 数据访问或格式化规则被顺便修改 | 回到固定字符串测试，只迁移模型边界 |

## 完成证据

- mypy strict 无问题，13 个及以上 unittest 全部通过。
- 报告器接受列表、元组和单次迭代器，惰性筛选行为保持不变。
- 两个默认构造对象不共享 `tags`，克隆对象的标签修改不污染原对象。
- 审计成功与缺失父目录失败都有真实文件测试。
- Python 与 C++ 应用的主报告逐字一致。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [Python 数据类](https://docs.python.org/3.11/library/dataclasses.html) | `@dataclass`、`field`、`replace` 与可变默认值 | Python 3.11.15，2026-07-15 核查 |
| [Python 数据模型](https://docs.python.org/3.11/reference/datamodel.html) | 类、实例、属性、特殊方法和上下文管理器 | Python 3.11.15，2026-07-15 核查 |
| [with 语句](https://docs.python.org/3.11/reference/compound_stmts.html#the-with-statement) | 进入、退出与异常传播顺序 | Python 3.11.15，2026-07-15 核查 |
| [contextlib](https://docs.python.org/3.11/library/contextlib.html) | 上下文管理器类型与后续扩展边界 | Python 3.11.15，2026-07-15 核查 |

## 下一步

对象与资源的双语言基础配对已经完成。下一节进入 **[装饰器、闭包与自定义上下文管理器](05-decorators-closures-custom-context-managers.md)**，解释函数包装、`contextmanager()` 和自定义资源边界；本节不提前实现 `__enter__`、`__exit__`、`ExitStack` 或异步上下文管理。
