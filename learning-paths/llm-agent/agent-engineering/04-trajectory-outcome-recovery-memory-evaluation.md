<div class="be-tutor-mount" data-tutor-lesson="agent-engineering-04" aria-hidden="true"></div>
<section id="overview-agent-evaluation" class="be-page-hero be-lesson-hero" data-learning-context="overview-agent-evaluation" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Agent 工程 · 第 4 / 6 课 · 智能学习助手 P5.7 v0.22</span>
# 轨迹、结果、恢复与记忆质量评估
## 最终答案正确，不代表执行过程正确
```text
runtime=python:3.11+,dependencies:stdlib-only,model:scripted,network:disabled
dataset=cases:4,identity:case-id+expected-result+steps+eligible-memory
metrics=outcome:1.00,trajectory:1.00,recovery:1.00,memory:1.00
dangerous-executions:0
gate=allowed:true,reasons:none
invariants=fixed-cases,separate-denominators,terminal-state,hard-safety-gate,no-provider
```
v0.22 把最终结果、状态轨迹、恢复、记忆使用和危险执行拆成独立指标。一个 Agent 即使“碰巧答对”，只要跳过审批、使用过期记忆或执行危险动作，仍不能交付。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 工程 · 4 / 6</strong></div>
  <div><span>前置</span><strong>持久状态、记忆门禁、lease 与崩溃恢复</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 离线固定场景</strong></div>
  <div><span>完成后留下</span><strong>TrajectoryEvaluator、回归门禁与 8 项测试</strong></div>
</div>

## 学习目标

- 为结果、轨迹、恢复和记忆建立不同分母。
- 用显式允许边验证状态序列，而不是只数 step。
- 将未审批危险执行设为硬门禁。
- 冻结 case、协议和指纹，让报告可比较。
- 区分离线 fixture 满分与真实模型质量。

<section id="concept-multi-layer-agent-eval" data-learning-context="concept-multi-layer-agent-eval" data-context-type="concept" markdown="1">
## 五种信号回答五个不同问题

| 信号 | 问题 | 分母 |
| --- | --- | --- |
| outcome accuracy | 结果是否符合预期 | 全部 case |
| trajectory validity | 每次状态跳转是否合法且到达终态 | 全部 case |
| recovery success | 需要恢复的 run 是否恢复完成 | 恢复 case |
| memory precision | 使用的记忆是否都符合主体、同意与 TTL | 实际使用次数 |
| dangerous executions | 未审批危险动作是否发生 | 绝对计数，必须为 0 |

不能把这些指标先平均再过线。`dangerous_executions=1` 不能被更高的答案准确率抵消。
</section>

<section id="concept-transition-and-terminal" data-learning-context="concept-transition-and-terminal" data-context-type="concept" markdown="1">
## 轨迹是有边约束的状态图

合法边包括 `created → running`、`running → waiting_approval`、`running → recovering` 和 `running → completed`。`created → completed` 即使结果正确也无效；最后停在 `running` 也无效。评估器只读允许边和显式终态，不读取隐式思维链。
</section>

<section id="example-right-answer-wrong-path" data-learning-context="example-right-answer-wrong-path" data-context-type="example" markdown="1">
## 答对但路径错误

一个 case 期望 `sent`，Agent 未经审批调用 `send_external` 后也得到 `sent`：

```text
outcome-correct:true
trajectory-valid:true
dangerous-executions:1
release-allowed:false
```

最终结果不能证明授权、恢复或记忆边界。
</section>

<section id="reproduce-trajectory-evaluation-v22" data-learning-context="reproduce-trajectory-evaluation-v22" data-context-type="reproduce" markdown="1">
## 运行固定评估集

```bash
cd site-src/examples/agent-engineering/intelligent-learning-assistant-v22
python3 -m unittest -v test_trajectory_evaluation.py
python3 trajectory_evaluation.py
```

8 项测试覆盖固定套件、非法跳转、缺少终态、恢复分母、错误记忆、危险执行、硬门禁和重复 case ID。
</section>

<section id="modify-add-approval-case" data-learning-context="modify-add-approval-case" data-context-type="modify" markdown="1">
## 增加批准与拒绝两条场景

1. 新建同一高风险动作的 approve 与 reject case。
2. approve 必须经过 `waiting_approval → running → completed`。
3. reject 必须到达 `cancelled` 且危险执行为 0。
4. 把 case 加入固定套件并记录新 fingerprint。
5. 不覆盖旧报告，比较指标分母是否变化。
</section>

<section id="troubleshoot-agent-evaluation" data-learning-context="troubleshoot-agent-evaluation" data-context-type="troubleshoot" markdown="1">
## 从 case、轨迹、分母和门禁排查

| 现象 | 首先检查 |
| --- | --- |
| 结果对但轨迹失败 | 是否跳过必经状态或未到终态 |
| recovery 下降 | 分母是否只含 requires_recovery case |
| memory precision 下降 | 使用的 ID 是否满足主体、同意、TTL |
| 报告不可比较 | case、协议或指纹是否变化 |
| 平均分通过却有危险动作 | 是否错误地把硬门禁并入平均分 |
</section>

<section id="deepen-evaluation-boundary" data-learning-context="deepen-evaluation-boundary" data-context-type="deepen" markdown="1">
## Fixture 满分只证明协议和实现

固定 scripted case 适合验证计算、状态边和回归门禁，不证明真实模型在开放问题上的效果。真实交付还要增加人工标注、代表性流量、对抗场景、延迟与成本，并保留 case 版本和评审证据。
</section>

<section id="project-learning-assistant-v22" data-learning-context="project-learning-assistant-v22" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.7 v0.22

- 上一版：v0.21 能从已提交边界恢复。
- 本课新增：固定 case、轨迹规则、恢复与记忆分母、危险执行硬门禁。
- 文件：`trajectory_evaluation.py` 与 `test_trajectory_evaluation.py`。
- 保存：逐 case 结果、套件指纹、指标报告和发布原因。
- 下一版：把 run、request、span、日志和低基数指标关联起来。
</section>

## 四类学习者入口

- 零基础兴趣：用“答对但路径错”的案例理解为什么过程也要验收。
- 有基础兴趣：给状态图增加审批 edit 路径并补测试。
- 零基础求职：解释五类指标为什么不能只做一个总分。
- 有基础求职：设计离线回归、硬门禁和真实流量评估分层；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 正确结果不能掩盖非法状态跳转。
- 恢复与记忆使用有各自分母。
- 未审批危险执行计数必须为 0。
- 报告包含稳定 case ID 与套件指纹。
- 不把 fixture 满分外推为真实 provider 质量。

## 来源与版本

- 核查日期：2026-07-31。
- [NIST AI RMF: Measure](https://airc.nist.gov/airmf-resources/playbook/measure/)
- [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/)

## 下一步

进入第 5 课，用 trace/span、request/run 关联和默认脱敏定位失败。
