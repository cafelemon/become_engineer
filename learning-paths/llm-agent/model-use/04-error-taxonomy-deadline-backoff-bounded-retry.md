<div class="be-tutor-mount" data-tutor-lesson="llm-use-04" aria-hidden="true"></div>
<section id="overview-bounded-recovery" class="be-page-hero be-lesson-hero" data-learning-context="overview-bounded-recovery" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">模型使用与结构化输出 · 第 4 / 6 课 · 智能学习助手 P5.1 v0.4</span>
# 错误分类、Deadline、退避与有界重试
## 重试不是再来一次，而是一台必须停止的状态机
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled,clock:virtual
taxonomy=retryable:rate_limited|unavailable|timeout
taxonomy=terminal:refused|invalid_request|authentication_failed|safety_blocked|invalid_output|missing_information
transient=status:completed,attempts:3,codes:unavailable>rate_limited>completed,elapsed_ms:250
authentication=status:failed,terminal:authentication_failed,attempts:1
deadline=status:failed,terminal:deadline_exceeded,attempts:2,elapsed_ms:200
budgets=attempt_timeout:per-call,deadline:whole-operation,max_attempts:hard-cap
backoff=deterministic-for-test,production-jitter:recommended,retry-after:provider-contract
logs=prompt:none,response:none,authorization:none,outcome-code:allowed,attempt:allowed
invariants=retry-transient-only,never-past-deadline,never-unbounded,no-rag,no-tools
```
v0.4 只让限流、暂时不可用和 timeout 进入重试。认证失败、拒绝、坏请求、Schema 失败和缺少用户事实立即停止；任何路径同时受单次 timeout、整个操作 deadline 和最大尝试次数约束。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>LLM 应用起步 · 4 / 6</strong></div>
  <div><span>前置</span><strong>归一化结果、严格结构化输出</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 离线虚拟时钟</strong></div>
  <div><span>完成后留下</span><strong>有界恢复状态机与 8 项测试</strong></div>
</div>

## 学习目标

- 先按可重试和终止错误分类，再决定是否再次调用。
- 区分单次调用 timeout 与整个用户操作 deadline。
- 用最大尝试次数和退避计划证明状态机必然停止。
- 在下一次调用前再次核对剩余时间，绝不越过 deadline。
- 解释确定性测试退避、生产 jitter 与 provider `Retry-After` 的边界。
- 只记录尝试序号和结果代码，不泄露 Prompt、回复或 Authorization。

<section id="concept-error-taxonomy" data-learning-context="concept-error-taxonomy" data-context-type="concept" markdown="1">
## 先问失败是否可能自行恢复

| 类别 | 示例 | 默认动作 |
| --- | --- | --- |
| 瞬时故障 | `rate_limited`、`unavailable`、`timeout` | 在预算内退避后重试 |
| 请求错误 | `invalid_request`、`invalid_output` | 修正请求或 Schema，当前操作停止 |
| 身份与安全 | `authentication_failed`、`safety_blocked` | 停止，不用重试掩盖配置或策略问题 |
| 产品语义 | `refused`、`missing_information` | 展示拒绝或向用户补问 |

“失败”不是一种恢复策略。把认证失败也重试三次，只会重复错误并延迟反馈。
</section>

<section id="concept-three-budgets" data-learning-context="concept-three-budgets" data-context-type="concept" markdown="1">
## 三层预算解决三个不同问题

- `attempt_timeout_ms`：单次 provider 调用最多等多久。
- `deadline_ms`：从用户发起到整个操作结束最多多久，包含调用与退避。
- `max_attempts`：无论每次多快，最多调用多少次。

每次调用使用 `min(attempt_timeout, remaining_deadline)`。timeout 可以重试，但如果它已经耗尽整体 deadline，终止码必须是 `deadline_exceeded`。
</section>

<section id="example-recovery-state-machine" data-learning-context="example-recovery-state-machine" data-context-type="example" markdown="1">
## 状态转移必须在调用前后都检查预算

```python
remaining = deadline_at - clock.now_ms
timeout = min(policy.attempt_timeout_ms, remaining)
outcome = adapter.call(timeout)

if outcome.code == "completed":
    return completed(outcome)
if outcome.code not in RETRYABLE_CODES:
    return failed(outcome.code)
if no_attempt_or_deadline_budget_left():
    return failed(budget_code)
