<div class="be-tutor-mount" data-tutor-lesson="agent-engineering-05" aria-hidden="true"></div>
<section id="overview-agent-observability" class="be-page-hero be-lesson-hero" data-learning-context="overview-agent-observability" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Agent 工程 · 第 5 / 6 课 · 智能学习助手 P5.8 v0.23</span>
# Trace、Span、关联指标与默认脱敏
## 能沿一次 run 找到证据，不等于记录所有原文
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled,export:json
correlation=trace:trace-001,spans:3,logs:1
metrics=series:1,route-template:true,status-class:true
redaction=secret-present:false,prompt:false,tool-output:false
sampling=errors:always,success:deterministic
invariants=run-request-trace,parents,low-cardinality,allowlist,default-redaction
```
v0.23 让 request、run、trace 和 span 可关联，同时限制字段、指标基数和采样。排错需要结构证据，不需要把 Authorization、Prompt、查询、记忆或工具原文复制进遥测系统。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 工程 · 5 / 6</strong></div>
  <div><span>前置</span><strong>run 状态、轨迹评估、日志脱敏边界</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 离线 JSON 导出</strong></div>
  <div><span>完成后留下</span><strong>Telemetry、低基数指标、采样与 8 项测试</strong></div>
</div>

## 学习目标

- 建立 request → run → trace → span 的关联。
- 用 parent span 表示检索、工具和恢复层级。
- 指标只使用 route template、status class 等低基数维度。
- 错误始终采样，成功按确定性比例采样。
- 用允许字段表和默认脱敏保护秘密与业务正文。

<section id="concept-trace-span-run" data-learning-context="concept-trace-span-run" data-context-type="concept" markdown="1">
## request、run、trace 和 span 各有身份

request ID 标识一次入口请求；run ID 标识可跨请求恢复的业务运行；trace ID 标识一次因果链；span ID 标识链中的检索、工具、审批或恢复阶段。恢复请求可以产生新 trace，但仍关联同一 run。不要把这些 ID 混成一个字段。
</section>

<section id="concept-low-cardinality-redaction" data-learning-context="concept-low-cardinality-redaction" data-context-type="concept" markdown="1">
## 指标维度受控，日志字段默认拒绝

HTTP 指标使用 `/api/runs/{run_id}` 和 `2xx/4xx/5xx`，不使用真实 run ID、用户问题或错误全文作为 label。日志和 span attributes 采用允许字段表；Authorization、Cookie、CSRF、Prompt、query、memory text 与 tool output 默认写为 `[REDACTED]` 或完全不保存。
</section>

<section id="example-one-run-three-spans" data-learning-context="example-one-run-three-spans" data-context-type="example" markdown="1">
## 一条 run 的三段证据

```text
agent.run span-root
├── retrieve span-retrieve
└── tool span-tool
```

三段共享 trace ID，子段携带 parent span ID；日志只带 run ID、request ID、step kind 和稳定错误码。管理台可由 ID 查运行结构，但不能展示隐式思维链。
</section>

<section id="reproduce-agent-telemetry-v23" data-learning-context="reproduce-agent-telemetry-v23" data-context-type="reproduce" markdown="1">
## 运行关联、指标、采样和脱敏

```bash
cd site-src/examples/agent-engineering/intelligent-learning-assistant-v23
python3 -m unittest -v test_agent_telemetry.py
python3 agent_telemetry.py
```

8 项测试覆盖父子 span、run/request 关联、敏感字段、未知高基数字段、指标聚合、错误采样、成功采样和固定导出。
</section>

<section id="modify-add-recovery-span" data-learning-context="modify-add-recovery-span" data-context-type="modify" markdown="1">
## 给恢复请求增加新 trace

1. 第一次请求建立 run 与 trace-A。
2. 崩溃后第二次请求建立 trace-B，但复用 run ID。
3. 新增 `recover` span，并记录稳定 `error_code`。
4. 证明 trace-A 与 trace-B 能按 run 查询。
5. 确认 checkpoint 与 Prompt 原文均未进入导出。
</section>

<section id="troubleshoot-agent-observability" data-learning-context="troubleshoot-agent-observability" data-context-type="troubleshoot" markdown="1">
## 从关联、基数、采样和脱敏排查

| 现象 | 首先检查 |
| --- | --- |
| 找不到恢复前轨迹 | 是否只按 trace 查而没有 run ID |
| 指标序列爆炸 | label 是否包含真实 ID、query 或错误全文 |
| 错误现场缺失 | error 是否错误套用成功采样率 |
| 日志出现凭据 | 是否绕过统一 redact/allowlist |
| 管理台显示思维链 | 是否把模型私有推理误当业务事件 |
</section>

<section id="deepen-observability-boundary" data-learning-context="deepen-observability-boundary" data-context-type="deepen" markdown="1">
## 可观测性是证据预算

更多数据并不自动带来更好诊断。保留业务状态、工具名、稳定错误码、时间和关联 ID 通常足够；原始正文应进入受控短期调试包，而不是长期普通日志。采样策略、字段表和保留期都属于发布契约。
</section>

<section id="project-learning-assistant-v23" data-learning-context="project-learning-assistant-v23" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.8 v0.23

- 上一版：v0.22 能从五类信号判断是否退化。
- 本课新增：trace/span、run/request 关联、低基数指标、采样和默认脱敏。
- 文件：`agent_telemetry.py` 与 `test_agent_telemetry.py`。
- 保存：脱敏 JSON trace、结构化日志与聚合指标。
- 下一版：用注入、记忆投毒、工具污染和跨主体测试建立安全发布门禁。
</section>

## 四类学习者入口

- 零基础兴趣：沿三段 span 图找一次运行发生了什么。
- 有基础兴趣：增加恢复 trace，并按 run 聚合。
- 零基础求职：解释日志、指标和 trace 的职责差异。
- 有基础求职：讨论高基数、采样、保留期和脱敏失败；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- request、run、trace、span 身份和父子关系清楚。
- 指标不使用真实主体、run 或 query 作标签。
- 错误始终采样，成功采样可复现。
- 敏感值和业务正文不进入普通导出。
- 不记录或展示隐式思维链。

## 来源与版本

- 核查日期：2026-07-31。
- [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

## 下一步

进入第 6 课，用攻击 fixture 与隔离断言封住发布路径。
