<div class="be-tutor-mount" data-tutor-lesson="llm-rag-eval-02" aria-hidden="true"></div>
<section id="overview-bm25-baseline" class="be-page-hero be-lesson-hero" data-learning-context="overview-bm25-baseline" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">检索、RAG 与评估 · 第 2 / 6 课 · 智能学习助手 P5.2 v0.8</span>
# 倒排索引、BM25、Top-k 与稳定排序
## 先建立能解释每一分的关键词基线
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
index=documents:3,terms:173,average-length:70.333333
query-permission=http-status:7.145603,python-venv:0.134575,sqlite-transaction:0.130743
query-environment=python-venv:18.087837
query-transaction=sqlite-transaction:6.868499
query-unknown=none
tokenizer=unicode-nfkc+lower+ascii-terms+han-unigram-bigram,general-segmentation:false
bm25=k1:1.2,b:0.75,idf:log1p-rsj,query-terms:deduplicated
ranking=score-desc,document-id-asc,zero-score:excluded,top-k:bounded
invariants=lexical-baseline,explainable-contributions,stable-ties,no-embedding,no-generation,no-tools
```
v0.8 把三篇规范文档变成倒排索引，并用 BM25 排序。每个结果能展开到具体 query term 的贡献；相同分数按稳定 `document_id` 排序，未知词明确返回空结果。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>LLM 应用工程化 · 2 / 6</strong></div>
  <div><span>前置</span><strong>语料快照、Counter、对数与排序</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 离线</strong></div>
  <div><span>完成后留下</span><strong>BM25 基线、分数解释与 8 项测试</strong></div>
</div>

## 学习目标

- 从 token、词频和 posting list 建立倒排索引。
- 用文档频率理解 IDF，用词频与长度归一理解 BM25。
- 明确 tokenizer 是检索契约的一部分，不是无关预处理。
- 让空查询、未知词、零分与非法 Top-k 有稳定行为。
- 按分数降序、文档 ID 升序获得可重复并列排序。
- 展开每个 matched term 的贡献，建立后续评估基线。

<section id="concept-inverted-index" data-learning-context="concept-inverted-index" data-context-type="concept" markdown="1">
## 倒排索引从“文档有什么”转成“词出现在哪里”

每篇文档保存 term frequency 和总长度；全局 posting list 保存每个 term 出现在哪些文档。查询只需合并相关 posting，不必每次扫描所有正文。

本实验数据很小，重点是可观察契约。真实索引还会处理增量更新、压缩、字段权重、停用词和持久化。
</section>

<section id="concept-bm25-score" data-learning-context="concept-bm25-score" data-context-type="concept" markdown="1">
## BM25 同时考虑稀有度、词频饱和与文档长度

```text
idf(t) = log(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
score(t,d) = idf(t) * tf(t,d) * (k1 + 1)
             / (tf(t,d) + k1 * (1 - b + b * dl/avgdl))
```

稀有 term 的 IDF 更高；重复出现有收益但会饱和；较长文档按平均长度归一。这里固定 `k1=1.2`、`b=0.75`，参数变化必须进入评估配置。
</section>

<section id="example-tokenizer-contract" data-learning-context="example-tokenizer-contract" data-context-type="example" markdown="1">
## 中文 tokenizer 要诚实标注能力边界

```python
normalized = unicodedata.normalize("NFKC", text).lower()
# ASCII 连续词作为 term；汉字同时生成单字和相邻二元组
```

这种规则能让“权限”匹配 `zh2:权限`，也可能因常见单字产生低分噪声。它不是通用中文分词，不应把三条 fixture 的成功外推为真实语料质量。
</section>

<section id="reproduce-bm25-v08" data-learning-context="reproduce-bm25-v08" data-context-type="reproduce" markdown="1">
## 运行三条命中与一条未知查询

```bash
cd site-src/examples/llm-rag-eval/intelligent-learning-assistant-v08
python3 -m unittest -v test_bm25_retriever.py
python3 bm25_retriever.py
```

8 项测试覆盖 tokenizer、固定排序、无结果、Top-k、并列顺序、IDF、分数解释和固定报告。测试不依赖搜索服务或 embedding。
</section>

<section id="modify-bm25-tokenizer" data-learning-context="modify-bm25-tokenizer" data-context-type="modify" markdown="1">
## 加入明确停用词，再用查询集判断是否更好

1. 记录当前四条查询的完整排名与分数。
2. 只移除经过说明的高频单字，如对任务无区分力的词。
3. tokenizer 版本进入索引配置和 fingerprint。
4. 重新构建索引，比较目标文档排名与误命中。
5. 若某条查询变差，保留证据而不是只展示改进样例。

停用词不是“越多越好”；它改变可检索信息，必须由固定评估集约束。
</section>

<section id="troubleshoot-bm25-ranking" data-learning-context="troubleshoot-bm25-ranking" data-context-type="troubleshoot" markdown="1">
## 从 token 到贡献逐层排查

| 现象 | 先检查 |
| --- | --- |
| 明明有词却无结果 | NFKC、大小写和中英文 token 是否一致 |
| 无关文档有低分 | 汉字单字是否产生公共 term |
| 常见词权重过高 | posting 的 document frequency 是否正确 |
| 长文档被过度惩罚 | `b` 与平均长度计算 |
| 同分每次顺序变化 | 是否缺少 document ID 次级排序 |
| explanation 与 score 不同 | query term 去重和贡献求和是否使用同一规则 |
| Top-k 为 bool 被接受 | Python bool/int 子类边界是否显式排除 |
</section>

<section id="deepen-lexical-baseline" data-learning-context="deepen-lexical-baseline" data-context-type="deepen" markdown="1">
## 关键词基线不是落后方案，而是比较坐标

词面精确、可解释、无模型费用、更新快，是 lexical retrieval 的实际优势；同义表达、拼写变化和跨语言则可能失败。后续向量检索必须用同一查询集与 BM25 比较，而不是只展示一个“看起来更智能”的答案。

本课不做生成，所以检索命中不等于最终回答正确。第 5 课才建立 claim 与 citation 门禁。
</section>

<section id="deepen-lexical-debug-console" data-learning-context="deepen-lexical-debug-console" data-context-type="deepen" markdown="1">
## 应用里需要一张关键词检索调试单

用户说“文档明明有这句话却搜不到”时，只展示最终 Top 3 不够。调试页应按阶段给出允许公开的结构化信息：规范化后的 query、tokenizer 版本、query terms、每个 term 的 df/IDF、命中文档字段、字段权重、过滤条件、候选数和截断原因。正文与原始敏感查询仍不写入普通日志。

标题、正文、标签和路径不应被当成一个字段。可先给标题更高权重，再用固定查询集验证；如果路径中的高频词把无关结果推到前面，就应降低字段权重或停止索引该字段，而不是手工给某篇文档加分。

```text
query
  → normalize/tokenize
  → metadata + ACL filter
  → fielded lexical recall
  → candidate budget
  → stable ranking + explanation
```

“查询无结果”也要区分：没有 token、token 不在索引、权限过滤后为空、候选被预算裁掉、索引版本过旧。只有第一种适合提示用户改写，权限过滤为空不能泄露“其实存在一篇无权文档”。

后续应用课会把 lexical ranking 作为混合检索的一路，并在管理台保存脱敏 retrieval trace。BM25 仍是回归基线：向量或重排上线后若连精确课程 ID、错误码、产品名都找不准，不能用“更语义”解释退化。
</section>

<section id="project-learning-assistant-v08" data-learning-context="project-learning-assistant-v08" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.2 v0.8

- 上一版：v0.7 冻结语料与来源身份。
- 本课新增：混合中英文 tokenizer、倒排索引、BM25、Top-k、并列顺序和 term 贡献。
- 文件：`bm25_retriever.py` 与 `test_bm25_retriever.py`。
- 保存：四条固定排名、8 项测试和一次 tokenizer 修改对比。
- 下一版：把长文档切成有精确来源坐标、可验证引用的 chunk。
- 应用承接：后续加入字段权重、ACL 前置过滤、候选预算和检索调试 trace。
</section>

## 四类学习者入口

- 零基础兴趣：手算一个词的 df、IDF 和两篇文档先后。
- 有基础兴趣：加入停用词版本并比较四条查询。
- 零基础求职：用倒排索引和“稀有词更有区分力”解释检索基线。
- 有基础求职：解释 tokenizer、BM25 参数和稳定并列排序；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 三条目标查询 Top 1 正确，未知查询返回空。
- 稀有 term 的 IDF 高于全语料常见 term。
- explanation 各 term 贡献之和等于结果 score。
- Top-k 必须为正整数且显式拒绝 bool。
- 能说明汉字 unigram/bigram 不是通用分词，BM25 命中不等于回答正确。

## 来源与版本

- 核查日期：2026-07-26。
- 适用环境：Python 3.11+ 标准库；自动测试离线。
- [Introduction to Information Retrieval：概率检索与 BM25](https://nlp.stanford.edu/IR-book/html/htmledition/probabilistic-information-retrieval-1.html)
- [SQLite FTS5 BM25 官方说明](https://www.sqlite.org/fts5.html#the_bm25_function)
- [Python unicodedata](https://docs.python.org/3.11/library/unicodedata.html)

## 下一步

进入第 3 课，建立有界 chunk、重叠策略、原文字符区间和可验证 citation。
