<div class="be-tutor-mount" data-tutor-lesson="cs-core-23" aria-hidden="true"></div>

<section id="overview-dijkstra-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-dijkstra-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">算法核心 · 第 3 课 · 可追踪优先队列与最短路实验</span>

# 带权图松弛、Dijkstra 与过期队列项

## 从 0 到 5，不是边最少，而是总代价最小

```text
非负权最短路
settled：0, 2, 1, 3, 4, 5
distances：0, 3, 1, 4, 7, 8, unreachable
parents：none, 2, 0, 1, 3, 4, none
edge_checks=16，relaxations=8
queue_pushes=9，stale_pops=3，max_frontier=4
path 0->5：0, 2, 1, 3, 4, 5，distance=8
```

顶点 1 一开始通过 `0—1` 得到距离 4，随后发现 `0—2—1` 只要 3。新距离写进表并重新入队，旧的距离 4 不会消失；它稍后弹出时会被认作过期项，直接跳过。

[看一次距离改进](#example-relax-improvement){ .md-button .md-button--primary }
[运行松弛轨迹](#reproduce-dijkstra-trace){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>算法核心 · 3 / 6</strong></span><span>前置<strong>带权图、稳定最小优先队列</strong></span><span>完成后留下<strong>非负权最短路、父链与过期项证据</strong></span></div>

</section>

## 开始前

- 能区分 BFS 的“边数最少”和带权图的“权重总和最小”。
- 会使用稳定最小优先队列的 `push`、`peek`、`pop`。
- 本课处理简单无向非负权图；负权最短路属于另一类算法。

<section id="concept-weighted-graph" data-learning-context="concept-weighted-graph" data-context-type="concept" markdown="1">

## 边权是经过一条边的代价

边 `(u, v, w)` 表示从 u 到 v 的代价为 w。无向图会把同一条边放进两个顶点的邻接表，但输入里只允许出现一次无向端点对。

本课允许零权边，拒绝负权、自环、反向重复边和越界端点。构造时复制输入、把端点整理为 `(min(u,v), max(u,v))`，并按邻居编号排序，这样交换输入顺序也不会改变 Python/C++ 轨迹。

</section>

<section id="example-weighted-contract" data-learning-context="example-weighted-contract" data-context-type="example" markdown="1">

## 三条边，只有第一条合法

```text
(0, 1, 0)   合法：零权不等于负权
(0, 1, -1)  拒绝：Dijkstra 的非负权前提被破坏
(1, 0, 2)   拒绝：若 (0,1,4) 已存在，这是重复无向边
```

距离使用有符号 64 位范围。计算 `distance + weight` 以前先检查剩余空间，不能让溢出后的负数参与“更短”比较。

</section>

<section id="concept-relaxation" data-learning-context="concept-relaxation" data-context-type="concept" markdown="1">

## 松弛：问一条边能不能带来更短路线

已知从起点到 u 的距离，检查边 `u—v(w)`：

```text
candidate = distance[u] + w
如果 distance[v] 未知，或 candidate < distance[v]：
    distance[v] = candidate
    parent[v] = u
    把 (candidate, sequence, v) 压入队列
```

这里必须是严格小于。相等候选没有改进距离，不覆盖第一次记录的父节点，路径便不会随重复扫描顺序漂移。

</section>

<section id="example-relax-improvement" data-learning-context="example-relax-improvement" data-context-type="example" markdown="1">

## 顶点 1 和 3 都被改短了一次

<div class="be-relax-trace" aria-label="Dijkstra 距离改进与过期项轨迹">
  <div><strong>先看 0→1</strong><code>∞ → 4</code><span>压入 (4,1)</span></div>
  <div><strong>再走 0→2→1</strong><code>4 → 3</code><span>压入新的 (3,1)</span></div>
  <div><strong>顶点 3</strong><code>6 → 4</code><span>更短项再次入队</span></div>
  <div data-stale="true"><strong>旧的 1</strong><code>queued 4 ≠ current 3</code><span>过期，跳过</span></div>
  <div data-stale="true"><strong>旧的 3</strong><code>queued 6 ≠ current 4</code><span>过期，跳过</span></div>
</div>

项目还会跳过顶点 4 的旧距离 10，因为当前距离已经改为 7。三个旧项都留在堆里，但不会再次扫描邻接边。

</section>

<section id="concept-dijkstra-invariant" data-learning-context="concept-dijkstra-invariant" data-context-type="concept" markdown="1">

## 为什么弹出的最小当前距离可以确定下来

队列每次给出尚待处理的最小暂定距离 d。假设还有一条未处理路线能把它变得更短，那条路线进入当前顶点前，必然先经过某个尚未处理顶点；非负权意味着到那个顶点的距离不可能大于整条更短路线，也就应当比 d 更早弹出，产生矛盾。

这个结论依赖所有边权非负。负权可能让一条后出现的边把已经处理的距离继续拉低，所以不能只给现有实现打个补丁。

</section>

<section id="example-stale-entry" data-learning-context="example-stale-entry" data-context-type="example" markdown="1">

## 不做 `decrease-key`，就允许新旧条目并存

Python `heapq` 和 C++ `priority_queue` 都不直接提供本项目需要的原地降权接口。更简单的做法是：每次改进都压入新条目，弹出时检查：

```python
distance, _, vertex = heappop(frontier)
if distances[vertex] != distance:
    stale_pops += 1
    continue
```

检查必须在扫描邻接表之前。删掉它，最终距离也许仍然正确，但旧的 4、6、10 会重复扫描边，计数和处理语义都被破坏。

</section>

<section id="reproduce-dijkstra-trace" data-learning-context="reproduce-dijkstra-trace" data-context-type="reproduce" markdown="1">

## 打印松弛和三个过期项

```bash
.venv/bin/python site-src/examples/algorithm-core/dijkstra_relaxation_trace.py
```

先找 `relax 2->1: 4->3` 和 `relax 1->3: 6->4`，再找三个 `stale`。最后应得到 `settled=0,2,1,3,4,5`，顶点 6 显示 `unreachable`。

</section>

<section id="reproduce-bilingual-dijkstra" data-learning-context="reproduce-bilingual-dijkstra" data-context-type="reproduce" markdown="1">

## 运行双语言完整实验

```bash
cd exercises/cs-core/traceable-priority-shortest-path-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_priority_shortest_path_lab dijkstra
```

```bash
cd exercises/cs-core/traceable-priority-shortest-path-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_priority_shortest_path_lab dijkstra
```

同时回归 `heap` 与 `queue`。最小堆、稳定队列、Dijkstra 三层报告必须继续逐字一致。

</section>

<section id="modify-zero-equal" data-learning-context="modify-zero-equal" data-context-type="modify" markdown="1">

## 加一条零权边，再造一条等距路线

用四个顶点建立 `(0,1,0)`、`(0,2,1)`、`(1,2,1)`。顶点 2 先通过 `0—2` 得到距离 1，随后 `0—1—2` 也是 1；因为候选没有严格变小，父节点仍是 0。

把条件临时改成 `candidate <= old`，观察父节点如何被等距路线覆盖。恢复严格小于，再交换输入边顺序，距离、父节点和处理顺序都应保持稳定。

</section>

<section id="modify-within-distance" data-learning-context="modify-within-distance" data-context-type="modify" markdown="1">

## 找出总代价不超过 4 的顶点

完成 `vertices_within_distance(graph, start, max_distance)`。样例从 0 出发应按确定顺序返回 `0,2,1,3`，而不是按顶点编号重新排序。

再检查上限 0、零权边、不可达顶点和负上限。负上限直接拒绝；函数不修改图、边序列或调用者输入。

</section>

<section id="troubleshoot-dijkstra" data-learning-context="troubleshoot-dijkstra" data-context-type="troubleshoot" markdown="1">

## 距离不对、计数变大或路径漂移

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 负权图仍然运行 | 没有守住算法前提 | 构造图时拒绝负权 |
| 边检查明显变多 | 过期项又扫描邻接表 | 弹出后先比较当前距离 |
| 等距路径反复改父节点 | 使用 `<=` 松弛 | 只接受严格更短候选 |
| 不可达点打印巨大整数 | 用哨兵冒充未知 | Python 用 `None`，C++ 用 `optional` |
| C++ 距离突然变负 | 有符号加法溢出 | 相加前检查 `MAX - weight` |
| 输入重排改变轨迹 | 邻接顺序不统一 | 规范端点并排序邻接表 |

</section>

<section id="project-priority-v10" data-learning-context="project-priority-v10" data-context-type="project" markdown="1">

## 可追踪优先队列与最短路实验 v1.0

这组项目从整数最小堆开始，加入稳定任务队列，最后接上非负权图、严格松弛、过期项、父链恢复与范围查询。现在既能解释容器不变量，也能证明容器怎样服务一个完整图算法。

[查看阶段作品](../../exercises/cs-core/traceable-priority-shortest-path-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-dijkstra-cost" data-learning-context="deepen-dijkstra-cost" data-context-type="deepen" markdown="1">

## 复杂度要和真实实现对上

邻接表让每条无向边最多被两端各检查一次。懒惰重复项实现每次成功松弛都可能增加一个队列项，总项数是 `O(E)`；每次堆操作为 `O(log E)`。

因此本实现时间写作 `O((V+E) log E)`，额外空间 `O(V+E)`。若使用支持原地 `decrease-key` 的堆，可以得到另一种常见界限，但不能拿它替代当前代码的分析。

</section>

<section id="career-dijkstra-evidence" data-learning-context="career-dijkstra-evidence" data-context-type="career" markdown="1">

## 用“4 改成 3”讲清 Dijkstra

先说前提：简单无向非负权图。接着用顶点 1 从 4 改成 3 展示松弛，再解释旧的 `(4,1)` 为什么留在队列、弹出时如何识别过期。

最后给出父链、不可达点、严格小于和复杂度。比起背一段模板，这条具体轨迹更容易证明你理解算法为什么成立、实现为什么这样写。

</section>

## 完成检查

- [ ] 能区分边数最少的 BFS 与权重和最小的 Dijkstra。
- [ ] 带权图拒绝负权、自环、重复边、越界和溢出。
- [ ] 松弛只在候选严格更小时更新距离、父节点并入队。
- [ ] 能解释新旧队列项并存和弹出时的过期检查。
- [ ] 能从父节点恢复 `0→5`，并正确处理顶点 6 不可达。
- [ ] `vertices_within_distance` 保留确定顺序和原输入。
- [ ] Python 类型检查、C++ CTest 与三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [MIT 6.006 Dijkstra](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/d819e7f4568aced8d5b59e03db6c7b67_MIT6_006S20_lec13.pdf) | 非负权前提、松弛与正确性 | 2026-07-18 核查 |
| [Python `heapq`](https://docs.python.org/3.11/library/heapq.html) | 最小堆、平局序号与重复项实现 | Python 3.11，2026-07-18 核查 |
| [C++ `priority_queue`](https://eel.is/c++draft/priority.queue) | 容器适配器与比较器接口 | 2026-07-18 核查 |

本课不进入负权最短路、有向图、全源最短路或可原地降权的索引堆；这些内容需要不同的接口、证明和测试。

## 下一步

进入[并查集、按大小合并与路径压缩](24-disjoint-set-union-path-compression.md)，用父森林回答两个顶点是否已经连通。
