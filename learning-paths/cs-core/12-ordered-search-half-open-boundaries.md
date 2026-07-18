<div class="be-tutor-mount" data-tutor-lesson="cs-core-12" aria-hidden="true"></div>

<section id="overview-search-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-search-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">共同算法基础 · 第 8 课 · 可追踪查找与排序实验</span>

# 有序查找、半开区间与左右边界

## 找到一个 3，不等于找到所有 3

```text
data：1, 3, 3, 3, 7, 9
linear：index=1，comparisons=2
lower_bound：index=1，comparisons=3
upper_bound：index=4，comparisons=3
equal_range：[1, 4)
```

线性查找找到第一个 3 就停；左右边界分别寻找第一个 `>= 3` 和第一个 `> 3` 的位置。它们合起来得到 `[1,4)`，正好覆盖三个 3。

[看区间怎样缩小](#example-bound-rounds){ .md-button .md-button--primary }
[运行完整轨迹](#reproduce-bound-micro){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>共同算法基础 · 8 / 16</strong></span><span>前置<strong>稳定输出与有序数据</strong></span><span>完成后留下<strong>线性命中、左右边界和相等区间</strong></span></div>

</section>

## 开始前

- 能按下标读取序列，并知道 `[left,right)` 不包含 `right`。
- 能区分元素下标和插入位置；插入位置允许等于序列长度。
- 本课不把排序偷偷放进查找函数。有序是进入二分之前必须满足的条件。

<section id="concept-sorted-values" data-learning-context="concept-sorted-values" data-context-type="concept" markdown="1">

## 先把“已经有序”变成可检查的条件

`SortedValues` 构造时复制输入并检查非递减顺序。查找函数只接收这个类型，因此不必每次重新验证，也不会被调用方随后修改原列表影响。

```text
原列表 [1,3,3,7] ──复制与验证──> SortedValues(1,3,3,7)
原列表后来改成 [9,3,3,7]       内部副本仍不变
```

构造验证是一次 `Θ(n)` 成本；后面的比较次数只统计本次查找。

</section>

<section id="concept-linear-search" data-learning-context="concept-linear-search" data-context-type="concept" markdown="1">

## 线性查找是清楚的比较基线

从左到右逐项比较，首次相等就返回。目标 3 先和 1 比，再和 3 比，所以 `index=1`、`comparisons=2`。没有命中时会比较全部 `n` 项。

即使数据有序，这个基线仍有价值：它不依赖二分不变量，也让“对数级改进”有一个可量化的参照。

</section>

<section id="concept-half-open" data-learning-context="concept-half-open" data-context-type="concept" markdown="1">

## 候选答案一直放在 `[left,right)`

- 区间长度是 `right-left`。
- `right` 本身不在候选区间里。
- `left==right` 时区间为空，`left` 就是边界答案。
- 初始 `[0,n)` 同时适用于普通序列和空序列。

每轮必须严格缩短候选区间，否则循环可能永远停不下来。

</section>

<section id="concept-lower-upper" data-learning-context="concept-lower-upper" data-context-type="concept" markdown="1">

## 两个边界只差一个等号

| 边界 | 要找的位置 | 中间值何时丢到左边 |
| --- | --- | --- |
| `lower_bound` | 第一个 `>= target` | `value < target` |
| `upper_bound` | 第一个 `> target` | `value <= target` |

遇到相等值时，lower 继续向左找，upper 继续向右找。不要把“找到相等就返回”写进边界查找。

</section>

<section id="example-bound-rounds" data-learning-context="example-bound-rounds" data-context-type="example" markdown="1">

## 目标 3 的三轮收缩

### lower：第一个大于等于 3

<div class="be-bound-steps" role="img" aria-label="lower bound三轮把区间从0到6缩小到位置1">
  <div><strong>round 1</strong><code>[0,6) mid=3 value=3</code><span>保留左半边 → [0,3)</span></div>
  <div><strong>round 2</strong><code>[0,3) mid=1 value=3</code><span>继续向左 → [0,1)</span></div>
  <div><strong>round 3</strong><code>[0,1) mid=0 value=1</code><span>丢掉0 → [1,1)</span></div>
</div>

### upper：第一个严格大于 3

<div class="be-bound-steps" role="img" aria-label="upper bound三轮把区间从0到6缩小到位置4">
  <div><strong>round 1</strong><code>[0,6) mid=3 value=3</code><span>相等也向右 → [4,6)</span></div>
  <div><strong>round 2</strong><code>[4,6) mid=5 value=9</code><span>保留左半边 → [4,5)</span></div>
  <div><strong>round 3</strong><code>[4,5) mid=4 value=7</code><span>收口 → [4,4)</span></div>
</div>

两次都比较三轮，但收口位置不同。

</section>

<section id="concept-end-position" data-learning-context="concept-end-position" data-context-type="concept" markdown="1">

## 返回 `n` 不是越界错误

边界表示分割位置，不一定指向现有元素。`[1,3]` 中寻找 9 的 lower bound 返回 2，意思是“若插入 9，应放在末尾”。空序列唯一的分割位置也是 0。

只有随后真的读取 `values[n]` 才越界；单独返回位置 `n` 是合法契约。

</section>

<section id="reproduce-bound-micro" data-learning-context="reproduce-bound-micro" data-context-type="reproduce" markdown="1">

## 运行左右边界轨迹

```bash
.venv/bin/python site-src/examples/algorithm-foundation/binary_bounds_trace.py
```

运行前先在纸上写出每轮 `[left,right)`、middle 和下一段。若某轮区间长度没有变，先检查更新是不是漏掉了 `middle+1`。

</section>

<section id="reproduce-bilingual-search" data-learning-context="reproduce-bilingual-search" data-context-type="reproduce" markdown="1">

## 回归双语言阶段作品

```bash
cd exercises/cs-core/traceable-search-sort-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_search_sort_lab search
```

```bash
cd exercises/cs-core/traceable-search-sort-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_search_sort_lab search
```

同时回归 `elementary` 与 `merge`，两种语言三份报告逐字一致。下一课会改排序练习，但不能破坏本课查找输出。

</section>

<section id="modify-targets" data-learning-context="modify-targets" data-context-type="modify" markdown="1">

## 查四类目标

仍用 `[1,3,3,3,7,9]`，分别查询：首项 1、重复值 3、间隙里的 5、以及大于全部元素的 10。先预测 linear、lower、upper 和 equal range，再运行测试。

缺失目标的左右边界应相等，形成空区间；它们不需要返回错误。

</section>

<section id="modify-equal-range" data-learning-context="modify-equal-range" data-context-type="modify" markdown="1">

## 组合出完整相等区间

`equal_range` 只组合两次边界查找：`first=lower.index`、`last=upper.index`，comparisons 为两者之和。它不重新排序、不重新验证，也不再次扫描 `[first,last)`。

为存在、缺失、空输入和全都相等四种数据补测试。

</section>

<section id="troubleshoot-bounds" data-learning-context="troubleshoot-bounds" data-context-type="troubleshoot" markdown="1">

## 二分结果差一位或循环不结束

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 重复值只得到中间一个 | 相等时立即返回 | 分别寻找 lower 与 upper |
| 循环不结束 | `left=middle` 没有缩小 | 丢左半时使用 `middle+1` |
| 空序列访问下标 0 | 把 right 当有效元素 | 初始化 `[0,0)`，循环不进入 |
| 返回 n 被误报越界 | 把边界当元素下标 | 区分位置与读取操作 |
| 无序输入给出偶然结果 | 忽略有序前提 | 在 `SortedValues` 构造时拒绝 |

</section>

<section id="project-search-v01" data-learning-context="project-search-v01" data-context-type="project" markdown="1">

## 可追踪查找与排序实验从边界开始

```text
有序副本 → 线性首命中
         ↘ lower / upper → equal_range
```

这一版冻结输入条件、返回位置和比较次数。下一课加入基础比较排序，再下一课用迭代归并建立稳定的 `Θ(n log n)` 排序轨迹。

[查看可追踪查找与排序实验](../../exercises/cs-core/traceable-search-sort-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-search-cost" data-learning-context="deepen-search-cost" data-context-type="deepen" markdown="1">

## 查找快，不代表插入也快

边界查找每轮把候选长度大致减半，比较次数是 `Θ(log n)`；但若要把新值插入数组中间，后续元素移动仍可能是 `Θ(n)`。

一次性构造与有序验证也是 `Θ(n)`。只有对同一份已验证数据执行多次查询时，这个成本才会被后续查询复用。

</section>

<section id="career-bound-evidence" data-learning-context="career-bound-evidence" data-context-type="career" markdown="1">

## 讲二分时先讲不变量

从 `[left,right)` 候选区间说起，再解释 lower 与 upper 在相等时走向不同。用重复值、空序列、缺失目标和返回 `n` 证明边界完整；最后说明验证、查询和插入是三种不同成本。

比背一份二分模板更重要的是：每次更新后，候选答案仍在区间里，而且区间确实缩小。

</section>

## 完成检查

- [ ] 无序输入在查找前受控拒绝，内部有序副本不受原列表修改影响。
- [ ] 线性查找覆盖空、首项、重复首项和缺失目标。
- [ ] 能逐轮解释 lower 与 upper 的半开区间收缩。
- [ ] 接受 0 到 n 的边界位置，不把返回 n 误作读取下标。
- [ ] `equal_range` 只组合两次边界，并覆盖存在、缺失与空输入。
- [ ] Python 类型检查与单元测试、C++ 构建与 CTest、三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [Python `bisect`](https://docs.python.org/3.11/library/bisect.html) | 左右插入点语义与插入移动成本 | Python 3.11，2026-07-17 核查 |
| [C++ 二分算法要求](https://eel.is/c++draft/alg.binary.search) | 分区前置与 lower/upper 契约 | C++20 教学基线，2026-07-17 核查 |
| [MIT 6.006 Sorting](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/6d1ae5278d02bbecb5c4428928b24194_MIT6_006S20_lec3.pdf) | 查找与排序成本背景 | 2020 课程，2026-07-17 核查 |

本课独立实现只为展示区间和比较次数；实际工程中应优先使用经过测试的标准库算法。

## 下一步

进入[插入排序、选择排序与稳定性](13-insertion-selection-sort-stability.md)，用带标签重复键区分“排好序”和“稳定”。
