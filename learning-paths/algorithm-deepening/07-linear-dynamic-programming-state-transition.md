<div class="be-tutor-mount" data-tutor-lesson="algorithm-deepening-07" aria-hidden="true"></div>

<section id="overview-linear-dp" class="be-page-hero be-lesson-hero" data-learning-context="overview-linear-dp" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">算法深化 · 第 7 / 10 课 · 可追踪约束模式实验 v0.7</span>

# 线性动态规划、状态与转移

## 状态先说明自己代表哪个子问题，再写公式

```text
values=4,5,4,1,1
dp=0,4,5,8,8,9
optimal=9 chosen_indices=0,2,4
highest_first=6 chosen_indices=1,3
transition=dp[i]=max(dp[i-1],dp[i-2]+value[i-1])
tie=skip-current
invariant=dp-prefix-optimum
```

本课求一组不相邻下标，使元素和最大；允许一个也不选。局部先取最大值只得到 6，动态规划通过前缀最优子问题得到 9。

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>算法深化 · 7 / 10</strong></div>
  <div><span>前置</span><strong>递归子问题、贪心反例与不变量</strong></div>
  <div><span>实现</span><strong>Python 3.11 + C++20 线性 DP</strong></div>
  <div><span>完成后留下</span><strong>状态表、选择重建、平局契约与 oracle</strong></div>
</div>

## 学习目标

- 用一句话定义 `dp[i]`，避免下标语义漂移。
- 从“跳过当前”和“选择当前”推导转移。
- 写出空前缀基线并解释负数输入为什么返回空选择。
- 从状态表重建一组最优下标，而不只返回最优值。
- 用穷举 oracle 和错误贪心反例验证状态设计。

<section id="concept-dp-state" data-learning-context="concept-dp-state" data-context-type="concept" markdown="1">

## dp[i] 是前 i 个元素的最优和

`dp[0]=0` 表示空前缀。处理第 `i-1` 个元素时只有两类合法最优解：

- 跳过它：值为 `dp[i-1]`；
- 选择它：相邻的 `i-2` 不能选，值为 `dp[i-2]+values[i-1]`。

因此：

```text
dp[i] = max(dp[i-1], dp[i-2] + values[i-1])
```

状态定义、数组长度和取值下标必须一起读；把“前 i 个”误写成“下标 i 的答案”，是最常见的偏一错误。

</section>

<section id="example-dp-table" data-learning-context="example-dp-table" data-context-type="example" markdown="1">

## 每个格子只依赖前两个前缀

| i | 当前值 | 跳过 | 选择 | dp[i] |
| ---: | ---: | ---: | ---: | ---: |
| 0 | — | — | — | 0 |
| 1 | 4 | 0 | 4 | 4 |
| 2 | 5 | 4 | 5 | 5 |
| 3 | 4 | 5 | 8 | 8 |
| 4 | 1 | 8 | 6 | 8 |
| 5 | 1 | 8 | 9 | 9 |

归纳不变量是：计算完 `dp[i]` 后，它等于前 `i` 个元素所有合法选择中的最大和。两类决策覆盖全部可能且互斥，因此转移没有漏解。

</section>

<section id="concept-dp-reconstruction" data-learning-context="concept-dp-reconstruction" data-context-type="concept" markdown="1">

## 最优值与一组最优解是两个契约

从表尾向前比较：

```python
if take > skip:
    choose(i - 1)
    i -= 2
else:
    i -= 1
```

平局固定跳过当前元素，保证多组最优解时输出可重复。样例重建下标 `0,2,4`。若只保留两个滚动值可把求值空间降到 `O(1)`，但无法直接按此方式重建路径；空间优化必须服从输出契约。

</section>

<section id="reproduce-linear-dp-v07" data-learning-context="reproduce-linear-dp-v07" data-context-type="reproduce" markdown="1">

## 运行状态、重建和反例实验

```bash
cd site-src/examples/algorithm-deepening/pattern-lab-v07
../../../../.venv/bin/python -m unittest -v test_linear_dp_trace.py
```

