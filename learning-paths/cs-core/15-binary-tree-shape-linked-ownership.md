<div class="be-tutor-mount" data-tutor-lesson="cs-core-15" aria-hidden="true"></div>

<section id="overview-tree-shape" class="be-page-hero be-lesson-hero" data-learning-context="overview-tree-shape" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">共同算法基础 · 第 11 课 · 可追踪树与遍历实验</span>

# 二叉树形状、链接所有权与槽位表示

## 下标 4 不只是一个位置，它还写着从根怎样走过去

```text
slots=[7,3,9,null,5,8,11]
index=0 value=7  path=root
index=4 value=5  path=LR
index=6 value=11 path=RR
size=6 height=2 leaves=3
```

同一棵树既可以写成一排槽位，也可以链接成父节点拥有孩子的结构。槽位方便保存和核对形状；链接节点方便后续遍历。本课先把两种表示之间的关系做实。

[看槽位怎样连成树](#example-slots-to-tree){ .md-button .md-button--primary }
[运行槽位轨迹](#reproduce-slot-trace){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>共同算法基础 · 11 / 16</strong></span><span>前置<strong>稳定归并与序列下标</strong></span><span>完成后留下<strong>合法树形、私有链接和根到槽位路径</strong></span></div>

</section>

## 开始前

- 会读零基下标，知道列表中 `None` 表示这个槽位没有节点。
- 不要求先会递归遍历；这节课只把树形和所有权搭好。
- 本实验按边数计算高度：根深度是 0，单节点树高度也是 0。

<section id="concept-tree-words" data-learning-context="concept-tree-words" data-context-type="concept" markdown="1">

## 根、孩子、叶子和高度

树从唯一的根开始。节点最多有左、右两个孩子；没有孩子的节点叫叶子。节点深度是从根走到它经过的边数，树高度是根到最深叶子的边数。

因此空树高度为 `-1`，单节点树高度为 `0`。这样写不是唯一约定，但一旦选定，就要让代码、测试和讲解一直使用同一套定义。

</section>

<section id="example-slots-to-tree" data-learning-context="example-slots-to-tree" data-context-type="example" markdown="1">

## 一排槽位怎样长成一棵树

<div class="be-tree-shape" role="img" aria-label="根槽位0的值是7；左孩子槽位1为3，右孩子槽位2为9；槽位3为空，槽位4为5，槽位5为8，槽位6为11">
  <div class="be-tree-level be-tree-level--root"><span><small>slot 0</small><strong>7</strong></span></div>
  <div class="be-tree-level be-tree-level--branches"><span><small>L · slot 1</small><strong>3</strong></span><span><small>R · slot 2</small><strong>9</strong></span></div>
  <div class="be-tree-level be-tree-level--leaves"><span class="is-empty"><small>L · slot 3</small><strong>null</strong></span><span><small>R · slot 4</small><strong>5</strong></span><span><small>L · slot 5</small><strong>8</strong></span><span><small>R · slot 6</small><strong>11</strong></span></div>
</div>

`None` 不能随手删掉。槽位 3 虽然没有节点，却说明 5 是 3 的右孩子，而不是左孩子。

</section>

<section id="concept-slot-formulas" data-learning-context="concept-slot-formulas" data-context-type="concept" markdown="1">

## 三个下标公式

对零基槽位 `i`：

```text
left(i)   = 2i + 1
right(i)  = 2i + 2
parent(i) = (i - 1) // 2   # i > 0
```

奇数槽来自父节点的左边，非零偶数槽来自右边。槽位 4 的父槽是 1，所以先从根走 L；4 又是 1 的右孩子，再走 R，得到路径 `LR`。

</section>

<section id="concept-valid-shape" data-learning-context="concept-valid-shape" data-context-type="concept" markdown="1">

## 数组里有值，不等于它属于这棵树

非空输入必须在槽位 0 有根。除此之外，每个非空子槽的父槽也必须非空。

`[7, None, 9, 4]` 看起来只是四个数组项，但槽位 3 的父槽 1 是空的；从根永远走不到 4。构造时拒绝这种“孤儿槽”，比等到遍历时才发现断链更容易排查。

</section>

<section id="concept-normalization" data-learning-context="concept-normalization" data-context-type="concept" markdown="1">

## 只裁掉末尾的空槽

`[7, 3, None, None]` 末尾两个 `None` 不再区分形状，可以规范成 `[7, 3]`。中间的空槽不能删；删掉以后，后续节点的父子关系会变化。

构造器还要复制调用方的列表。树建好后，即使原列表被改写，树的形状也不应跟着变化。

</section>

<section id="reproduce-slot-trace" data-learning-context="reproduce-slot-trace" data-context-type="reproduce" markdown="1">

## 运行一份短轨迹

```bash
.venv/bin/python site-src/examples/algorithm-foundation/binary_tree_slots_trace.py
```

运行前先在纸上算槽位 4 和 6 的父下标与路径。程序还会拒绝空根、孤儿槽和合法范围内的空槽；这些失败都由明确异常结束，不需要制造越界访问或空指针解引用。

</section>

<section id="concept-linked-ownership" data-learning-context="concept-linked-ownership" data-context-type="concept" markdown="1">

## 链接节点由谁负责释放

槽位适合稳定输入，遍历更适合沿 `left`、`right` 链接移动。Python 把 `_Node` 留在模块内部；C++ 让父节点通过 `std::unique_ptr` 单一拥有孩子。

```text
BinaryTree owns root
root owns left and right
each child owns its own children
```

树可以移动，但不能浅复制。树销毁时，根的所有权链会依次释放整棵树；调用方拿不到可能悬空的节点指针。

</section>

<section id="reproduce-bilingual-tree" data-learning-context="reproduce-bilingual-tree" data-context-type="reproduce" markdown="1">

## 回归双语言阶段作品

```bash
cd exercises/cs-core/traceable-tree-traversal-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_tree_traversal_lab shape
```

```bash
cd exercises/cs-core/traceable-tree-traversal-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_tree_traversal_lab shape
```

两种语言应逐字输出同一份槽位、大小、高度、叶子数和根孩子。`recursive`、`frontier` 也先做回归，下一课会正式拆解它们。

</section>

<section id="modify-trailing-null" data-learning-context="modify-trailing-null" data-context-type="modify" markdown="1">

## 加空槽，再修改原列表

给固定输入末尾追加三个 `None` 后构造树，再把原列表第一个值改成 99。树内部仍应规范为七个槽位，根值仍是 7。

再试着删除中间槽位 3。你应该会发现 5 的下标变化，`LR` 的路径也不再成立——这正是中间空槽必须保留的原因。

</section>

<section id="modify-slot-path" data-learning-context="modify-slot-path" data-context-type="modify" markdown="1">

## 换一个槽位算路径

选择槽位 5 或 6，不按值搜索，而是反复计算父下标并记录左右方向。到达根后把记录逆序，再用树的检查式访问确认槽位确实存在。

这棵树允许重复值，因此“找到值 11”不能替代“找到槽位 6”。路径由结构决定，不由值是否唯一决定。

</section>

<section id="troubleshoot-tree-shape" data-learning-context="troubleshoot-tree-shape" data-context-type="troubleshoot" markdown="1">

## 高度差一、路径反了或节点失联

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 单节点高度得到 1 | 把节点层数当成边数 | 根深度固定为 0 |
| `LR` 算成 `RL` | 从目标向根记录后没有逆序 | 到根后反转方向列表 |
| 5 变成 3 的左孩子 | 删除了中间空槽 | 只裁末尾空槽 |
| 孤儿节点悄悄消失 | 只按数组范围建节点 | 构造时逐项检查父槽 |
| 修改原列表后树也变化 | 保存了可变输入引用 | 构造时复制并冻结槽位 |
| C++ 出现重复释放风险 | 节点使用共享或裸拥有指针 | 父节点用 `unique_ptr` 单一拥有 |

</section>

<section id="project-tree-v01" data-learning-context="project-tree-v01" data-context-type="project" markdown="1">

## 可追踪树与遍历实验 v0.1

```text
规范化槽位 → 校验根与父槽 → 建立私有链接节点
                              ↓
                    形状报告与 path_to_slot
```

项目现在有一棵不会因调用方改写而变形、不会产生孤儿链接、能解释根到任意合法槽位路径的树。下一课直接复用这些私有链接，观察递归调用顺序和最大深度。

[查看可追踪树与遍历实验](../../exercises/cs-core/traceable-tree-traversal-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-sparse-space" data-learning-context="deepen-sparse-space" data-context-type="deepen" markdown="1">

## 稀疏树为什么不总适合槽位表示

构造器按规范化槽位长度 `m` 扫描并建树，时间和槽位空间都是 `Theta(m)`。链接节点只需要与真实节点数 `n` 同阶的节点空间。

接近完整的树里，m 与 n 很接近；极度稀疏的深树可能为了一个远处节点保留大量空槽。本实验同时保存两份表示，是为了比较结构和得到确定性证据，不是所有生产二叉树的默认方案。

</section>

<section id="career-tree-evidence" data-learning-context="career-tree-evidence" data-context-type="career" markdown="1">

## 面试里别只背三个下标公式

先画出槽位 0、1、2、4 的关系，再解释为什么内部空槽不能删除、孤儿槽必须拒绝。随后说明链接节点的单一所有权，以及槽位和链接表示在稀疏树上的空间取舍。

最后用 `path_to_slot(4) == LR` 和空槽受控失败收尾。这样既讲了表示，也讲了不变量、资源边界和测试。

</section>

## 完成检查

- [ ] 能说清根、孩子、叶子、深度和按边数计算的高度。
- [ ] 能用零基公式算槽位 4、5、6 的父子关系和根路径。
- [ ] 空根、孤儿槽、负下标、空槽和越界都有明确失败。
- [ ] 只裁末尾空槽，构造后修改原列表不会改变树。
- [ ] C++ 链接节点由 `unique_ptr` 单一拥有，树可移动但不可复制。
- [ ] Python 类型检查与单元测试、C++ 构建与 CTest、三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [MIT 6.006 Binary Trees](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/376714cc85c6c784d90eec9c575ec027_MIT6_006S20_lec6.pdf) | 二叉树术语、深度与高度 | 2020 课程，2026-07-17 核查 |
| [Open Data Structures BinaryTree](https://opendatastructures.org/ods-python/6_1_BinaryTree_Basic_Binary.html) | 树形结构与空树高度 | 2026-07-17 核查 |
| [C++ `unique_ptr`](https://eel.is/c++draft/unique.ptr.single) | 单一所有权和移动语义 | C++20 教学基线，2026-07-17 核查 |

槽位与链接双表示是为了让学习过程可追踪；实际工程要按树的稠密程度、更新方式和访问需求选择表示。

## 下一步

进入[递归深度优先遍历、基线条件与调用深度](16-recursive-dfs-traversal-call-frames.md)，沿同一棵链接树观察前序、中序、后序和递归帧。
