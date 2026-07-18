<div class="be-tutor-mount" data-tutor-lesson="cs-core-16" aria-hidden="true"></div>

<section id="overview-recursive-orders" class="be-page-hero be-lesson-hero" data-learning-context="overview-recursive-orders" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">共同算法基础 · 第 12 课 · 可追踪树与遍历实验</span>

# 递归深度优先遍历、基线条件与调用深度

## 同一棵树，只把“记录当前节点”的时机换了三个位置

```text
preorder：  7, 3, 5, 9, 8, 11
inorder：   3, 5, 7, 8, 9, 11
postorder： 5, 3, 8, 11, 9, 7
visits=6，max_depth=2
```

三种顺序都沿左、右孩子做深度优先遍历。区别不在“走哪条边”，而在进入节点、左边返回或两边都返回时，哪一刻把当前值写进结果。

[看前序调用帧](#example-preorder-frames){ .md-button .md-button--primary }
[运行短轨迹](#reproduce-recursive-frames){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>共同算法基础 · 12 / 16</strong></span><span>前置<strong>合法树形与私有链接</strong></span><span>完成后留下<strong>三种顺序、调用深度和目标层剪枝</strong></span></div>

</section>

## 开始前

- 能沿 `left`、`right` 看懂一棵链接二叉树。
- 知道空树没有根，单节点树的根深度为 0。
- 不通过无限递归学习失败；课程使用可恢复的显式深度保护。

<section id="concept-recursive-contract" data-learning-context="concept-recursive-contract" data-context-type="concept" markdown="1">

## 递归要回答三个问题

1. **什么时候停？** 节点为空时立即返回。
2. **非空时做什么？** 处理当前节点，再进入左右孩子。
3. **为什么最终会停？** 孩子子树严格小于当前子树，每条路径最后都会走到空链接。

只写“空节点返回”还不够。若递归调用没有进入更小的问题，仍可能永远到不了基线条件。

</section>

<section id="example-preorder-frames" data-learning-context="example-preorder-frames" data-context-type="example" markdown="1">

## 前序为什么先得到 7、3、5

<div class="be-call-frames" role="img" aria-label="前序遍历进入7、3、5时活动调用帧逐层增加，5返回后恢复3，再恢复7">
  <div><strong>进入 7</strong><code>[7]</code><span>记录 7，准备走左边</span></div>
  <div><strong>进入 3</strong><code>[7, 3]</code><span>记录 3，准备走右边的 5</span></div>
  <div><strong>进入 5</strong><code>[7, 3, 5]</code><span>记录 5，左右都为空</span></div>
  <div><strong>返回</strong><code>[7, 3] → [7]</code><span>恢复未完成调用，继续右子树</span></div>
</div>

每个未返回的调用帧保存当前节点和“回来以后从哪里继续”。它不是把整棵树复制一遍，只保留当前根到节点这条路径上的工作。

</section>

<section id="concept-visit-position" data-learning-context="concept-visit-position" data-context-type="concept" markdown="1">

## 三种顺序只移动一行代码

```text
preorder：  record(node) → left → right
inorder：   left → record(node) → right
postorder： left → right → record(node)
```

前序适合先看到父节点；中序在二叉搜索树中会得到有序键，但普通二叉树并不保证有序；后序等孩子处理完才处理父节点，常用于自底向上汇总或释放。

</section>

<section id="example-three-orders" data-learning-context="example-three-orders" data-context-type="example" markdown="1">

## 用根节点 7 检查记录时机

| 顺序 | 7 什么时候出现 | 固定输出中的位置 |
| --- | --- | --- |
| 前序 | 进入根时 | 第 1 个 |
| 中序 | 左子树全部返回后 | 第 3 个 |
| 后序 | 左右子树都返回后 | 最后 1 个 |

只要根的位置不符合这张表，就先检查 `record(node)` 放在两次递归调用的哪个位置。

</section>

<section id="concept-empty-single" data-learning-context="concept-empty-single" data-context-type="concept" markdown="1">

## 空树和单节点树最适合检查基线

空树没有任何非空节点被访问，所以三种结果都是空序列，`visits=0`、`max_depth=-1`。单节点树只访问根，三种顺序都得到 `(7,)`，最深深度为 0。

这两组测试很短，却能同时发现忘记空节点返回、空树深度写错和记录位置重复等问题。

</section>

<section id="reproduce-recursive-frames" data-learning-context="reproduce-recursive-frames" data-context-type="reproduce" markdown="1">

## 运行调用帧短轨迹

```bash
.venv/bin/python site-src/examples/algorithm-foundation/recursive_dfs_frames_trace.py
```

先预测每次 `enter` 后的 `stack`。当 5 离开时，程序恢复到 3；3 离开后恢复到 7，再进入右孩子 9。这里的列表只是把运行时调用关系打印出来，正式递归函数仍由语言运行时管理调用栈。

</section>

<section id="reproduce-bilingual-recursive" data-learning-context="reproduce-bilingual-recursive" data-context-type="reproduce" markdown="1">

## 回归双语言阶段作品

```bash
cd exercises/cs-core/traceable-tree-traversal-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_tree_traversal_lab recursive
```

```bash
cd exercises/cs-core/traceable-tree-traversal-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_tree_traversal_lab recursive
```

同时回归 `shape` 和 `frontier`。两种语言仍使用上一课的固定树，三份报告必须逐字一致。

</section>

<section id="modify-labeled-orders" data-learning-context="modify-labeled-orders" data-context-type="modify" markdown="1">

## 给重复值加结构标签

把两个节点都改成值 5，并在调试输出里临时附加槽位标签，例如 `5@1`、`5@4`。预测三种顺序后再运行。

最终公开接口仍返回整数值；标签只帮助你确认遍历顺序来自节点位置，而不是误以为每个值都唯一。

</section>

<section id="modify-count-depth" data-learning-context="modify-count-depth" data-context-type="modify" markdown="1">

## 只数目标层，不必走到更深处

`count_at_depth(tree, depth)` 携带当前深度。到达目标层就计数并返回，不再进入孩子：

```text
depth 0 → count=1，visits=1
depth 1 → count=2，visits=3
depth 2 → count=3，visits=6
depth 3 → count=0，visits=6
```

负深度不属于接口契约，应明确拒绝；合法但不存在的层返回 0。

</section>

<section id="troubleshoot-recursion" data-learning-context="troubleshoot-recursion" data-context-type="troubleshoot" markdown="1">

## 不终止、顺序相同或深度失真

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 递归不终止 | 没有空节点返回，或递归回到原节点 | 先锁定基线，再确认只进孩子 |
| 三种顺序完全相同 | `record` 总在同一位置 | 对照左递归、记录、右递归 |
| 空树深度为 0 | 把未访问的根算进结果 | 空树 deepest 初始为 -1 |
| `max_depth=1` 仍访问深度 2 | 检查写在记录之后 | 进入节点、记录值之前检查 |
| 超限后返回半份序列 | 吞掉异常并继续组装结果 | 让调用整体失败，不发布局部轨迹 |
| 目标层访问数过大 | 到层后仍继续递归 | 计数后立即 return |

</section>

<section id="project-tree-v02" data-learning-context="project-tree-v02" data-context-type="project" markdown="1">

## 可追踪树与遍历实验 v0.2

```text
v0.1 规范槽位与私有链接
          ↓
v0.2 前中后序 + visits/max_depth + count_at_depth
```

项目现在不仅知道树长什么样，还能解释递归如何沿链接推进、在何处记录值、同时保留多少调用帧。下一课把这份隐式调用栈换成显式栈和队列。

[查看可追踪树与遍历实验](../../exercises/cs-core/traceable-tree-traversal-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-recursive-cost" data-learning-context="deepen-recursive-cost" data-context-type="deepen" markdown="1">

## 时间看节点数，活动空间看树高

完整遍历让每个非空节点恰好被记录一次，时间是 `Theta(n)`。同一时刻尚未返回的调用帧只沿一条根到当前节点路径存在，辅助空间是 `Theta(h)`。

平衡树的 h 通常与 `log n` 同阶；退化成链的树可能 h=n。递归空间不是恒定的，也不能只看平均形状忽略最坏情况。

</section>

<section id="deepen-depth-guard" data-learning-context="deepen-depth-guard" data-context-type="deepen" markdown="1">

## 用显式上限观察风险

固定树高度为 2。传入 `max_depth=1` 时，遍历准备进入深度 2 节点就抛出受控异常；改为 2 后完整结果恢复。

Python 的 `sys.getrecursionlimit()` 只作为运行时背景，不在课程里修改；C++ 也不制造真实栈溢出。显式上限让失败可预测、可测试、不会破坏当前进程。

</section>

<section id="career-recursion-evidence" data-learning-context="career-recursion-evidence" data-context-type="career" markdown="1">

## 怎样讲清一次树递归

先说空节点基线和“只进入更小子树”的进展，再用前序的 `[7] → [7,3] → [7,3,5]` 展示活动帧。随后把记录位置移动到左右递归之间和之后，得到中序、后序。

最后补上 `Theta(n)`、`Theta(h)`、显式深度保护和目标层剪枝。这样回答既有正确性，也有运行状态、成本和失败方式。

</section>

## 完成检查

- [ ] 能用基线条件、递归情况和规模缩小说明遍历为什么终止。
- [ ] 能在固定树上手算前序、中序、后序，并指出记录位置。
- [ ] 空树得到 0 次访问和 -1 深度，单节点三种顺序一致。
- [ ] `max_depth=1` 在进入深度 2 前失败，恢复后没有状态残留。
- [ ] `count_at_depth` 到目标层立即返回，四个固定深度的计数和访问数正确。
- [ ] Python 类型检查与单元测试、C++ 构建与 CTest、三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [MIT 6.006 Binary Trees](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/376714cc85c6c784d90eec9c575ec027_MIT6_006S20_lec6.pdf) | 树遍历与高度成本 | 2020 课程，2026-07-17 核查 |
| [Open Data Structures BinaryTree](https://opendatastructures.org/ods-python/6_1_BinaryTree_Basic_Binary.html) | 递归遍历与树高 | 2026-07-17 核查 |
| [Python `sys.getrecursionlimit`](https://docs.python.org/3.11/library/sys.html#sys.getrecursionlimit) | 解释器递归限制背景 | Python 3.11，2026-07-17 核查 |

课程通过显式教学上限演示深度失败，不建议为了绕过算法结构问题随意提高运行时递归限制。

## 下一步

进入[迭代 DFS、BFS 与层级前沿](17-iterative-dfs-bfs-frontier-levels.md)，把隐式调用栈改成可观察的显式容器。
