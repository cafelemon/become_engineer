# Tool Calling 与有界工作流

本组继续演进“可评估的智能学习助手”P5.5。进入条件是检索、RAG 与评估已开放。

当前进度：6 / 6 已开放。

1. [工具定义、注册表、候选调用与严格参数](01-tool-definition-registry-candidate-call-strict-arguments.md)
2. [业务校验、主体授权与只读工具执行](02-business-validation-authorization-read-only-execution.md)
3. [多工具调用、call_id 关联与部分失败隔离](03-multiple-calls-call-id-correlation-partial-failure.md)
4. [受控副作用、人工确认与幂等保护](04-controlled-side-effects-confirmation-idempotency.md)
5. [有界工具循环、状态预算与显式终止](05-bounded-tool-loop-state-budgets-termination.md)
6. [固定对抗评估、预算指标与回归交付](06-fixed-adversarial-evaluation-regression-delivery.md)

六课累计 48 项真实离线测试、60 张小码卡、120 条固定问法和 12 条未知问题；固定对抗评估、严格构建、站内链接与多模式浏览器组级验收通过后正式开放。

所有自动测试使用 Python 3.11+ 标准库、合成学习数据和离线 scripted model，不联网、不读取真实密钥。模型输出始终只是候选调用；应用拥有验证、授权、确认、执行和停止权。任意 SQL、Shell、文件系统、网络浏览与无限自主循环不进入本组。
