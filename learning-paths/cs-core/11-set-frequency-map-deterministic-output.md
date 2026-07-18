<div class="be-tutor-mount" data-tutor-lesson="cs-core-11" aria-hidden="true"></div>

<section id="overview-application-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-application-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">共同算法基础 · 第 7 课 · 可追踪哈希实验</span>

# 集合去重、频次映射与稳定输出

## 同一组数据，回答三个不同问题

```text
data：7, 3, 7, 9, 3
first_duplicate=7，visits=3
unique_in_order：7, 3, 9
frequencies：3=2, 7=2, 9=1
```

首个重复值看输入顺序；保序去重保留第一次出现的位置；频次报告按键排序。三个结果都用哈希容器加速，但输出顺序来自明确规则，不来自容器碰巧怎样遍历。

[看一次完整扫描](#example-scan-trace){ .md-button .md-button--primary }
[直接运行小例子](#reproduce-applications-micro){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>共同算法基础 · 7 / 16</strong></span><span>前置<strong>分离链接、负载与扩容</strong></span><span>完成后留下<strong>首重复、保序唯一值和排序频次</strong></span></div>

</section>

## 开始前

- 能说清集合保存成员关系，映射保存键与值的关联。
- 已经知道哈希只缩小候选范围，不承诺业务需要的输出顺序。
- 本课用标准库集合与映射解决应用问题，不重复实现上一课的桶链。

<section id="concept-three-questions" data-learning-context="concept-three-questions" data-context-type="concept" markdown="1">

## 先问清楚程序要回答什么

| 问题 | 最小状态 | 输出规则 |
| --- | --- | --- |
| 这个值见过吗 | 集合 `seen` | 布尔结果 |
| 每个值出现几次 | 映射 `counts[value]` | 按键排序 |
| 去重后保留什么顺序 | 集合 + 输出序列 | 首次出现顺序 |

集合不能单独保存次数；映射也不会自动替你决定报告顺序。数据结构提供能力，业务问题决定组合方式。

</section>

<section id="concept-unordered-contract" data-learning-context="concept-unordered-contract" data-context-type="concept" markdown="1">

## “无序”不是“每次随机”

Python `set`／`dict` 和 C++ `unordered_set`／`unordered_map` 的遍历结果可能在某次运行里看起来稳定，但不能据此建立跨语言报告的顺序契约。

程序需要什么顺序，就显式写出什么顺序：频次按键排序；保序去重另建结果序列。

</section>

<section id="example-scan-trace" data-learning-context="example-scan-trace" data-context-type="example" markdown="1">

## 从左到右扫一遍

<div class="be-dedup-trace" role="img" aria-label="依次读取7、3、7、9、3；第三项7和第五项3是重复值，唯一序列保持7、3、9">
  <div><strong>visit 1</strong><code>7 · first</code><span>unique 7</span></div>
  <div><strong>visit 2</strong><code>3 · first</code><span>unique 7,3</span></div>
  <div data-repeat="true"><strong>visit 3</strong><code>7 · repeat</code><span>首个重复</span></div>
  <div><strong>visit 4</strong><code>9 · first</code><span>unique 7,3,9</span></div>
  <div data-repeat="true"><strong>visit 5</strong><code>3 · repeat</code><span>输出不再追加</span></div>
</div>

先查 `seen`，未见过才加入集合并追加到唯一序列；无论是否重复，频次都加一。第三次访问 7 时可以返回首重复，但完整频次和完整去重仍需继续扫描。

</section>

<section id="concept-first-duplicate" data-learning-context="concept-first-duplicate" data-context-type="concept" markdown="1">

## visits 是已经读过多少项

```python
def first_duplicate(values: list[int]) -> DuplicateTrace:
    seen: set[int] = set()
    for visits, value in enumerate(values, start=1):
        if value in seen:
            return DuplicateTrace(value, visits)
        seen.add(value)
    return DuplicateTrace(None, len(values))
```

空输入返回空值和 0；没有重复时 visits 等于长度。计数从 1 开始，和“读到第几项”保持一致。

</section>

<section id="concept-frequency-order" data-learning-context="concept-frequency-order" data-context-type="concept" markdown="1">

## 计数结束以后再决定展示顺序

```python
counts[value] = counts.get(value, 0) + 1
rows = [FrequencyRow(value, counts[value]) for value in sorted(counts)]
```

只排序派生出的键，不原地排序输入。这样 `[7,3,7,9,3]` 仍保持原样，报告稳定输出 `3=2, 7=2, 9=1`。

</section>

<section id="concept-order-preserving-dedup" data-learning-context="concept-order-preserving-dedup" data-context-type="concept" markdown="1">

## 保序去重要两份状态

`seen` 负责快速判断是否出现过，`result` 保存第一次出现的顺序。把集合直接转成列表，或先排序再去重，都无法得到“首次出现顺序”。

```text
[7, 3, 7, 9, 3] → [7, 3, 9]
[3, 7, 3]       → [3, 7]
```

</section>

<section id="reproduce-applications-micro" data-learning-context="reproduce-applications-micro" data-context-type="reproduce" markdown="1">

## 运行逐项扫描

```bash
.venv/bin/python site-src/examples/algorithm-foundation/set_frequency_trace.py
```

先预测每行是 `first` 还是 `repeat`。最后应看到唯一序列停在 `[7,3,9]`，频次按数值升序输出 `3:2, 7:2, 9:1`。

</section>

<section id="reproduce-bilingual-applications" data-learning-context="reproduce-bilingual-applications" data-context-type="reproduce" markdown="1">

## 回归双语言三种模式

```bash
cd exercises/cs-core/traceable-hash-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_hash_lab applications
```

```bash
cd exercises/cs-core/traceable-hash-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_hash_lab applications
```

继续回归 `hash` 和 `table`，逐字比较两种语言的三份报告。应用层换用标准容器，不应破坏前两课已经冻结的桶事件和扩容轨迹。

</section>

<section id="modify-new-data" data-learning-context="modify-new-data" data-context-type="modify" markdown="1">

## 换一组数据先预测再运行

使用 `[-1, 0, -1, 2, 0]`，先写下首重复值与 visits、保序唯一序列和按键排序的频次行。负数不会改变算法；它只提醒你不要把“值”和“数组下标”混为一谈。

</section>

<section id="modify-no-duplicate" data-learning-context="modify-no-duplicate" data-context-type="modify" markdown="1">

## 再试完全没有重复的数据

对 `[4, 1, 8]`，首重复应为空、visits 为 3；唯一序列与输入相同，每个频次都是 1。测试还要保存输入副本，确认三个函数没有修改调用方数据。

</section>

<section id="troubleshoot-output-order" data-learning-context="troubleshoot-output-order" data-context-type="troubleshoot" markdown="1">

## 输出有时会换顺序

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 唯一值顺序变化 | 直接遍历集合 | 用独立结果序列记录首次出现 |
| Python 与 C++ 频次顺序不同 | 直接遍历无序映射 | 转成行后按键排序 |
| visits 少一 | 先判断、后计数 | 每读一项就确定本次 visits |
| 原输入被重排 | 为稳定输出原地排序 | 只排序派生键或结果副本 |
| Python 列表不能作键 | 可变对象不可哈希 | 改用满足哈希契约的不可变键 |

</section>

<section id="project-hash-v03" data-learning-context="project-hash-v03" data-context-type="project" markdown="1">

## 可追踪哈希实验完成第一轮应用

```text
桶路由与冲突 → 键值链、比较与扩容
                         ↓
          首重复、保序去重、排序频次
```

这一版没有继续堆哈希表内部功能，而是用标准容器解决三个常见数据问题。前两课解释结构为什么可用，这一课练习怎样把结构组合成稳定接口。

[查看可追踪哈希实验](../../exercises/cs-core/traceable-hash-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-cost-and-memory" data-learning-context="deepen-cost-and-memory" data-context-type="deepen" markdown="1">

## 一次扫描也要说明成立条件

三个函数都只从左到右读取输入一次。合理哈希分布下，每次成员查询或计数更新有期望常量成本，整体期望 `Θ(n)`；最坏冲突集中时仍可能退化。

额外集合、映射或结果序列最多保存 `u` 个不同值，空间 `Θ(u)`。显式排序 `u` 个频次键还会增加 `Θ(u log u)`。

</section>

<section id="career-stable-output" data-learning-context="career-stable-output" data-context-type="career" markdown="1">

## 不要只说“用了 set 所以很快”

更完整的表达是：集合负责成员关系，映射负责计数，额外序列和排序分别建立两种输出顺序；同时测试空输入、无重复、负数、输入不变和双语言一致。

最后补上复杂度条件：扫描期望线性，频次排序取决于不同值数量，无序容器的遍历顺序从未进入公开结果。

</section>

## 完成检查

- [ ] 能根据问题选择集合、映射或两者组合。
- [ ] 能手算首重复值及 visits，并覆盖空和无重复。
- [ ] 保序去重保留首次出现顺序，不靠排序或集合遍历。
- [ ] 频次行按键排序，源输入保持不变。
- [ ] 能解释“无序”为什么不等于“随机”，也不能成为输出契约。
- [ ] Python 类型检查与单元测试、C++ 构建与 CTest、三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [Python 数据模型](https://docs.python.org/3.11/reference/datamodel.html) | 可哈希性、相等与键约束 | Python 3.11，2026-07-17 核查 |
| [Python 集合与映射](https://docs.python.org/3.11/library/stdtypes.html#set-types-set-frozenset) | 成员关系、集合与字典接口 | Python 3.11，2026-07-17 核查 |
| [C++ 无序关联容器要求](https://eel.is/c++draft/unord.req.general) | 等价键、桶与无序容器要求 | C++20 教学基线，2026-07-17 核查 |
| [Open Data Structures](https://www.opendatastructures.org/ods-python.pdf) | 哈希集合与映射应用背景 | 2026-07-17 核查 |

本课稳定顺序全部由项目代码显式建立，没有把某次标准容器遍历结果当作语言保证。

## 下一步

进入[有序查找、半开区间与左右边界](12-ordered-search-half-open-boundaries.md)，从稳定排序的数据开始追踪查找区间。
