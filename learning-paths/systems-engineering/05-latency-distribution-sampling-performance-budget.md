<div class="be-tutor-mount" data-tutor-lesson="systems-engineering-05" aria-hidden="true"></div>

<section id="overview-performance-evidence" class="be-page-hero be-lesson-hero" data-learning-context="overview-performance-evidence" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">系统工程 · 第 5 / 6 课 · 可诊断系统服务 v0.5</span>

# 延迟分布、采样分析与性能预算

## 平均值正常，尾部请求仍可能很慢

本课把性能证据拆成可重复的分布回放和真实但不稳定的本机测量：

```text
replay_samples=20
percentile_method=nearest-rank
p50_us=30
p95_us=120
p99_us=200
budget_p95_us=150 result=pass
measurement_clock=steady_clock
warmup_iterations=1000
measurement_samples=2000
elapsed=observed-not-asserted
```

固定样本用于验证百分位算法和预算判断；墙钟测量用于学习预热、采样和噪声边界，不把某台机器的一次耗时写成跨环境门槛。

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>系统工程 · 5 / 6</strong></div>
  <div><span>前置</span><strong>真实 I/O 状态 + 稳定输出契约</strong></div>
  <div><span>环境</span><strong>C++20 chrono + 确定性样本回放</strong></div>
  <div><span>完成后留下</span><strong>p50/p95/p99、预热采样与预算证据</strong></div>
</div>

## 开始前

- 你知道单次运行结果不能代表完整分布。
- 你能区分功能正确性与速度目标。
- 本课不做跨机器排行榜，也不把微基准直接外推为整机容量。

## 学习目标

- 从延迟样本计算并解释 p50、p95 与 p99。
- 明确百分位算法，避免不同工具算出不同结果却无法解释。
- 分离预热、测量和结果汇总。
- 使用单调时钟测量持续时间。
- 把性能预算写成指标、阈值、负载和环境共同组成的契约。

<section id="concept-latency-distribution" data-learning-context="concept-latency-distribution" data-context-type="concept" markdown="1">

## 百分位描述“有多少样本不超过这个值”

将 20 个延迟从小到大排列，最近秩方法取：

```text
rank = ceil(percentile / 100 * sample_count)
value = sorted_samples[rank - 1]
```

因此本课 p95 是第 19 个样本 120µs，p99 是第 20 个样本 200µs。p50 描述中间体验，p95/p99 暴露尾部；平均值可能被大量快请求掩盖，也可能被少数极端值拉高，不能替代分布。

```mermaid
flowchart LR
  A["定义负载与边界"] --> B["预热"]
  B --> C["采集独立样本"]
  C --> D["排序并计算百分位"]
  D --> E{"p95 <= 预算?"}
  E -->|是| F["记录通过与环境"]
  E -->|否| G["剖析慢路径并复测"]
```

</section>

<section id="example-sampling-clock" data-learning-context="example-sampling-clock" data-context-type="example" markdown="1">

## 墙钟负责观察，不负责让测试碰运气

测量持续时间使用 `std::chrono::steady_clock`，它不会因系统时间校准而倒退。预热的 1000 次调用不进入测量区间，随后执行 2000 个相同粒度的样本工作。

本课故意输出 `elapsed=observed-not-asserted`，不输出某次纳秒数。CI 负载、CPU 频率、编译器、温度和后台进程都会影响绝对耗时。若要做性能回归门禁，需要固定运行环境、重复批次、保存基线与置信边界。

</section>

<section id="reproduce-performance-v05" data-learning-context="reproduce-performance-v05" data-context-type="reproduce" markdown="1">

## 运行分布与采样实验

```bash
cd site-src/examples/systems-engineering/diagnostic-service-v05
../../../../.venv/bin/python -m unittest -v test_performance_budget.py
```

5 项测试覆盖：

1. 20 个回放样本得到固定 p50/p95/p99。
2. p95 与 150µs 预算比较，而非用平均值替代。
3. 真实测量使用单调时钟，但不断言绝对耗时。
4. 1000 次预热与 2000 次测量明确分离。
5. 外层超时保证错误实现不会无限运行。

</section>

<section id="concept-performance-budget" data-learning-context="concept-performance-budget" data-context-type="concept" markdown="1">

## 性能预算必须带上测量条件

“接口要快”无法验收。较完整的预算至少说明：

