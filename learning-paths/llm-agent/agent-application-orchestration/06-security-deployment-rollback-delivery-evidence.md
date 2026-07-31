<div class="be-tutor-mount" data-tutor-lesson="agent-application-orchestration-06" aria-hidden="true"></div>
<section id="overview-agent-delivery" class="be-page-hero be-lesson-hero" data-learning-context="overview-agent-delivery" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Agent 应用编排与交付 · 第 6 / 6 课 · 智能学习助手 P5.17 v0.36</span>
# 安全、部署、回滚与交付证据
## 安全门禁、可恢复数据与可回退版本一起交付
```text
security=default-deny:true,acl-before-data:true,injection-isolated:true,secrets-redacted:true
release=gate:true,backup-restored:true,faults:5
rollback=application:true,schema-compatible:true
delivery=container:true,non-root:true,health:true,metrics:true,evidence:true
framework=langgraph:optional,required:false
```
v0.36 完成权限矩阵、注入隔离、跨主体保护、发布门禁、容器、健康、指标、备份恢复、故障注入和兼容回滚，并交付运行/审批/脱敏 trace 控制台。
</section>
<div class="be-lesson-overview"><div><span>课程位置</span><strong>Agent 应用编排与交付 · 6 / 6</strong></div><div><span>前置</span><strong>RAG 应用、编排、持久恢复和八层评估</strong></div><div><span>环境</span><strong>Python 3.11 · FastAPI · TypeScript · Docker/PostgreSQL</strong></div><div><span>完成后留下</span><strong>交付控制台、门禁、容器与 10 项测试</strong></div></div>

## 学习目标

- 让每个主体、动作、资源和结果进入默认拒绝权限矩阵。
- 将文档、记忆和工具结果都视为不可信数据，防止注入升级为指令。
- 用测试、迁移、备份恢复、健康和零容忍安全指标共同决定发布。
- 只在旧应用健康且 schema 兼容时回滚；否则明确阻止并走前向修复。

<section id="concept-security-matrix" data-learning-context="concept-security-matrix" data-context-type="concept" markdown="1">
## 权限与数据边界贯穿完整 Agent 流水线

learner 可创建和读取自己的 run、决定自己的 approval；operator 只拥有明确诊断动作。未声明动作默认拒绝。owner/ACL 在读取 run、文档、记忆、候选和审批前执行，跨主体数据不能进入检索、重排、上下文、工具参数、日志或 trace。
</section>

<section id="concept-release-rollback-gates" data-learning-context="concept-release-rollback-gates" data-context-type="concept" markdown="1">
## 发布与回滚是两个独立判断

发布要求测试、迁移、独立数据库恢复和 readiness 全部通过，同时跨主体泄露、危险执行、引用失真和重复副作用均为 0。应用回滚还要求上一镜像健康、数据库采用 expand/contract 且旧版本能读当前 schema。破坏性 contract 已执行时，不能假装“一键回滚”。
</section>

<section id="example-delivery-console" data-learning-context="example-delivery-console" data-context-type="example" markdown="1">
## 控制台只展示行动证据

```text
POST /api/agent-runs
GET  /api/agent-runs/{run_id}
POST /api/approval-requests/{approval_id}/decision
GET  /health/live | /health/ready | /metrics
```

页面展示 run 状态、结构化 step、注入分类和审批结果，不显示 Authorization、Cookie、原始 Prompt 或 chain-of-thought。无 JavaScript 时仍能读取 API 与启动说明。
</section>

<section id="reproduce-agent-delivery-v36" data-learning-context="reproduce-agent-delivery-v36" data-context-type="reproduce" markdown="1">
## 运行安全、API、前端和容器
```bash
cd site-src/examples/agent-application-orchestration/intelligent-learning-assistant-v36
../../../../.venv/bin/python -m unittest -v test_delivery.py
../../web-engineering/learning-dashboard-v12/node_modules/.bin/tsc -p tsconfig.json
docker compose up -d --build app
```
10 项测试覆盖默认拒绝、跨主体 404、提示注入隔离、秘密/思维链脱敏、发布证据、安全硬门禁、schema 回滚阻断、五类故障恢复、运行审批 API 和健康指标页面。
</section>

