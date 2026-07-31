<div class="be-tutor-mount" data-tutor-lesson="agent-application-orchestration-03" aria-hidden="true"></div>
<section id="overview-task-planning" class="be-page-hero be-lesson-hero" data-learning-context="overview-task-planning" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Agent 应用编排与交付 · 第 3 / 6 课 · 智能学习助手 P5.14 v0.33</span>
# 任务拆解、子任务预算与重规划
## 计划是可验证的依赖图，不是模型愿望清单
```text
plan=revision:1,tasks:3,budget:4/12
ready=retrieve-b
failure=timeout:retryable,permission_denied:terminal
replan=completed-immutable:true,max-tasks:6,termination:explicit
```
v0.33 用严格 `Plan/Task` Schema 保存目标、动作、依赖、预算、状态和尝试次数；重规划只能替换未完成部分。
</section>
<div class="be-lesson-overview"><div><span>课程位置</span><strong>Agent 应用编排与交付 · 3 / 6</strong></div><div><span>前置</span><strong>状态图、上下文预算与工具白名单</strong></div><div><span>环境</span><strong>Python 3.11+ · 标准库 · scripted planner</strong></div><div><span>完成后留下</span><strong>严格计划、DAG 校验、重规划与 8 项测试</strong></div></div>

## 学习目标

- 用 Schema 限制动作、任务数、单任务预算和总预算。
- 验证依赖存在、ID 唯一且没有环，只调度依赖已完成的任务。
- 区分可重试故障与终止故障，让重试消耗任务预算。
- 重规划保留已完成事实，提升 revision，并保持显式终态。

<section id="concept-strict-plan-schema" data-learning-context="concept-strict-plan-schema" data-context-type="concept" markdown="1">
## Planner 输出数据，不输出可执行代码

每个 Task 只有 `task_id`、白名单 `action`、`depends_on`、正整数 `budget`、`status` 和 `attempts`。最多 6 个任务、总预算最多 12。`shell` 等未知动作立即拒绝，不能因为它出现在自然语言计划中就获得执行权。
</section>

<section id="concept-dependency-and-ready" data-learning-context="concept-dependency-and-ready" data-context-type="concept" markdown="1">
## 依赖图决定 ready set

校验器拒绝重复 ID、未知依赖和环。调度器只返回 `pending` 且所有依赖为 `completed` 的任务；并行只发生在 ready set 内。计划顺序不是依赖语义，不能仅按数组从前到后执行。
</section>

<section id="example-failure-replan" data-learning-context="example-failure-replan" data-context-type="example" markdown="1">
## 故障分类决定重试还是停止

`timeout`、`temporary_unavailable`、`lease_lost` 属于可重试，但尝试次数达到 Task budget 后仍进入 failed。`permission_denied`、Schema 错误和安全拒绝直接终止。重规划创建 revision 2，只能替换 pending/failed 任务，completed 任务及结果不可改写。
</section>

<section id="reproduce-task-planning-v33" data-learning-context="reproduce-task-planning-v33" data-context-type="reproduce" markdown="1">
## 运行计划验证和重规划
```bash
cd site-src/examples/agent-application-orchestration/intelligent-learning-assistant-v33
python3 -m unittest -v test_task_planning.py
python3 task_planning.py
```
8 项测试覆盖合法依赖、未知动作、依赖环、任务/预算上限、依赖解锁、重试耗尽、完成任务不可变和显式终态。
</section>

<section id="modify-add-parallel-budget" data-learning-context="modify-add-parallel-budget" data-context-type="modify" markdown="1">
## 增加并发预算而不改变依赖

1. 给 Plan 增加 `max_parallel=2`。
2. 从 ready set 稳定选择最多两项。
3. 高风险动作即使 ready 也先进入审批。
4. 并发失败分别记账，不整体重放已完成任务。
5. 测试依赖未满足、并发上限和完成事实不重复。
</section>

<section id="troubleshoot-task-planning" data-learning-context="troubleshoot-task-planning" data-context-type="troubleshoot" markdown="1">
## 从 Schema、依赖、预算和故障分类排查

| 现象 | 首先检查 |
| --- | --- |
| 计划无限变长 | max_tasks 与 total_budget 是否在服务端校验 |
| 子任务提前执行 | ready set 是否验证全部依赖 |
| 重试永不停止 | attempts 是否消耗 Task budget |
| 重规划重复副作用 | completed 是否不可变、工具是否幂等 |
| 权限失败仍重试 | failure code 是否错误标为 retryable |
| 所有任务 pending 但无 ready | 是否存在环或缺失依赖 |
</section>

<section id="deepen-planner-evaluation" data-learning-context="deepen-planner-evaluation" data-context-type="deepen" markdown="1">
## 计划质量不等于计划写得长

固定任务集标注必要子任务、允许动作、依赖和终止条件。评估 Schema valid rate、必要步骤覆盖、冗余任务率、依赖正确率、预算超限率、重规划成功率与副作用重复率。计划越长通常意味着更高故障面，而非更智能。
</section>

<section id="project-learning-assistant-v33" data-learning-context="project-learning-assistant-v33" data-context-type="project" markdown="1">
## 智能学习助手 P5.14 v0.33

- 上一版：v0.32 构造有预算的上下文包。
- 本课新增：严格计划 Schema、DAG 校验、ready set、故障分类、尝试预算、revision 和完成事实不可变。
- 文件：`task_planning.py` 与 `test_task_planning.py`。
- 保存：计划版本、依赖、预算、结果和失败码；不保存模型自由文本推理。
- 下一版：把高风险任务挂起给人工审批，并用 PostgreSQL lease/checkpoint 恢复。
</section>

## 四类学习者入口

- 零基础兴趣：画三节点依赖图，看为什么 compare 必须等两次 retrieve。
- 有基础兴趣：增加并发预算并验证 ready set。
- 零基础求职：解释计划 Schema、DAG 和终止条件。
- 有基础求职：展示预算耗尽、故障分类、重规划与副作用边界；不编造岗位频率。

## 完成检查

- 8 项 unittest 和固定报告通过。
- 未知动作、依赖环和超预算计划拒绝。
- 只有 ready task 可以执行。
- 重试消耗预算，权限失败不重试。
- 重规划不能改写 completed 事实。

## 来源与版本

- 核查日期：2026-07-31。
- [JSON Schema](https://json-schema.org/specification)
- [DAG scheduling overview](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html)

## 下一步

进入第 4 课：人工审批、长任务与恢复。
