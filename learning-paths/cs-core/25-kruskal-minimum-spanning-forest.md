<div class="be-tutor-mount" data-tutor-lesson="cs-core-25" aria-hidden="true"></div>

<section id="overview-kruskal-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-kruskal-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">算法核心 · 第 5 课 · 可追踪生成森林实验</span>

# Kruskal、环检测与最小生成森林

## 八条候选边，只留下五条

```text
edges_sorted：5-6@-1, 0-2@1, 1-2@2, 3-4@2, 2-3@3, 0-1@4, 1-3@5, 2-4@6
accepted：5-6@-1, 0-2@1, 1-2@2, 3-4@2, 2-3@3
rejected_cycles=3，components=2
total_weight=7，edge_count=5
```

Kruskal 从最轻边开始检查。边的两端还不连通，就接纳并合并分量；两端已经同根，再加这条边只会成环，所以拒绝。样例图本来就断开，结果自然是两棵树组成的森林。

[看边怎样被接纳](#example-edge-decisions){ .md-button .md-button--primary }
[运行环检测轨迹](#reproduce-kruskal-trace){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>算法核心 · 5 / 6</strong></span><span>前置<strong>带权无向图与并查集</strong></span><span>完成后留下<strong>确定性 Kruskal、环拒绝与森林契约</strong></span></div>

</section>

## 开始前

- 能用并查集判断两点是否属于同一分量。
- 知道一棵包含 V 个顶点的树恰有 `V-1` 条边。
- 不把“连接全图的总成本”与“从一个起点到各点的距离”混为一谈。

<section id="concept-tree-forest-goal" data-learning-context="concept-tree-forest-goal" data-context-type="concept" markdown="1">

## 最短路径和最小生成森林在优化不同目标

Dijkstra 关心从一个起点到其他点的路线；最小生成树关心用哪些边连接整个连通图，使选边总权重最小。两种结构通常不是同一棵树。

断开图无法用一棵树覆盖。每个连通分量各取一棵最小树，合起来是最小生成森林。若图有 V 个顶点、C 个分量，森林恰有 `V-C` 条边。

</section>

<section id="example-negative-disconnected" data-learning-context="example-negative-disconnected" data-context-type="example" markdown="1">

## 负权边可以选，断开图也可以返回结果

边 `5—6@-1` 会最先接纳。MST 没有 Dijkstra 那种“距离一旦确定就不能再下降”的前提，负权边只是让总成本更低。

样例中 `{0,1,2,3,4}` 与 `{5,6}` 互不相连，所以 C=2、V=7，森林必须有 5 条边。要求单棵树的 `minimum_spanning_tree()` 应当失败，而 `kruskal_forest()` 正常返回两分量结果。

</section>

<section id="concept-edge-order" data-learning-context="concept-edge-order" data-context-type="concept" markdown="1">

## 先规范端点，再按 `(weight,u,v)` 排序

无向边统一保存为 `u<v`。图允许负权、零权和相同权重，拒绝越界、自环与重复端点对。

Kruskal 按权重、起点、终点依次升序。端点只用于相同权重时得到稳定轨迹；它保证 Python/C++ 可复现，不代表最优森林在数学上唯一。

</section>

<section id="example-edge-decisions" data-learning-context="example-edge-decisions" data-context-type="example" markdown="1">

## 前五条连接分量，后三条只会成环

<div class="be-kruskal-edges" aria-label="Kruskal 接纳与拒绝边">
  <div><strong>接纳</strong><code>5-6@-1</code><span>连接 5 与 6</span></div>
  <div><strong>接纳</strong><code>0-2@1</code><span>建立主分量</span></div>
  <div><strong>接纳</strong><code>1-2@2</code><span>把 1 接入</span></div>
  <div><strong>接纳</strong><code>3-4@2</code><span>建立另一小树</span></div>
  <div><strong>接纳</strong><code>2-3@3</code><span>合并两棵主树</span></div>
  <div data-rejected="true"><strong>拒绝</strong><code>0-1@4</code><span>两端已经同根</span></div>
  <div data-rejected="true"><strong>拒绝</strong><code>1-3@5</code><span>加入会形成环</span></div>
  <div data-rejected="true"><strong>拒绝</strong><code>2-4@6</code><span>仍在同一分量</span></div>
</div>

每接纳一条边，分量数减一；拒绝边不改变并查集。最终分量从 7 降到 2，正好接纳 5 条。

</section>

<section id="concept-dsu-cycle" data-learning-context="concept-dsu-cycle" data-context-type="concept" markdown="1">

## 同根意味着两端已经有一条路径

检查边 `(u,v)` 时，若 `find(u)==find(v)`，当前森林中已经有路径连接两端；再加入这条边必然闭合成环。若根不同，`union(u,v)` 合并两个分量并接纳边。

总权重在接纳边时执行有符号 64 位安全加法。若溢出，算法受控失败，不返回一份看似完整的半成品森林。

</section>

<section id="example-same-weight" data-learning-context="example-same-weight" data-context-type="example" markdown="1">

## 同权边可能产生不止一个最优结果

两条权重同为 2 的边按端点顺序检查。另一种合法平局顺序可能选择不同边，只要仍满足无环、覆盖相同分量且总权重最小，就可能同样正确。

因此测试应锁定本项目的确定输出，同时用总权重、分量数和 `V-C` 边数验证最优森林契约，不能把固定输出误说成唯一答案。

</section>

<section id="reproduce-kruskal-trace" data-learning-context="reproduce-kruskal-trace" data-context-type="reproduce" markdown="1">

## 打印每条边的接纳或拒绝

```bash
.venv/bin/python site-src/examples/algorithm-core/kruskal_cycle_trace.py
```

最后三条应显示 `same_root=0` 并被拒绝；汇总为 `total_weight=7 components=2 edge_count=5`。

</section>

<section id="reproduce-bilingual-kruskal" data-learning-context="reproduce-bilingual-kruskal" data-context-type="reproduce" markdown="1">

## 运行双语言生成森林实验

```bash
cd exercises/cs-core/traceable-spanning-forest-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_spanning_forest_lab kruskal
```

```bash
cd exercises/cs-core/traceable-spanning-forest-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_spanning_forest_lab kruskal
```

回归 `dsu` 和 `prim`；三种模式的双语言输出都要一致。

</section>

<section id="modify-isolated-overflow" data-learning-context="modify-isolated-overflow" data-context-type="modify" markdown="1">

## 加一个孤立点，再试一次安全加法

加入孤立顶点后，分量数增加 1，接纳边数仍应等于 `V-C`；森林接口成功，单树接口失败。

再构造两条必须接纳、总和超过有符号 64 位范围的边。Python 与 C++ 都应在返回结果前拒绝溢出，不能依赖某种语言的整数行为掩盖契约。

</section>

<section id="modify-rejected-edges" data-learning-context="modify-rejected-edges" data-context-type="modify" markdown="1">

## 返回所有成环拒绝边

完成 `rejected_cycle_edges(graph)`，按 Kruskal 检查顺序返回拒绝项。覆盖空图、原本就是树、单环、多分量、同权和输入重排。

接受数应为 `V-C`，拒绝数应为 `E-(V-C)`，调用前后的输入边保持不变。

</section>

<section id="troubleshoot-kruskal" data-learning-context="troubleshoot-kruskal" data-context-type="troubleshoot" markdown="1">

## 权重对了但结构错，或结果随输入漂移

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 把结果当最短路径树 | 混淆优化目标 | 检查总连接权重，不检查单源距离 |
| 错误拒绝负权边 | 套用了 Dijkstra 前提 | MST 允许负权 |
| 断开图强行返回单树 | 忽略分量数 | 返回森林；单树接口受控失败 |
| 输入重排改变结果 | 没有规范边排序 | 使用 `(weight,u,v)` |
| 同权时宣称结果唯一 | 把确定输出当数学唯一性 | 只承诺可复现的一个最优森林 |
| 边数不等于 `V-C` | 接纳了环或漏了跨分量边 | 每条边先用 DSU 判断根 |

</section>

<section id="project-forest-v02" data-learning-context="project-forest-v02" data-context-type="project" markdown="1">

## 可追踪生成森林实验 v0.2

这一版把并查集接到真实算法：规范并排序边，用同根拒绝环，用跨根合并分量，并输出接受／拒绝轨迹、总权重和分量数。下一课会用 Lazy Prim 从局部割边前沿得到同样的总权重。

[查看阶段作品](../../exercises/cs-core/traceable-spanning-forest-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-kruskal-cost" data-learning-context="deepen-kruskal-cost" data-context-type="deepen" markdown="1">

## 排序是主要成本

对 E 条边排序需要 `O(E log E)`。随后每条边做常数次并查集操作，总计 `O(E α(V))`，不超过排序主项，所以整体写作 `O(E log E)`。

额外空间包括排序后的边、并查集父森林和结果边，为 `O(V+E)`。

</section>

<section id="career-kruskal-evidence" data-learning-context="career-kruskal-evidence" data-context-type="career" markdown="1">

## 解释 Kruskal 时，先说“同根就成环”

给出 `(weight,u,v)` 顺序，走前五条接纳边，再用 `0-1@4` 展示同根拒绝。随后说明断开图返回森林、负权合法、同权不保证唯一。

最后用 `V-C` 和总权重 7 收口。这样算法、数据结构、边界与验证都在同一个例子里。

</section>

## 完成检查

- [ ] 能区分最短路径、最小生成树与最小生成森林。
- [ ] 边按 `(weight,u,v)` 确定排序，允许负权与同权。
- [ ] DSU 同根拒绝成环，跨根接纳并合并分量。
- [ ] 断开图返回森林，单树接口安全失败。
- [ ] 接纳数为 `V-C`，拒绝数为 `E-(V-C)`。
- [ ] 能解释同权确定输出不等于最优森林唯一。
- [ ] Python 类型检查、C++ CTest 与三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [Princeton Minimum Spanning Trees](https://algs4.cs.princeton.edu/43mst/index.php) | Kruskal、割性质与森林边界 | 2026-07-18 核查 |
| [MIT 6.046 Minimum Spanning Trees](https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/4a7fdddff3bc419c70bb470106a1663a_MIT6_046JS15_lec12.pdf) | 正确性与复杂度 | 2026-07-18 核查 |

本课不进入动态 MST、次小生成树、唯一性判定或稠密图专用实现。

## 下一步

进入[Lazy Prim、割边前沿与过期边](26-lazy-prim-cut-frontier-stale-edges.md)，从当前已访问集合向外选择最轻边，并与 Kruskal 对照。
