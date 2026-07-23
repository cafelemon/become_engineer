<div class="be-tutor-mount" data-tutor-lesson="algorithm-deepening-09" aria-hidden="true"></div>
<section id="overview-advanced-graph" class="be-page-hero be-lesson-hero" data-learning-context="overview-advanced-graph" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">算法深化 · 第 9 / 10 课 · 可追踪约束模式实验 v0.9</span>
# 高阶图：拓扑、强连通与多源路径
## 先识别依赖、环与起点集合，再选择遍历
```text
topological=A,B,C,D,E,F
cycle_topological=cycle
scc=A,B,C|D,E|F
condensation=0>1,1>2
sources=A,B distances=A:0,B:0,C:1,D:2,E:2,F:3
invariants=zero-indegree-only,scc-condensation-acyclic,first-discovery-shortest
```
同一有向图问题可能在问依赖顺序、环内等价节点或离多个源最近的距离；三者需要不同状态与不变量。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>算法深化 · 9 / 10</strong></div>
  <div><span>前置</span><strong>BFS/DFS、入度与 DP 依赖顺序</strong></div>
  <div><span>实现</span><strong>Python 3.11 + C++20 高阶图实验</strong></div>
  <div><span>完成后留下</span><strong>拓扑序、环状态、SCC 缩点与多源距离</strong></div>
</div>
## 学习目标
- 用 Kahn 算法产生确定性拓扑序并显式报告环。
- 用正反图两遍 DFS 求强连通分量。
- 证明 SCC 缩点图无环。
- 把多个源同时以距离零加入 BFS。
- 区分有向依赖、互相可达与无权最短边数。
<section id="concept-topological-frontier" data-learning-context="concept-topological-frontier" data-context-type="concept" markdown="1">
## 零入度前沿表示依赖已经满足
Kahn 算法维护入度，只取当前入度为零的节点。用最小堆让多个可选节点按标签稳定输出 `A,B,C,D,E,F`。若最终处理节点数小于总数，剩余节点位于有向环中；返回 `cycle`，不能把部分顺序冒充完整拓扑序。
</section>
<section id="example-scc-condensation" data-learning-context="example-scc-condensation" data-context-type="example" markdown="1">
## SCC 把环压成一个可排序节点
样例中 `A,B,C` 互相可达，`D,E` 互相可达，`F` 单独成分。Kosaraju 第一遍在原图记录完成顺序，第二遍按逆序在反图收集分量，固定得到 `A,B,C|D,E|F`。
若缩点图仍有环，环上的多个 SCC 实际互相可达，本应属于同一分量，因此缩点图一定是 DAG；样例边为 `0>1,1>2`。
</section>
<section id="concept-multisource-bfs" data-learning-context="concept-multisource-bfs" data-context-type="concept" markdown="1">
## 多源 BFS 相当于增加一个虚拟超级源
把 A、B 都以距离 0 入队，然后执行普通 BFS。无权图按层扩展，节点第一次发现时已取得到任一源的最少边数：`A:0,B:0,C:1,D:2,E:2,F:3`。若边有不同非负权重，应改用多源 Dijkstra。
</section>
<section id="reproduce-advanced-graph-v09" data-learning-context="reproduce-advanced-graph-v09" data-context-type="reproduce" markdown="1">
## 运行三类图状态实验
```bash
cd site-src/examples/algorithm-deepening/pattern-lab-v09
../../../../.venv/bin/python -m unittest -v test_advanced_graph_trace.py
```
6 项测试覆盖拓扑边顺序、环、SCC 与缩点、多源距离、非法端点／空源和双语言报告一致。三类算法均为 `O(V+E)`；确定性前沿使用堆时拓扑排序增加 `O(V log V)`。
</section>
<section id="modify-advanced-graph" data-learning-context="modify-advanced-graph" data-context-type="modify" markdown="1">
## 改变环、源点和权重
1. 删除 `C>A`，观察 SCC 拆分与拓扑恢复。
2. 给缩点图执行拓扑排序，验证所有跨分量边方向。
3. 只保留源 A，比较 C 以后距离与双源结果。
4. 加入权重 0 与 5，说明普通 BFS 的首次发现证明为何失效。
</section>
<section id="troubleshoot-advanced-graph" data-learning-context="troubleshoot-advanced-graph" data-context-type="troubleshoot" markdown="1">
## 图错误按方向、完成状态和发现时机定位
| 现象 | 原因 | 恢复 |
| --- | --- | --- |
| 环图输出部分顺序 | 未核对处理数 | 少于 V 就报告 cycle |
| SCC 被拆散 | 第二遍仍走原图 | 构建并使用反图 |
| SCC 顺序漂移 | 邻接和成分未排序 | 固定节点与输出次级顺序 |
| 多源距离偏大 | 逐个源分别跑且错误合并 | 所有源距离 0 同时入队 |
| 节点重复入队 | 出队才标记发现 | 入队时写距离 |
| 带权边仍用 BFS | 层数不等于路径权重 | 改用合适最短路算法 |
</section>
<section id="project-pattern-lab-v09" data-learning-context="project-pattern-lab-v09" data-context-type="project" markdown="1">
## 可追踪约束模式实验 v0.9
- v0.9 固定展示依赖前沿、环压缩和多个起点三种图视角。
- Python/C++20 对拓扑、SCC、缩点边和距离逐字一致。
- 最后一版进入 Trie 与 KMP，比较前缀共享结构和失败函数复用匹配信息。
</section>
## 四类学习者入口
- 零基础兴趣：画出 DAG，每次圈出所有零入度点。
- 有基础兴趣：给缩点图再次拓扑并核对跨分量边。
- 零基础求职：区分拓扑失败、SCC 与普通连通分量。
- 有基础求职：把多源无权图改成非负带权图并设计验证。
<section id="career-advanced-graph" data-learning-context="career-advanced-graph" data-context-type="career" markdown="1">
## 求职加练：同一个环可以是错误，也可以是分析对象
原创追问：构建系统发现拓扑排序只输出部分任务。请先证明存在环，再输出强连通分量作为最小互相依赖组，压缩成 DAG；最后从两个入口计算最少依赖层数，并说明何时必须换成 Dijkstra。
</section>
## 完成检查
- 6 项测试通过，Python/C++20 报告一致。
- DAG 拓扑序固定，环图不返回伪完整顺序。
- SCC 为 `A,B,C|D,E|F`，缩点边为 `0>1,1>2`。
- 多源距离为 `0,0,1,2,2,3`。
- 三个不变量分别约束前沿、缩点和首次发现。
## 来源与版本
- Python 3.11、C++20；核查日期 2026-07-23。
- [CP-Algorithms: Topological Sorting](https://cp-algorithms.com/graph/topological-sort.html)
- [CP-Algorithms: Strongly Connected Components](https://cp-algorithms.com/graph/strongly-connected-components.html)
- [CP-Algorithms: Breadth First Search](https://cp-algorithms.com/graph/breadth-first-search.html)
## 下一步
进入第 10 课《Trie、KMP 与字符串匹配》，完成算法深化十课闭环。

