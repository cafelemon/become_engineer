<div class="be-tutor-mount" data-tutor-lesson="cs-core-17" aria-hidden="true"></div>

<section id="overview-frontier-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-frontier-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">共同算法基础 · 第 13 课 · 可追踪树与遍历实验</span>

# 迭代 DFS、BFS 与层级前沿

## 换一个待处理容器，访问顺序就变了

```text
dfs_preorder：   7, 3, 5, 9, 8, 11   max_frontier=2
bfs_level_order：7, 3, 9, 5, 8, 11   max_frontier=3
levels：0=[7] 1=[3,9] 2=[5,8,11]
```

DFS 把待处理节点放进栈，最后加入的先处理；BFS 放进队列，最早发现的先处理。两者都访问同样的 6 个节点，但前沿里同时等待的节点和最终顺序不同。

[比较两种前沿](#example-stack-queue){ .md-button .md-button--primary }
[运行完整轨迹](#reproduce-frontier-trace){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>共同算法基础 · 13 / 16</strong></span><span>前置<strong>递归 DFS 与调用深度</strong></span><span>完成后留下<strong>显式栈队列、层级行和最宽层</strong></span></div>

</section>

## 开始前

- 能说出栈的后进先出与队列的先进先出。
- 已有一棵经过校验、没有环、每个节点只有唯一父节点的树。
- 本课先处理树；一般图为什么需要 `visited`，留到下一组正式展开。

<section id="concept-frontier" data-learning-context="concept-frontier" data-context-type="concept" markdown="1">

## 前沿是“已经发现，但还没处理”

根先进入容器，成为第一个前沿节点。每次取出一个节点并记录它，再把存在的孩子加入容器。容器中剩下的元素，就是下一步可能处理的范围。

前沿不等于已经访问的节点集合，也不等于容器分配的容量；课程统计的是当时真实等待处理的节点数。

</section>

<section id="example-stack-queue" data-learning-context="example-stack-queue" data-context-type="example" markdown="1">

## 处理完 7，两种容器里都有 3 和 9

<div class="be-frontier-compare">
  <div><strong>DFS · 栈</strong><code>[9, 3] ← top</code><span>3 最后压入，所以下一个弹出 3</span></div>
  <div><strong>BFS · 队列</strong><code>front → [3, 9]</code><span>3 先入队，所以下一个取出 3</span></div>
</div>

第二步开始分叉：DFS 继续深入 3 的孩子 5；BFS 会先处理与 3 同层的 9。

</section>

<section id="concept-dfs-push-order" data-learning-context="concept-dfs-push-order" data-context-type="concept" markdown="1">

## 想先访问左孩子，就要先压右孩子

栈是后进先出。处理 7 时先压 9、再压 3，3 才会位于栈顶。弹出节点时记录当前值，就能得到与递归前序完全相同的结果。

```text
pop 7 → push 9,3
pop 3 → push 5
pop 5 → pop 9 → ...
```

</section>

<section id="concept-bfs-levels" data-learning-context="concept-bfs-levels" data-context-type="concept" markdown="1">

## 队列为什么自然形成层序

队列从头取出、从尾加入。深度 1 的 3、9 都比深度 2 的 5、8、11 更早入队，所以一定先完成浅层。

让队列项携带深度；首次看到新深度时创建一行，后续同深度节点按入队顺序追加，就得到 `[7] [3,9] [5,8,11]`。

</section>

<section id="example-frontier-trace" data-learning-context="example-frontier-trace" data-context-type="example" markdown="1">

## 峰值出现在什么时候

| 遍历 | 产生峰值的时刻 | 等待节点 | 峰值 |
| --- | --- | --- | ---: |
| DFS | 处理 7 或 9 后 | `[9,3]` / `[11,8]` | 2 |
| BFS | 处理 9 后 | `[5,8,11]` | 3 |

初始根进入容器时也要参与统计。空树没有根，峰值为 0；单节点树峰值为 1。

</section>

<section id="reproduce-frontier-trace" data-learning-context="reproduce-frontier-trace" data-context-type="reproduce" markdown="1">

## 逐项打印两个容器

```bash
.venv/bin/python site-src/examples/algorithm-foundation/tree_frontier_trace.py
```

运行前先写出处理 9 之后的栈和队列。轨迹将固定打印每次 `pop` 后剩余的前沿，并在末尾给出 DFS 的 2 和 BFS 的 3。

</section>

<section id="reproduce-bilingual-frontier" data-learning-context="reproduce-bilingual-frontier" data-context-type="reproduce" markdown="1">

## 回归双语言阶段作品

```bash
cd exercises/cs-core/traceable-tree-traversal-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_tree_traversal_lab frontier
```

```bash
cd exercises/cs-core/traceable-tree-traversal-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_tree_traversal_lab frontier
```

同时回归 `shape` 与 `recursive`。两种语言三份报告必须逐字一致，迭代前序还要逐项等于递归前序。

</section>

<section id="modify-reverse-push" data-learning-context="modify-reverse-push" data-context-type="modify" markdown="1">

## 故意把压栈顺序反过来

临时改成先压左、再压右。右孩子会最后进入、最先弹出，序列在 7 后变成 9 开头。

不要修改节点链接或预期输出来“修测试”。恢复先右后左，再用递归前序作为独立参照，确认完整序列逐项相等。

</section>

<section id="modify-widest-level" data-learning-context="modify-widest-level" data-context-type="modify" markdown="1">

## 找到最宽层

按深度扫描已经生成的层级行，只在当前宽度**严格大于**已知宽度时更新：

```text
固定树 → depth=2, width=3, visits=6
单节点 → depth=0, width=1, visits=1
空树   → depth=None, width=0, visits=0
```

严格大于让并列宽度保留较浅的第一层；结果不依赖节点值排序。

</section>

<section id="troubleshoot-frontier" data-learning-context="troubleshoot-frontier" data-context-type="troubleshoot" markdown="1">

## DFS 走右边、BFS 变深搜或峰值少算

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| DFS 在 7 后访问 9 | 先压左、后压右 | 恢复先右后左 |
| BFS 不按层 | 从队尾取出，队列被当成栈 | 头部取出、尾部加入 |
| `max_frontier` 少 1 | 只在取出后统计 | 初始根和每次加入后更新 |
| 空树峰值为 1 | 无条件假设根已入容器 | 空根直接返回零轨迹 |
| 层级深度跳号 | 孩子没有携带 `depth+1` | 队列项保存节点和深度 |
| 树遍历无故重复跳过 | 提前套用图的 `visited` | 先依赖已验证的无环树契约 |

</section>

<section id="project-tree-v10" data-learning-context="project-tree-v10" data-context-type="project" markdown="1">

## 可追踪树与遍历实验 v1.0

```text
v0.1 形状、槽位与链接所有权
v0.2 递归三序、调用深度与层计数
v1.0 显式 DFS/BFS、前沿峰值、层级行与最宽层
```

树组现在从输入表示一直走到递归和迭代遍历，正常、空树、顺序反转、深度超限和并列宽度都有测试。下一组把“唯一父节点、没有环”的树放宽为一般无向图。

[查看可追踪树与遍历实验](../../exercises/cs-core/traceable-tree-traversal-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-frontier-space" data-learning-context="deepen-frontier-space" data-context-type="deepen" markdown="1">

## 两种遍历都是线性时间，空间形状不同

DFS、BFS 都让每个节点进入并离开容器一次，完整遍历时间是 `Theta(n)`。BFS 前沿通常由最大层宽 `w` 主导；迭代 DFS 保存待处理分支，在某些树形下也可能积累到线性规模。

不要简单说“DFS 永远只用树高空间”。递归调用栈沿单条路径是 `Theta(h)`；这里统计的显式前沿还可能同时保留多个尚未处理的右分支。

</section>

<section id="deepen-tree-graph-boundary" data-learning-context="deepen-tree-graph-boundary" data-context-type="deepen" markdown="1">

## 为什么这节课没有 `visited`

当前 `BinaryTree` 在构造时保证唯一根、唯一父节点和无环链接，从根沿孩子边不会再次遇到同一节点，因此不需要访问集合。

一般图允许多个邻居指向同一顶点，也可能形成环。下一组必须在加入前沿时管理发现状态，否则会重复处理甚至无法终止。

</section>

<section id="career-frontier-evidence" data-learning-context="career-frontier-evidence" data-context-type="career" markdown="1">

## 用同一棵树比较 DFS 与 BFS

先说明前沿的定义，再展示处理 7 后的栈 `[9,3]` 和队列 `[3,9]`。继续走到 DFS 峰值 2、BFS 峰值 3，并说明先右后左为何复现递归前序。

最后补上层级行、最宽层、空树和树／图边界。这样的比较包含容器语义、固定轨迹、空间证据和适用条件。

</section>

## 完成检查

- [ ] 能区分前沿、已访问节点和容器容量。
- [ ] 迭代 DFS 先压右后压左，完整序列等于递归前序。
- [ ] BFS 头部取出、尾部按左后右加入，生成连续层级行。
- [ ] 固定树 DFS/BFS 峰值分别为 2、3，空树与单节点正确。
- [ ] `widest_level` 并列时保留较浅层，空树返回无深度。
- [ ] Python 类型检查与单元测试、C++ 构建与 CTest、三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [Open Data Structures BinaryTree](https://opendatastructures.org/ods-python/6_1_BinaryTree_Basic_Binary.html) | 树的 BFS 与队列前沿 | 2026-07-17 核查 |
| [Open Data Structures Graph Traversal](https://opendatastructures.org/ods-python/12_3_Graph_Traversal.html) | DFS/BFS 容器差异与图边界 | 2026-07-17 核查 |
| [Python `deque`](https://docs.python.org/3.11/library/collections.html#collections.deque) | 头部取出和尾部加入 | Python 3.11，2026-07-17 核查 |
| [C++ 容器适配器](https://eel.is/c++draft/container.adaptors.general) | `stack` 与 `queue` 接口 | C++20 教学基线，2026-07-17 核查 |

本课的 BFS 只说明层序遍历；“BFS 给出最短路”还需要无权或等权边条件，将在图课程中单独证明。

## 下一步

树的表示、递归与显式遍历基础闭环完成。进入[简单无向图、邻接表示与输入边界](18-undirected-graph-adjacency-representations.md)，把唯一父节点的树扩展为可能存在多条到达路径的一般图。
