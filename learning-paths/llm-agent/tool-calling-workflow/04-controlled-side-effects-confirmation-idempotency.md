<div class="be-tutor-mount" data-tutor-lesson="agent-tool-calling-04" aria-hidden="true"></div>
<section id="overview-controlled-side-effects" class="be-page-hero be-lesson-hero" data-learning-context="overview-controlled-side-effects" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Tool Calling 与有界工作流 · 第 4 / 6 课 · 智能学习助手 P5.5 v0.16</span>
# 受控副作用、人工确认与幂等保护
## 模型只能提议写入，应用与人共同决定是否执行
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
tool=name:set_weekly_goal,risk:write,permission:learning_plan:write,default:deny
unconfirmed=status:error,error:confirmation_required,writes:0
confirmed=status:ok,minutes:180,replayed:false
retry=status:ok,replayed:true,writes:1
confirmation=human:true,bound-subject:true,bound-call:true,bound-tool:true,bound-arguments:true,expires:true,single-use:true
idempotency=scoped-subject-tool-key:true,same-payload:replay,different-payload:conflict
rejection=unknown-tool:true,invalid-arguments:true,forbidden:true,missing-confirmation:true,expired:true,mismatch:true,reused-grant:true,idempotency-conflict:true
logs=grant:none,idempotency-key:none,arguments:none,call-id:allowed,tool-name:allowed,status:allowed,error-code:allowed
invariants=validate-authorize-confirm-write,default-deny,write-once,replay-safe,no-model-confirmation,no-network
```
v0.16 新增 `set_weekly_goal` 合成写工具。没有权限、所有权或绑定当前动作的人类确认时零写入；网络重试复用相同幂等键和参数时返回原结果，不重复产生副作用。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 工程 · 4 / 6</strong></div>
  <div><span>前置</span><strong>严格参数、主体授权、call_id 与结果 envelope</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 合成内存存储</strong></div>
  <div><span>完成后留下</span><strong>确认授权中心、幂等写入、默认拒绝与 8 项测试</strong></div>
</div>

## 学习目标

- 按风险把只读和写入工具分开。
- 让人工确认绑定主体、call ID、工具和参数指纹。
- 让确认短期有效且只能消费一次。
- 用幂等键让同一业务请求重试不重复写入。
- 拒绝相同幂等键配不同参数。
- 证明模型文本或模型生成字段不能替代人工确认。

<section id="concept-confirmation-binding" data-learning-context="concept-confirmation-binding" data-context-type="concept" markdown="1">
## “用户确认过”必须绑定具体动作

只保存一个布尔值 `confirmed=true` 无法回答用户确认的是谁、哪个 call、哪个工具和哪组参数。确认授权中心在应用控制面生成短期 grant，绑定五项信息并单次消费；参数改一分钟也会得到 `confirmation_mismatch`。

grant 不交给模型生成，也不进入日志。演示使用运行时随机 nonce，只在内存保存短期状态。
</section>

<section id="concept-idempotent-write" data-learning-context="concept-idempotent-write" data-context-type="concept" markdown="1">
## 幂等保护解决重试，不解决授权

记录以 `主体 + 工具 + 幂等键` 为作用域，并保存规范参数指纹。相同 payload 重试返回 `replayed:true`，写计数仍是 1；同 key 不同 payload 返回 `idempotency_conflict`。

幂等键不能绕过首次授权和确认。只有已经成功完成的同请求才能安全 replay。
</section>

<section id="example-default-deny-write" data-learning-context="example-default-deny-write" data-context-type="example" markdown="1">
## 未确认与确认后的差异由写计数证明

固定场景先在 `confirmation=None` 下调用，得到 `confirmation_required` 和 `writes:0`。随后由模拟的人类控制面签发绑定 grant，首次写入 180 分钟；新 call ID 携带同一幂等键和参数重试，直接返回原业务结果，`writes:1`。
</section>

<section id="reproduce-controlled-write-v16" data-learning-context="reproduce-controlled-write-v16" data-context-type="reproduce" markdown="1">
## 运行确认、冲突和零写入测试

```bash
cd site-src/examples/agent-tool-calling/intelligent-learning-assistant-v16
python3 -m unittest -v test_controlled_write.py
python3 controlled_write.py
```

8 项测试覆盖权限/所有权、缺失/过期/错配/复用确认、首次写入、同 payload replay、不同 payload 冲突、未知工具、严格数值和报告脱敏。
</section>

<section id="modify-confirmation-ttl" data-learning-context="modify-confirmation-ttl" data-context-type="modify" markdown="1">
## 把确认有效期从 60 秒改为 10 秒

1. 仍由调用方明确传入 TTL，不读取真实墙钟。
2. 用 `now=100` 签发，在 110 时成功、111 时失败。
3. 确认边界到底采用 `>` 还是 `>=`，并写入测试。
4. 不把过期 grant 自动刷新成新确认。
5. 解释生产系统为何还需要持久化事务和审计证据。
</section>

<section id="troubleshoot-write-gates" data-learning-context="troubleshoot-write-gates" data-context-type="troubleshoot" markdown="1">
## 按拒绝层定位零写入

| 错误 | 含义 |
| --- | --- |
| `unknown_tool` / `invalid_arguments` | 工具或业务参数不合法 |
| `forbidden` | 主体无权限或不是资源所有者 |
| `confirmation_required` | 没有人类确认 |
| `confirmation_expired` / `mismatch` | 确认不再有效或绑定不同动作 |
| `invalid_confirmation` | grant 未知或已消费 |
| `idempotency_conflict` | 同 key 被用于不同参数 |

每条拒绝路径都检查 `write_count`，只看错误码不足以证明没有副作用。
</section>

<section id="deepen-atomic-idempotency-boundary" data-learning-context="deepen-atomic-idempotency-boundary" data-context-type="deepen" markdown="1">
## 本课内存原子性不能外推到生产系统

演示在单进程内先消费确认再写内存。真实数据库、队列或外部 API 需要事务、唯一约束、outbox 或供应商幂等协议，避免进程在“已写但未记结果”之间崩溃。

本课证明控制顺序与契约，不声称实现分布式 exactly-once。
</section>

<section id="project-learning-assistant-v16" data-learning-context="project-learning-assistant-v16" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.5 v0.16

- 上一版：v0.15 处理多个只读候选与局部失败。
- 本课新增：写风险、默认拒绝、绑定确认、短期单次 grant 和幂等 replay。
- 文件：`controlled_write.py` 与 `test_controlled_write.py`。
- 保存：零写入拒绝、一次写入、重试 replay、冲突和 8 项测试。
- 下一版：把模型、工具和停止条件放入有轮数、调用数与 deadline 的状态机。
</section>

## 四类学习者入口

- 零基础兴趣：用“确认单”标注它绑定的主体、动作和参数。
- 有基础兴趣：将 TTL 改为 10 秒并冻结边界测试。
- 零基础求职：解释人工确认与幂等分别解决什么问题。
- 有基础求职：说明单进程幂等和分布式 exactly-once 的差距；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 未授权、未确认、过期、错配和复用 grant 均零写入。
- 确认绑定主体、call、工具和参数指纹，且短期单次。
- 同 key 同 payload replay，同 key 不同 payload 冲突。
- 模型不能签发确认，应用默认拒绝未知动作。
- 日志不保存 grant、幂等键或参数正文。

## 来源与版本

- 核查日期：2026-07-26。
- [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP LLM Excessive Agency](https://genai.owasp.org/llmrisk/llm06-excessive-agency/)

## 下一步

进入第 5 课，用确定性状态机限制模型轮数、工具调用数、deadline 与终止分支。
