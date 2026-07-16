# DFS、连通分量与无向环检测

<div class="be-tutor-mount" data-tutor-lesson="cs-core-20" aria-hidden="true"></div>

> **任务先行：** 从一次可达性搜索扩展为全图 DFS，并用父边规则区分无向边的回看与真正的环证据。

## 任务路线

<div class="be-task-route" role="list" aria-label="本课六步任务"><span role="listitem">1 BFS 基线</span><span role="listitem">2 递归 DFS</span><span role="listitem">3 连通分量</span><span role="listitem">4 无向环</span><span role="listitem">5 父边误判</span><span role="listitem">6 标签迁移</span></div>

<section id="step-1" class="be-task-step" data-step-id="step-1" markdown="1">

## 第一步：运行 BFS 与全图 DFS 基线

先运行 `bfs` 再运行 `dfs`。**当前任务：**区分“从起点可达的遍历”和“覆盖所有顶点的遍历”。**成功证据：**BFS 从 0 访问 5 个顶点；全图 DFS 访问 7 个并得到 2 个分量。

</section>

<section id="step-2" class="be-task-step" data-step-id="step-2" markdown="1">

## 第二步：实现带已访问状态的递归 DFS

进入顶点后立即标记，再按升序递归未访问邻居。`max_depth` 以每个分量起点为 0 重新计算；空图为 -1。与树不同，一般图若没有 `visited` 会沿环重复递归。

**主动修改：**交换输入边顺序。**成功证据：**规范化邻接表使 DFS 序列保持不变。

</section>

<section id="step-3" class="be-task-step" data-step-id="step-3" markdown="1">

## 第三步：从最小未访问顶点启动全图 DFS

外层按 `0..V-1` 扫描；每遇到未访问顶点就创建新分量并递归。孤立顶点也是大小为 1 的连通分量，不能因没有边而消失。

```mermaid
flowchart LR
    S["扫描最小未访问顶点"] --> D["DFS 收集一个分量"]
    D --> R{"仍有未访问顶点?"}
    R -- 是 --> S
    R -- 否 --> O["输出分量与标签"]
```

**成功证据：**样例分量依次为 `[0,1,3,2,4]` 和 `[5,6]`。

</section>

<section id="step-4" class="be-task-step" data-step-id="step-4" markdown="1">

## 第四步：排除父边后检测无向环

无向边会在两个邻接表中出现。DFS 从 `u` 走到 `v` 后，`v` 看见已访问的 `u` 只是父边；只有已访问邻居不等于父节点时才构成环证据。首次证据规范为 `(min,max)`，样例为 `(0,2)`。

**复杂度证据：**全图访问每个顶点一次、检查每个无向邻接项一次，即 `V` 次访问与 `2E` 次边检查，时间 `Theta(V+E)`。

</section>

<section id="step-5" class="be-task-step" data-step-id="step-5" markdown="1">

## 第五步：复现未排除父边的误判

临时删除 `neighbor != parent` 条件，在只有 `0—1—2` 的无环路径上运行。**预期失败：**1 回看 0 时被误报为环。**恢复标准：**重新排除父边后路径图无环，真正的四边环仍能识别。

</section>

<section id="step-6" class="be-task-step" data-step-id="step-6" markdown="1">

## 第六步：完成 `build_component_labels` 迁移验收

按分量发现顺序为每个顶点写标签。空图返回空标签和 0 个分量；孤立顶点各自获得新标签。**成功证据：**样例标签为 `0,0,0,0,0,1,1`，所有顶点恰好写一次。

</section>

## 课程信息

| 项目 | 内容 |
| --- | --- |
| 前置 | [BFS、无权距离与最短路径](19-bfs-unweighted-distances-shortest-paths.md) |
| 阶段作品 | [可追踪图遍历实验](../../exercises/cs-core/traceable-graph-traversal-lab/README.md) |
| 完整遍历 | 邻接表下时间 `Theta(V+E)`，已访问、递归与结果空间最坏 `Theta(V)` |
| 事实核查 | MIT 6.006、Open Data Structures，2026-07-16 |

## 固定输出

```text
全图 DFS
components=2
component 0：0, 1, 3, 2, 4
component 1：5, 6
visits=7，edge_checks=12，max_depth=3
cycle=yes，first_edge=(0, 2)
labels：0, 0, 0, 0, 0, 1, 1
```

## 常见错误与排查

| 现象 | 原因 | 恢复 |
| --- | --- | --- |
| 只得到起点所在分量 | 缺少外层顶点扫描 | 从每个未访问顶点重启 DFS |
| 每条边都像环 | 把返回父节点的边也计入 | 记录并排除 DFS 父边 |
| 环上无限递归 | 递归后才标记 | 进入顶点立即标记 |
| 分量编号漂移 | 顶点或邻接顺序不稳定 | 顶点与邻接点都升序 |

## 来源与版本

| 来源 | 用途 | 核查日期 |
| --- | --- | --- |
| [MIT 6.006 Lecture 10](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/f3e349e0eb3288592289d2c81e0c4f4d_MIT6_006S20_lec10.pdf) | DFS、全图搜索与连通分量 | 2026-07-16 |
| [Open Data Structures Graph Traversal](https://opendatastructures.org/ods-python/12_3_Graph_Traversal.html) | 已访问状态与遍历框架 | 2026-07-16 |
| [C++ 容器适配器](https://eel.is/c++draft/container.adaptors.general) | 后续显式栈/队列对照 | 2026-07-16 |

本地材料只用于检查 DFS/BFS、复杂度与环判断的易错条件；有向图的回边、拓扑排序和强连通分量不在本课契约内。

## 下一步

一般图表示与基础遍历闭环完成。下一课进入[二叉最小堆、隐式树与堆不变量](21-binary-min-heap-implicit-tree-invariant.md)；有向图算法、最小生成树和并查集仍未开放。
