<div class="be-tutor-mount" data-tutor-lesson="llm-rag-eval-04" aria-hidden="true"></div>
<section id="overview-hybrid-retrieval" class="be-page-hero be-lesson-hero" data-learning-context="overview-hybrid-retrieval" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">检索、RAG 与评估 · 第 4 / 6 课 · 智能学习助手 P5.3 v0.10</span>
# Embedding 适配器、余弦相似度与 RRF 混合检索
## 固定向量验证工程契约，不冒充语义能力
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
embedding=adapter:fixture,batch:true,dimension:2,semantic-claim:false,provider-call:false
vector-ranking=chunk-http,chunk-python,chunk-sqlite
vector-scores=chunk-http:1.000000,chunk-python:0.970143,chunk-sqlite:0.000000
lexical-ranking=chunk-python,chunk-http,chunk-sqlite
fusion=method:rrf,rank-constant:60,top-k:3
fused-ranking=chunk-http,chunk-python,chunk-sqlite
fused-ranks=chunk-http:2/1,chunk-python:1/2,chunk-sqlite:3/3
validation=finite:true,dimension:true,nonzero:true,bool-rejected:true,stable-ties:true
rejection=unknown-fixture:true,batch-shape:true,duplicate-rank:true,unknown-rank:true
logs=query-text:none,chunk-text:none,vectors:none,chunk-id:allowed,score:allowed,error-code:allowed
invariants=replaceable-adapter,cosine,stable-top-k,rrf-ranks,no-semantic-claim,no-generation,no-tools
```
v0.10 把向量生成放在可替换适配器后，严格验证批次、维度、有限值和非零范数；向量排序与 BM25 排名只通过名次做 RRF，不直接比较不可比的原始分数。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>LLM 应用工程化 · 4 / 6</strong></div>
  <div><span>前置</span><strong>BM25、chunk 身份、向量与排序</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 离线固定向量</strong></div>
  <div><span>完成后留下</span><strong>Embedding 边界、向量索引、RRF 与 8 项测试</strong></div>
</div>

## 学习目标

- 用 `Protocol` 隔离 embedding provider，而不把凭据或 SDK 写进检索核心。
- 验证一段文本恰好对应一个同维、有限、非零向量。
- 计算余弦相似度，并用 chunk ID 打破同分。
- 保持关键词分数与向量分数各自在自己的排序空间。
- 用 Reciprocal Rank Fusion 融合名次，并保留每个来源排名。
- 明确固定二维向量只能测试接口和算法，不能证明自然语言语义质量。

<section id="concept-embedding-boundary" data-learning-context="concept-embedding-boundary" data-context-type="concept" markdown="1">
## Embedding 是外部能力边界

`EmbeddingAdapter.embed(texts)` 的契约是“每个输入返回一个向量”，不是“向量一定语义正确”。索引器按 chunk ID 排序后批量调用，随后核对批次数、维度、数值和范数。未知 fixture 文本显式返回 `fixture_text_unknown`，不会偷偷生成随机向量。

真实 provider 将来可替换 adapter，但仍需另行处理模型版本、限流、成本、数据出境和索引重建。本课不联网、不读 key。
</section>

<section id="concept-cosine-ranking" data-learning-context="concept-cosine-ranking" data-context-type="concept" markdown="1">
## 余弦比较方向，不比较长度

$$
\cos(a,b)=\frac{a\cdot b}{\lVert a\rVert\lVert b\rVert}
$$

零向量没有定义，NaN/Infinity 会破坏全序，不同维度无法点积，所以都在排序前拒绝。命中按 `score desc, chunk_id asc` 排序，使相同输入始终获得相同 Top-k。
</section>

<section id="example-rrf-fusion" data-learning-context="example-rrf-fusion" data-context-type="example" markdown="1">
## RRF 只消费排名

```python
for rank, chunk_id in enumerate(ranking, start=1):
    score[chunk_id] += 1 / (60 + rank)
