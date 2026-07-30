<div class="be-tutor-mount" data-tutor-lesson="agent-engineering-03" aria-hidden="true"></div>
<section id="overview-crash-safe-resume" class="be-page-hero be-lesson-hero" data-learning-context="overview-crash-safe-resume" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Agent 工程 · 第 3 / 6 课 · 智能学习助手 P5.6 v0.21</span>
# Lease、幂等 step 与崩溃恢复
## worker 在副作用中途崩溃，接手者从未提交边界继续
```text
runtime=python:3.11+,dependencies:stdlib-only,storage:sqlite,clock:virtual,network:disabled
lease=worker-a:acquired,worker-b:lease_busy,takeover-after-expiry:true
prepare=committed:true,side-effects:1
crash=injected_failure,committed:false,next-step:write,side-effects:1
resume=worker-b,write:committed,replay:true,next-step:none,side-effects:2
invariants=single-live-lease,expired-takeover,checkpoint-boundary,idempotent-step,atomic-side-effect,no-duplicate-effect,no-network
```
恢复不是“从头再跑一遍”。v0.21 用 lease 限制同一时刻的执行者，把 step 与副作用放入同一事务，并用幂等键证明超时重试不会重复写入。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 工程 · 3 / 6</strong></div>
  <div><span>前置</span><strong>原子 checkpoint、记忆资格门禁、SQLite 事务</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 临时 SQLite · 虚拟时钟</strong></div>
  <div><span>完成后留下</span><strong>RecoverableWorker、lease、幂等 step 与 8 项测试</strong></div>
</div>

## 学习目标

- 用带过期时间的 lease 限制同时执行者。
- 让过期 lease 可以被新 worker 接手。
- 从第一条未提交 step 恢复，而不是重放全部计划。
- 把副作用记录和 step 完成放在一个事务中。
- 用幂等键区分安全 replay 与冲突请求。

<section id="concept-lease-not-lock" data-learning-context="concept-lease-not-lock" data-context-type="concept" markdown="1">
## Lease 是会过期的所有权声明，不是永久锁

worker-a 取得 10 秒 lease 后，worker-b 得到 `lease_busy`。虚拟时钟前进 11 秒，worker-b 可以接手并获得更高 generation；旧 worker 再执行会得到 `lease_lost`。

单机 SQLite 实验能说明租约语义，但不等同于分布式共识、严格时钟同步或 exactly-once 网络副作用。
</section>

<section id="concept-commit-boundary-replay" data-learning-context="concept-commit-boundary-replay" data-context-type="concept" markdown="1">
## 只相信已提交边界

`prepare` 已提交，所以恢复时 next step 是 `write`。注入故障发生在副作用插入和 step 完成之间时，事务同时回滚，恢复仍看到 `write` 未完成。

同 step、同幂等键、同 payload 重试返回 replay；改变 payload 则 `step_conflict`，不能借重试身份改写结果。
</section>

<section id="example-two-worker-timeline" data-learning-context="example-two-worker-timeline" data-context-type="example" markdown="1">
## 两个 worker 的确定性时间线

| 时刻 | 动作 | 结果 |
| ---: | --- | --- |
| 100 | worker-a acquire | 成功 |
| 100 | worker-b acquire | `lease_busy` |
| 100 | prepare | step 与副作用同时提交 |
| 111 | worker-b acquire | 旧 lease 过期，接手成功 |
| 111 | write 注入崩溃 | 事务回滚，副作用仍为 1 |
| 111 | write resume + retry | 首次提交，随后 replay，副作用为 2 |
</section>

<section id="reproduce-recoverable-worker-v21" data-learning-context="reproduce-recoverable-worker-v21" data-context-type="reproduce" markdown="1">
## 运行租约、崩溃窗口与恢复

```bash
cd site-src/examples/agent-engineering/intelligent-learning-assistant-v21
python3 -m unittest -v test_recoverable_worker.py
python3 recoverable_worker.py
```

8 项测试覆盖互斥 lease、过期接手、旧 owner、顺序、崩溃回滚、幂等 replay、冲突 payload 和恢复入口。
</section>

<section id="modify-lease-renewal" data-learning-context="modify-lease-renewal" data-context-type="modify" markdown="1">
## 在长 step 前续租

1. worker-a 取得 10 秒 lease。
2. 时钟前进 8 秒后调用 `renew`。
3. 再前进 5 秒，证明 worker-b 仍不能接手。
4. 前进到续租后的过期点，再证明接手成功。
5. 添加旧 generation 不能执行的断言。
</section>

<section id="troubleshoot-resume-worker" data-learning-context="troubleshoot-resume-worker" data-context-type="troubleshoot" markdown="1">
## 从 lease、计划顺序和幂等身份排查

| 错误 | 首先检查 |
| --- | --- |
| `lease_busy` | 现有 owner 是否仍在 TTL 内 |
| `lease_lost` | owner 是否变化或 lease 已过期 |
| `step_out_of_order` | 是否跳过第一条未提交 step |
| `step_conflict` | 同 step 的 key 或 payload 是否变化 |
| `injected_failure` | side effect 与 step 是否都已回滚 |

不要在 lease 丢失后继续执行，也不要用新 key 掩盖同一业务动作的重试。
</section>

<section id="deepen-delivery-semantics" data-learning-context="deepen-delivery-semantics" data-context-type="deepen" markdown="1">
## 幂等不等于全世界 exactly once

本课把教学副作用和 step 放在同一 SQLite 事务，因此能证明本数据库内不重复。若副作用是邮件、支付或远端 API，需要对方接受幂等键、使用 outbox/inbox 或进行补偿；崩溃窗口不能靠一句“重试即可”消失。
</section>

<section id="project-learning-assistant-v21" data-learning-context="project-learning-assistant-v21" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.6 v0.21

- 上一版：v0.20 只把合格记忆装配进上下文。
- 本课新增：lease、虚拟时钟、幂等 step、事务副作用与 resume。
- 文件：`recoverable_worker.py` 与 `test_recoverable_worker.py`。
- 保存：两 worker 时间线、崩溃窗口、replay 证据和 8 项测试。
- 下一版：用固定场景同时评估结果、轨迹、恢复和记忆质量。
</section>

## 四类学习者入口

- 零基础兴趣：沿时间表说清谁在什么时候拥有执行权。
- 有基础兴趣：实现 lease renew 并覆盖过期边界。
- 零基础求职：解释“从头重跑”为什么会重复副作用。
- 有基础求职：讨论 lease、幂等键、outbox 与 exactly-once 边界；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- live lease 排除第二 worker，过期后允许接手。
- 旧 owner 和乱序 step 被拒绝。
- 崩溃时 step 与副作用同时回滚。
- 同 key 同 payload replay，不重复副作用。
- 外部系统的 exactly-once 不在本课证明范围内。

## 来源与版本

- 核查日期：2026-07-30。
- [SQLite transactions](https://www.sqlite.org/lang_transaction.html)
- [Python sqlite3 transaction control](https://docs.python.org/3.11/library/sqlite3.html#transaction-control)
- [AWS Builders Library: Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

## 下一步

进入第 4 课，用冻结场景和轨迹规则验证恢复正确不只看最终答案。
