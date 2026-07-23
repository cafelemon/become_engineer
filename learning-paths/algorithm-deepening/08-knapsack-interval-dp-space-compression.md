<div class="be-tutor-mount" data-tutor-lesson="algorithm-deepening-08" aria-hidden="true"></div>

<section id="overview-structured-dp" class="be-page-hero be-lesson-hero" data-learning-context="overview-structured-dp" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">算法深化 · 第 8 / 10 课 · 可追踪约束模式实验 v0.8</span>

# 背包、区间动态规划与空间压缩

## 同一个公式换一种循环顺序，可能就换了问题

```text
knapsack_weights=2,3,4,5 values=3,4,5,8 capacity=7
knapsack_dp=0,0,3,4,5,8,8,11
knapsack_optimal=11
forward_single_item=6 correct_single_item=3
matrix_dims=10,30,5,60
matrix_cost=4500 order=((A1A2)A3)
orders=capacity-descending,interval-length-ascending
invariants=item-used-at-most-once,subintervals-ready
```

本课把动态规划的计算顺序当作正确性的一部分：0/1 背包压缩后容量倒序，区间 DP 按长度递增。

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>算法深化 · 8 / 10</strong></div>
  <div><span>前置</span><strong>线性 DP 状态、转移与重建</strong></div>
  <div><span>实现</span><strong>Python 3.11 + C++20 结构化 DP</strong></div>
  <div><span>完成后留下</span><strong>容量表、错误复用反例、区间顺序与括号化</strong></div>
</div>

## 学习目标

- 从二维 0/1 背包理解压缩容量维度的前提。
- 证明倒序容量让每件物品在本轮至多使用一次。
- 区分 0/1 背包与完全背包的循环语义。
- 用区间长度组织矩阵链子问题。
- 判断空间优化保留了什么、覆盖了什么证据。

<section id="concept-knapsack-state" data-learning-context="concept-knapsack-state" data-context-type="concept" markdown="1">

## 0/1 背包的二维来源

未压缩时，`dp[item_count][capacity]` 表示只使用前若干件物品、容量不超过上限时的最大价值。处理一件重量 `w`、价值 `v` 的物品：

```text
skip = previous[c]
take = previous[c-w] + v
current[c] = max(skip, take)
```

每件物品只有选择或跳过两种决策，不能重复使用。压缩成一维后，仍必须确保 take 读取的是“处理当前物品之前”的状态。

</section>

<section id="example-capacity-order" data-learning-context="example-capacity-order" data-context-type="example" markdown="1">

## 容量倒序保护旧层状态

```python
for weight, value in items:
    for capacity in range(limit, weight - 1, -1):
        dp[capacity] = max(dp[capacity], dp[capacity - weight] + value)
```

倒序时 `dp[capacity-weight]` 尚未被本轮当前物品更新，所以不会重复使用。若单件物品重量 2、价值 3、容量 4 改为正序，本轮先写 `dp[2]=3`，随后又用它写出 `dp[4]=6`，已经悄悄变成可重复取物品的模型。

</section>

<section id="concept-interval-order" data-learning-context="concept-interval-order" data-context-type="concept" markdown="1">

## 区间 DP 按长度从短到长

矩阵维度 `10,30,5,60` 表示三矩阵 `A1(10×30)`、`A2(30×5)`、`A3(5×60)`。状态 `cost[left][right]` 是这一连续矩阵区间的最少标量乘法次数。

计算长度为 `length` 的区间前，所有更短子区间必须完成。枚举切分点 `middle`：

```text
cost[l][r] =
  min(cost[l][m] + cost[m+1][r] + dims[l]*dims[m+1]*dims[r+1])
```

结果 `((A1A2)A3)` 需要 4500 次乘法；另一种 `A1(A2A3)` 需要 27000 次。区间长度正序保证转移依赖已就绪。

</section>

<section id="reproduce-structured-dp-v08" data-learning-context="reproduce-structured-dp-v08" data-context-type="reproduce" markdown="1">

## 运行容量方向与区间长度实验

```bash
cd site-src/examples/algorithm-deepening/pattern-lab-v08
../../../../.venv/bin/python -m unittest -v test_structured_dp_trace.py
```

