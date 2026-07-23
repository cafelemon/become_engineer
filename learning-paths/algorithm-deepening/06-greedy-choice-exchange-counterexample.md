<div class="be-tutor-mount" data-tutor-lesson="algorithm-deepening-06" aria-hidden="true"></div>

<section id="overview-greedy" class="be-page-hero be-lesson-hero" data-learning-context="overview-greedy" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">算法深化 · 第 6 / 10 课 · 可追踪约束模式实验 v0.6</span>

# 贪心选择、交换论证与反例

## 局部选择只有连同目标、前提和证明才成立

```text
intervals=A[1,4),B[3,5),C[0,6),D[5,7),E[3,9),F[5,9),G[6,10),H[8,11),I[8,12),J[2,14),K[12,16)
order_by_finish=A,B,C,D,E,F,G,H,I,J,K
select=A,D,H,K count=4
earliest_start_select=C,G,K count=3
exchange=finish-no-later-preserves-room
invariant=selected-intervals-nonoverlap
```

本课目标是选择最多个互不重叠区间。按结束时间最早选择能留下不少于其他首选的后续空间；“开始最早”看似合理，却在同一输入上只得到 3 个。

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>算法深化 · 6 / 10</strong></div>
  <div><span>前置</span><strong>排序、半开区间与反例</strong></div>
  <div><span>实现</span><strong>Python 3.11 + C++20 区间调度</strong></div>
  <div><span>完成后留下</span><strong>局部规则、交换证明、反例与小规模 oracle</strong></div>
</div>

## 学习目标

- 先固定优化目标，再判断局部选择是否适用。
- 用交换论证证明最早结束选择不损失最优解。
- 用具体反例淘汰最早开始等错误直觉。
- 区分用于生产的贪心算法与仅用于小输入的穷举 oracle。
- 明确无权区间计数、带权区间价值与边界语义不是同一问题。

<section id="concept-interval-contract" data-learning-context="concept-interval-contract" data-context-type="concept" markdown="1">

## 先冻结目标与半开区间契约

输入区间使用 `[start,end)`，目标是最大化选中区间的**数量**。因此 `[1,4)` 与 `[4,7)` 可以相接，兼容条件是下一段 `start >= last_end`。

如果目标改为总时长或总价值，最早结束不再自动正确；如果区间改为闭区间，相接边界也要改成严格大于。证明只能服务于它明确写出的契约。

</section>

<section id="example-earliest-finish" data-learning-context="example-earliest-finish" data-context-type="example" markdown="1">

## 按结束时间排序后只扫描一次

```python
ordered = sorted(intervals, key=lambda item: (item.end, item.start, item.label))
selected = []
for item in ordered:
    if not selected or item.start >= selected[-1].end:
        selected.append(item)
```

排序主键是结束时间；开始时间和标签只让同结束时间的报告稳定，不承担正确性。样例固定选择 `A,D,H,K`，任意相邻两段都不重叠。

</section>

<section id="concept-exchange-proof" data-learning-context="concept-exchange-proof" data-context-type="concept" markdown="1">

## 用交换论证把局部选择接到全局最优

设贪心首选为结束最早的区间 `g`，某个最优解首段为 `o`。因为 `end(g) <= end(o)`，把最优解中的 `o` 换成 `g`，不会减少后续可用空间，也不会减少区间数量。

交换后得到一个包含 `g` 的最优解。删去与 `g` 冲突的前缀，剩余问题仍是同一种区间调度，因此可重复应用这个论证。这里证明的是“存在一个以贪心首选开头的最优解”，不是“每个看起来短的区间都应选择”。

</section>

<section id="reproduce-greedy-v06" data-learning-context="reproduce-greedy-v06" data-context-type="reproduce" markdown="1">

## 运行贪心、反例与穷举对照

```bash
cd site-src/examples/algorithm-deepening/pattern-lab-v06
../../../../.venv/bin/python -m unittest -v test_greedy_interval_trace.py
```

