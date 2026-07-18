<div class="be-tutor-mount" data-tutor-lesson="cs-core-26" aria-hidden="true"></div>

<section id="overview-prim-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-prim-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">算法核心 · 第 6 课 · 可追踪生成森林实验</span>

# Lazy Prim、割边前沿与过期边

## 从顶点 0 出发，也能得到总权重 7

```text
Lazy Prim 最小生成森林
component_starts：0, 5
accepted：0-2@1, 1-2@2, 2-3@3, 3-4@2, 5-6@-1
edge_scans=16，queue_pushes=8，stale_pops=3，max_frontier=4
components=2，total_weight=7
matches_kruskal=yes
```

Kruskal 把全图的边排好序；Prim 则站在已经长出的树边上，只看跨过当前边界的候选边。走法不同，但都能得到两分量、五条边、总权重 7 的最小生成森林。

[看前沿怎样变化](#example-frontier-growth){ .md-button .md-button--primary }
[运行 Prim 轨迹](#reproduce-prim-trace){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>算法核心 · 6 / 6</strong></span><span>前置<strong>最小堆、带权图、Kruskal</strong></span><span>完成后留下<strong>割边前沿、过期边与双算法对照</strong></span></div>

</section>

## 开始前

- 能读懂最小堆的压入与弹出。
- 知道无向图的一条边会出现在两个顶点的邻接表里。
- 已经用 Kruskal 得到过同一份最小生成森林。

<section id="concept-cut-frontier" data-learning-context="concept-cut-frontier" data-context-type="concept" markdown="1">

## 先画一道线：已访问在里面，未访问在外面

把已经接入当前树的顶点放在集合 S，其他顶点放在 V-S。连接两边的边叫作当前割上的边。Prim 每次只从这些边里取最轻的一条，把一个新顶点接进来。

这与“取全图还没用过的最轻边”不同。后者可能完全落在另一分量里，也可能两端都在当前树内；它们都不能扩张眼前这棵树。

</section>

<section id="example-frontier-growth" data-learning-context="example-frontier-growth" data-context-type="example" markdown="1">

## 前沿随着树一起长，也会留下旧候选

<div class="be-prim-frontier" aria-label="Lazy Prim 前沿变化">
  <div><strong>访问 0</strong><code>0-2@1, 0-1@4</code><span>先放入两条割边</span></div>
  <div><strong>接入 2</strong><code>1-2@2, 2-3@3, 0-1@4, 2-4@6</code><span>前沿达到 4 条</span></div>
  <div><strong>接入 1</strong><code>2-3@3, 0-1@4, 1-3@5, 2-4@6</code><span>0-1 已经开始变旧</span></div>
  <div><strong>接入 3、4</strong><code>0-1@4, 1-3@5, 2-4@6</code><span>剩下三条两端都已访问</span></div>
  <div><strong>从 5 重启</strong><code>5-6@-1</code><span>第二个分量独立生长</span></div>
</div>

最小堆只保证弹出队列中键最小的候选，不会自动删除已经失效的边。Lazy Prim 的“lazy”就在这里：等它弹出时再判断是否还跨割。

</section>

<section id="concept-visit-push" data-learning-context="concept-visit-push" data-context-type="concept" markdown="1">

## `visit()` 扫描全部邻接项，只压入通向外面的边

访问一个新顶点时，先把它标为已访问，再遍历它的邻接表。每看一项，`edge_scans` 加一；只有邻居仍未访问，才把边按 `(weight,u,v)` 压入最小堆，并让 `queue_pushes` 加一。

`max_frontier` 在每次真正压入后，用当前队列长度更新。空图和纯孤立点没有候选边，所以峰值保持 0。

</section>

<section id="example-stale-edge" data-learning-context="example-stale-edge" data-context-type="example" markdown="1">

## `0-1@4` 压入时有用，弹出时已经过期

访问 0 时，顶点 1 尚未接入，`0-1@4` 确实跨割。后来更轻的 `0-2@1` 与 `1-2@2` 先把 1 接进树；等 `0-1@4` 弹出时，两端都已访问。

这条边现在是内部边。跳过它并计一次 `stale_pop`；若仍接纳，就会在 0、1、2 之间形成环。样例中 `0-1@4`、`1-3@5`、`2-4@6` 都会过期。

</section>

<section id="concept-component-restart" data-learning-context="concept-component-restart" data-context-type="concept" markdown="1">

## 队列空了，不代表整张图已经结束

顶点 0 所在分量完成后，扫描顶点编号，从最小的未访问顶点 5 重启。访问 5 后，`5-6@-1` 成为唯一候选并被接纳。

孤立顶点也要记录为一个分量起点，只是不会产生边。空图则没有起点、没有边，分量数为 0。

</section>

<section id="example-kruskal-contrast" data-learning-context="example-kruskal-contrast" data-context-type="example" markdown="1">

## 两种算法不必选出完全相同的边

Kruskal 与 Prim 都应返回相同总权重、相同分量数，并各有 `V-C` 条边。同权图可能存在多份最优森林，所以逐条比较边集会把合法结果误判为错误。

本项目仍使用 `(weight,u,v)` 作为确定键，锁定 Python 与 C++ 的复现轨迹；这只是工程上的稳定输出，不是对数学唯一性的承诺。

</section>

<section id="reproduce-prim-trace" data-learning-context="reproduce-prim-trace" data-context-type="reproduce" markdown="1">

## 先运行一份短轨迹

```bash
.venv/bin/python site-src/examples/algorithm-core/lazy_prim_frontier_trace.py
```

你会看到五条 `accept`、三条 `stale`，随后从顶点 5 重启。最后一行应为：

```text
starts=0,5 scans=16 pushes=8 stale=3 max_frontier=4 total_weight=7 components=2
```

</section>

<section id="reproduce-bilingual-prim" data-learning-context="reproduce-bilingual-prim" data-context-type="reproduce" markdown="1">

## 再跑完整的 Python 与 C++ 实现

```bash
cd exercises/cs-core/traceable-spanning-forest-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_spanning_forest_lab prim
```

```bash
cd exercises/cs-core/traceable-spanning-forest-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_spanning_forest_lab prim
```

顺手回归 `dsu` 与 `kruskal`。三种模式的 Python/C++ 输出都应逐字一致。

</section>

<section id="modify-isolated-ties" data-learning-context="modify-isolated-ties" data-context-type="modify" markdown="1">

## 加一个孤立点，再交换同权边的输入顺序

把顶点数加到 8，但不给顶点 7 连边。`component_starts` 应多出 7，分量数增为 3，接受边和总权重不变，边数仍满足 `V-C`。

然后打乱输入边，尤其交换两条权重为 2 的边。因为端点规范化、邻接表排序和堆键都确定，双语言轨迹不应随输入排列漂移。

</section>

<section id="modify-compare-forests" data-learning-context="modify-compare-forests" data-context-type="modify" markdown="1">

## 写一个只比较森林不变量的对照器

让 `compare_spanning_forests(graph)` 同时运行 Kruskal 与 Prim，检查总权重、分量数以及双方边数是否都为 `V-C`。覆盖空图、孤立点、负权、同权、多分量与输入不变性。

不要把“边集完全相同”写进契约。你可以另造一个有多份最优解的同权图，确认两份不同边集仍能通过不变量检查。

</section>

<section id="troubleshoot-prim" data-learning-context="troubleshoot-prim" data-context-type="troubleshoot" markdown="1">

## 总权重不对、边数过多，先查这几处

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 每次选全图最轻边 | 把 Prim 写成了 Kruskal | 堆里只放当前树向外的边 |
| 接纳边超过 `V-C` | 弹出时没复查两端状态 | 两端都访问就计过期并跳过 |
| 断开图漏掉顶点 5 | 只从顶点 0 启动一次 | 队列耗尽后找最小未访问点 |
| `edge_scans` 少一半 | 只统计无向边一次 | 统计每个访问顶点的全部邻接项 |
| 前沿峰值偏小 | 在弹出或整轮结束后统计 | 每次真实压入后立即更新 |
| 两算法边集不同就失败 | 忽略同权多解 | 比较权重、分量和 `V-C` 边数 |

</section>

<section id="project-forest-v10" data-learning-context="project-forest-v10" data-context-type="project" markdown="1">

## 可追踪生成森林实验 v1.0

这条项目线现在有三层：并查集负责动态连通，Kruskal 用同根判断拒绝成环边，Lazy Prim 用局部割边前沿生长森林。两种生成森林算法共同回归空图、孤立点、负权、同权、断开图、溢出与输入不变性。

[查看阶段作品](../../exercises/cs-core/traceable-spanning-forest-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-prim-cost" data-learning-context="deepen-prim-cost" data-context-type="deepen" markdown="1">

## 懒惰边队列的代价是 `O(E log E)`

无向图共扫描 `2E` 个邻接项。每条边至多被压入一次，候选边的压入和弹出各花 `O(log E)`，所以整体时间为 `O(E log E)`，额外队列空间为 `O(E)`。

使用索引优先队列的 eager Prim 可以把前沿改为“每个未访问顶点当前最轻的连接边”，复杂度表达也会变化；那是后续深化内容，本课先把 lazy 版本的状态和失败路径走清楚。

</section>

<section id="career-prim-evidence" data-learning-context="career-prim-evidence" data-context-type="career" markdown="1">

## 讲 Prim 时，拿一条过期边说明为什么要复查

先画出已访问集合与未访问集合，再解释只把跨割边放进最小堆。用 `0-1@4` 说明“压入时合法，弹出时过期”，比只背一段伪代码更容易讲清 lazy 的含义。

最后拿 Kruskal 对照：一个按全局边序，一个按局部前沿；同权时边集可能不同，但权重、分量数和 `V-C` 边数必须一致。

</section>

## 完成检查

- [ ] 能画出当前割，并说清哪些边可以进入前沿。
- [ ] 访问顶点时扫描全部邻接项，只压入通向未访问邻居的边。
- [ ] 弹出边时重新检查两端，过期内部边不会进入森林。
- [ ] 断开图从最小未访问顶点重启，孤立点也计作分量。
- [ ] 能解释 `edge_scans`、`queue_pushes`、`stale_pops` 与 `max_frontier`。
- [ ] Kruskal 与 Prim 比较森林不变量，不强求相同边集。
- [ ] Python 类型检查、C++ CTest 与三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [Princeton Minimum Spanning Trees](https://algs4.cs.princeton.edu/43mst/index.php) | 割性质、Lazy Prim 与复杂度 | 2026-07-18 核查 |
| [Princeton LazyPrimMST](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/LazyPrimMST.html) | 懒惰边前沿与过期边 | 2026-07-18 核查 |
| [Python 3.11 `heapq`](https://docs.python.org/3.11/library/heapq.html) | Python 最小堆接口 | 3.11；2026-07-18 核查 |
| [C++ `priority_queue`](https://eel.is/c++draft/priority.queue) | C++ 队列适配器与比较键 | 工作草案；2026-07-18 核查 |

本课不进入 eager Prim、动态最小生成树、次小生成树或稠密图专用实现。

## 下一步

现有 55 节正式课程到这里完成内容架构 V2 迁移。系统编程、网络、数据库与更高阶算法仍在课程总表中等待建设；先回到[完整课程地图](../curriculum-map.md)选择下一条已开放方向。
