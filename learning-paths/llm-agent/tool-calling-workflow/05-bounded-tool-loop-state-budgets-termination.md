<div class="be-tutor-mount" data-tutor-lesson="agent-tool-calling-05" aria-hidden="true"></div>
<section id="overview-bounded-tool-loop" class="be-page-hero be-lesson-hero" data-learning-context="overview-bounded-tool-loop" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Tool Calling 与有界工作流 · 第 5 / 6 课 · 智能学习助手 P5.5 v0.17</span>
# 有界工具循环、状态预算与显式终止
## 应用拥有循环，模型只能返回下一步事件
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
limits=max-rounds:3,max-tool-calls:4,deadline-ms:100,max-same-signature:1
completed=status:completed,rounds:2,tool-calls:1,elapsed-ms:15
branches=needs-input:needs_input,refused:refused,tool-error:tool_error
budgets=call-status:call_budget_exceeded,calls-executed:0,deadline-status:deadline_exceeded,deadline-calls:0
cycle=status:cycle_detected,calls-executed:1,repeat-second-executed:false
termination=completed,needs_input,refused,tool_error,round_budget_exceeded,call_budget_exceeded,deadline_exceeded,cycle_detected,protocol_error
trace=allowlisted-events-only,user-text:none,arguments:none,tool-data:none
invariants=application-owned-state,check-before-execute,monotonic-budgets,explicit-terminal,repeat-detection,no-unbounded-retry,no-network
```
v0.17 把 scripted model 和工具放进应用控制的状态机。轮数、调用数、虚拟 deadline 和重复语义调用都在执行前检查；成功、追问、拒绝、工具失败、超预算与循环各有可验收终态。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 工程 · 5 / 6</strong></div>
  <div><span>前置</span><strong>候选、结果关联、确认与幂等</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 虚拟时钟 · scripted model</strong></div>
  <div><span>完成后留下</span><strong>确定性状态机、九种终态、预算证据与 8 项测试</strong></div>
</div>

## 学习目标

- 让应用而不是模型拥有 `while` 循环和状态。
- 分别限制模型轮数、工具调用数和总 deadline。
- 在执行前检查预算，避免“先超支再报错”。
- 识别不同 call ID 下重复的同工具同参数语义循环。
- 为成功、追问、拒绝、失败和保护性停止定义终态。
- 让 trace 只保存允许列表事件，不记录用户文本和工具数据。

<section id="concept-application-owned-loop" data-learning-context="concept-application-owned-loop" data-context-type="concept" markdown="1">
## 模型返回事件，不拥有控制流

每轮模型只能返回 `final`、`needs_input`、`refused` 或非空 `tool_calls`。应用校验事件、更新单调预算、执行工具并决定是否进入下一轮。模型无法修改 `max_rounds` 或宣称 deadline 尚未到。

`final` 同时携带工具调用、空工具批次或复用 call ID 都进入 `protocol_error`。
</section>

<section id="concept-monotonic-budgets" data-learning-context="concept-monotonic-budgets" data-context-type="concept" markdown="1">
## 三类预算解决不同失控方式

- `max_rounds=3`：限制模型往返。
- `max_tool_calls=4`：限制实际工具副作用与成本。
- `deadline_ms=100`：限制累计时间。

计数只增不减。一次事件提出五个调用时，整个批次在工具前停止，`calls-executed:0`；事件耗时跨过 deadline 时同样不执行其中的调用。
</section>

<section id="example-cycle-detection" data-learning-context="example-cycle-detection" data-context-type="example" markdown="1">
## 换 call ID 不能躲过循环检测

第一次 `call_first` 执行 `get_learning_status(learner-001)`，第二轮换成 `call_second` 但工具和规范参数相同。状态机比较语义签名，在第二次执行前进入 `cycle_detected`，因此实际只调用一次。

参数发生受控变化时签名不同，可以继续，但仍受总轮数与调用数约束。
</section>

<section id="reproduce-bounded-loop-v17" data-learning-context="reproduce-bounded-loop-v17" data-context-type="reproduce" markdown="1">
## 运行九种终态与八项测试

```bash
cd site-src/examples/agent-tool-calling/intelligent-learning-assistant-v17
python3 -m unittest -v test_bounded_tool_loop.py
python3 bounded_tool_loop.py
```

测试覆盖工具后完成、需要输入、拒绝、工具失败、轮数/调用预算、deadline、重复调用循环和脱敏固定报告。
</section>

<section id="modify-loop-budgets" data-learning-context="modify-loop-budgets" data-context-type="modify" markdown="1">
## 把轮数预算改为 2

1. 传入 `LoopLimits(max_rounds=2)`，不要修改模型脚本。
2. 让脚本先工具、再工具、最后 final。
3. 验证第二个工具可以执行，但 final 前进入 `round_budget_exceeded`。
4. 把第二轮改成 final，确认正常完成。
5. 说明预算变化为何必须进入评估基线。
</section>

<section id="troubleshoot-loop-terminal" data-learning-context="troubleshoot-loop-terminal" data-context-type="troubleshoot" markdown="1">
## 先看终态，再看最后一条允许事件

| 终态 | 含义 |
| --- | --- |
| `completed` | final 合法返回 |
| `needs_input` / `refused` | 主动停止，不是假失败 |
| `tool_error` | 某工具返回错误终态 |
| `round_budget_exceeded` / `call_budget_exceeded` | 对应计数将越界 |
| `deadline_exceeded` | 虚拟累计耗时越界 |
| `cycle_detected` | 相同语义调用重复 |
| `protocol_error` | 模型事件违反协议 |

trace 不保存 prompt、参数或工具数据；需要深排时使用受限、分级且脱敏的诊断域。
</section>

<section id="deepen-retry-vs-loop" data-learning-context="deepen-retry-vs-loop" data-context-type="deepen" markdown="1">
## 重试策略不能藏在无限循环里

本课工具失败直接进入 `tool_error`，不自动重试。若后续只对瞬时错误重试，重试次数必须计入工具调用预算和 deadline，并保持写工具幂等。

“模型再想一轮”也消耗 round；提示词要求谨慎不能替代应用强制停止。
</section>

<section id="project-learning-assistant-v17" data-learning-context="project-learning-assistant-v17" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.5 v0.17

- 上一版：v0.16 让单次写入受授权、确认和幂等保护。
- 本课新增：应用状态机、三类预算、重复签名检测和九种显式终态。
- 文件：`bounded_tool_loop.py` 与 `test_bounded_tool_loop.py`。
- 保存：各分支结果、零额外执行证据、允许列表 trace 和 8 项测试。
- 下一版：用固定正常与对抗案例计算调用正确性、安全拒绝和预算合规门禁。
</section>

## 四类学习者入口

- 零基础兴趣：画出事件到九种终态的分支图。
- 有基础兴趣：把轮数预算改为 2，观察 final 前停止。
- 零基础求职：解释“应用拥有循环”具体意味着什么。
- 有基础求职：说明重试怎样共享调用预算、deadline 与幂等边界；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 三种预算由应用持有且单调递增。
- 超调用与超 deadline 均在工具前停止。
- 换 call ID 的相同语义调用在第二次执行前停止。
- 所有路径进入明确终态，不存在无限 `while`。
- trace 不保存用户文本、arguments 或工具数据。

## 来源与版本

- 核查日期：2026-07-26。
- [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling)
- [OpenAI Tools](https://developers.openai.com/api/docs/guides/tools)
- [OWASP LLM Excessive Agency](https://genai.owasp.org/llmrisk/llm06-excessive-agency/)

## 下一步

进入第 6 课，冻结正常与对抗案例、指标分母和回归门禁，完成整组交付。