6 项测试覆盖贪心与穷举最优值一致、最早开始反例、半开区间相接、结束时间并列、空／非法输入和 Python/C++20 固定报告一致。

穷举会枚举子集，只适合小规模测试 oracle；正式算法排序为 `O(n log n)`、扫描为 `O(n)`，额外结果空间为 `O(n)`。

</section>

<section id="modify-greedy" data-learning-context="modify-greedy" data-context-type="modify" markdown="1">

## 主动改变目标与边界

1. 给每个区间增加价值，构造“一个长区间价值高于多个短区间”的输入，观察计数贪心失效。
2. 把半开区间改为闭区间，修正相接判定并增加边界测试。
3. 把排序改为最早开始，复现 `C,G,K` 只有 3 个的反例。
4. 随机生成至多 12 个区间，用穷举 oracle 比较贪心计数；不要把指数算法用于大输入。

</section>

<section id="troubleshoot-greedy" data-learning-context="troubleshoot-greedy" data-context-type="troubleshoot" markdown="1">

## 贪心错误按目标、选择和证明定位

| 现象 | 原因 | 恢复 |
| --- | --- | --- |
| 样例通过但隐藏用例失败 | 局部规则只有直觉 | 写交换对象与不劣关系 |
| 相接区间被判冲突 | 混用闭区间语义 | 固定 `[start,end)` 和 `>=` |
| 选中数量对、总价值错 | 优化目标已改变 | 使用带权区间 DP |
| 同结束时间输出漂移 | 缺少稳定次级键 | 增加 start、label 排序键 |
| 穷举测试超时 | 把 oracle 当生产算法 | 只限制在小 n |
| 按最早开始得到 3 个 | 错误局部选择占用未来 | 改为最早结束并保留反例 |

</section>

<section id="project-pattern-lab-v06" data-learning-context="project-pattern-lab-v06" data-context-type="project" markdown="1">

## 可追踪约束模式实验 v0.6

- v0.6 在前五版的状态轨迹之外，首次把局部规则、反例和证明义务放进同一固定报告。
- Python 用小规模穷举校验样例最优值，C++20 实现同一生产贪心；两端报告逐字一致。
- 下一版进入线性动态规划：当局部选择无法证明时，显式保存子问题最优值与决策来源。

</section>

## 四类学习者入口

- 零基础兴趣：在时间轴上标出 `A,D,H,K`，逐段检查相接边界。
- 有基础兴趣：生成小区间集，用穷举 oracle 搜索错误规则的反例。
- 零基础求职：口述“目标—选择—可行性—交换—复杂度”五段解释。
- 有基础求职：把问题改为带权区间，说明为何原证明断裂并给出 DP 状态。

<section id="career-greedy-proof" data-learning-context="career-greedy-proof" data-context-type="career" markdown="1">

## 求职加练：反例比“贪心一般可用”更有信息

原创追问：同事按最早开始选择区间，并用几个样例声称最优。请用本课数据给出 3 对 4 的反例，写出最早结束的交换论证；随后加入区间价值，指出原证明哪一步不再保留目标，并提出下一步算法。

</section>

## 完成检查

- 6 项测试通过，Python 与 C++20 固定报告一致。
- 最早结束得到 `A,D,H,K` 共 4 个，最早开始只得到 `C,G,K` 共 3 个。
- 交换论证明确使用 `end(g) <= end(o)` 和最大数量目标。
- 半开区间允许端点相接，同结束时间的次级键只保证确定性。
- 穷举只作为小规模 oracle；生产路径为 `O(n log n)`。

## 来源与版本

- Python 3.11、C++20；核查日期 2026-07-23。
- [CP-Algorithms: Scheduling jobs on one machine](https://cp-algorithms.com/schedules/schedule_one_machine.html)：区间调度贪心与交换思路。
- [Python sorting HOWTO](https://docs.python.org/3.11/howto/sorting.html)：稳定排序和复合键。

## 下一步

进入第 7 课《线性动态规划、状态与转移》，用显式子问题状态处理无法由单次局部选择证明的问题。

