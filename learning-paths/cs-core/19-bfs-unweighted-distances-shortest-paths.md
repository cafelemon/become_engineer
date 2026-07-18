<div class="be-tutor-mount" data-tutor-lesson="cs-core-19" aria-hidden="true"></div>

<section id="overview-bfs-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-bfs-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">共同算法基础 · 第 15 课 · 可追踪图遍历实验</span>

# BFS、无权距离与最短路径

## 从 0 到 4，至少经过几条边

```text
0 ─ 1 ─ 3 ─ 4
└─ 2 ─┘       5 ─ 6

一条最短路径：0 → 1 → 3 → 4
距离：3
```

先在图上从 0 一层一层向外看：第一层是 1、2，第二层是 3，第三层才到 4。BFS 用队列保持这个顺序，再把第一次到达每个顶点的来源记下来，最后就能还原路径。

[跟着队列走一遍](#example-bfs-queue){ .md-button .md-button--primary }
[运行完整轨迹](#reproduce-bfs-trace){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>共同算法基础 · 15 / 16</strong></span><span>前置<strong>简单无向图与邻接表示</strong></span><span>完成后留下<strong>距离、父链、最短路径和范围查询</strong></span></div>

</section>

## 开始前

- 图已经通过输入校验，每行邻居按升序保存。
- 知道队列从头取出、从尾加入。
- 这里的“最短”指经过的边最少，只适用于无权图或所有边代价相同的图。

<section id="concept-layer-order" data-learning-context="concept-layer-order" data-context-type="concept" markdown="1">

## 队列让浅层先于深层处理

起点距离是 0。处理距离为 `d` 的顶点时，新发现的邻居距离就是 `d+1`，并排到队尾。队头仍然保留更早发现、距离不大于 `d+1` 的顶点，所以更深的层不可能插队。

因此一个顶点第一次被发现时，已经找到了从起点到它的最少边数。这个结论依赖队列顺序和等权条件，不是“搜索过就一定最短”。

</section>

<section id="example-bfs-queue" data-learning-context="example-bfs-queue" data-context-type="example" markdown="1">

## 让队列、距离和父节点一起走

<div class="be-bfs-trace" data-bfs-trace aria-label="BFS 队列、距离和父节点单步演示">
  <div class="be-bfs-trace__stage">
    <strong data-bfs-title>先把 0 放进队列</strong>
    <div class="be-bfs-trace__state"><span data-bfs-queue>队列：0</span><span data-bfs-distance>距离：0=0</span><span data-bfs-parent>父节点：0←无</span></div>
  </div>
  <div class="be-bfs-trace__controls"><button type="button" data-bfs-prev>上一步</button><button type="button" data-bfs-next>下一步</button><button type="button" data-bfs-reset>重新开始</button><span data-bfs-position class="be-bfs-trace__position">1 / 6</span></div>
</div>

??? info "没有 JavaScript 时，按这张表走"
    | 时刻 | 取出 | 队列 | 新发现 | 父节点 |
    | --- | --- | --- | --- | --- |
    | 0 | — | 0 | 0 | 0←无 |
    | 1 | 0 | 1,2 | 1,2 | 1←0，2←0 |
    | 2 | 1 | 2,3 | 3 | 3←1 |
    | 3 | 2 | 3 | 无 | 3 不改变 |
    | 4 | 3 | 4 | 4 | 4←3 |
    | 5 | 4 | 空 | 无 | 结束 |

</section>

<section id="concept-mark-on-enqueue" data-learning-context="concept-mark-on-enqueue" data-context-type="concept" markdown="1">

## 顶点进队时，就算已经发现

处理 1 时，3 第一次进入队列，同时写入 `distance[3]=2` 和 `parent[3]=1`。轮到 2 扫描邻居时，3 已有距离，直接跳过。

如果等到 3 出队才标记，1 和 2 都会把它加入队列。小图可能仍能结束，但前沿会膨胀，计数和父节点也不再稳定。

</section>

<section id="concept-distance-parent" data-learning-context="concept-distance-parent" data-context-type="concept" markdown="1">

## 距离回答“多远”，父节点回答“从哪来”

第一次从 `u` 发现 `v` 时：

```text
distance[v] = distance[u] + 1
parent[v] = u
```

起点距离为 0、父节点为空；不可达顶点的距离和父节点也为空。两者不能只看 `parent` 区分，要先看距离是否存在。

</section>

<section id="example-path-reconstruction" data-learning-context="example-path-reconstruction" data-context-type="example" markdown="1">

## 路径先倒着得到，再反转

从目标 4 沿父节点往回走：

```text
4 ← 3 ← 1 ← 0
```

反转后得到 `0 → 1 → 3 → 4`。目标 6 的距离为空，说明它不在起点 0 的连通分量里；这时直接返回空路径，不拼一条没有走通的父链。

</section>

<section id="reproduce-bfs-trace" data-learning-context="reproduce-bfs-trace" data-context-type="reproduce" markdown="1">

## 在终端打印每次发现

先写下处理 2 时队列里还有什么，再运行：

```bash
.venv/bin/python site-src/examples/algorithm-foundation/bfs_shortest_path_trace.py
```

输出会逐项打印 `pop`、新发现顶点、距离、父节点和队列，并在末尾还原 `0→4`，同时证明 `0→6` 不可达。

</section>

<section id="reproduce-bilingual-bfs" data-learning-context="reproduce-bilingual-bfs" data-context-type="reproduce" markdown="1">

## 回到双语言阶段作品

```bash
cd exercises/cs-core/traceable-graph-traversal-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_graph_traversal_lab bfs
```

```bash
cd exercises/cs-core/traceable-graph-traversal-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_graph_traversal_lab bfs
```

固定报告应访问 `0,1,2,3,4`，距离为 `0,1,1,2,3`，边检查数为 10，最大前沿为 2。再回归 `graph` 与 `dfs`，三份 Python/C++ 输出都要逐字一致。

</section>

<section id="modify-start-component" data-learning-context="modify-start-component" data-context-type="modify" markdown="1">

## 把起点换成 5

先不要改图。用同一套 BFS 从 5 开始，应该只看到 `5,6`：距离分别为 0、1，其他顶点全部不可达。

这不是算法漏走，而是图有两个连通分量。BFS 从一个起点只覆盖它所在的分量；下一课才会从所有未访问顶点重新启动，遍历整张图。

</section>

<section id="modify-reachable-within" data-learning-context="modify-reachable-within" data-context-type="modify" markdown="1">

## 只要两步以内的顶点

实现 `reachable_within(start, max_distance)`，复用 BFS 已经算出的距离，并保持发现顺序：

```text
start=0, max_distance=0 → 0
start=0, max_distance=1 → 0,1,2
start=0, max_distance=2 → 0,1,2,3
```

负距离应明确拒绝，不可达顶点不进入结果。不要为了这个查询修改图或重新按编号排序。

</section>

<section id="troubleshoot-bfs" data-learning-context="troubleshoot-bfs" data-context-type="troubleshoot" markdown="1">

## 重复入队、路径漂移或不可达变成 0

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 3 被放进队列两次 | 出队时才标记 | 首次入队前写距离和父节点 |
| 不可达顶点距离为 0 | 用数值 0 初始化全部距离 | 使用 `None/optional` 表示未发现 |
| 起点与不可达父节点混淆 | 只看 `parent` | 先检查距离是否存在 |
| 同一图路径每次不同 | 邻接点遍历顺序不固定 | 沿用上一课的升序邻接表 |
| `edge_checks` 只有 5 | 只按访问顶点计数 | 每扫描一个邻接项计一次 |
| 带权图路线不对 | 把最少边数当成最小代价 | 改用适合边权的算法 |

</section>

<section id="project-graph-v02" data-learning-context="project-graph-v02" data-context-type="project" markdown="1">

## 可追踪图遍历实验 v0.2

```text
v0.1 规范边、确定性邻接表、输入校验和度数不变量
v0.2 队列前沿、无权距离、父链、最短路径和范围查询
```

这一版不只给出一条路径，还留下为什么可信的过程：发现顺序、距离、父节点、访问数、邻接项检查数和最大队列都能被测试。下一课会在同一张图上加入全图 DFS、连通分量与无向环检测。

[查看可追踪图遍历实验](../../exercises/cs-core/traceable-graph-traversal-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-bfs-proof" data-learning-context="deepen-bfs-proof" data-context-type="deepen" markdown="1">

## 为什么第一次发现就是最少边数

可以按距离层归纳：起点的距离 0 显然最短。假设距离不超过 `d` 的顶点都已按最短距离发现；队列会先处理这些顶点，才处理更深层。由距离 `d` 顶点首次发现的邻居得到长度 `d+1`，任何更短路径都应从更浅层提前发现它，矛盾。

父节点记录的正是这次首次发现，因此沿父链回到起点会得到一条最短路径。若存在多条同长路径，升序邻接顺序决定本项目稳定选择哪一条。

</section>

<section id="deepen-bfs-cost" data-learning-context="deepen-bfs-cost" data-context-type="deepen" markdown="1">

## 时间来自顶点和邻接项，空间来自状态和队列

使用邻接表时，每个可达顶点最多入队一次，每个已访问顶点的邻接项扫描一次。遍历起点所在分量的时间为 `Theta(Vr+Er)`；遍历整张图的上界写作 `Theta(V+E)`。

距离、父节点和发现状态需要 `Theta(V)` 空间，队列最坏也可保存线性数量的顶点。路径恢复只沿父链走，时间与返回路径长度成正比。

</section>

<section id="career-bfs-evidence" data-learning-context="career-bfs-evidence" data-context-type="career" markdown="1">

## 讲 BFS 时，把“为什么最短”走出来

先画出 0 到 4 的三层，再展示处理 1 时发现 3、处理 2 时跳过 3，说明入队标记如何锁定第一次发现。接着沿 `4←3←1←0` 恢复路径，并用 5、6 解释不可达。

最后说清无权条件、`Theta(V+E)` 的来源和带权图边界。这样的回答既有算法直觉，也有状态、不变量、失败场景和可复现输出。

</section>

## 完成检查

- [ ] 能在纸上逐步写出队列、距离和父节点。
- [ ] 顶点首次入队前标记，3 不会重复进入队列。
- [ ] `0→4` 恢复为 `0,1,3,4`，`0→6` 返回不可达。
- [ ] 起点换成 5 后只访问 5、6；范围查询保留 BFS 顺序。
- [ ] 能说清最短路成立条件、`Theta(V+E)` 来源和带权图边界。
- [ ] Python 类型检查与单元测试、C++ 构建与 CTest、三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [MIT 6.006 Lecture 9](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/196a95604877d326c6586e60477b59d4_MIT6_006S20_lec9.pdf) | BFS 分层、距离、父节点和复杂度 | 2026-07-17 核查 |
| [Open Data Structures 图遍历](https://opendatastructures.org/ods-python/12_3_Graph_Traversal.html) | 队列式图遍历与发现状态 | 2026-07-17 核查 |
| [Python `deque`](https://docs.python.org/3.11/library/collections.html#collections.deque) | 头部取出与尾部加入 | Python 3.11，2026-07-17 核查 |
| [C++ `queue`](https://eel.is/c++draft/queue) | 标准队列适配器接口 | C++20 教学基线，2026-07-17 核查 |

BFS 在一般带权图中仍可用于可达性，但“第一次发现就是最小总代价”不再成立。非负权最短路会在优先队列与 Dijkstra 课程中单独处理。

## 下一步

进入 [DFS、连通分量与无向环检测](20-dfs-connected-components-undirected-cycles.md)，从单一起点遍历扩展到整张不连通图。