clock.advance(backoff)
```

测试中的虚拟时钟不睡真实时间，却执行同一状态转移。它让 200 ms deadline 的证据固定、快速且无抖动。
</section>

<section id="reproduce-recovery-v04" data-learning-context="reproduce-recovery-v04" data-context-type="reproduce" markdown="1">
## 运行瞬时成功、终止失败和 deadline 三条路径

```bash
cd site-src/examples/llm-use/intelligent-learning-assistant-v04
python3 -m unittest -v test_recovery_policy.py
python3 recovery_policy.py
```

8 项测试覆盖两次瞬时失败后成功、认证失败不重试、拒绝/坏输出终止、单次 timeout、整体 deadline、退避越界、尝试预算和固定脱敏报告。脚本离线且没有真实等待。
</section>

<section id="modify-retry-policy" data-learning-context="modify-retry-policy" data-context-type="modify" markdown="1">
## 加入 provider 建议等待时间

1. 给 `AttemptOutcome` 增加可选 `retry_after_ms`。
2. 只接受非负且有上限的值，不能盲目信任响应头。
3. 选择 `max(policy_backoff, retry_after)` 或写下另一条明确策略。
4. 在 sleep 前核对它不会到达或越过 deadline。
5. 用虚拟时钟新增“小于预算”和“超过剩余预算”两项测试。

这次修改关注契约，不要求发起真实网络请求。
</section>

<section id="troubleshoot-bounded-retry" data-learning-context="troubleshoot-bounded-retry" data-context-type="troubleshoot" markdown="1">
## 重试异常时先画时间线

| 现象 | 先检查 |
| --- | --- |
| 调用次数超出上限 | 循环边界和 script exhaustion |
| 总耗时超过 deadline | 退避前是否检查剩余时间 |
| 第二次调用仍使用完整 timeout | 是否取 `min(timeout, remaining)` |
| 认证失败被重复调用 | 错误映射是否误归为瞬时故障 |
| 所有客户端同一时刻重试 | 生产环境是否加入 jitter |
| 日志能看到用户内容 | 审计记录是否只保留代码和次数 |
</section>

<section id="deepen-backoff-jitter" data-learning-context="deepen-backoff-jitter" data-context-type="deepen" markdown="1">
## 退避降低压力，jitter 避免同步重试

固定退避适合确定性单元测试，但大量生产客户端若都按 100、200、400 ms 重试，可能在同一时刻再次冲击服务。生产策略通常加入有界随机抖动，并尊重 provider 明确给出的等待契约。

jitter 不能取消 deadline，也不能让不可重试错误变成可重试。测试可注入固定随机源，而不是接受不可复现结果。
</section>

<section id="project-learning-assistant-v04" data-learning-context="project-learning-assistant-v04" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.1 v0.4

- 上一版：v0.3 能拒绝畸形结构化输出并区分补问。
- 本课新增：错误分类、单次 timeout、整体 deadline、退避和尝试预算。
- 文件：`recovery_policy.py` 与 `test_recovery_policy.py`。
- 保存：三条固定状态轨迹、8 项测试和一次 `Retry-After` 修改记录。
- 下一版：把一次完整回复改为有序 delta，并处理完成、截断与取消。
</section>

## 四类学习者入口

- 零基础兴趣：按“失败—等待—再试—停止”回放三次调用。
- 有基础兴趣：实现可注入 jitter 与 `Retry-After` 上限。
- 零基础求职：用三层预算解释为何重试不会无限执行。
- 有基础求职：比较 timeout、deadline 和尝试预算的故障边界；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过，运行时没有真实 sleep。
- 只有三类瞬时故障可重试，认证、拒绝、坏请求和缺信息均立即停止。
- 后续调用 timeout 受剩余 deadline 收窄。
- 退避若会触及 deadline，就停止而不是先睡再越界。
- 第四次脚本结果永远不能绕过三次尝试预算。
- 日志不包含 Prompt、模型原文或 Authorization。

## 来源与版本

- 核查日期：2026-07-26。
- 适用环境：Python 3.11+ 标准库；自动测试离线、虚拟时钟。
- [OpenAI Error codes](https://platform.openai.com/docs/guides/error-codes)
- [OpenAI Rate limits](https://platform.openai.com/docs/guides/rate-limits)
- [Python time](https://docs.python.org/3.11/library/time.html)

## 下一步

进入第 5 课，用有序流事件组装内容，处理 finish reason、乱序、重复和取消。
