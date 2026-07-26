<div class="be-tutor-mount" data-tutor-lesson="agent-tool-calling-06" aria-hidden="true"></div>
<section id="overview-tool-workflow-eval" class="be-page-hero be-lesson-hero" data-learning-context="overview-tool-workflow-eval" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Tool Calling 与有界工作流 · 第 6 / 6 课 · 智能学习助手 P5.5 v0.18</span>
# 固定对抗评估、预算指标与回归交付
## 先冻结协议和分母，再决定工作流能否开放
```text
runtime=python:3.11+,dependencies:stdlib-only,model:scripted,network:disabled
protocol=version:1,cases:8,fingerprint:4f12e1c5f3ba,limits-frozen:true
case-mix=benign:2,safety:3,budget:3,unknown-tool:true,cross-owner:true,unconfirmed-write:true,cycle:true,call-budget:true,deadline:true
metrics=outcome-accuracy:1.00,benign-outcome:1.00,call-accounting:1.00
safety=rejection-accuracy:1.00,unsafe-executions:0
budgets=compliance:1.00,zero-extra-execution:true
gate=passed:true,reason:passed,same-protocol-required:true,no-regression:true
artifacts=case-manifest:true,per-case-results:true,aggregate-report:true,baseline-comparison:true
logs=prompts:none,arguments:none,tool-data:none,secrets:none,case-id:allowed,status:allowed,counts:allowed
boundaries=eight-cases-not-production-quality,scripted-model-not-provider-quality,no-real-side-effects,no-network
```
v0.18 冻结 8 个正常、安全和预算案例及全部限制。报告同时保留逐例结果和聚合指标；协议指纹不同不可比较，任何指标退化或一次不安全执行都会阻止交付。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 工程 · 6 / 6</strong></div>
  <div><span>前置</span><strong>工具协议、授权、副作用与有界状态机</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · scripted model · 完全离线</strong></div>
  <div><span>完成后留下</span><strong>固定案例、指标报告、回归门禁与 8 项测试</strong></div>
</div>

## 学习目标

- 冻结案例、期望、预算和指纹，防止测试随实现漂移。
- 将正常结果、安全拒绝和预算停止分开统计。
- 精确核对模型轮次之外的工具调用与 handler 次数。
- 把不安全执行设为必须为零的硬门禁。
- 只比较同协议和同案例数的基线与候选。
- 保存可复核证据，同时对 prompt、参数和工具数据脱敏。

<section id="concept-frozen-eval-protocol" data-learning-context="concept-frozen-eval-protocol" data-context-type="concept" markdown="1">
## 评估协议也需要身份

案例 manifest 包含事件、期望终态、预期工具/handler 次数、安全/预算分组和循环限制，再用规范 JSON 生成 SHA-256 指纹。案例顺序变化不改变指纹，期望调用数或内容变化会形成新协议。

指纹不同意味着题目或分母变了，不能把分数差解释为代码变好或变坏。
</section>

<section id="concept-separated-metrics" data-learning-context="concept-separated-metrics" data-context-type="concept" markdown="1">
## 五个指标不能揉成一个平均分

- 全部 8 例：outcome accuracy、call accounting。
- 2 个正常例：benign outcome。
- 3 个安全例：rejection accuracy 与 unsafe executions。
- 3 个预算例：budget compliance。

每个分母非空且由 manifest 固定。不安全执行为 0 是硬约束，不能用正常案例高分抵消。
</section>

<section id="example-adversarial-cases" data-learning-context="example-adversarial-cases" data-context-type="example" markdown="1">
## 三类对抗失败都不触达危险 handler

未知 Shell 工具、读取另一学习者和未确认写入分别返回受控错误。循环案例只执行第一次安全读取，五调用与超 deadline 案例为零工具执行。逐例结果记录终态、工具数与 handler 数，证明“拒绝”不只是最终文案。
</section>

<section id="reproduce-tool-eval-v18" data-learning-context="reproduce-tool-eval-v18" data-context-type="reproduce" markdown="1">
## 运行固定评估与退化门禁

```bash
cd site-src/examples/agent-tool-calling/intelligent-learning-assistant-v18
python3 -m unittest -v test_tool_workflow_eval.py
python3 tool_workflow_eval.py
```

8 项测试覆盖指纹稳定/敏感性、逐例结果、正常分母、安全拒绝、预算合规、指标退化、协议不兼容和报告脱敏。
</section>

<section id="modify-eval-case" data-learning-context="modify-eval-case" data-context-type="modify" markdown="1">
## 增加“确认已过期”安全案例

1. 不修改已有 8 例，追加新 case ID。
2. 期望 `tool_error`、一次候选调用、零 handler。
3. 将它计入 safety 分母，并重新生成 protocol fingerprint。
4. 建立同一新协议的 baseline 后才比较候选。
5. 解释为什么不能沿用旧 3/3 安全分数。
</section>

<section id="troubleshoot-eval-gate" data-learning-context="troubleshoot-eval-gate" data-context-type="troubleshoot" markdown="1">
## 门禁失败先区分“不可比”与“退化”

| 原因 | 处理 |
| --- | --- |
| `incompatible_protocol` | 核对 fingerprint、case count 和限制 |
| `unsafe_execution` | 立即阻止交付并定位实际 handler |
| `regressed:<metric>` | 查看对应分组逐例结果 |
| `quality_gate_failed` | 某硬阈值未达到 |
| `passed` | 只说明当前固定协议通过 |

不要在看到失败后删除难例、改期望或缩小分母；那是新协议，不是修复。
</section>

<section id="deepen-eval-boundary" data-learning-context="deepen-eval-boundary" data-context-type="deepen" markdown="1">
## 8 例满分不是生产质量

scripted model 只让控制流确定性可测，没有覆盖真实 provider 的参数质量、延迟、成本、漂移和内容风险；内存写入也没有覆盖外部副作用和崩溃恢复。

本课交付的是可扩展评估骨架与诚实边界。下一模块才继续建设状态持久化、记忆、上下文恢复、可观测性和更广安全评估。
</section>

<section id="project-learning-assistant-v18" data-learning-context="project-learning-assistant-v18" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.5 v0.18

- 上一版：v0.17 已能在九种终态中确定性停止。
- 本课新增：8 例冻结 manifest、协议指纹、五项指标、零危险执行和回归门禁。
- 文件：`tool_workflow_eval.py` 与 `test_tool_workflow_eval.py`。
- 保存：案例 manifest、逐例结果、聚合报告、基线比较和 8 项测试。
- 整组产出：v0.13–v0.18、48 项测试、60 卡、120 问与组级验收证据。
</section>

## 四类学习者入口

- 零基础兴趣：把 8 个案例分到正常、安全和预算三组。
- 有基础兴趣：追加确认过期案例并生成新指纹。
- 零基础求职：解释为什么“零危险执行”不能被平均分抵消。
- 有基础求职：解释协议兼容、分组指标和真实 provider 评估缺口；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 8 个案例、限制、期望和分组有稳定协议指纹。
- 五项指标各自使用明确非空分母。
- 三个安全案例零危险 handler，三个预算案例零额外执行。
- 同协议无退化才通过，协议不同直接不可比。
- 报告不保存 prompt、arguments、工具数据或秘密。

## 来源与版本

- 核查日期：2026-07-26。
- [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling)
- [OpenAI Tools](https://developers.openai.com/api/docs/guides/tools)
- [OWASP LLM Excessive Agency](https://genai.owasp.org/llmrisk/llm06-excessive-agency/)

## 下一步

进入 Agent 工程模块，继续建设持久状态、记忆与上下文、恢复、评估、可观测性和安全。
