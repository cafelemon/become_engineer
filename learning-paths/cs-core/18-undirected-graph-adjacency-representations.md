# 简单无向图、邻接表示与输入边界

<div class="be-tutor-mount" data-tutor-lesson="cs-core-18" aria-hidden="true"></div>

> **任务先行：** 把边集合规范化为可验证的简单无向图，并用邻接表与邻接矩阵解释同一关系的不同成本。

## 任务路线

<div class="be-task-route" role="list" aria-label="本课六步任务"><span role="listitem">1 锁定基线</span><span role="listitem">2 图契约</span><span role="listitem">3 边规范化</span><span role="listitem">4 两种表示</span><span role="listitem">5 非法输入</span><span role="listitem">6 度数迁移</span></div>

<section id="step-1" class="be-task-step" data-step-id="step-1" markdown="1">

## 第一步：锁定树实验与图实验基线

先回归树实验的 `frontier`，再运行图实验 `graph`。**当前任务：**确认新项目没有改变旧成果线。**成功证据：**图报告固定为 7 个顶点、6 条边和 12 个邻接项。

</section>

<section id="step-2" class="be-task-step" data-step-id="step-2" markdown="1">

## 第二步：定义简单无向图契约

顶点编号为 `[0, vertex_count)`；无向边 `{u,v}` 没有方向。本实验允许零顶点空图，但拒绝自环和重复边。图不是树：它可能有环，也可能不连通，因此后续遍历必须维护 `visited`。

**主动修改：**加入一个没有任何边的孤立顶点。**成功证据：**顶点仍存在、度数为 0，边数不变。

</section>

<section id="step-3" class="be-task-step" data-step-id="step-3" markdown="1">

## 第三步：校验并规范化边

每条边先检查端点，再变为 `(min(u,v), max(u,v))`，最后排序并查重。这样 `(2,0)` 与 `(0,2)` 被识别为同一条无向边，调用方之后修改原输入也不会改变图。

```mermaid
flowchart LR
    I["原始边 (2,0)"] --> V["检查端点与自环"]
    V --> C["规范边 (0,2)"]
    C --> S["排序并拒绝重复"]
    S --> A["建立双向邻接项"]
```

</section>

<section id="step-4" class="be-task-step" data-step-id="step-4" markdown="1">

## 第四步：建立邻接表与邻接矩阵

邻接表只保存存在的邻接关系，空间为 `Theta(V+E)`，扫描顶点 `u` 的邻居为 `Theta(deg(u))`。邻接矩阵占 `Theta(V^2)`，检查一对顶点是否相邻为常量访问，但枚举邻居要扫描整行。

**成功证据：**无向边在矩阵中关于主对角线对称，在邻接表中贡献两个邻接项；不要把矩阵和列表说成“谁总是更快”。

</section>

<section id="step-5" class="be-task-step" data-step-id="step-5" markdown="1">

## 第五步：执行非法图安全失败实验

分别传入越界端点、自环 `(1,1)` 和方向相反的重复边 `(0,2),(2,0)`。**预期失败：**构造阶段受控报错，不返回半成品图。**恢复标准：**修正输入后，邻接点仍按升序输出，旧基线逐字不变。

</section>

<section id="step-6" class="be-task-step" data-step-id="step-6" markdown="1">

## 第六步：完成 `degree_sequence` 迁移验收

为每个顶点返回邻接项数量，顶点顺序不得丢失。覆盖空图、孤立顶点、单边和固定样例；验证所有度数之和等于 `2E`。**成功证据：**样例为 `2,2,2,3,1,1,1`，输入图不变。

</section>

## 课程信息

| 项目 | 内容 |
| --- | --- |
| 前置 | [迭代 DFS、BFS 与层级前沿](17-iterative-dfs-bfs-frontier-levels.md) |
| 阶段作品 | [可追踪图遍历实验](../../exercises/cs-core/traceable-graph-traversal-lab/README.md) |
| 表示边界 | 邻接表 `Theta(V+E)`；邻接矩阵 `Theta(V^2)` |
| 事实核查 | MIT 6.006、Open Data Structures，2026-07-16 |

## 固定输出

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

## 常见错误与排查

| 现象 | 原因 | 恢复 |
| --- | --- | --- |
| 一条无向边只出现一次 | 只写入一个邻接表 | 同时写入 `u→v` 与 `v→u` |
| 反向重复边未被发现 | 查重早于规范化 | 先变为 `(min,max)` 再查重 |
| 遍历输出不稳定 | 依赖输入或哈希遍历顺序 | 规范边与邻接点都升序 |
| 把图当树递归 | 没有维护已访问状态 | 一般图遍历显式维护 `visited` |

## 来源与版本

| 来源 | 用途 | 核查日期 |
| --- | --- | --- |
| [MIT 6.006 Lecture 9](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/196a95604877d326c6586e60477b59d4_MIT6_006S20_lec9.pdf) | 简单图与邻接表成本 | 2026-07-16 |
| [Open Data Structures 邻接矩阵](https://opendatastructures.org/ods-python/12_1_AdjacencyMatrix_Repres.html) | 矩阵空间与边查询 | 2026-07-16 |
| [Open Data Structures 邻接表](https://opendatastructures.org/ods-python/12_2_AdjacencyLists_Graph_a.html) | 邻接表操作边界 | 2026-07-16 |
| [C++ `vector`](https://eel.is/c++draft/vector) | 连续动态序列接口 | 2026-07-16 |

本地图素材只用于术语与误区审计；课程不复制 Java 模板、图片或面试题，也不沿用“顶点集合必须非空”等超出本实验边界的概括。

## 下一步

继续进入 [BFS、无权距离与最短路径](19-bfs-unweighted-distances-shortest-paths.md)。
