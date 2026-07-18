<div class="be-tutor-mount" data-tutor-lesson="cs-core-24" aria-hidden="true"></div>

<section id="overview-dsu-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-dsu-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">算法核心 · 第 4 课 · 可追踪生成森林实验</span>

# 并查集、按大小合并与路径压缩

## 5 原来要走两级父节点，查询后只走一级

```text
parents_before_find：0, 0, 0, 0, 0, 4, 4
find(5)：root=0，visits=3，compressed=1
parents_after_find：0, 0, 0, 0, 0, 0, 4
connected(3,6)=yes
```

查询 5 时依次访问 `5→4→0`，根是 0。查询结束后，5 直接指向 0；4 本来就指向 0，不需要重复写。下一次查询 5，只访问 `5→0`。

[看懂父森林](#example-parent-forest){ .md-button .md-button--primary }
[运行路径压缩](#reproduce-dsu-trace){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>算法核心 · 4 / 6</strong></span><span>前置<strong>树、连通分量与数组下标</strong></span><span>完成后留下<strong>确定性并查集、压缩轨迹与分组接口</strong></span></div>

</section>

## 开始前

- 知道根节点可以代表一棵树，多个根构成森林。
- 能区分“两个元素属于同一组”和“原图中两点之间的具体路径”。
- 本课先建立集合维护结构；下一课再把它用于 Kruskal 环检测。

<section id="concept-parent-forest" data-learning-context="concept-parent-forest" data-context-type="concept" markdown="1">

## 每个元素只保存一个父下标

初始化时 `parent[i]=i`、`size[i]=1`，每个元素各自是一棵单节点树。根的父节点等于自己；沿父下标向上走，最终到达集合代表。

父数组不是原图的边表。`parent[5]=4` 只说明 5 通过集合维护结构到达代表，不能证明原图一定有一条 `5—4` 边，也不能用它恢复原图路径。

</section>

<section id="example-parent-forest" data-learning-context="example-parent-forest" data-context-type="example" markdown="1">

## 同一片父森林的四个位置

<div class="be-dsu-forest" aria-label="元素 5 到根 0 的父森林与压缩">
  <div><strong>元素 5</strong><code>parent[5] = 4</code><span>查询起点</span></div>
  <div><strong>元素 4</strong><code>parent[4] = 0</code><span>中间父节点</span></div>
  <div><strong>根 0</strong><code>parent[0] = 0</code><span>集合代表</span></div>
  <div data-compressed="true"><strong>压缩以后</strong><code>parent[5] = 0</code><span>后续少走一级</span></div>
</div>

元素 6 仍可以保持 `6→4→0`，因为本次只查询了 5。路径压缩修改查询路径上的槽位，不会无缘无故扫描整棵树。

</section>

<section id="concept-find-compression" data-learning-context="concept-find-compression" data-context-type="concept" markdown="1">

## `find` 先找根，再压平走过的路径

迭代 `find(5)` 先收集完整路径 `[5,4,0]`，然后把根以前的元素直接指向 0。

- `visits` 包含起点和根，所以是 3。
- `compressions` 只统计父值真正改变的槽位。
- 5 从 4 改为 0，计 1 次；4 已经是 0，不计写入。

越界检查必须在读取父数组以前完成。Python 要主动拒绝负下标，不能让 `-1` 被解释成末尾元素。

</section>

<section id="example-find-again" data-learning-context="example-find-again" data-context-type="example" markdown="1">

## 再查一次 5，计数会变

```text
第一次：path=5→4→0，visits=3，compressions=1
第二次：path=5→0，  visits=2，compressions=0
```

第二次没有新的父值变化，但查询仍访问起点和根。不要把“压缩后很快”误写成“每次只访问一次”。

</section>

<section id="concept-union-by-size" data-learning-context="concept-union-by-size" data-context-type="concept" markdown="1">

## 合并时只挂根，而且小树挂到大树

`union(a,b)` 先分别 `find` 两端。若根不同，比较根记录的 `size`，把较小树的根挂到较大树的根，并让分量数减一。

只能挂根：大小只对根有效，把任意内部元素挂过去会破坏集合大小和树形推理。若两棵树一样大，本项目让编号较小的根留下，保证 Python/C++ 和不同参数顺序得到同一代表。

</section>

<section id="example-union-tie" data-learning-context="example-union-tie" data-context-type="example" markdown="1">

## `union(1,0)` 的根仍是 0

两个单元素集合大小都是 1，按平局规则保留较小根 0。`union(3,2)` 保留 2；随后把两棵大小为 2 的树合并，仍保留较小根 0。

再次 `union(3,1)` 时两端已经同根：返回“未合并”，父数组、根大小和分量数不再变化。只有真实连接两个不同分量时才减分量数。

</section>

<section id="reproduce-dsu-trace" data-learning-context="reproduce-dsu-trace" data-context-type="reproduce" markdown="1">

## 打印 `5→4→0` 的压缩过程

```bash
.venv/bin/python site-src/examples/algorithm-core/dsu_compression_trace.py
```

你应该看到 `visits=3 compressions=1`，以及父数组中只有位置 5 从 4 变成 0。根 0 的集合大小仍是 7。

</section>

<section id="reproduce-bilingual-dsu" data-learning-context="reproduce-bilingual-dsu" data-context-type="reproduce" markdown="1">

## 运行 Python 和 C++ 生成森林实验

```bash
cd exercises/cs-core/traceable-spanning-forest-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_spanning_forest_lab dsu
```

```bash
cd exercises/cs-core/traceable-spanning-forest-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_spanning_forest_lab dsu
```

同时回归 `kruskal` 和 `prim`，三种模式的 Python/C++ 标准输出必须逐字一致。

</section>

<section id="modify-small-repeated" data-learning-context="modify-small-repeated" data-context-type="modify" markdown="1">

## 从 0 个、1 个元素开始试

- `DisjointSet(0)` 有 0 个分量，`groups()` 返回空。
- `DisjointSet(1)` 有 1 个分量，`find(0)` 访问一次。
- 对已经连通的两点重复 `union`，分量数不变。
- 查询 `-1` 或 `element_count`，受控失败且父数组不变。

这里先别急着用大数据。最小规模最容易暴露空数组、负下标和重复合并错误。

</section>

<section id="modify-groups" data-learning-context="modify-groups" data-context-type="modify" markdown="1">

## 把父森林整理成确定分组

实现 `groups()`：对每个元素调用 `find`，按根聚合；分组按代表编号排序，成员也按编号排序。

用两个分量、一个孤立元素和重复合并检查结果。每个元素必须恰好出现一次；改变 `union` 参数顺序后，按大小与平局规则仍应给出相同分组。

</section>

<section id="troubleshoot-dsu" data-learning-context="troubleshoot-dsu" data-context-type="troubleshoot" markdown="1">

## 根乱了、分量少了或压缩计数偏大

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 把父数组当作原图路径 | 混淆维护结构与输入图 | 只把父链解释为代表关系 |
| 平局根跨语言不同 | 没有确定规则 | 同大小保留编号较小根 |
| 压缩次数等于路径长度 | 把读取也算写入 | 只统计父值真实变化 |
| 重复合并减少分量数 | 同根后仍继续修改 | 同根立即返回未合并 |
| 树越来越高 | 大树挂到小树或挂内部节点 | 比根大小，只把根相连 |
| Python `find(-1)` 没报错 | 沿用了负下标语义 | 访问数组前显式检查范围 |

</section>

<section id="project-forest-v01" data-learning-context="project-forest-v01" data-context-type="project" markdown="1">

## 可追踪生成森林实验 v0.1

第一版建立父森林、按大小合并、确定平局、完整路径压缩、精确访问／写入计数和稳定分组。下一课 Kruskal 会逐条拿候选边的两个端点做 `union`：合并成功就接纳，已经同根就拒绝成环边。

[查看阶段作品](../../exercises/cs-core/traceable-spanning-forest-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-dsu-cost" data-learning-context="deepen-dsu-cost" data-context-type="deepen" markdown="1">

## `O(α(n))` 是一串操作的摊还界限

单次 `find` 仍可能沿父链访问多个节点。按大小合并控制树高，路径压缩又让走过的节点靠近根，两者共同让一系列操作的摊还代价达到 `O(α(n))`。

反阿克曼函数增长极慢，因此工程里常说“接近常量”；但它不等于宣称每次操作的最坏情况严格是 `O(1)`。

</section>

<section id="career-dsu-evidence" data-learning-context="career-dsu-evidence" data-context-type="career" markdown="1">

## 用 `5→4→0` 讲并查集最清楚

先解释父数组只表示集合代表，再走一次 `find(5)`：访问三个位置，只发生一次真实写入。接着说按大小合并、同大小较小根留下，以及重复合并为什么不减分量。

最后补 `O(α(n))` 是摊还结论，并说明下一课如何用同根判断环。这样结构、优化、计数和用途就连起来了。

</section>

## 完成检查

- [ ] 能解释父森林、根和分量数，不把父数组当原图路径。
- [ ] `find` 记录完整路径，只统计真实压缩写入。
- [ ] `union` 只连接根，小树挂大树，同大小保留较小根。
- [ ] 重复合并、越界、空集合和单元素都有确定行为。
- [ ] `groups()` 让所有元素恰好出现一次并稳定排序。
- [ ] 能正确表述 `O(α(n))` 的摊还含义。
- [ ] Python 类型检查、C++ CTest 与三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [Princeton Union-Find](https://algs4.cs.princeton.edu/15uf/) | 父森林、加权合并与路径压缩 | 2026-07-18 核查 |
| [MIT 6.046 Minimum Spanning Trees](https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/4a7fdddff3bc419c70bb470106a1663a_MIT6_046JS15_lec12.pdf) | 并查集在 Kruskal 中的用途 | 2026-07-18 核查 |

本课不进入可撤销并查集、持久化并查集、带权并查集或动态连通性；它们需要额外状态与不同的复杂度讨论。

## 下一步

进入[Kruskal、环检测与最小生成森林](25-kruskal-minimum-spanning-forest.md)，用并查集决定每条候选边是连接分量还是形成环。
