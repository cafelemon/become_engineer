<div class="be-tutor-mount" data-tutor-lesson="agent-tool-calling-03" aria-hidden="true"></div>
<section id="overview-multi-call-correlation" class="be-page-hero be-lesson-hero" data-learning-context="overview-multi-call-correlation" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Tool Calling 与有界工作流 · 第 3 / 6 课 · 智能学习助手 P5.5 v0.15</span>
# 多工具调用、call_id 关联与部分失败隔离
## 批次有界，结果按身份配对，而不是猜数组位置
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
batch=calls:3,max:4,unique-call-ids:true,execution:sequential
calls=call_status:get_learning_status,call_outline:get_course_outline,call_unknown:unknown_tool
outputs=call_status:ok,call_outline:ok,call_unknown:error:unknown_tool
correlation=by-call-id:true,exactly-once:true,input-order:true,out-of-order-restored:true
partial-failure=isolated:true,successes:2,errors:1,batch-aborted:false
rejection=empty-batch:true,too-large:true,bad-call-id:true,duplicate-call-id:true,missing-output:true,extra-output:true,duplicate-output:true,name-mismatch:true
envelope=call-id:true,tool-name:true,status:true,data-or-error:true
logs=arguments:none,results:none,call-id:allowed,tool-name:allowed,status:allowed,error-code:allowed
invariants=bounded-batch,validate-before-handlers,one-output-per-call,call-id-not-index,stable-order,partial-failure-isolation,no-parallel-claim,no-network
```
v0.15 允许一次模型响应提出最多四个候选调用。每个输出必须按唯一 `call_id` 回到原调用，错一个工具不会抹掉已经成功的其他结果；本课按顺序执行，不把多调用偷换成并发。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 工程 · 3 / 6</strong></div>
  <div><span>前置</span><strong>候选协议、只读执行、结果 envelope</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 完全离线</strong></div>
  <div><span>完成后留下</span><strong>批次门禁、call_id assembler、部分失败证据与 8 项测试</strong></div>
</div>

## 学习目标

- 限制单轮候选调用数量，并在任何 handler 前拒绝坏批次。
- 把 `call_id` 当成关联身份，而不是数组下标或工具名。
- 保证每个原调用恰好有一个同名工具输出。
- 即使底层结果乱序，也恢复模型提出调用时的稳定顺序。
- 把未知工具或单个 handler 失败隔离为局部错误。
- 明确“多调用”不等于“并发执行”。

<section id="concept-call-identity" data-learning-context="concept-call-identity" data-context-type="concept" markdown="1">
## call_id 是协议身份

同一种工具可以在一轮里调用两次，数组顺序也可能因执行策略改变，所以工具名和位置都不是可靠关联键。应用先验证 `call_id` 格式与唯一性，再要求输出集合与输入集合完全相等。

`missing_output`、`unexpected_output`、`duplicate_output` 和 `tool_name_mismatch` 都是协议错误，不能静默补齐或猜测。
</section>

<section id="concept-bounded-partial-failure" data-learning-context="concept-bounded-partial-failure" data-context-type="concept" markdown="1">
## 局部失败不等于整批失败

三次调用中两个成功、一个未知工具时，assembler 保留两个成功 envelope，并把第三个标记为 `unknown_tool`。这不是忽略错误：上层仍能看到每个 call 的最终状态，同时不会重做已经成功的只读动作。

批次本身若重复 ID 或超过四个，则在 handler 前整体拒绝，因为此时无法保证可靠关联或预算。
</section>

<section id="example-out-of-order-restore" data-learning-context="example-out-of-order-restore" data-context-type="example" markdown="1">
## 结果逆序到达也按原调用顺序输出

示例先得到 `call_status` 和 `call_outline`，再故意把 outputs 逆序交给 assembler。它以 `call_id` 建表、核对集合和工具名，最后按原 calls 顺序输出。

这只证明关联逻辑能处理乱序，不代表本课启动了线程、异步任务或并发网络请求。
</section>

<section id="reproduce-multi-call-v15" data-learning-context="reproduce-multi-call-v15" data-context-type="reproduce" markdown="1">
## 运行三调用与八组协议测试

```bash
cd site-src/examples/agent-tool-calling/intelligent-learning-assistant-v15
python3 -m unittest -v test_multi_call_batch.py
python3 multi_call_batch.py
```

测试覆盖空/超大批次、重复和非法 ID、稳定顺序、乱序恢复、缺失/额外/重复输出、工具名错配、部分失败与脱敏报告。
</section>

<section id="modify-batch-budget" data-learning-context="modify-batch-budget" data-context-type="modify" markdown="1">
## 把单轮预算从 4 改为 2

1. 将 `MAX_CALLS` 改为 2。
2. 保留三调用演示，观察它在执行 handler 前被拒绝。
3. 把演示缩为两个已知工具，再确认顺序与关联通过。
4. 更新固定报告与测试，不只改常量。
5. 解释为什么预算属于应用控制面，而不是 prompt 建议。
</section>

<section id="troubleshoot-output-assembly" data-learning-context="troubleshoot-output-assembly" data-context-type="troubleshoot" markdown="1">
## 从集合不变量定位关联错误

| 错误码 | 首先检查 |
| --- | --- |
| `duplicate_call_id` | 候选批次是否复用身份 |
| `missing_output` | 是否有 handler 没生成终态 |
| `unexpected_output` | 是否混入另一批或伪造结果 |
| `duplicate_output` | 重试是否重复提交同一结果 |
| `tool_name_mismatch` | call ID 是否被错绑到另一工具 |

不要用输出长度相同就判定正确；两个结果互换工具名仍会通过长度检查。
</section>

<section id="deepen-sequential-vs-parallel" data-learning-context="deepen-sequential-vs-parallel" data-context-type="deepen" markdown="1">
## 多调用、乱序和并发是三件事

本课 executor 明确 `execution:sequential`。assembler 支持乱序，是为了让协议不依赖未来的执行策略；它没有证明并发安全、线程安全、超时取消或副作用顺序。

涉及写操作时不能因为存在多个 call 就并发执行。下一课先建立风险、确认和幂等边界，再讨论更复杂调度。
</section>

<section id="project-learning-assistant-v15" data-learning-context="project-learning-assistant-v15" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.5 v0.15

- 上一版：v0.14 只执行一个经过授权的只读工具。
- 本课新增：最多四个候选、唯一 call ID、逐调用 envelope、乱序恢复和部分失败隔离。
- 文件：`multi_call_batch.py` 与 `test_multi_call_batch.py`。
- 保存：三调用固定报告、关联拒绝证据和 8 项测试。
- 下一版：为写入动作增加风险分级、人工确认和幂等保护。
</section>

## 四类学习者入口

- 零基础兴趣：用三张写着 call ID 的卡片手工还原逆序结果。
- 有基础兴趣：把预算改为 2，验证超预算在 handler 前停止。
- 零基础求职：解释为什么工具名不能代替 call ID。
- 有基础求职：区分多调用、乱序和并发，并说明部分失败的上层策略；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 单轮最多四个 call，ID 唯一且格式受控。
- 输入与输出 call ID 集合完全相等，每个恰好一次。
- 工具名错配、缺失、额外和重复输出都被拒绝。
- 局部失败不丢弃其他成功结果。
- 日志不保存 arguments 或 result 正文。

## 来源与版本

- 核查日期：2026-07-26。
- [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling)
- [OpenAI Tools](https://developers.openai.com/api/docs/guides/tools)
- [OWASP LLM Excessive Agency](https://genai.owasp.org/llmrisk/llm06-excessive-agency/)

## 下一步

进入第 4 课，把写入工具置于默认拒绝、人工确认和幂等保护之下。