<section id="modify-add-version-drill" data-learning-context="modify-add-version-drill" data-context-type="modify" markdown="1">
## 做一次 v0.35 → v0.36 → v0.35 回滚演练

1. 保存两版镜像 digest 和迁移版本。
2. 用独立数据库验证备份，不覆盖活动库。
3. 发布 v0.36 并检查 ready、指标和固定 E2E。
4. 注入 worker crash，验证 checkpoint 恢复且 effect 不重复。
5. 只有 compatibility gate 通过才切回 v0.35，并记录时间线与结论。
</section>

<section id="troubleshoot-agent-delivery" data-learning-context="troubleshoot-agent-delivery" data-context-type="troubleshoot" markdown="1">
## 从权限、就绪、数据和版本排查

| 现象 | 首先检查 |
| --- | --- |
| run 在 trace 中不可见 | owner、采样和run/request关联 |
| ready 失败但 live 正常 | PostgreSQL、schema、active index和worker依赖 |
| 回滚后旧版启动失败 | contract 是否破坏旧字段/枚举 |
| 恢复后重复动作 | effect receipt 与外部幂等键 |
| 注入文本触发工具 | 文档/记忆/工具结果是否标成数据 |
| 指标泄露用户输入 | 是否把query、subject或run ID当label |
| 备份文件生成成功 | 是否真正恢复并核对约束，而非只看文件存在 |
</section>

<section id="deepen-langgraph-optional" data-learning-context="deepen-langgraph-optional" data-context-type="deepen" markdown="1">
## LangGraph 只做可选概念映射

自建 `Run` 对应 graph state，严格 transition 对应 edge，PostgreSQL checkpoint 对应 checkpointer，waiting_approval 对应 interrupt，resume 对应 command。只有能保持授权、终态、预算、lease 和幂等不变量时才替换框架。本课程不安装 LangGraph，也不把它设为运行或 CI 依赖。
</section>

<section id="project-learning-assistant-v36" data-learning-context="project-learning-assistant-v36" data-context-type="project" markdown="1">
## 智能学习助手 P5.17 v0.36

- 上一版：v0.35 提供分层评估与脱敏 trace。
- 本课新增：安全矩阵、发布/回滚 guard、故障恢复映射、FastAPI 运行与审批 API、原生 TypeScript 控制台、非 root 容器、健康和指标。
- 文件：`delivery_guard.py`、`app.py`、`src/app.ts`、`Dockerfile`、`compose.yml` 与测试。
- 组级验收：六课 50 项代码/真实 PostgreSQL 测试、72 卡/144 问、容器、备份恢复、浏览器、严格构建和站内链接。
- 后续 P5.18 才评估框架对照；P5.19 才讨论是否微调，本批不做多 Agent 炫技。
</section>

## 四类学习者入口

- 零基础兴趣：在控制台创建 run、查看 step、批准并观察状态。
- 有基础兴趣：执行双版本回滚演练并写复盘。
- 零基础求职：解释发布通过为何不自动等于可安全回滚。
- 有基础求职：展示权限、注入、真实恢复、门禁、容器和回滚证据；不编造岗位频率。

## 完成检查

- 10 项测试、TypeScript 编译、非 root 容器和健康检查通过。
- 跨主体、危险执行、引用失真、重复副作用门禁均为 0。
- 备份恢复到独立数据库并核对表/约束。
- 五类故障有明确恢复结果。
- 旧应用或 schema 不兼容时阻止回滚。
- LangGraph 未进入默认依赖。

## 来源与版本

- 核查日期：2026-07-31。
- [OWASP Agentic AI Threats and Mitigations](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/)
- [PostgreSQL backup and restore](https://www.postgresql.org/docs/16/backup.html)
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/)
- [LangGraph persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)

## 下一步

完成 RAG 与 Agent 应用联合验收、治理同步和 Pages SHA 校验。