6 项测试覆盖固定背包表、正序复用反例、随机小输入穷举对照、矩阵链顺序、非法输入和 Python/C++20 固定报告一致。

一维 0/1 背包时间 `O(items×capacity)`、空间 `O(capacity)`；矩阵链有 `O(n²)` 个区间、每个枚举 `O(n)` 切分点，因此时间 `O(n³)`、空间 `O(n²)`。

</section>

<section id="modify-structured-dp" data-learning-context="modify-structured-dp" data-context-type="modify" markdown="1">

## 主动改变复用、输出与依赖

1. 把问题改成完全背包，明确允许重复后将容量改为正序，并增加模型名称。
2. 要求输出背包选中的物品；比较完整二维表、父指针与仅一维值表。
3. 给矩阵链增加第四个矩阵，打印每个长度完成后的区间成本。
4. 故意按左端点正序、右端点正序填表，找到读取未完成子区间的反例。

</section>

<section id="troubleshoot-structured-dp" data-learning-context="troubleshoot-structured-dp" data-context-type="troubleshoot" markdown="1">

## 结构化 DP 按模型、维度和依赖顺序排错

| 现象 | 原因 | 恢复 |
| --- | --- | --- |
| 单件物品产生双倍价值 | 0/1 背包容量正序 | 容量倒序 |
| 完全背包只能取一次 | 错用了倒序 | 明确允许复用后正序 |
| 价值正确但无法列物品 | 压缩掉决策来源 | 保存二维表或父指针 |
| 矩阵链成本为零或过小 | 读取未完成区间 | 按长度递增 |
| 维度乘法下标错位 | 矩阵数和 dimensions 混淆 | 矩阵 i 为 dims[i]×dims[i+1] |
| 样例正确但模型不明 | 循环顺序靠记忆 | 写出本轮读的是旧层还是新层 |

</section>

<section id="project-pattern-lab-v08" data-learning-context="project-pattern-lab-v08" data-context-type="project" markdown="1">

## 可追踪约束模式实验 v0.8

- v0.8 将计算顺序提升为固定报告字段：`capacity-descending` 与 `interval-length-ascending`。
- 单件物品 6 对 3 的反例验证压缩方向；矩阵链同时输出最少成本和括号化。
- 下一版本回到图结构，比较拓扑依赖、强连通压缩和多源最短距离的不同状态边界。

</section>

## 四类学习者入口

- 零基础兴趣：手算单件物品正序与倒序两张容量表。
- 有基础兴趣：增加物品重建，说明为何一维表不足。
- 零基础求职：对比 0/1 与完全背包的循环方向及模型含义。
- 有基础求职：推导矩阵链状态、长度顺序与 `O(n³)` 复杂度。

<section id="career-structured-dp" data-learning-context="career-structured-dp" data-context-type="career" markdown="1">

## 求职加练：空间压缩不能只背一行模板

原创追问：候选人把二维 0/1 背包压成一维后容量正序，样例仍通过。请用单件物品构造 6 对 3 的反例，解释新旧层状态为何混合；再让其设计一个区间 DP 的填表顺序，并说明每个读取依赖何时就绪。

</section>

## 完成检查

- 6 项测试通过，Python 与 C++20 固定报告一致。
- 背包容量 7 的状态表为 `0,0,3,4,5,8,8,11`。
- 单件物品正序错误得到 6，倒序正确得到 3。
- 矩阵链最少成本 4500，括号化为 `((A1A2)A3)`。
- 两个顺序不变量分别是物品至多一次和子区间已经完成。

## 来源与版本

- Python 3.11、C++20；核查日期 2026-07-23。
- [CP-Algorithms: Knapsack Problem](https://cp-algorithms.com/dynamic_programming/knapsack.html)：0/1 与完全背包的一维迭代方向。
- [MIT OpenCourseWare: Dynamic Programming II](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-20-dynamic-programming-ii-text-justification-blackjack/)：子问题依赖与计算顺序。

## 下一步

进入第 9 课《高阶图：拓扑、强连通与多源路径》，把 DP 的依赖顺序迁移到图上的依赖、环与距离。

