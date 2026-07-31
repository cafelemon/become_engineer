# 检索、RAG 与评估

本组继续演进“可评估的智能学习助手”P5.2–P5.4。进入条件是模型使用与结构化输出、Web 工程化均已开放。

当前进度：6 / 6 已开放。

1. [语料文档契约、来源身份与可复现索引](01-corpus-document-source-reproducible-index.md)
2. [倒排索引、BM25、Top-k 与稳定排序](02-inverted-index-bm25-top-k-stable-ranking.md)
3. [分块、重叠、来源坐标与精确引用](03-chunk-overlap-source-coordinates-citation.md)
4. [Embedding 适配器、余弦相似度与 RRF 混合检索](04-embedding-cosine-rrf-hybrid-retrieval.md)
5. [有证据回答、Claim-Citation 门禁与缺证据拒答](05-grounded-claim-citation-abstention.md)
6. [固定评估集、检索指标、引用质量与回归门禁](06-fixed-eval-retrieval-citation-regression-gates.md)

六课 48 项测试、全量检索、严格构建、站内链接和六页多模式浏览器验收均已通过。

六课保留最小机制实验，同时已经补入应用映射：文档生命周期、关键词检索调试、五类切片模型、查询路由与候选预算、重排/语义压缩/Prompt 分层，以及 ingestion 到 answer 的六层评估。完整 PostgreSQL/pgvector、管理台和聊天页在后续“RAG 应用工程”连续项目中实现，不把概念表冒充已交付服务。

所有自动测试使用合成公开语料和 Python 3.11+ 标准库，不联网、不读取真实密钥。固定向量只验证 adapter、相似度和排序契约，不冒充真实语义 embedding；Tool Calling 与 Agent 属于后续模块。
