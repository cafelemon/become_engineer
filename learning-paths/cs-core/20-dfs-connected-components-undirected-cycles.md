<div class="be-tutor-mount" data-tutor-lesson="cs-core-20" aria-hidden="true"></div>

<section id="overview-dfs-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-dfs-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">共同算法基础 · 第 16 课 · 可追踪图遍历实验</span>

# DFS、连通分量与无向环检测

## 从 0 出发看不到 5，怎样把整张图走完

```text
全图 DFS
components=2
component 0：0, 1, 3, 2, 4
component 1：5, 6
visits=7，edge_checks=12，max_depth=3
cycle=yes，first_edge=(0, 2)
labels：0, 0, 0, 0, 0, 1, 1
```

一次 DFS 只能走完起点所在的连通部分。要覆盖整张图，就继续按顶点编号扫描；每遇到一个没访问过的顶点，再启动一次 DFS。上面的固定图会从 0 和 5 各启动一次，因此有两个连通分量。

[看全图扫描怎样重启](#example-component-scan){ .md-button .md-button--primary }
[运行递归轨迹](#reproduce-dfs-trace){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>共同算法基础 · 16 / 16</strong></span><span>前置<strong>无权 BFS、距离与父链</strong></span><span>完成后留下<strong>全图遍历、分量标签与无向环证据</strong></span></div>

</section>

## 开始前

- 图仍是简单无向图，每行邻居按升序保存。
- 能区分“已发现”与“尚未访问”，知道一般图可能形成环。
- 本课只判断无向环；有向图的回边、拓扑排序和强连通分量另行学习。

<section id="concept-single-full-search" data-learning-context="concept-single-full-search" data-context-type="concept" markdown="1">

## 单起点搜索与全图遍历回答不同问题

从 0 运行 BFS 或 DFS，只能回答“哪些顶点能从 0 到达”。全图 DFS 在外面再加一层顶点扫描，回答“整张图可以分成多少块”。

外层扫描不改变单次 DFS 的写法。它只负责找到下一个尚未访问的起点，并为这个新分量准备空结果。

</section>

<section id="example-component-scan" data-learning-context="example-component-scan" data-context-type="example" markdown="1">

## 扫描到 5 时，启动第二次 DFS

<div class="be-component-scan" aria-label="全图 DFS 收集连通分量">
  <div><strong>扫描 0</strong><code>未访问</code><span>启动分量 0</span></div>
  <div><strong>DFS(0)</strong><code>0,1,3,2,4</code><span>五个顶点标记完成</span></div>
  <div><strong>继续到 5</strong><code>未访问</code><span>启动分量 1</span></div>
  <div><strong>DFS(5)</strong><code>5,6</code><span>所有顶点均已访问</span></div>
</div>

顶点 1–4 在外层扫描时已经访问，不会重复启动。若顶点没有任何边，它仍会作为一个只含自己的分量被收集。

</section>

<section id="concept-mark-before-recursion" data-learning-context="concept-mark-before-recursion" data-context-type="concept" markdown="1">

## 进入顶点，先标记，再看邻居

递归函数一进入 `vertex` 就把它加入 `visited`，然后按升序扫描邻居。若邻居尚未访问，才沿这条边递归。

这里不能把标记推迟到递归返回之后。环上的另一个顶点会立刻沿边回来，再次进入同一个调用，递归便无法收束。

</section>

<section id="concept-parent-edge" data-learning-context="concept-parent-edge" data-context-type="concept" markdown="1">

## 孩子回看父节点，不是发现了环

无向边 `{0,1}` 同时出现在 0 和 1 的邻接表里。DFS 从 0 走到 1 后，1 必然会看见已经访问的 0；那只是刚才走过的树边反向项。

因此遇到已访问邻居时，还要判断它是否等于当前调用的父节点。只有“已访问且不是父节点”才提供无向环证据。

</section>

<section id="example-cycle-evidence" data-learning-context="example-cycle-evidence" data-context-type="example" markdown="1">

## 路径图没有环，固定图有

```text
无环路径：0 — 1 — 2
1 看见 0：父边，跳过
2 看见 1：父边，跳过

固定图的一部分：0 — 1 — 3 — 2 — 0
2 看见 0：已访问且不是父节点，得到环证据 (0,2)
```

项目把首次证据规范为 `(min(u,v), max(u,v))`。它证明存在环，但不承诺立即返回完整环路径。

</section>

<section id="reproduce-dfs-trace" data-learning-context="reproduce-dfs-trace" data-context-type="reproduce" markdown="1">

## 看递归在哪里进入新分量

先猜第二个 `start_component` 会打印哪个顶点，再运行：

```bash
.venv/bin/python site-src/examples/algorithm-foundation/full_graph_dfs_trace.py
```

缩进表示递归深度。脚本会打印进入顶点、检查边、首次环证据、两个分量和最终标签，便于把调用栈与图结构对在一起。

</section>

<section id="reproduce-bilingual-dfs" data-learning-context="reproduce-bilingual-dfs" data-context-type="reproduce" markdown="1">

## 回归一般图三份报告

```bash
cd exercises/cs-core/traceable-graph-traversal-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_graph_traversal_lab dfs
```

```bash
cd exercises/cs-core/traceable-graph-traversal-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_graph_traversal_lab dfs
```

Python 与 C++ 都应输出两个分量、7 次访问、12 次邻接项检查、最大深度 3 和首次环边 `(0,2)`。同时回归 `graph`、`bfs`，三份报告逐字一致。

</section>

<section id="modify-edge-order" data-learning-context="modify-edge-order" data-context-type="modify" markdown="1">

## 打乱边顺序，DFS 轨迹仍不变

把原始边列表倒序，再运行全图 DFS。上一课的图构造会把规范边和每行邻居重新排序，所以分量顺序仍是 `[0,1,3,2,4]`、`[5,6]`。

如果结果跟着输入排列变化，先修邻接表示，不要在 DFS 里硬编码期望顺序。

</section>

<section id="modify-isolated-components" data-learning-context="modify-isolated-components" data-context-type="modify" markdown="1">

## 三个没有边的顶点有几个分量

建立 `V=3`、边集为空的图。外层扫描会分别从 0、1、2 启动，得到三个单顶点分量，标签是 `0,1,2`，没有环，最大深度为 0。

空图则没有任何启动点：分量和标签都为空，项目把最大深度定义为 -1。两者不要混在一起。

</section>

<section id="troubleshoot-dfs" data-learning-context="troubleshoot-dfs" data-context-type="troubleshoot" markdown="1">

## 少分量、无限递归或所有边都像环

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 只得到 `[0,1,3,2,4]` | 只从 0 调用一次 DFS | 外层扫描所有顶点并在未访问点重启 |
| 环上反复递归 | 进入后没有立即标记 | 扫描邻居前写入 `visited` |
| 路径 `0—1—2` 被判有环 | 没有排除父边 | 已访问邻居必须不等于父节点 |
| 分量编号每次不同 | 顶点或邻接顺序不固定 | 外层编号和每行邻居都升序 |
| 孤立顶点消失 | 从边集合反推顶点 | 按 `[0,V)` 扫描完整顶点集合 |
| 空图深度变成 0 | 默认假设启动过 DFS | 无分量时明确返回 -1 |

</section>

<section id="project-graph-v10" data-learning-context="project-graph-v10" data-context-type="project" markdown="1">

## 可追踪图遍历实验 v1.0

```text
v0.1 简单无向图、规范边、邻接表示和输入校验
v0.2 BFS、无权距离、父链、最短路径和范围查询
v1.0 全图 DFS、连通分量、分量标签和无向环证据
```

三课已经把输入、表示、单起点搜索和全图分析串在一起。正常图、空图、孤立点、不可达目标、父边误判和输入重排都有固定测试，Python 与 C++ 使用同一公开报告契约。

[查看可追踪图遍历实验](../../exercises/cs-core/traceable-graph-traversal-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-dfs-counts" data-learning-context="deepen-dfs-counts" data-context-type="deepen" markdown="1">

## 为什么完整 DFS 是 `Theta(V+E)`

外层扫描每个顶点一次，首次进入时才加入 `visited`。邻接表中的每个条目也只在所属顶点被处理时扫描一次；无向边有两个邻接项，所以固定图的 6 条边对应 12 次检查。

总工作量是 `V+2E`，省略常数后为 `Theta(V+E)`。`visited`、分量结果和递归栈最坏都可能占 `Theta(V)` 空间。

</section>

<section id="deepen-recursion-boundary" data-learning-context="deepen-recursion-boundary" data-context-type="deepen" markdown="1">

## 递归深度不是连通分量大小

固定图第一个分量有 5 个顶点，但按当前邻接顺序形成的 DFS 树最深只有 3 条树边。深度取决于 DFS 树形，不等于顶点数或最短距离。

长链图的递归深度会接近 `V-1`，可能碰到语言调用栈限制。需要处理超深输入时，应改用显式栈并保持相同的发现与父边规则。

</section>

<section id="career-dfs-evidence" data-learning-context="career-dfs-evidence" data-context-type="career" markdown="1">

## 用一个误判讲清无向环检测

先用 `0—1—2` 说明孩子必然回看父节点，因此“看见已访问邻居”不能直接判环。再换到 `0—1—3—2—0`，指出 2 看见 0 时它不是父节点，才得到真实环证据。

接着补上外层重启如何收集两个分量、孤立点如何处理，以及 7 次顶点访问和 12 次邻接检查。这个回答比只说“DFS 可以判环”更完整，也更容易被代码和测试验证。

</section>

## 完成检查

- [ ] 能区分单起点搜索与覆盖整张图的外层扫描。
- [ ] 进入顶点先标记，固定图不会沿环重复递归。
- [ ] 路径图不误报；已访问且非父节点的邻居提供环证据。
- [ ] 固定图得到两个分量和标签 `0,0,0,0,0,1,1`。
- [ ] 空图、三个孤立顶点、边输入重排和深链边界都能解释。
- [ ] Python 类型检查与单元测试、C++ 构建与 CTest、三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [MIT 6.006 Lecture 10](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/f3e349e0eb3288592289d2c81e0c4f4d_MIT6_006S20_lec10.pdf) | DFS、全图搜索与连通分量 | 2026-07-17 核查 |
| [Open Data Structures 图遍历](https://opendatastructures.org/ods-python/12_3_Graph_Traversal.html) | 已访问状态和邻接表遍历成本 | 2026-07-17 核查 |
| [Python 递归限制](https://docs.python.org/3.11/library/sys.html#sys.getrecursionlimit) | 深链输入的调用栈边界 | Python 3.11，2026-07-17 核查 |
| [C++ 函数调用](https://eel.is/c++draft/expr.call) | 递归调用语义边界 | C++20 教学基线，2026-07-17 核查 |

本课的父边规则只适用于无向图。有向图需要按发现、处理中和完成等状态区分边类型，不能删除 `parent` 判断后直接沿用。

## 下一步

共同算法与数据结构基础到这里闭环。进入算法核心的[二叉最小堆、隐式树与堆不变量](21-binary-min-heap-implicit-tree-invariant.md)，开始处理“始终取出当前最小项”的数据结构。
