# NLP 与 Transformer

本组沿用[文本分类模型演进](../../../projects/text-classification-evolution/README.md)这一条项目线：先锁定任务、语料和评估协议，再在同一划分上逐步比较传统特征、浅层网络、序列模型和 Transformer。每一步都要保留错误样本与训练／推理成本，不能只报最高准确率。

当前进度：已开放 7 / 7。七课均有正文、运行项目、测试与小码数据；本机组级验收通过。

1. [文本任务、数据契约、切分与指标](01-text-data-contract-splits-metrics.md)（P3.1）
2. [分词、TF-IDF 与线性分类基线](02-tokenization-tfidf-linear-baseline.md)（P3.2）
3. [词表、Embedding 与池化浅层网络](03-vocabulary-embedding-pooling-network.md)（P3.3）
4. [GRU、CNN 序列基线与公平比较](04-rnn-cnn-sequence-baselines.md)（P3.4）
5. [缩放点积注意力、Mask 与位置](05-scaled-dot-product-attention-mask-position.md)（P3.5 前半）
6. [Transformer Encoder 文本分类与消融](06-transformer-encoder-classification-ablation.md)（P3.5 后半）
7. [预训练路径、统一评测与模型卡](07-pretrained-path-unified-evaluation-model-card.md)（P3.6–P3.7）

真实预训练模型的下载与微调为可选实验；必修路径保持离线可复现，不把离线适配器或随机初始化模型称作预训练实测。

本组是 AI 模型方向深化，不是学习现有 LLM API、RAG 或应用 Agent 的通用前置。教学语料是原创合成文本，不含个人数据；它能证明代码与评估契约可运行，不能代表真实任务效果。
