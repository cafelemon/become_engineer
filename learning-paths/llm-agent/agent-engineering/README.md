# Agent 工程

本组继续演进“可评估的智能学习助手”P5.6–P5.8。进入条件是 Tool Calling 与有界工作流 6/6 已开放。

当前进度：3 / 6 建设中。

1. [SQLite 运行状态、事件日志与原子 checkpoint](01-sqlite-run-state-event-log-atomic-checkpoint.md)
2. [记忆来源、同意、TTL 与上下文预算](02-memory-provenance-consent-ttl-context-budget.md)
3. [Lease、幂等 step 与崩溃恢复](03-lease-idempotent-step-crash-resume.md)

后续按课完成后再登记：轨迹评估、可观测性、安全交付。

全部自动测试使用 Python 3.11+ 标准库、临时 SQLite、虚拟时钟和离线 scripted model。持久状态只保存显式业务事件和有界 checkpoint，不保存隐式思维链；本组不引入外部记忆服务、遥测平台、Agent 框架、真实凭据或网络依赖。
