<div class="be-tutor-mount" data-tutor-lesson="agent-application-orchestration-05" aria-hidden="true"></div>
<section id="overview-agent-evaluation" class="be-page-hero be-lesson-hero" data-learning-context="overview-agent-evaluation" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Agent 应用编排与交付 · 第 5 / 6 课 · 智能学习助手 P5.16 v0.35</span>
# 端到端评估、轨迹与故障定位
## 先找到最早失败层，再讨论最终答案
```text
evaluation=good:true,missing-first:retrieval
layers=task,retrieval,tool,context,trajectory,outcome,latency,cost
trace=run:run-1,request:req-1,spans:1,authorization:[REDACTED]
diagnosis=first-failing-layer:true,chain-of-thought:false
```
v0.35 联合任务、检索、工具、上下文、轨迹、结果、延迟和成本，并用 run/request 关联的脱敏 span 定位最早失败层。
</section>
<div class="be-lesson-overview"><div><span>课程位置</span><strong>Agent 应用编排与交付 · 5 / 6</strong></div><div><span>前置</span><strong>RAG 分层评估、Agent trace、计划与恢复</strong></div><div><span>环境</span><strong>Python 3.11+ · 标准库 · 固定评估案例</strong></div><div><span>完成后留下</span><strong>EvalCase、Trace、聚合门禁与 8 项测试</strong></div></div>

## 学习目标

- 为每个案例固定预期终态、必要证据、允许工具、步数、延迟和成本。
- 将“检索到了但上下文丢了”与“根本没召回”分开。
- 对 trace 默认脱敏并用 run_id/request_id 关联，不保存隐式思维链。
- 以最早失败层指导排查，以全层通过作为发布门禁。

<section id="concept-layered-agent-evaluation" data-learning-context="concept-layered-agent-evaluation" data-context-type="concept" markdown="1">
## 八层指标回答八类不同问题

task 检查终态是否合法；retrieval 检查必要证据是否召回；tool 检查工具白名单与危险执行；context 检查证据是否进入最终包；trajectory 检查步数和状态路径；outcome 检查业务终态；latency/cost 检查交付预算。最终答案正确不能抵消越权工具或超预算。
</section>

<section id="concept-trace-redaction" data-learning-context="concept-trace-redaction" data-context-type="concept" markdown="1">
## Trace 保存可解释事件，不保存秘密和思维链

每个 span 关联 run ID 与 request ID，记录节点名、结构化输入摘要、状态、耗时和错误码。Authorization、Cookie、密码、CSRF、原始 Prompt 和 chain-of-thought 默认替换为 `[REDACTED]`。查询和文档正文也不应成为高基数指标标签。
</section>

<section id="example-first-failing-layer" data-learning-context="example-first-failing-layer" data-context-type="example" markdown="1">
## 最早失败层缩小搜索范围

案例要求 `source-1`。若 retrieval 没有它、context 也没有、最终拒答，首个失败是 retrieval；无需先调 Prompt。若 retrieval 有而 context 没有，首个失败是 context，应查重排、压缩和预算。若层层通过但 outcome 错，再看回答或终态判定。
</section>

<section id="reproduce-agent-evaluation-v35" data-learning-context="reproduce-agent-evaluation-v35" data-context-type="reproduce" markdown="1">
## 运行评估和脱敏 trace
```bash
cd site-src/examples/agent-application-orchestration/intelligent-learning-assistant-v35
python3 -m unittest -v test_evaluation_trace.py
python3 evaluation_trace.py
```
8 项测试覆盖好运行、检索定位、工具违规、上下文丢失、轨迹预算、延迟/成本、敏感字段脱敏和分层聚合。
</section>

<section id="modify-add-fault-injection" data-learning-context="modify-add-fault-injection" data-context-type="modify" markdown="1">
## 增加可复现故障注入矩阵

1. 分别注入 retrieval empty、tool timeout、context drop、checkpoint crash。
2. 每个注入只改变一个层级变量。
3. 断言 first_failure 与预期一致。
4. 验证 trace 有错误码但没有敏感值。
5. 恢复后再次运行，确认门禁恢复而副作用不重复。
</section>

<section id="troubleshoot-agent-evaluation" data-learning-context="troubleshoot-agent-evaluation" data-context-type="troubleshoot" markdown="1">
## 从案例、关联、层级和采样排查

| 现象 | 首先检查 |
| --- | --- |
| 结果错却没有失败层 | EvalCase 是否标注必要证据和终态 |
| 检索通过但回答无引用 | context 检查是否覆盖最终证据包 |
| trace 无法串联 | run/request ID 是否贯穿异步 step |
| 指标正常但个别用户失败 | 采样是否保留错误与慢请求 |
| 日志泄露令牌 | redaction 是否在写出前执行 |
| 平均延迟正常但超时多 | 是否只看平均值而没有分布/阈值 |
</section>

<section id="deepen-evaluation-gates" data-learning-context="deepen-evaluation-gates" data-context-type="deepen" markdown="1">
## 发布门禁应包含硬失败和趋势

跨主体泄露、危险执行、引用失真和恢复重复副作用是零容忍硬门禁。任务成功、检索、上下文、轨迹、延迟和成本可设置基线与退化阈值。固定 adapter 的满分只能说明这些固定案例，没有证明开放世界效果。
</section>

<section id="project-learning-assistant-v35" data-learning-context="project-learning-assistant-v35" data-context-type="project" markdown="1">
## 智能学习助手 P5.16 v0.35

- 上一版：v0.34 让审批与长任务可持久恢复。
- 本课新增：八层 EvalCase、最早失败定位、run/request trace、默认脱敏和聚合门禁。
- 文件：`evaluation_trace.py` 与 `test_evaluation_trace.py`。
- 管理台后续只展示结构化 span、错误码、预算和引用，不展示秘密或隐式思维链。
- 下一版：完成安全矩阵、容器部署、备份、发布门禁、故障注入和版本回滚。
</section>

## 四类学习者入口

- 零基础兴趣：对照两个案例看“没检索到”和“上下文丢了”的区别。
- 有基础兴趣：增加四类故障注入并验证定位。
- 零基础求职：解释为什么只看任务成功率不够。
- 有基础求职：展示分层门禁、关联 trace、脱敏和恢复回归；不编造岗位频率。

## 完成检查

- 8 项 unittest 和固定报告通过。
- retrieval、context 和 outcome 可独立失败。
- 非白名单工具与 unsafe action 使门禁失败。
- latency/cost 超限可定位。
- trace 不记录 Authorization 或 chain-of-thought。

## 来源与版本

- 核查日期：2026-07-31。
- [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

## 下一步

进入第 6 课：安全、部署、回滚与交付证据。
