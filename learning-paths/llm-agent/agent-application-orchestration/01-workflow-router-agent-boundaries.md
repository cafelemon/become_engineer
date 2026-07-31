<div class="be-tutor-mount" data-tutor-lesson="agent-application-orchestration-01" aria-hidden="true"></div>
<section id="overview-orchestration-boundaries" class="be-page-hero be-lesson-hero" data-learning-context="overview-orchestration-boundaries" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Agent 应用编排与交付 · 第 1 / 6 课 · 智能学习助手 P5.12 v0.31</span>
# 工作流、路由器与 Agent 的边界
## 自由度只给真正需要决策的节点
```text
workflow=terminal:completed,steps:3
router=terminal:completed,tool-selected:true
agent=terminal:completed,steps:4,bounded:true
boundary=state-schema:strict,model-transition:false,unknown-action:default-deny
```
v0.31 用同一状态 Schema 比较确定性工作流、受限路由器和开放循环。模型只能提出受 Schema 限制的选择，应用验证并执行状态迁移。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 应用编排与交付 · 1 / 6</strong></div>
  <div><span>前置</span><strong>RAG 应用、Tool Calling、Agent 状态与恢复</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · scripted choices</strong></div>
  <div><span>完成后留下</span><strong>严格状态图、三种模式与 8 项测试</strong></div>
</div>

## 学习目标

- 根据任务不确定性选择 workflow、router 或 agent，而不是默认 Agent。
- 用显式状态和合法迁移连接授权、检索、工具与回答。
- 对未知动作默认拒绝，对空证据拒答，对开放循环设置步数预算。
- 让模型输出选择数据，不能直接改变运行状态或执行工具。

<section id="concept-three-control-modes" data-learning-context="concept-three-control-modes" data-context-type="concept" markdown="1">
## 三种控制模式是自由度阶梯

| 模式 | 谁决定下一步 | 适合场景 |
| --- | --- | --- |
| workflow | 代码中的固定图 | 登录、上传、检索后回答等稳定流程 |
| router | 模型/规则从白名单分支选择 | 查询类型、只读诊断工具路由 |
| agent | 模型在有界循环中多次选择 | 步骤事先未知的调查任务 |

可预测任务优先 workflow。路由器只决定已注册分支；Agent 也必须受最大步数、动作权限、终态和副作用审批约束。
</section>

<section id="concept-state-transition-owner" data-learning-context="concept-state-transition-owner" data-context-type="concept" markdown="1">
## 状态迁移权属于应用

`Run.transition(expected, target)` 同时校验当前状态和步数预算。模型返回 `inspect` 只是建议，应用把它映射到允许的 `retrieved → inspected`；`invent_tool` 没有映射，运行进入 `failed`。这样 trace 中的状态是系统事实，不是模型叙述。

四个终态为 `completed`、`refused`、`failed`、`budget_exhausted`，每次运行都必须明确结束。
</section>

<section id="example-one-request-three-modes" data-learning-context="example-one-request-three-modes" data-context-type="example" markdown="1">
## 同一应用中的三条路线

```text
answer → authorize → retrieve → answer → completed
diagnostic → authorize → retrieve → select registered tool → answer → completed
open investigation → authorize → retrieve → inspect ... → answer or budget_exhausted
```

授权在检索之前。任一模式没有证据都进入 `refused`，不能因为 Agent 更“聪明”就绕过证据门槛。
</section>

<section id="reproduce-workflow-graph-v31" data-learning-context="reproduce-workflow-graph-v31" data-context-type="reproduce" markdown="1">
## 运行三种模式和非法路径

```bash
cd site-src/examples/agent-application-orchestration/intelligent-learning-assistant-v31
python3 -m unittest -v test_workflow_graph.py
python3 workflow_graph.py
```

8 项测试覆盖确定性工作流、工具路由、Agent 选择、默认拒绝、空证据、非法迁移、未知选择和步数耗尽。
</section>

<section id="modify-add-clarification-state" data-learning-context="modify-add-clarification-state" data-context-type="modify" markdown="1">
## 增加需要用户澄清的终态

1. 增加 `needs_input` 终态，不复用 `failed`。
2. 只有缺少会改变执行路线的必要字段才能进入。
3. 保存缺少字段名，不保存模型自由文本推理。
4. 用户补充后创建新事件并从 checkpoint 恢复。
5. 测试无关问题不会被误判为需要输入。
</section>

<section id="troubleshoot-orchestration-boundaries" data-learning-context="troubleshoot-orchestration-boundaries" data-context-type="troubleshoot" markdown="1">
## 从模式、迁移、权限和终态排查

| 现象 | 首先检查 |
| --- | --- |
| 简单回答跑了很多步 | 是否错误使用 Agent 而非 workflow |
| 模型调用未注册工具 | 选择是否经过白名单映射 |
| 运行卡住没有结果 | 是否缺少显式终态或步数预算 |
| 拒绝后仍出现候选 | 授权是否晚于检索 |
| trace 状态与代码不符 | 是否让模型直接写状态 |
| 重试重复执行工具 | 副作用是否有幂等键与审批边界 |
</section>

<section id="deepen-framework-mapping" data-learning-context="deepen-framework-mapping" data-context-type="deepen" markdown="1">
## 先理解图，再选择框架

框架通常提供 node、edge、state、checkpoint 和 interrupt，但不会替你定义授权、终态、预算或幂等语义。先让自建图的 8 项测试通过，后续才能判断框架映射是否保持相同不变量，而不是被 API 名称牵着走。
</section>

<section id="project-learning-assistant-v31" data-learning-context="project-learning-assistant-v31" data-context-type="project" markdown="1">
## 智能学习助手 P5.12 v0.31

- 上一版：v0.30 交付文档管理、检索和聊天应用。
- 本课新增：`Request`、`Run`、严格 transition、三种控制模式、四个终态和步数预算。
- 文件：`workflow_graph.py` 与 `test_workflow_graph.py`。
- 保存：模式、状态事件、选择、终态和预算消耗；不保存隐式思维链。
- 下一版：建立会话窗口、结构化摘要、用户事实和知识检索的上下文管理。
</section>

## 四类学习者入口

- 零基础兴趣：按三条文字路线理解为什么简单任务不需要 Agent。
- 有基础兴趣：增加 `needs_input` 并补状态迁移测试。
- 零基础求职：解释 workflow、router 与 Agent 的选择标准。
- 有基础求职：展示默认拒绝、非法迁移、预算耗尽和 trace 证据；不编造岗位频率。

## 完成检查

- 8 项 unittest 和固定报告通过。
- 所有状态迁移由应用校验。
- 未知动作在检索前拒绝。
- Agent 循环有最大步数和显式终态。
- 固定工作流不会因模型输出改变图结构。

## 来源与版本

- 核查日期：2026-07-31。
- [LangGraph workflows and agents](https://langchain-ai.github.io/langgraph/concepts/workflows/)
- [OWASP Agentic AI Threats and Mitigations](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/)

## 下一步

进入第 2 课，管理会话上下文、摘要和记忆召回。
