<div class="be-tutor-mount" data-tutor-lesson="cs-core-18" aria-hidden="true"></div>

<section id="overview-graph-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-graph-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">共同算法基础 · 第 14 课 · 可追踪图遍历实验</span>

# 简单无向图、邻接表示与输入边界

## 六条边，为什么会有十二个邻接项

```text
可追踪无向图实验
vertices=7，edges=6，adjacency_entries=12
0：[1, 2]
1：[0, 3]
2：[0, 3]
3：[1, 2, 4]
4：[3]
5：[6]
6：[5]
degrees：2, 2, 2, 3, 1, 1, 1
```

边 `{0, 2}` 没有方向：从 0 能到 2，从 2 也能回到 0。因此它会在两个顶点的邻接表里各出现一次。先把输入边整理成统一形式，再建立双向邻接关系，图的结构才容易检查和复现。

[看一条边怎样进入图](#example-canonical-edge){ .md-button .md-button--primary }
[运行边规范化轨迹](#reproduce-graph-normalization){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>共同算法基础 · 14 / 16</strong></span><span>前置<strong>树的 DFS、BFS 与前沿</strong></span><span>完成后留下<strong>确定性邻接表、输入校验和度数检查</strong></span></div>

</section>

## 开始前

- 知道列表、矩阵和半开区间 `[0, V)` 的含义。
- 能解释树为什么没有环，而一般图可能从多条路径到达同一顶点。
- 本课只处理简单无向图：没有自环，也没有重复边。

<section id="concept-graph-vs-tree" data-learning-context="concept-graph-vs-tree" data-context-type="concept" markdown="1">

## 把树放宽，就得到更一般的连接关系

树有唯一根，每个非根节点只有一个父节点，任意两点之间只有一条简单路径。图不必满足这些条件：它可以不连通，可以有环，也可以有多条路通向同一点。

这也是后续图遍历需要 `visited` 的原因。仅靠“不要回到父节点”不够，另一个邻居仍可能把同一顶点再次放进队列。

</section>

<section id="concept-simple-graph-contract" data-learning-context="concept-simple-graph-contract" data-context-type="concept" markdown="1">

## 先说清这份图接受什么

顶点用整数编号，合法范围是 `[0, vertex_count)`。`vertex_count=0` 且没有边，是一张合法空图；顶点可以存在而没有任何边，它叫孤立顶点。

课程项目拒绝三类输入：端点越界、自环 `{u,u}`、已经出现过的无向边。构造失败时不返回半张图，修正输入后重新建立完整结构。

</section>

<section id="example-canonical-edge" data-learning-context="example-canonical-edge" data-context-type="example" markdown="1">

## `(2, 0)` 和 `(0, 2)` 是同一条边

<div class="be-edge-pipeline" aria-label="无向边规范化过程">
  <div><strong>原始输入</strong><code>(2, 0)</code><span>调用方可以用任意端点顺序</span></div>
  <div><strong>检查</strong><code>0 ≤ u,v &lt; V</code><span>同时拒绝 u == v</span></div>
  <div><strong>统一方向</strong><code>(min, max) = (0, 2)</code><span>方向不再影响边的身份</span></div>
  <div><strong>排序查重</strong><code>(0, 2)</code><span>反向重复会在这里被发现</span></div>
</div>

只有先规范化再查重，`(2,0)` 与 `(0,2)` 才会碰到同一个键。图还会复制并排序输入；调用方之后调整原列表，不会暗中改变已经建好的图。

</section>

<section id="concept-adjacency-list" data-learning-context="concept-adjacency-list" data-context-type="concept" markdown="1">

## 邻接表只保存真的存在的连接

每个顶点有一行邻居。边 `{0,2}` 同时把 2 放进第 0 行、把 0 放进第 2 行：

```text
0 → [1, 2]
1 → [0, 3]
2 → [0, 3]
```

邻接表占 `Theta(V+E)` 空间，枚举顶点 `u` 的所有邻居需要 `Theta(deg(u))`。稀疏图里大量不存在的边不占槽位。

</section>

<section id="concept-adjacency-matrix" data-learning-context="concept-adjacency-matrix" data-context-type="concept" markdown="1">

## 邻接矩阵把每一对顶点都留出位置

矩阵的第 `u` 行、第 `v` 列表示两点是否相邻。无向图必须满足 `A[u][v] == A[v][u]`，简单图的主对角线全是 0。

它需要 `Theta(V²)` 空间，检查一条边只需访问一个格子；但枚举一个顶点的邻居要扫完整行。邻接表和矩阵没有绝对的“谁更快”，要看图的密度和程序最常做的操作。

</section>

<section id="example-degree-invariant" data-learning-context="example-degree-invariant" data-context-type="example" markdown="1">

## 度数和为什么正好是 `2E`

顶点的度数就是它的邻接项数量。每条非自环无向边连接两个端点，对总度数贡献两次，所以：

```text
2 + 2 + 2 + 3 + 1 + 1 + 1 = 12 = 2 × 6
```

这条握手关系是很实用的整体检查。它不能证明每条边都正确，却能迅速发现漏写单向邻接项、度数少算或边数统计错位。

</section>

<section id="reproduce-graph-normalization" data-learning-context="reproduce-graph-normalization" data-context-type="reproduce" markdown="1">

## 看三条乱序边怎样被整理

先猜一下 `(3,1)` 会变成什么，再运行：

```bash
.venv/bin/python site-src/examples/algorithm-foundation/undirected_graph_normalization_trace.py
```

脚本会打印规范边、邻接表、度数和，并分别试一次自环和反向重复。错误输入会在建立邻接表前停止，不会留下半成品。

</section>

<section id="reproduce-bilingual-graph" data-learning-context="reproduce-bilingual-graph" data-context-type="reproduce" markdown="1">

## 运行双语言图实验

```bash
cd exercises/cs-core/traceable-graph-traversal-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_graph_traversal_lab graph
```

```bash
cd exercises/cs-core/traceable-graph-traversal-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_graph_traversal_lab graph
```

Python 与 C++ 的图报告应逐字一致。再分别运行 `bfs` 和 `dfs`，确认这次改造没有改变后续遍历的公开输出。

</section>

<section id="modify-isolated-vertex" data-learning-context="modify-isolated-vertex" data-context-type="modify" markdown="1">

## 加一个没有边的顶点

把顶点数从 7 改为 8，但不增加边。第 7 行应该是空邻接表，度数序列末尾多一个 0，边数和原来的七行都不变。

如果第 7 个顶点没有出现在报告里，程序很可能是从边反推顶点，而不是从 `vertex_count` 建立完整顶点集合。

</section>

<section id="modify-input-order" data-learning-context="modify-input-order" data-context-type="modify" markdown="1">

## 打乱边的输入顺序

把六条边倒序或随机重排，再生成一次报告。规范边和每行邻居仍按升序输出，整份报告应与原来相同。

接着在建图后修改调用方的原始边列表。图也不应跟着变化；这说明对象已经取得自己的数据，而不是借用一份随时会变的输入。

</section>

<section id="troubleshoot-graph-input" data-learning-context="troubleshoot-graph-input" data-context-type="troubleshoot" markdown="1">

## 邻接项少了、反向边没报错，先查这里

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 6 条边只有 6 个邻接项 | 每条边只写入了一个端点 | 同时写入 `u→v` 与 `v→u` |
| `(0,2)` 与 `(2,0)` 都被接受 | 在规范化以前查重 | 先变成 `(min,max)`，再查重 |
| 邻接输出每次不同 | 依赖集合或输入遍历顺序 | 规范边和每行邻居都升序 |
| 孤立顶点消失 | 只为边里出现的端点建行 | 先按 `[0,V)` 建立所有行 |
| 越界后得到半张图 | 边检查与邻接写入交错 | 先完成全部校验，再提交结构 |
| 图遍历反复入队 | 没有维护已发现状态 | 后续 BFS 在入队时标记发现 |

</section>

<section id="project-graph-v01" data-learning-context="project-graph-v01" data-context-type="project" markdown="1">

## 可追踪图遍历实验 v0.1

```text
输入边 → 端点校验 → 无向边规范化 → 确定性邻接表 → 图报告
```

这一版先把图的身份和表示做稳：空图、孤立点、自环、重复边、输入顺序和双语输出都有固定检查。下一课才让 BFS 在这份图上计算距离和最短路径。

[查看可追踪图遍历实验](../../exercises/cs-core/traceable-graph-traversal-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-representation-cost" data-learning-context="deepen-representation-cost" data-context-type="deepen" markdown="1">

## 表示方式会改变后续算法的实际工作量

在邻接表上遍历整张无向图，每行只扫描真实邻居，总邻接项是 `2E`，因此是 `Theta(V+E)`。在邻接矩阵上，即使图很稀疏，也要为每个出队顶点扫描一整行，完整遍历是 `Theta(V²)`。

反过来，矩阵检查 `{u,v}` 是否存在只需一次下标访问；普通邻接列表需要在 `u` 的邻居中查找。选择结构之前，先写清最频繁的操作和图的规模。

</section>

<section id="career-graph-evidence" data-learning-context="career-graph-evidence" data-context-type="career" markdown="1">

## 讲图表示时，别只背两行复杂度

可以拿 `(2,0)` 演示规范化，拿 6 条边和 12 个邻接项解释无向对称，再用孤立顶点证明顶点集合不由边推断。最后比较“查一条边”和“枚举所有邻居”两种操作，说明为什么表示选择没有统一答案。

如果再补上越界、自环、反向重复、输入重排和双语言一致性，回答就从概念定义变成了可验证的工程判断。

</section>

## 完成检查

- [ ] 能解释图与树在环、连通性和到达路径上的区别。
- [ ] 无向边先变成 `(min,max)`，反向重复会被拒绝。
- [ ] 邻接表保留所有顶点，每条边产生两个升序邻接项。
- [ ] 能用矩阵对称和度数和 `2E` 检查表示。
- [ ] 空图、孤立点、越界、自环、重边和输入重排都有测试。
- [ ] Python 类型检查与单元测试、C++ 构建与 CTest、三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [MIT 6.006 Lecture 9](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/196a95604877d326c6586e60477b59d4_MIT6_006S20_lec9.pdf) | 简单图、邻接表示和遍历成本 | 2026-07-17 核查 |
| [Open Data Structures 邻接矩阵](https://opendatastructures.org/ods-python/12_1_AdjacencyMatrix_Repres.html) | 矩阵空间与边查询 | 2026-07-17 核查 |
| [Open Data Structures 邻接表](https://opendatastructures.org/ods-python/12_2_AdjacencyLists_Graph_a.html) | 邻接表结构与操作边界 | 2026-07-17 核查 |
| [Open Data Structures 图遍历](https://opendatastructures.org/ods-python/12_3_Graph_Traversal.html) | 一般图的发现状态与线性遍历 | 2026-07-17 核查 |

本课使用简单无向图作为教学契约。允许平行边、自环、方向或权重的图需要另一套身份规则，不能直接套用这里的查重方式。

## 下一步

进入 [BFS、无权距离与最短路径](19-bfs-unweighted-distances-shortest-paths.md)，在这份确定性邻接表上记录发现时刻、距离和父节点。
