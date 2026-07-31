<div class="be-tutor-mount" data-tutor-lesson="agent-application-orchestration-04" aria-hidden="true"></div>
<section id="overview-approval-recovery" class="be-page-hero be-lesson-hero" data-learning-context="overview-approval-recovery" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Agent 应用编排与交付 · 第 4 / 6 课 · 智能学习助手 P5.15 v0.34</span>
# 人工审批、长任务与恢复
## 高风险动作先持久化意图，再等待人决定
```text
approval=approve:true,edit:true,reject:true,cross-subject:hidden
run=checkpoint:cursor-1,resumed:true,state:running
effect=idempotent:true,key:publish:lesson:1
storage=postgresql:true,lease:true,mock:false
```
v0.34 用真实 PostgreSQL 保存 run、step、approval 和 effect receipt，覆盖 approve/edit/reject、中断、lease、checkpoint、恢复和幂等副作用。
</section>
<div class="be-lesson-overview"><div><span>课程位置</span><strong>Agent 应用编排与交付 · 4 / 6</strong></div><div><span>前置</span><strong>计划、审批边界、事务与 Agent 恢复</strong></div><div><span>环境</span><strong>Python 3.11 · psycopg 3 · PostgreSQL 16 容器</strong></div><div><span>完成后留下</span><strong>RunStore、4 张表、真实 8 项测试</strong></div></div>

## 学习目标

- 在执行前保存高风险动作、目标和参数，进入 waiting_approval。
- 区分 approve、edit 和 reject，审批资源跨主体统一不可见。
- 用 lease 防止两个 worker 同时推进，用 checkpoint 原子保存进度。
- 用 effect key 让崩溃后的重复执行返回首次 receipt。

<section id="concept-durable-interrupt" data-learning-context="concept-durable-interrupt" data-context-type="concept" markdown="1">
## Interrupt 是持久化状态，不是阻塞线程

`request_approval` 在同一事务写入审批请求并把 run 切到 `waiting_approval`，随后释放 lease。进程可以退出；用户稍后审批时，通过 run ID 与 checkpoint 恢复。不能让 Web 请求或 Python 线程一直等待人工点击。
</section>

<section id="concept-approval-decisions" data-learning-context="concept-approval-decisions" data-context-type="concept" markdown="1">
## approve、edit、reject 有不同语义

- approve：接受持久化的 proposed payload。
- edit：审批人提交替代 payload，保留原提议和最终决定以供审计。
- reject：run 进入 rejected，不允许恢复执行。

只有 approval.owner_id 匹配的主体可决定；他人看到 404 式不可见结果。重复决定返回错误，不能覆盖首次人工结论。
</section>

<section id="example-lease-checkpoint-effect" data-learning-context="example-lease-checkpoint-effect" data-context-type="example" markdown="1">
## lease、checkpoint 和幂等键共同恢复

worker-a 取得 30 秒 lease，完成 retrieve 后在一个事务写 `run_steps` 和 checkpoint。审批期间 lease 为空。通过后 worker-b 可重新取得 lease，从 cursor 1 继续。`publish:lesson:1` 第一次写 effect receipt；崩溃重放同一 key 时返回首次结果，不再发布第二次。
</section>

<section id="reproduce-approval-recovery-v34" data-learning-context="reproduce-approval-recovery-v34" data-context-type="reproduce" markdown="1">
## 在真实 PostgreSQL 运行恢复实验
```bash
cd site-src/examples/agent-application-orchestration/intelligent-learning-assistant-v34
docker compose up -d postgres
# 从 docker compose ps 取得随机回环端口后：
AGENT_POSTGRES_URL=postgresql://agent:agent-local-only@127.0.0.1:PORT/agent_jobs \
  ../../../../.venv/bin/python -m unittest -v test_long_run_store.py
```
8 项测试覆盖单 lease、过期接管、原子 checkpoint、错误 worker、approve 恢复、edit payload、reject/主体隔离和 effect 幂等；测试拒绝在无数据库时假装通过。
</section>

<section id="modify-add-approval-expiry" data-learning-context="modify-add-approval-expiry" data-context-type="modify" markdown="1">
## 增加审批过期与重新提议

1. approval 增加 `expires_at`。
2. 过期决定被拒绝，run 进入 `approval_expired`。
3. 重新提议创建新 approval ID，不复用旧记录。
4. 原 proposed payload 和审计事件保持不可变。
5. 用固定时钟测试边界时刻、重复请求和旧链接。
</section>

<section id="troubleshoot-approval-recovery" data-learning-context="troubleshoot-approval-recovery" data-context-type="troubleshoot" markdown="1">
## 从审批、lease、checkpoint 和 receipt 排查

| 现象 | 首先检查 |
| --- | --- |
| 两个 worker 同时执行 | lease 更新是否原子且检查到期时间 |
| 审批后从头开始 | checkpoint 是否与 step 在同一事务 |
| 编辑后仍用旧参数 | 是否读取 decided_payload |
| 拒绝后还能恢复 | resume 是否只接受 approved |
| 崩溃后重复发送 | effect_key 是否在外部语义上稳定 |
| 他人能看到审批 | owner 条件是否在查询阶段执行 |
</section>

<section id="deepen-exactly-once-boundary" data-learning-context="deepen-exactly-once-boundary" data-context-type="deepen" markdown="1">
## 数据库 receipt 不自动等于外部 exactly-once

本课证明同一 effect key 在本数据库只产生一个 receipt。若外部服务不支持幂等键，数据库提交与外部调用仍可能处于不一致窗口，需要 outbox、状态查询或补偿。不要把单库唯一约束外推成端到端 exactly-once。
</section>

<section id="project-learning-assistant-v34" data-learning-context="project-learning-assistant-v34" data-context-type="project" markdown="1">
## 智能学习助手 P5.15 v0.34

- 上一版：v0.33 产出带依赖和预算的计划。
- 本课新增：真实 PostgreSQL `agent_runs`、`run_steps`、`approval_requests`、`effect_receipts`，以及 lease、checkpoint、三种审批与恢复。
- 文件：`long_run_store.py`、`test_long_run_store.py`、`compose.yml`。
- 保存：结构化提议、决定、主体、checkpoint、lease 和 receipt；不保存 Authorization 或隐式思维链。
- 下一版：把任务、检索、工具、上下文、轨迹、延迟和成本放入同一评估与故障定位台。
</section>

## 四类学习者入口

- 零基础兴趣：按“提议 → 暂停 → 批准 → 恢复”观察状态变化。
- 有基础兴趣：增加审批过期与重新提议。
- 零基础求职：解释为什么人工审批不能靠线程等待。
- 有基础求职：展示真实事务、lease 竞争、恢复与幂等 receipt；不编造岗位频率。

## 完成检查

- 真实 PostgreSQL 容器中的 8 项测试和固定报告通过。
- approve/edit/reject 与主体隔离都有回归。
- 只有当前 lease owner 可写 checkpoint。
- checkpoint 与完成 step 原子提交。
- 同一 effect key 只保留首次结果。

## 来源与版本

- 核查日期：2026-07-31。
- [PostgreSQL transactions](https://www.postgresql.org/docs/16/tutorial-transactions.html)
- [PostgreSQL explicit locking](https://www.postgresql.org/docs/16/explicit-locking.html)

## 下一步

进入第 5 课：端到端评估、轨迹与故障定位。