- 指标：端到端延迟、CPU 时间、队列等待或吞吐。
- 统计：p50、p95、p99 或最大值，及具体计算方法。
- 阈值：例如 p95 不超过 150µs。
- 负载：消息大小、并发数、持续时间和冷／热状态。
- 环境：硬件、OS、编译模式与依赖版本。
- 失败动作：阻止发布、仅告警，还是要求复测。

本课的 150µs 只适用于固定回放数据，用来验证判断逻辑；它不是对所有机器上 `diagnostic_work` 的承诺。

</section>

<section id="modify-performance-budget" data-learning-context="modify-performance-budget" data-context-type="modify" markdown="1">

## 主动让尾部预算失败

1. 把第 19 个样本从 120 改为 180，确认 p95 预算失败并返回非零。
2. 只改最后一个样本为 500，比较 p95 与 p99 的变化。
3. 删除预热阶段，连续运行多批并记录首批差异，但不要据一次变化下结论。
4. 将最近秩改成线性插值，先写出算法名称和预期值再改测试。

恢复后固定输出应回到 `budget_p95_us=150 result=pass`。

</section>

<section id="troubleshoot-performance-evidence" data-learning-context="troubleshoot-performance-evidence" data-context-type="troubleshoot" markdown="1">

## 性能结论先审测量设计

| 现象 | 优先检查 | 恢复 |
| --- | --- | --- |
| 平均值稳定但用户仍抱怨慢 | 是否只看均值 | 检查 p95/p99 和慢样本 |
| CI 偶发越过绝对耗时线 | 环境是否共享且未固定 | 分离功能测试与受控性能门禁 |
| 两个工具百分位不同 | 算法与样本边界是否一致 | 声明最近秩或插值方法 |
| 首批明显更慢 | 是否包含冷启动与预热 | 分别报告冷、热阶段 |
| 基准快得不合理 | 工作是否被编译器消除 | 消费结果并核对功能输出 |
| 样本很多仍无法比较 | 负载、版本或环境是否漂移 | 给每批结果附元数据 |
| p95 通过但 p99 恶化 | 预算是否覆盖真实尾部风险 | 按业务目标增加尾部护栏 |

</section>

<section id="project-diagnostic-service-v05" data-learning-context="project-diagnostic-service-v05" data-context-type="project" markdown="1">

## 可诊断系统服务 v0.5

- v0.1–v0.4 已建立描述符、停止、队列与非阻塞网络边界。
- v0.5 新增最近秩百分位、固定回放、p95 预算、预热与 `steady_clock` 观测。
- 固定判断使用可重复数据；真实墙钟只作观测，不污染跨机器快照。
- 下一版本把前五课能力放进故障注入与恢复验收，检查资源是否回到基线。

</section>

## 四类学习者入口

- 零基础兴趣：手工排序 20 个样本并找到 p50、p95、p99。
- 有基础兴趣：加入直方图区间，并验证所有样本恰好落入一个桶。
- 零基础求职：解释为什么“平均 30µs”不能证明尾部体验。
- 有基础求职：设计包含环境、负载、统计方法和回归动作的性能门禁。

<section id="career-tail-latency" data-learning-context="career-tail-latency" data-context-type="career" markdown="1">

## 求职加练：平均延迟下降，超时却增加

原创追问：优化后平均延迟从 40ms 降到 30ms，但超时率上升。你会补采哪些分布、队列等待和负载证据？如何定义可复测的 p95/p99 预算，并避免共享 CI 上一次墙钟抖动误阻发布？

回答至少包含样本边界、百分位方法、预热、单调时钟、环境元数据和失败后的复测／剖析动作。

</section>

## 完成检查

- 5 项测试通过，固定样本的 p50/p95/p99 可复算。
- 明确使用最近秩方法，不把平均值当作尾部分布。
- p95 预算具有指标、阈值和数据边界。
- 真实测量使用 `steady_clock`，预热与测量分离。
- 墙钟绝对值不进入跨机器固定快照。
- 能说明微基准为何不能直接代表端到端容量。

## 来源与版本

- 适用 C++20；核查日期 2026-07-23。
- [C++ `steady_clock`](https://en.cppreference.com/w/cpp/chrono/steady_clock.html)：单调时钟语义。
- [C++ `duration_cast`](https://en.cppreference.com/w/cpp/chrono/duration/duration_cast.html)：持续时间单位转换。
- [Google Benchmark user guide](https://google.github.io/benchmark/user_guide.html)：预热、重复和结果解释参考；本课不引入该第三方依赖。

## 下一步

进入第 6 课《故障注入、资源泄漏与恢复验收》，把错误、超时、关闭和资源基线组合成系统工程组级出口。
