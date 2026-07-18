<div class="be-tutor-mount" data-tutor-lesson="cs-core-09" aria-hidden="true"></div>

<section id="overview-hash-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-hash-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">共同算法基础 · 第 5 课 · 可追踪哈希实验</span>

# 哈希函数、键相等与冲突

## 1、5、9 不相等，为什么都去了桶 1

```text
key | bucket | chain_before | collision
1   | 1      | 0            | no
5   | 1      | 1            | yes
9   | 1      | 2            | yes
2   | 2      | 0            | no
```

本课先用四个桶和一条公开规则：`bucket = key % 4`。1、5、9 除以 4 的余数都是 1，所以进入同一个桶；它们仍是三个不同的键。哈希先缩小查找范围，桶内还要继续比较完整键。

[看四个桶怎样装值](#example-bucket-layout){ .md-button .md-button--primary }
[直接运行小例子](#reproduce-hash-micro){ .md-button }

<div class="be-lesson-facts" markdown="1">
<span>课程位置<strong>共同算法基础 · 5 / 16</strong></span>
<span>前置<strong>线性查找、链表与确定性操作轨迹</strong></span>
<span>完成后留下<strong>桶事件、冲突证据和双语言回归</strong></span>
</div>

</section>

## 开始前

- 能解释链表查找为什么要逐个比较，并读懂 `visits`。
- 知道取模结果会落在固定余数范围。
- 本课使用非负整数键和公开教学规则；标准库内部实现不在本课猜测范围内。

<section id="concept-hash-routing" data-learning-context="concept-hash-routing" data-context-type="concept" markdown="1">

## 哈希先决定去哪个桶

```text
完整键
  → hash / bucket_index
  → 候选桶
  → 桶内逐键比较
  → 找到相等键，或确认缺失
```

如果有 100 个键和 10 个桶，理想情况下不必每次比较全部 100 个键，而是先去一个更小的候选集合。能否真的更快，取决于哈希分布、桶数量、负载和冲突处理；不能只凭“用了哈希”就宣布每次一定常量时间。

</section>

<section id="example-bucket-layout" data-learning-context="example-bucket-layout" data-context-type="example" markdown="1">

## 四个桶里真正保存了什么

<div class="be-hash-buckets" role="img" aria-label="四个哈希桶中，桶0为空，桶1按顺序保存1、5、9，桶2保存2，桶3为空">
  <div><strong>桶 0</strong><code>[]</code><span>空</span></div>
  <div data-collision="true"><strong>桶 1</strong><code>[1, 5, 9]</code><span>两次冲突</span></div>
  <div><strong>桶 2</strong><code>[2]</code><span>无冲突</span></div>
  <div><strong>桶 3</strong><code>[]</code><span>空</span></div>
</div>

桶 1 保留输入顺序。插入 5 前，链里已经有 1；插入 9 前，链里已经有 1、5。下一课会把这种“每桶一条小链”升级成支持增删改查的分离链接哈希表。

</section>

<section id="concept-equality-contract" data-learning-context="concept-equality-contract" data-context-type="concept" markdown="1">

## 相等键必须同哈希，反过来不成立

哈希容器依赖这条契约：

```text
key_a == key_b  ⇒  hash(key_a) == hash(key_b)
```

若两个相等键被送到不同桶，容器可能永远找不到已经保存的键。但相同哈希只代表候选桶相同：

```text
1 % 4 == 5 % 4 == 1
1 != 5
```

所以冲突不是“两个键相等”，也不是程序故障；它是有限桶空间中必须处理的正常情况。

</section>

<section id="concept-teaching-hash" data-learning-context="concept-teaching-hash" data-context-type="concept" markdown="1">

## 取模规则只属于这个可复现实验

课程固定：

```python
bucket = key % bucket_count
```

这样 Python 与 C++ 能对同一组整数生成完全一致的桶号和冲突事件。它不表示 Python `dict/set`、C++ `unordered_map`，或其他语言的标准容器必须使用这条算法。

正式代码依赖标准库承诺的行为、复杂度条件和键契约；教学实验则可以对自己公开的规则写精确断言。

</section>

<section id="concept-bucket-index" data-learning-context="concept-bucket-index" data-context-type="concept" markdown="1">

## 桶索引必须先通过输入检查

`bucket_index(key, bucket_count)` 的合法结果满足：

```text
0 <= bucket < bucket_count
```

本实验先拒绝 `bucket_count <= 0`，避免除零和不存在的桶；再拒绝负键，让 Python 与 C++ 不受负数余数规则差异影响。只有检查通过以后才执行取模。

这种限制是教学接口的公开选择，不是说真实哈希表不能支持负整数键。

</section>

<section id="example-collision-events" data-learning-context="example-collision-events" data-context-type="example" markdown="1">

## `chain_before` 记录插入前已有多少候选

| key | bucket | 插入前链长 | collision |
| ---: | ---: | ---: | --- |
| 1 | 1 | 0 | no |
| 5 | 1 | 1 | yes |
| 9 | 1 | 2 | yes |
| 2 | 2 | 0 | no |

事件必须在追加键之前读取链长，否则第一项会错误地从 1 开始。`collision` 等价于 `chain_before > 0`；它说明新键进入了非空桶，还没有说明桶里存在相等键。

</section>

<section id="concept-input-order" data-learning-context="concept-input-order" data-context-type="concept" markdown="1">

## 不要为了好看先把键排序

`first_collision` 问的是输入过程里第一次冲突发生在哪里。若把 `[9, 1, 5]` 先排成 `[1, 5, 9]`，桶内容看似相同，事件顺序和第一个冲突键却变了。

本项目按输入顺序追加，桶链、事件和首个冲突都因此可重复。展示结果若需要排序，应在单独的输出层完成，不能偷偷改变操作历史。

</section>

<section id="reproduce-hash-micro" data-learning-context="reproduce-hash-micro" data-context-type="reproduce" markdown="1">

## 运行一份完整桶轨迹

```bash
.venv/bin/python site-src/examples/algorithm-foundation/hash_bucket_trace.py
```

运行前手算 `1、5、9、2` 在 4 个桶中的余数，再预测每行 `chain_before`。最后应看到：

```text
buckets=0:[] 1:[1, 5, 9] 2:[2] 3:[]
```

小程序先记录事件再插入，适合从输出回到代码逐行核对。

</section>

<section id="reproduce-bilingual-hash" data-learning-context="reproduce-bilingual-hash" data-context-type="reproduce" markdown="1">

## 在正式项目里对照三种模式

```bash
cd exercises/cs-core/traceable-hash-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_hash_lab hash
```

```bash
cd exercises/cs-core/traceable-hash-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_hash_lab hash
```

`hash`、`table`、`applications` 三种模式都要通过，Python 与 C++ 的报告逐字一致。后两种模式提前存在，是为了保护接下来两课的项目契约。

</section>

<section id="modify-new-buckets" data-learning-context="modify-new-buckets" data-context-type="modify" markdown="1">

## 换桶数以后，冲突会跟着变

固定键 `[1, 5, 9, 2]`，分别使用 3、4、5 个桶：

1. 先手算每个键的桶号。
2. 再预测第一个冲突键。
3. 调用 `trace_bucket_inserts` 和 `first_collision` 核对。
4. 比较桶数变化是否改变键相等关系。

桶布局会变，键本身是否相等不会变。桶更多也不保证没有冲突，只是这组小数据可能分散得更开。

</section>

<section id="modify-first-collision" data-learning-context="modify-first-collision" data-context-type="modify" markdown="1">

## 找到输入顺序里的第一次冲突

`first_collision(keys, bucket_count)` 返回第一个 `collision=True` 的完整事件；没有冲突时返回 `None`／空 `optional`。

请覆盖：

- 空输入。
- `[0, 1, 2]` 与 4 个桶，没有冲突。
- `[1, 5, 9]` 与 4 个桶，首个冲突是键 5。
- 多次冲突但仍只返回第一项。

直接复用事件追踪，别另写一套稍有不同的冲突规则。

</section>

<section id="troubleshoot-invalid-input" data-learning-context="troubleshoot-invalid-input" data-context-type="troubleshoot" markdown="1">

## 除零和负索引不该成为报错方式

桶数为 0 或负数、键为负数时，Python 抛 `ValueError`，C++ 抛 `std::invalid_argument`。错误发生在取模和桶修改之前。

先验证、再计算，得到的是稳定的接口错误；依赖除零、数组越界或负索引得到的是语言偶然行为，跨语言报告也无法对齐。

</section>

<section id="troubleshoot-unhashable-key" data-learning-context="troubleshoot-unhashable-key" data-context-type="troubleshoot" markdown="1">

## Python 列表为什么不能放进 `set`

```python
set().add([])  # TypeError: unhashable type: 'list'
```

列表可以原地修改。一个键进入哈希容器后若哈希值随内容变化，容器可能再也到不了原来的桶。Python 因此不让可变列表直接作为集合元素；不可变元组只有在其成员也可哈希时才可哈希。

</section>

<section id="project-hash-v01" data-learning-context="project-hash-v01" data-context-type="project" markdown="1">

## 可追踪哈希实验从桶事件开始

```text
整数键序列
  → bucket_index
  → BucketEvent(key, bucket, chain_before, collision)
  → 确定性桶链
  → first_collision
  → Python / C++ 同一份报告
```

这版还不是完整哈希表。它先把路由、冲突和输入顺序变成可检查的事件，下一课再在同一规则上增加键值、更新、查询、删除、负载和扩容。

[查看可追踪哈希实验](../../exercises/cs-core/traceable-hash-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-performance-conditions" data-learning-context="deepen-performance-conditions" data-context-type="deepen" markdown="1">

## “哈希查找 O(1)”需要条件

若哈希分布合理、负载受控，桶内候选通常较少，查找可以达到期望常量时间。最坏情况下，许多键集中到同一个桶，仍可能退化为线性比较。

所以性能讨论至少要说明：平均、期望还是最坏；哈希质量如何；负载因子多大；冲突怎样处理。下一课会用可见的比较次数和扩容事件继续补齐这些条件。

</section>

<section id="career-hash-evidence" data-learning-context="career-hash-evidence" data-context-type="career" markdown="1">

## 讲哈希时，先把单向契约说准

可以用 1 和 5 说明：相等键必须得到相同哈希，但相同哈希不代表键相等；同桶以后仍要比较完整键。再用 `chain_before` 说明冲突是怎样被记录的。

如果继续问复杂度，就补充合理分布和受控负载下的期望性能，以及全部键落在同桶时的最坏线性情况。最后展示负桶数、负键、不可哈希列表和双语言测试，答案才有可复核的边界。

</section>

## 完成检查

- [ ] 能手算 1、5、9、2 在 4 个桶中的位置与插入前链长。
- [ ] 能解释相等键必须同哈希，但同哈希不代表相等。
- [ ] 能区分课程取模规则和标准库实现。
- [ ] 桶数与键在计算前完成校验，错误不修改状态。
- [ ] `first_collision` 覆盖空、无冲突、首个冲突和多重冲突。
- [ ] 能说明为什么输入顺序影响事件，但不影响键相等关系。
- [ ] Python 类型检查与单元测试、C++ 构建与 CTest、三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [MIT 6.006 哈希讲义](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/mit6_006s20_lec4/) | 哈希、冲突与期望性能条件 | 2020 课程，2026-07-17 核查 |
| [Open Data Structures](https://www.opendatastructures.org/ods-python.pdf) | 哈希表表示与冲突处理 | 2026-07-17 核查 |
| [Python 数据模型](https://docs.python.org/3.11/reference/datamodel.html#object.__hash__) | 可哈希对象与相等契约 | Python 3.11，2026-07-17 核查 |
| [C++ 无序关联容器要求](https://eel.is/c++draft/unord.req.general) | 等价键、哈希与桶接口 | C++20 教学基线，2026-07-17 核查 |

本地 JavaGuide 哈希页只用于检查冲突、负载和扩容的常见说法；桶规则、事件、代码和测试均由本项目独立编写。

## 下一步

进入[分离链接、负载因子与扩容](10-separate-chaining-load-factor-rehash.md)，把静态桶链升级为支持插入、更新、查询和删除的键值表。