6 项测试覆盖固定状态表与重建、随机小输入穷举对照、错误贪心反例、空与全负输入、平局规则和 Python/C++20 固定报告一致。

生产算法时间 `O(n)`；保存完整表和结果为 `O(n)`。穷举只服务于小规模测试，不属于生产复杂度。

</section>

<section id="modify-linear-dp" data-learning-context="modify-linear-dp" data-context-type="modify" markdown="1">

## 改变输出、间隔与循环结构

1. 只要求最大值，把完整表压成两个滚动变量，并保留与原实现的对照测试。
2. 把“不相邻”改为至少间隔 `k` 个位置，重新定义选择分支的前驱状态。
3. 禁止空选择，观察全负输入的基线和答案如何变化。
4. 把平局规则改为选择当前，确认最优值不变但重建下标改变。

</section>

<section id="troubleshoot-linear-dp" data-learning-context="troubleshoot-linear-dp" data-context-type="troubleshoot" markdown="1">

## DP 错误按状态、基线、转移和顺序定位

| 现象 | 原因 | 恢复 |
| --- | --- | --- |
| 第一个元素越界 | 没有空前缀基线 | 建立长度 `n+1` 的 dp |
| 选择了相邻元素 | take 错接 `dp[i-1]` | 选择当前时接 `dp[i-2]` |
| 全负输入返回负数 | 忘记允许空选择 | 保持 `dp[0]=0` 与 max |
| 最优值对、路径相邻 | 重建逻辑与转移不一致 | 使用同一 take/skip 比较 |
| 多次运行路径漂移 | 平局没有契约 | 固定 `take > skip` 才选择 |
| 压缩后无法重建 | 丢弃了决策来源 | 保存表／父指针或改变输出契约 |

</section>

<section id="project-pattern-lab-v07" data-learning-context="project-pattern-lab-v07" data-context-type="project" markdown="1">

## 可追踪约束模式实验 v0.7

- v0.7 把“无法证明单次局部选择”的问题拆为重叠前缀子问题。
- 固定报告同时保留输入、完整状态表、最优值、重建下标、错误贪心和状态不变量。
- 下一版将进入二维与区间状态，比较 0/1 背包的迭代方向、空间压缩和区间 DP 的长度顺序。

</section>

## 四类学习者入口

- 零基础兴趣：手填六个 dp 格子，并为每格圈出 take 或 skip。
- 有基础兴趣：实现只求值的 `O(1)` 空间版本，与完整表随机对照。
- 零基础求职：按“状态—基线—转移—顺序—答案”解释样例。
- 有基础求职：加入至少间隔 `k` 的限制，给出新转移、复杂度和重建方案。

<section id="career-linear-dp" data-learning-context="career-linear-dp" data-context-type="career" markdown="1">

## 求职加练：公式不是状态定义的替代品

原创追问：候选人直接写出 `max(a,b+x)`，却无法说明 `a`、`b` 属于哪个前缀，也无法重建选择。请让其定义状态、证明两类决策完备、处理全负输入与平局，再说明压缩空间会丢失什么证据。

</section>

## 完成检查

- 6 项测试通过，Python 与 C++20 固定报告一致。
- 状态表为 `0,4,5,8,8,9`，重建下标为 `0,2,4`。
- “先取最大值”只得到 6，证明需要保存子问题而不能沿用该局部规则。
- 空与全负输入在允许空选择的契约下返回 0。
- 平局跳过当前；状态不变量是 `dp-prefix-optimum`。

## 来源与版本

- Python 3.11、C++20；核查日期 2026-07-23。
- [CP-Algorithms: Introduction to Dynamic Programming](https://cp-algorithms.com/dynamic_programming/intro-to-dp.html)：状态、转移与自底向上计算。
- [MIT OpenCourseWare: Dynamic Programming](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-19-dynamic-programming-i-fibonacci-shortest-paths/)：子问题与递推设计。

## 下一步

进入第 8 课《背包、区间动态规划与空间压缩》，把一维前缀状态扩展到容量和左右边界。

