# Agent 应用编排与交付

本组在 RAG 应用与 Agent 工程基础上，用显式状态图连接检索、回答、工具、计划、记忆、审批、恢复、评估和发布。框架不是主线；每个状态、终态、预算和副作用先用自建严格接口验证。

当前进度：6 / 6 已开放。

1. [工作流、路由器与 Agent 的边界](01-workflow-router-agent-boundaries.md)
2. [会话上下文、摘要与记忆召回](02-session-context-summary-memory-retrieval.md)
3. [任务拆解、子任务预算与重规划](03-task-decomposition-budget-replanning.md)
4. [人工审批、长任务与恢复](04-human-approval-long-running-recovery.md)
5. [端到端评估、轨迹与故障定位](05-end-to-end-evaluation-trace-fault-localization.md)
6. [安全、部署、回滚与交付证据](06-security-deployment-rollback-delivery-evidence.md)

六课代码、知识库、登记与组级验收均已完成：50 项课程测试通过，v0.34 在真实 PostgreSQL 中完成备份与独立库恢复，v0.36 容器以非 root 用户运行并通过健康检查；课程页 18 项多模式浏览器检查、应用页 3 项端到端检查、严格构建与站内链接全部通过。

LangGraph 仅在最后作为可选概念映射，不进入默认依赖、运行路径或 CI。
