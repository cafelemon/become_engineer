<div class="be-tutor-mount" data-tutor-lesson="agent-engineering-01" aria-hidden="true"></div>
<section id="overview-durable-run-state" class="be-page-hero be-lesson-hero" data-learning-context="overview-durable-run-state" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Agent 工程 · 第 1 / 6 课 · 智能学习助手 P5.6 v0.19</span>
# SQLite 运行状态、事件日志与原子 checkpoint
## 状态和事件同一事务提交，进程退出后仍可解释
```text
runtime=python:3.11+,dependencies:stdlib-only,storage:sqlite,network:disabled
schema=runs:true,events:true,foreign-key:true,event-id-unique:true
created=status:created,version:0,events:0
running=status:running,version:1,events:1
waiting=status:waiting_input,version:2,events:2
replay=status:waiting_input,version:2,replayed:true,events:2
concurrency=expected-version:true,stale:stale_version,current-version:2
atomicity=injected-failure:storage_failure,status:waiting_input,version:2,events:2
checkpoint=allowlist:true,next-step:true,tool-status:true,completed-step-ids:true,reasoning:false,prompt:false
invariants=event-and-state-one-transaction,monotonic-version,ordered-events,idempotent-event,conflict-detected,no-hidden-chain-of-thought,no-network
```
v0.19 将 run 当前快照和有序事件写入真实临时 SQLite。每次转移携带预期版本和唯一 event ID；状态更新与事件追加要么同时提交，要么同时回滚。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 工程 · 1 / 6</strong></div>
  <div><span>前置</span><strong>有界工具循环、事务、幂等与显式终态</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 临时 SQLite</strong></div>
  <div><span>完成后留下</span><strong>run repository、事件日志、checkpoint 门禁与 8 项测试</strong></div>
</div>

## 学习目标

- 区分当前 run snapshot 与追加式事件记录。
- 用单个 SQLite 事务原子更新事件和状态。
- 用单调 version 拒绝并发旧快照写入。
- 用 event ID 处理重复提交和冲突 payload。
- 限制状态转移与 checkpoint 字段。
- 明确持久 Agent 状态不应保存隐式思维链。

<section id="concept-snapshot-event-log" data-learning-context="concept-snapshot-event-log" data-context-type="concept" markdown="1">
## 快照回答“现在”，事件回答“怎样到这里”

`runs` 保存当前 status、version 和小型 checkpoint，读取恢复入口高效；`run_events` 以 sequence 记录每次显式业务转移，支持审计和排错。两者不是两份任意可改真相：repository 在 `BEGIN IMMEDIATE` 中先追加事件，再以预期 version 更新快照。

注入故障发生在两条 SQL 之间时，事务回滚后事件数和版本都不变。
</section>

<section id="concept-version-event-id" data-learning-context="concept-version-event-id" data-context-type="concept" markdown="1">
## version 处理竞争，event ID 处理重试

两个 worker 都读到 version 1，只有第一个能更新到 2；第二个得到 `stale_version`，不能覆盖新状态。客户端超时后用同 event ID 和同 payload 重试，则读取已提交结果并标记 `replayed:true`。

同 event ID 换 payload 返回 `event_conflict`。重复身份不能成为改写历史的入口。
</section>

<section id="example-atomic-checkpoint" data-learning-context="example-atomic-checkpoint" data-context-type="example" markdown="1">
## created → running → waiting_input

固定 run 从 version 0 开始，`run_started` 写入 version 1；工具完成后 `input_requested` 写入 version 2 和下一步 `await_goal`。重复第二个 event 不新增第三条记录。

checkpoint 只允许 next step、最后工具状态和最多 8 个已完成 step ID，不保存 prompt、原始工具数据、reasoning 或 chain of thought。
</section>

<section id="reproduce-durable-state-v19" data-learning-context="reproduce-durable-state-v19" data-context-type="reproduce" markdown="1">
## 运行真实事务、竞争与回滚

```bash
cd site-src/examples/agent-engineering/intelligent-learning-assistant-v19
python3 -m unittest -v test_durable_run_state.py
python3 durable_run_state.py
```

8 项测试覆盖创建读取、原子转移、非法状态、旧版本、重复/冲突事件、注入失败回滚、checkpoint 门禁与固定报告。
</section>

<section id="modify-transition-graph" data-learning-context="modify-transition-graph" data-context-type="modify" markdown="1">
## 增加 cancelled 终态

1. 把 `cancelled` 加入终态集合。
2. 只允许 `running` 和 `waiting_input` 转入。
3. 新增 `run_cancelled` 事件类型。
4. 验证 completed/failed 仍不能再转移。
5. 更新固定报告、测试和事件协议说明。
</section>

<section id="troubleshoot-run-state" data-learning-context="troubleshoot-run-state" data-context-type="troubleshoot" markdown="1">
## 用 version、event ID 和事务边界定位

| 错误 | 首先检查 |
| --- | --- |
| `stale_version` | 是否基于旧 snapshot 提交 |
| `event_conflict` | 重试是否改变 payload 或 run |
| `invalid_transition` | 当前 status 是否允许目标状态 |
| `invalid_checkpoint` | 是否混入 prompt、reasoning 或无界列表 |
| `storage_failure` | 事务是否完整回滚 |

不要在 stale 后盲目覆盖；重新读取状态，依据业务规则决定是否生成新事件。
</section>

<section id="deepen-state-not-reasoning" data-learning-context="deepen-state-not-reasoning" data-context-type="deepen" markdown="1">
## 持久状态不是隐藏思维链仓库

恢复需要的是显式目标、已完成 step、tool envelope、等待原因和版本，不需要模型未验证的内部推理。保存长 prompt 或 chain of thought 会扩大隐私、注入、保留和访问控制风险，也让恢复依赖不可验证文本。

本课事件只保存类型、目标状态和指纹；生产系统还需租户授权、加密、备份与保留策略。
</section>

<section id="project-learning-assistant-v19" data-learning-context="project-learning-assistant-v19" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.6 v0.19

- 上一版：v0.18 的工作流只在单次进程中运行和评估。
- 本课新增：SQLite run、事件日志、乐观版本、幂等 event 与原子 checkpoint。
- 文件：`durable_run_state.py` 与 `test_durable_run_state.py`。
- 保存：正常转移、重复、冲突、旧版本、注入故障回滚和 8 项测试。
- 下一版：区分工作记忆与持久事实，用来源、同意、TTL 和上下文预算装配输入。
</section>

## 四类学习者入口

- 零基础兴趣：画出 snapshot 和 event log 的关系。
- 有基础兴趣：增加 cancelled 终态并补齐转移测试。
- 零基础求职：解释 version 与 event ID 分别解决什么问题。
- 有基础求职：说明事件溯源、checkpoint 与隐式思维链的边界；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- snapshot 与 event 在同一事务中提交或回滚。
- version 单调递增，旧版本写入拒绝。
- event ID 同 payload replay，不同 payload 冲突。
- 状态图与 checkpoint 均为允许列表。
- prompt、reasoning 和 chain of thought 不进入持久状态。

## 来源与版本

- 核查日期：2026-07-26。
- [Python sqlite3 transaction control](https://docs.python.org/3.11/library/sqlite3.html#transaction-control)
- [SQLite transactions](https://www.sqlite.org/lang_transaction.html)
- [OWASP LLM Excessive Agency](https://genai.owasp.org/llmrisk/llm06-excessive-agency/)

## 下一步

进入第 2 课，建立有来源、可过期、按主体隔离的记忆与确定性上下文预算。
