# RAG 应用工程

本组在检索/RAG/评估基础课之上，把来源、版本、切片、向量索引、检索路由、重排压缩、Prompt、管理台和聊天页接成可交付闭环。

当前进度：6 / 6 已开放。

1. [文档接入、解析、版本与索引作业](01-document-ingestion-parsing-version-index-jobs.md)
2. [切片模型、切片策略与对照实验](02-chunking-models-strategies-comparison.md)
3. [Embedding 契约、pgvector 与索引生命周期](03-embedding-contract-pgvector-index-lifecycle.md)
4. [查询理解、过滤、混合检索与策略路由](04-query-understanding-filter-hybrid-routing.md)
5. [重排、语义压缩与上下文选择](05-rerank-semantic-compression-context-selection.md)
6. [Prompt、引用、管理台、聊天页与发布](06-prompt-citation-admin-chat-release.md)

六课共 58 项代码与真实数据库测试、72 卡/144 问、真实 pgvector/Compose、18 项课程页面和 3 项应用浏览器检查、严格构建与站内链接验收均已通过。

核心接口和状态机由项目自行实现。Markdown、HTML 和数字文本 PDF 属于本组范围；扫描 PDF 返回 `ocr_required`。真实 embedding、reranker 和生成模型只提供可替换接法，不在本机下载或运行。
