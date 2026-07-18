<div class="be-tutor-mount" data-tutor-lesson="cs-core-21" aria-hidden="true"></div>

<section id="overview-heap-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-heap-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">算法核心 · 第 1 课 · 可追踪优先队列与最短路实验</span>

# 二叉最小堆、隐式树与堆不变量

## 最小值在最前面，但数组并没有排好序

```text
push：7, 3, 9, 1, 5
heap：1, 3, 9, 7, 5
comparisons=5，swaps=3
pop_min=1
remaining：3, 5, 9, 7
```

`1,3,9,7,5` 不是升序数组，却是合法最小堆：每个父节点都不大于自己的孩子。这个局部条件足以让根始终保存最小值，同时避免每次插入后重排整份数据。

[把数组看成一棵树](#example-index-map){ .md-button .md-button--primary }
[运行上浮与下沉轨迹](#reproduce-heap-trace){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>算法核心 · 1 / 6</strong></span><span>前置<strong>数组、完全二叉树与复杂度</strong></span><span>完成后留下<strong>可追踪最小堆、线性建堆与精确计数</strong></span></div>

</section>

## 开始前

- 能使用零基数组下标，并理解完全二叉树按层从左到右填充。
- 知道 `Theta(log n)` 是完全二叉树的高度量级。
- 本课实现教学用最小堆；标准库 `heapq` 用于对照，不替代轨迹实现。

<section id="concept-implicit-tree" data-learning-context="concept-implicit-tree" data-context-type="concept" markdown="1">

## 完全二叉树可以直接放进数组

完全二叉树除了最后一层外都填满，最后一层从左往右连续出现，因此不需要节点指针和空槽。对下标 `i`：

```text
left  = 2*i + 1
right = 2*i + 2
parent = (i-1)//2   # i > 0
```

数组长度已经告诉我们孩子是否存在；超出长度的下标不属于树。

</section>

<section id="example-index-map" data-learning-context="example-index-map" data-context-type="example" markdown="1">

## 同一份数据，两种视角

<div class="be-heap-map" aria-label="最小堆数组下标与隐式树位置">
  <div><strong>1</strong><code>index 0</code><span>根</span></div>
  <div><strong>3</strong><code>index 1</code><span>0 的左孩子</span></div>
  <div><strong>9</strong><code>index 2</code><span>0 的右孩子</span></div>
  <div><strong>7</strong><code>index 3</code><span>1 的左孩子</span></div>
  <div><strong>5</strong><code>index 4</code><span>1 的右孩子</span></div>
</div>

位置 1、2 的父节点都是 0；位置 3、4 的父节点都是 1。这里 9 排在 7、5 前面没有问题，因为它们不在同一条父子边上。

</section>

<section id="concept-heap-invariant" data-learning-context="concept-heap-invariant" data-context-type="concept" markdown="1">

## 堆有序只约束父子

最小堆对每条父子边要求 `parent <= child`。它不比较兄弟，也不保证左子树全部小于右子树。

因此根一定是全局最小值：任何其他节点都能沿父链回到根，链上数值不会向上变大。但第二小值只能在根的孩子中，不能直接从数组下标 1 以外的位置猜。

</section>

<section id="example-sift-up" data-learning-context="example-sift-up" data-context-type="example" markdown="1">

## 插入 1：先追加，再沿父链上浮

插入前是 `[3,5,9,7]`。把 1 追加到下标 4：

```text
[3,5,9,7,1]
1 < 5 → 交换 → [3,1,9,7,5]
1 < 3 → 交换 → [1,3,9,7,5]
```

相等时不交换，因为 `parent <= child` 已经成立。课程计数只记录元素值比较和真实交换，不把循环条件与下标边界混进去。

</section>

<section id="concept-sift-down" data-learning-context="concept-sift-down" data-context-type="concept" markdown="1">

## 删除根：末尾补位，再选择较小孩子下沉

移除根 1，把末尾 5 放到根，得到 `[5,3,9,7]`。左右孩子是 3、9，先选较小的 3，再比较 `3 < 5` 并交换：`[3,5,9,7]`。

不能永远选左孩子；右孩子可能更小。每轮都先在存在的孩子中选较小者，再决定是否继续下沉。

</section>

<section id="reproduce-heap-trace" data-learning-context="reproduce-heap-trace" data-context-type="reproduce" markdown="1">

## 打印每次比较与交换

```bash
.venv/bin/python site-src/examples/algorithm-core/min_heap_trace.py
```

运行前先算插入 1 的两次父下标。脚本最终应锁定五次比较、三次交换；删除根时是三次比较、一次交换。

</section>

<section id="reproduce-bilingual-heap" data-learning-context="reproduce-bilingual-heap" data-context-type="reproduce" markdown="1">

## 运行双语言阶段作品

```bash
cd exercises/cs-core/traceable-priority-shortest-path-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_priority_shortest_path_lab heap
```

```bash
cd exercises/cs-core/traceable-priority-shortest-path-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_priority_shortest_path_lab heap
```

同时回归 `queue` 和 `dijkstra`。三份 Python/C++ 报告必须逐字一致，避免基础堆改动破坏后续优先队列和最短路。

</section>

<section id="modify-duplicates-underflow" data-learning-context="modify-duplicates-underflow" data-context-type="modify" markdown="1">

## 加入重复值，再排空堆

插入两个相同的 3。第二个 3 与父节点相等时停止，不产生交换；连续 `pop_min` 应按值从小到大取出全部元素。

堆空后再 `peek` 或 `pop`：Python 抛 `IndexError`，C++ 抛 `std::out_of_range`。检查发生在写操作以前，失败后仍为空堆。

</section>

<section id="modify-bottom-up-build" data-learning-context="modify-bottom-up-build" data-context-type="modify" markdown="1">

## 不逐个插入，直接自底向上建堆

复制输入，从最后一个非叶节点 `len//2-1` 开始，向根逐个下沉。覆盖空序列、负数、重复值和已经成堆的输入；结果满足不变量，原输入不变。

这里不要偷偷调用多次 `push`。两者都能得到合法堆，但复杂度证据不同。

</section>

<section id="troubleshoot-heap" data-learning-context="troubleshoot-heap" data-context-type="troubleshoot" markdown="1">

## 根不是最小、下沉后仍违规或计数对不上

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 把合法堆判为未排序 | 检查了全数组升序 | 只检查父节点与存在的孩子 |
| 下沉后右侧仍违规 | 固定选择左孩子 | 先选择较小孩子 |
| 重复值反复交换 | 使用 `<=` 触发交换 | 只有严格更小时交换 |
| 比较次数偏大 | 把边界和循环判断计入 | 只统计元素值比较 |
| 空堆状态损坏 | 先修改再检查 | 写操作前拒绝下溢 |
| 建堆成了 `n log n` | 逐项调用 `push` | 从最后一个非叶节点下沉 |

</section>

<section id="project-priority-v01" data-learning-context="project-priority-v01" data-context-type="project" markdown="1">

## 可追踪优先队列与最短路实验 v0.1

这一版提供最小堆的 `push`、`peek_min`、`pop_min`、不变量检查和线性建堆，并记录比较与交换。下一课会把整数换成带优先级和稳定序号的任务。

[查看阶段作品](../../exercises/cs-core/traceable-priority-shortest-path-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-heap-complexity" data-learning-context="deepen-heap-complexity" data-context-type="deepen" markdown="1">

## 根读取常量时间，上浮下沉对数时间

根固定在下标 0，读取最小值是 `Theta(1)`。完全二叉树高度为 `Theta(log n)`，插入与删除最多沿一条根叶路径移动，所以是 `Theta(log n)`。

堆只快速暴露一个极值；若要完整排序，仍需反复删除 n 次，总时间为 `Theta(n log n)`。

</section>

<section id="deepen-linear-build" data-learning-context="deepen-linear-build" data-context-type="deepen" markdown="1">

## 为什么自底向上建堆是线性的

粗略地说“n 个节点每个下沉 log n”会高估。约一半节点是叶子，不下沉；约四分之一最多下沉一层；约八分之一最多两层。总工作量受下面的收敛级数控制：

```text
n/4 × 1 + n/8 × 2 + n/16 × 3 + ... = Theta(n)
```

少数靠近根的节点下沉得深，但绝大多数节点离叶子很近。

</section>

<section id="career-heap-evidence" data-learning-context="career-heap-evidence" data-context-type="career" markdown="1">

## 用 `[1,3,9,7,5]` 讲清“局部有序”

先映射父子下标，指出 9 在 7、5 前面不违规；再走插入 1 的两次上浮和删除根的一次下沉。最后对比逐项插入 `Theta(n log n)` 与自底向上建堆 `Theta(n)`。

配上重复值、空堆和精确计数，回答便同时包含结构、不变量、操作过程、复杂度与失败边界。

</section>

## 完成检查

- [ ] 能从数组下标计算父节点和两个孩子。
- [ ] 能解释堆有序与全局排序的差别。
- [ ] 插入只在严格更小时上浮，删除先选较小孩子下沉。
- [ ] 固定轨迹得到插入 5/3、删除 3/1 的比较与交换计数。
- [ ] 空堆安全失败；自底向上建堆不修改原输入。
- [ ] 能解释 `peek`、`push/pop` 和线性建堆复杂度。
- [ ] Python 类型检查、C++ CTest 和三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [MIT 6.006 Binary Heaps](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/40d4851e550507ca14dc778b9b2266cc_MIT6_006S20_lec8.pdf) | 堆接口、建堆和复杂度 | 2026-07-17 核查 |
| [Open Data Structures BinaryHeap](https://opendatastructures.org/ods-python/10_1_BinaryHeap_Implicit_Bi.html) | 隐式树索引与上浮下沉 | 2026-07-17 核查 |
| [Python `heapq`](https://docs.python.org/3.11/library/heapq.html) | 零基最小堆标准库对照 | Python 3.11，2026-07-17 核查 |

本课不进入最大堆、堆排序、Top-K 或可删除任意项的索引堆；它们建立在相同不变量上，但接口与验证范围不同。

## 下一步

进入[稳定优先队列、同优先级顺序与下溢](22-stable-priority-queue-tie-order-underflow.md)，让相同优先级的任务保持先来先出。