hits.sort(key=lambda hit: (-hit.score, hit.chunk_id))
```

BM25 的数值尺度与 cosine 不同，直接相加需要校准。RRF 用名次表达两个检索器的共同支持；固定案例中 HTTP 在关键词排第 2、向量排第 1，因此融合后排第 1。每个 ranking 内重复 ID、未知 ID 都拒绝，避免重复加分和跨语料污染。
</section>

<section id="reproduce-hybrid-v10" data-learning-context="reproduce-hybrid-v10" data-context-type="reproduce" markdown="1">
## 回放向量排序与混合排序

```bash
cd site-src/examples/llm-rag-eval/intelligent-learning-assistant-v10
python3 -m unittest -v test_hybrid_retriever.py
python3 hybrid_retriever.py
```

8 项测试覆盖批次顺序、未知 fixture、维度/非有限/零向量/bool、cosine、稳定同分、Top-k、RRF 排名与坏输入。
</section>

<section id="modify-ranking-fusion" data-learning-context="modify-ranking-fusion" data-context-type="modify" markdown="1">
## 修改一个向量，再修改融合常数

1. 把 HTTP 向量从 `(1, 0)` 改为 `(0.6, 0.4)`，记录向量排名。
2. 保持 BM25 排名不变，分别使用 RRF 常数 10、60、100。
3. 保存每个 chunk 的两个来源名次和融合分数。
4. 增加一个仅被单路召回的 chunk，观察它是否进入 Top-k。
5. 不凭单个演示选择参数；第 6 课在固定评估集上比较。

常数越大，头部名次间差距越小；这不是“60 永远最好”的理由。
</section>

<section id="troubleshoot-vector-fusion" data-learning-context="troubleshoot-vector-fusion" data-context-type="troubleshoot" markdown="1">
## 先检查向量契约，再检查融合输入

| 错误 | 含义 |
| --- | --- |
| `adapter_shape_mismatch` | 返回向量数与输入文本数不同 |
| `dimension_mismatch` | 索引或查询向量维度不同 |
| `invalid_vector` | 含 bool、非数字、NaN 或 Infinity |
| `zero_vector` | cosine 分母为零 |
| `duplicate_ranked_chunk` | 同一路 ranking 重复加分 |
| `unknown_ranked_chunk` | 排名引用当前语料之外的 chunk |

若结果“不符合直觉”，先打印允许字段中的 chunk ID、score 和 rank；不要记录原始查询、正文或完整向量。
</section>

<section id="deepen-semantic-claim-boundary" data-learning-context="deepen-semantic-claim-boundary" data-context-type="deepen" markdown="1">
## 算法正确不等于语义有效

固定二维向量是测试替身：它能证明批量顺序、维度门禁、cosine 和稳定排序实现正确，不能证明“连接为什么超时”在真实 embedding 空间里最接近 HTTP。真实语义质量必须用版本固定的模型和第 6 课评估集验证。

向量也可能泄露输入特征，本课日志契约不记录查询文本、chunk 文本或向量原值。
</section>

<section id="deepen-retrieval-strategy-routing" data-learning-context="deepen-retrieval-strategy-routing" data-context-type="deepen" markdown="1">
## 检索策略不是把所有召回器同时打开

应用查询至少分成精确标识、自然语言事实、多约束问题和复合问题。课程 ID、错误码、版本号优先走 lexical；同义表达可走 vector；带课程、版本、主体条件的查询先做 ACL 与 metadata filter；复合问题可拆成有界子查询后再合并。路由结果应是严格结构，例如 `{lexical_k, vector_k, filters, rewrite, max_candidates}`，不能让模型生成任意 SQL。

候选预算要贯穿全链路：每路召回多少、融合后保留多少、进入 reranker 多少、最终上下文多少。一路返回 1000 条再在末端截断，会浪费数据库、重排和上下文成本，也使故障难以解释。

| 策略 | 适合的失败 | 不应承担 |
| --- | --- | --- |
| query normalization | 大小写、全半角、稳定别名 | 发明用户未说的约束 |
| multi-query | 同一意图的词面变化 | 无限生成改写 |
| decomposition | 可独立求证的复合问题 | 把强依赖问题硬拆散 |
| hybrid + RRF | lexical/vector 互补 | 掩盖两路都召回错误 |
| parent expansion | child 命中但上下文不足 | 绕过来源与 ACL |

后续应用课会在 PostgreSQL/pgvector 上保存 index manifest，并比较 exact、HNSW、过滤和 RRF。模型名、维度、距离函数、归一化、切片策略与语料版本共同决定索引身份；任何一项变化都应重建或创建新索引版本，而不是把新向量写进旧列。
</section>

<section id="project-learning-assistant-v10" data-learning-context="project-learning-assistant-v10" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.3 v0.10

- 上一版：v0.9 形成可追溯 chunk。
- 本课新增：可替换 embedding adapter、向量校验、cosine Top-k 和 RRF。
- 文件：`hybrid_retriever.py` 与 `test_hybrid_retriever.py`。
- 保存：关键词/向量/融合三组排名及 8 项测试。
- 下一版：只让检索证据进入回答，并对每条 claim 做 citation 门禁。
- 应用承接：后续实现查询路由、ACL/metadata 过滤、候选预算、pgvector 索引版本与重建切换。
</section>

## 四类学习者入口

- 零基础兴趣：画两个二维箭头，观察方向相同为何 cosine 为 1。
- 有基础兴趣：比较原始分数相加和 RRF 的假设差异。
- 零基础求职：解释“适配器—校验—排序—融合”四层职责。
- 有基础求职：说明固定向量、真实模型漂移、评估和日志边界；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 一条输入对应一条同维有限非零向量，bool 不冒充数字。
- cosine 同分按 chunk ID 稳定排序，Top-k 只接受正整数。
- RRF 保存来源名次，拒绝重复或未知 chunk。
- 固定向量明确标注 `semantic-claim:false`，没有真实 provider 调用。
- 日志不保存查询、正文和向量。

## 来源与版本

- 核查日期：2026-07-26。
- 适用环境：Python 3.11+ 标准库；自动测试离线。
- [OpenAI Embeddings 指南](https://platform.openai.com/docs/guides/embeddings)
- [Reciprocal Rank Fusion 原始论文](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- [Python math](https://docs.python.org/3.11/library/math.html)

## 下一步

进入第 5 课，构造受限上下文包、逐 claim 精确引用与缺证据拒答。
