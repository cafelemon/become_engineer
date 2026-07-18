<div class="be-tutor-mount" data-tutor-lesson="python-core-03" aria-hidden="true"></div>

<section id="overview-iterator" class="be-page-hero be-lesson-hero" data-learning-context="overview-iterator" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 核心 · 第三课 · 值什么时候才产生</span>

# Python 容器协议、迭代器与生成器

## 第一次有三项，第二次为什么空了

~~~python
iterator = iter([1, 2, 3])
print(list(iterator))
print(list(iterator))
~~~

~~~text
[1, 2, 3]
[]
~~~

列表还在，但这个迭代器已经走到终点。列表可以重新取得新的迭代器；同一个迭代器通常只会向前走一次。

<div class="be-page-actions" markdown="1">
[手动推进一个迭代器](#concept-iteration-protocol){ .md-button .md-button--primary }
[运行惰性筛选例子](#reproduce-lazy-pipeline){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 核心 · 3 / 5</strong></div>
  <div><span>前置</span><strong>函数接口、容器、循环、类型提示和异常</strong></div>
  <div><span>完成后留下</span><strong>惰性筛选、单次消费记录和有界生成器</strong></div>
</div>

## 开始前

- 能用 `for` 遍历列表，并写带返回值的函数。
- 知道接口类型应表达函数真正需要的操作。
- 本课只使用标准库；不要求先学 C++ 迭代器。
- 准备亲手调用几次 `next()`，只读结果很难建立消费直觉。

<section id="concept-iteration-protocol" data-learning-context="concept-iteration-protocol" data-context-type="concept" markdown="1">

## for 循环怎样知道该停了

~~~mermaid
flowchart LR
    A["可迭代对象"] -->|"iter(source)"| B["迭代器：保存当前位置"]
    B -->|"next(iterator)"| C{"还有值吗"}
    C -->|有| D["返回一个值并暂停"]
    D --> B
    C -->|没有| E["StopIteration"]
    E --> F["for 循环正常结束"]
~~~

手动走一次：

~~~python
courses = ["Python", "CS"]
iterator = iter(courses)

print(next(iterator))
print(next(iterator))
print(next(iterator, "没有更多课程"))
~~~

不提供默认值时，第三次 `next()` 会抛出 `StopIteration`。这不是业务故障，而是协议表示“已经耗尽”的方式；`for` 循环会接住它并正常结束。

</section>

<section id="concept-iterable-iterator" data-learning-context="concept-iterable-iterator" data-context-type="concept" markdown="1">

## 容器和迭代器不是同一个角色

| 对象 | 可交给 `iter()` | 可交给 `next()` | 通常能重新遍历 | 保存本次位置 |
| --- | --- | --- | --- | --- |
| `list`、`tuple`、`str` | 是 | 否 | 是 | 否 |
| 列表迭代器 | 是 | 是 | 否 | 是 |
| 生成器对象 | 是 | 是 | 否 | 是 |

~~~python
values = [10, 20]
first = iter(values)
second = iter(values)

print(first is second)        # False
print(iter(first) is first)   # True
~~~

容器保存数据；迭代器保存一次遍历的状态。需要重走时，重新从容器调用 `iter()`，或重新调用生成器函数创建新对象。

</section>

<section id="concept-generator" data-learning-context="concept-generator" data-context-type="concept" markdown="1">

## yield 会把函数暂停在中间

~~~python
from collections.abc import Iterator


def trace_courses() -> Iterator[str]:
    print("开始执行")
    yield "Python"
    print("继续执行")
    yield "CS"
~~~

调用 `trace_courses()` 只创建生成器，不会立刻打印。第一次 `next()` 才进入函数体，执行到 `yield` 后返回一个值，并保存局部变量与执行位置。

~~~mermaid
stateDiagram-v2
    [*] --> Created: 调用生成器函数
    Created --> Running: 第一次 next
    Running --> Suspended: 执行到 yield
    Suspended --> Running: 再次 next
    Running --> Closed: return 或函数结束
~~~

生成器耗尽后不会自动重启。惰性计算的异常也可能延后到某次消费才出现，所以测试要覆盖“创建”和“真正推进”两个时刻。

</section>

<section id="example-eager-lazy" data-learning-context="example-eager-lazy" data-context-type="example" markdown="1">

## 列表推导立刻算，生成器表达式按需算

~~~python
eager = [value * 2 for value in range(4)]
lazy = (value * 2 for value in range(4))
~~~

- `eager` 立即保存四个结果，可以反复读取。
- `lazy` 保存计算状态，消费到哪里算到哪里。
- `list(lazy)` 会物化剩余结果，同时耗尽这个生成器。

惰性不自动代表更快。少量结果要多次读取时，列表更直接；大量数据只需顺序处理一次时，生成器可以减少同时保存的中间结果。性能结论仍要测量，不能只看语法。

</section>

<section id="concept-iterator-types" data-learning-context="concept-iterator-types" data-context-type="concept" markdown="1">

## 类型签名要说明消费方式

~~~python
from collections.abc import Iterable, Iterator, Sequence
~~~

| 类型 | 承诺的能力 | 适合 |
| --- | --- | --- |
| `Iterable[T]` | 至少能取得迭代器并遍历 | 单次累计、筛选、转换 |
| `Iterator[T]` | 可直接 `next()`，保存消费状态 | 生成器返回值 |
| `Sequence[T]` | 长度、索引、稳定顺序 | 需要下标、切片或多次读取 |

~~~python
def positive(values: Iterable[int]) -> Iterator[int]:
    for value in values:
        if value > 0:
            yield value
~~~

若函数标成 `Iterable`，实现却偷偷调用 `len()`、索引或遍历两次，签名和真实需求就不一致。要么改成一次处理，要么在明确边界物化，要么把接口准确写成 `Sequence`。

</section>

<section id="troubleshoot-double-consume" data-learning-context="troubleshoot-double-consume" data-context-type="troubleshoot" markdown="1">

## 两次统计为什么第二次得到 0

~~~python
def broken_summary(values: Iterable[float]) -> tuple[float, int]:
    total = sum(values)
    count = sum(1 for _ in values)
    return total, count
~~~

列表会为两次遍历创建新迭代器，看不出问题；传入生成器时，第一次 `sum()` 已经耗尽它，第二次计数为 0。

能一次完成时，就只走一次：

~~~python
def one_pass_summary(values: Iterable[float]) -> tuple[float, int]:
    total = 0.0
    count = 0
    for value in values:
        total += value
        count += 1
    return total, count
~~~

如果后面确实要汇总、排序和筛选多次，在一个公开边界写出 `snapshot = list(values)`。物化不是失败，隐藏在多个深层函数里重复物化才难以理解和控制。

</section>

<section id="example-iteration-tools" data-learning-context="example-iteration-tools" data-context-type="example" markdown="1">

## 常用工具也有消费规则

`enumerate()` 增加编号，`zip()` 并排消费多个来源：

~~~python
names = ["Python", "CS"]
hours = [10.0, 8.0]

for index, (name, hour) in enumerate(zip(names, hours, strict=True), start=1):
    print(index, name, hour)
~~~

`strict=True` 会在长度不一致时抛出 `ValueError`，避免较长输入被悄悄截掉。

无限生成器必须配有有限消费者：

~~~python
from itertools import islice


def natural_numbers() -> Iterator[int]:
    value = 0
    while True:
        yield value
        value += 1


print(list(islice(natural_numbers(), 5)))
~~~

不要执行 `list(natural_numbers())`；它没有自然终点。

</section>

<section id="reproduce-lazy-pipeline" data-learning-context="reproduce-lazy-pipeline" data-context-type="reproduce" markdown="1">

## 看见生成器什么时候真正开始

~~~python
--8<-- "examples/python-core/iterators_generators.py"
~~~

~~~bash
.venv/bin/python -m mypy --strict site-src/examples/python-core/iterators_generators.py
python site-src/examples/python-core/iterators_generators.py
~~~

你应该看到：

~~~text
before=[]
first=Python
after_first=['start', 'Python']
remaining=['CS']
exhausted=[]
one_pass=(10.0, 2)
bounded=[0, 1, 2, 3, 4]
~~~

`before=[]` 证明创建生成器时来源还没执行；取得第一个匹配项后只推进到 Python；继续消费才找到 CS；最后一次再读取为空。

</section>

<section id="modify-incomplete-courses" data-learning-context="modify-incomplete-courses" data-context-type="modify" markdown="1">

## 增加“只看未完成课程”

写一个惰性函数：

~~~python
def iter_incomplete(records: Iterable[StudyRecord]) -> Iterator[StudyRecord]:
    ...
~~~

先写四个测试，再实现：

1. 创建后来源没有执行。
2. 第一次 `next()` 只推进到第一个未完成课程。
3. 结果按输入顺序产生。
4. 耗尽后再次消费为空，重新调用函数才能重走。

不要在函数内部先 `list(records)` 再筛选；那会失去惰性。也不要返回原记录后在调用者修改它，当前报告器的筛选接口应保留副本隔离。

</section>

<section id="project-reporter-iterator" data-learning-context="project-reporter-iterator" data-context-type="project" markdown="1">

## 找到报告器唯一的物化边界

当前报告器已经有 `iter_by_tag()`、`iter_progress_rows()` 和接受 `Iterable[StudyRecord]` 的 `build_report()`。审阅这条路径：

~~~text
任意 Iterable
    -> build_report() 入口复制为 snapshot
    -> summarize / sort / tag filter / progress rows
    -> 固定报告文字
~~~

报告生成需要汇总、排序和筛选多次读取，所以在入口只物化一次是有意设计。检查更深层函数没有各自再次 `list()`，并运行当前 30 项测试，确认：

- 列表、元组和一次性生成器都能生成相同报告。
- 惰性筛选在 `next()` 前不执行。
- 同一生成器只消费一次。
- 排序和筛选不修改原始记录。

本课不修改 C++ 输出，也不改变公开报告。新增的 `iter_incomplete()` 先作为 Python 内部视图和测试存在。

</section>

<section id="deepen-lazy-cost" data-learning-context="deepen-lazy-cost" data-context-type="deepen" markdown="1">

## 惰性把成本推迟了，也把失败推迟了

生成器可以减少中间存储，并在只取前几项时避免多余计算；代价是执行时机不再等于创建时机，异常、文件读取和网络请求也可能在后续某次 `next()` 才发生。

设计惰性接口时要写清：

- 谁拥有并消费迭代器。
- 是否允许只消费一部分。
- 失败发生在创建还是推进阶段。
- 何时关闭文件、连接等资源。
- 调用者是否需要再次遍历。

下一课的上下文管理会继续处理资源生命周期。惰性生成器若包着文件句柄，更不能只看“省内存”就忽略关闭时机。

</section>

<section id="career-iterator-evidence" data-learning-context="career-iterator-evidence" data-context-type="career" markdown="1">

## 讲惰性处理时，说明消费次数

项目表达可以是：

> 报告器接受任意 `Iterable`，在需要多次分析的报告入口只物化一次；标签筛选与进度行使用 `Iterator` 按需产生。测试证明生成器在首次 `next()` 前不执行、耗尽后不重启、无限来源由 `islice` 限制，并保持列表、元组和一次性生成器输出一致。

若被问“为什么不全用生成器”，回答应承认取舍：结果很少且要反复读取时列表更简单；惰性适合大来源、流水处理或提前停止，但需要更严格地管理消费和资源边界。

</section>

## 完成检查

- [ ] 我能区分容器、`Iterable`、`Iterator` 和生成器。
- [ ] 我手动调用过 `iter()`、`next()`，并观察 `StopIteration` 或默认值。
- [ ] 我证明列表可创建新迭代器，同一个迭代器耗尽后不会重启。
- [ ] 我知道生成器函数在调用时创建对象、在消费时才执行。
- [ ] 我能按真实需求选择 `Iterable`、`Iterator` 或 `Sequence`。
- [ ] 我复现并修复了重复消费造成的错误计数。
- [ ] 我使用 `zip(strict=True)` 和 `islice` 建立消费边界。
- [ ] 我运行了惰性筛选例子和严格 mypy 检查。
- [ ] 我实现并测试了 `iter_incomplete()`，没有隐藏物化。
- [ ] 我确认报告器只有一个明确物化边界，30 项测试保持通过。

## 来源与版本

- 适用版本：Python 3.11 及以上；mypy 2.2.0 严格模式。
- 核查日期：2026-07-17。
- 事实来源：[Python 迭代器类型](https://docs.python.org/3.11/library/stdtypes.html#iterator-types)用于 `iter()`、`next()`、耗尽和生成器行为；[Python 表达式参考](https://docs.python.org/3.11/reference/expressions.html#generator-expressions)用于生成器表达式；[`collections.abc`](https://docs.python.org/3.11/library/collections.abc.html)用于 `Iterable`、`Iterator` 与 `Sequence`；[`itertools.islice`](https://docs.python.org/3.11/library/itertools.html#itertools.islice)用于有限消费。
- 代码验证：仓库脚本覆盖惰性启动、单次消费、重新创建、一遍汇总、标签筛选、`zip(strict=True)`、无限来源限制、输入不变、严格 mypy 和正式项目 30 项测试；不联网。

## 下一步

进入[数据模型、数据类与上下文管理](04-data-model-dataclasses-context-managers.md)，把类型化字典迁移为有行为的对象，并明确文件资源何时打开和关闭。

[进入下一课](04-data-model-dataclasses-context-managers.md){ .md-button .md-button--primary }
