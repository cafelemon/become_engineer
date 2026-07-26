# 模型使用与结构化输出

本组用“可评估的智能学习助手”P5.1 连续建设六课。应用型 LLM 起步不强制完成机器学习、深度学习或 Transformer；前置是 Python 工程化与 Web/API。

当前进度：6 / 6 已开放。

1. [模型边界、消息与离线适配器](01-model-boundary-messages-offline-adapter.md)
2. [Prompt 角色、版本、参数与上下文预算](02-prompt-roles-version-parameters-context-budget.md)
3. [JSON、严格 Schema、语义校验与缺失信息](03-json-schema-semantic-validation-missing-information.md)
4. [错误分类、Deadline、退避与有界重试](04-error-taxonomy-deadline-backoff-bounded-retry.md)
5. [流事件、Delta 顺序、终止原因与取消](05-stream-delta-order-finish-cancel.md)
6. [Provider 配置、秘密、脱敏与可选真实验收](06-provider-config-secrets-redaction-delivery.md)

六课正文、项目、48 项测试、60 张小码卡、120 条固定问法、严格构建、站内链接和 18 项多模式浏览器验收全部通过。

所有自动测试默认离线，不读取真实密钥、不产生模型费用、不保存原始 Prompt 或回复。RAG、Tool Calling 和 Agent 属于后续模块。
