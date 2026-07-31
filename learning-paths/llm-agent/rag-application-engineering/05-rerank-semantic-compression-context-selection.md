<div class="be-tutor-mount" data-tutor-lesson="rag-application-engineering-05" aria-hidden="true"></div>
<section id="overview-context-selection" class="be-page-hero be-lesson-hero" data-learning-context="overview-context-selection" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">RAG 应用工程 · 第 5 / 6 课 · 智能学习助手 P5.10 v0.29</span>
# 重排、语义压缩与上下文选择
## 把“召回到的候选”变成“可引用的证据包”
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
pipeline=retrieved:2,reranked:2,extracted:2,deduped:1
context=selected:1,characters:34,budget-ok:true
citation=source:guide,version:2,page:1,exact:true
adapters=reranker:fixed,compressor:extractive,real-cross-encoder:false
```
v0.29 串起 `retrieved → reranked → extracted → deduped → selected`。每段证据保留来源版本、页码、块和字符坐标，生成式摘要不能伪装成原文引用。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>RAG 应用工程 · 5 / 6</strong></div>
  <div><span>前置</span><strong>混合检索、RRF、chunk 坐标与 ACL</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 固定 rerank adapter · 不下载模型</strong></div>
  <div><span>完成后留下</span><strong>Reranker、ContextCompressor、选择器与 8 项测试</strong></div>
</div>

## 学习目标

- 理解 CrossEncoder 是有界候选上的第二阶段，而不是全库检索器。
- 用统一接口替换固定 adapter 与真实模型，不让模型依赖侵入业务边界。
- 通过抽取、去重、多样性和预算构造上下文包。
- 缓解 lost in the middle，并保留每条引用回到原文的精确坐标。

<section id="concept-reranker-contract" data-learning-context="concept-reranker-contract" data-context-type="concept" markdown="1">
## Reranker 只重排有界候选

第一阶段检索负责从大语料快速召回，第二阶段重排器只接收 `candidate_pool`。CrossEncoder 可联合阅读查询与候选，通常更精确但更慢；因此必须记录输入池大小、输出数量、版本和延迟。把全库内容逐条交给 CrossEncoder 既不可扩展，也绕开了检索预算。

本课的 `FixedReranker` 用稳定词项重叠模拟接口，不代表真实模型效果。真实实验可在独立环境安装 `sentence-transformers==5.6.0` 并实现同一 `Reranker` 协议；本机、默认依赖与 CI 不安装或下载模型。
</section>

<section id="concept-extractive-compression" data-learning-context="concept-extractive-compression" data-context-type="concept" markdown="1">
## 抽取式压缩保留引用坐标

`ContextCompressor` 从原 chunk 选择与问题有关的完整句子，同时携带：

```text
source_id + version + page/block + chunk_id + start/end
```

只有 `source_text[start:end] == evidence.text` 才算精确引用。生成式摘要可能有价值，但它是新文本，不能继承原句坐标并冒充逐字证据。
</section>

<section id="example-context-selection" data-learning-context="example-context-selection" data-context-type="example" markdown="1">
## 去重、多样性、预算和中部遗失一起处理

1. 重排后只保留前 N 个候选。
2. 抽取相关句子并按来源坐标去重。
3. 用 MMR 思路平衡相关性与来源多样性。
4. 按字符预算逐条装入，超出则停止。
5. 长上下文把最高相关证据放在开头，将第二高相关证据移到末尾，降低重要内容被埋在中间的风险。

多样性不是随机打散；低相关内容仍不能仅因来源不同而入选。
</section>

<section id="reproduce-context-selection-v29" data-learning-context="reproduce-context-selection-v29" data-context-type="reproduce" markdown="1">
## 运行重排、压缩和选择

```bash
cd site-src/examples/rag-application-engineering/intelligent-learning-assistant-v29
python3 -m unittest -v test_context_selection.py
python3 context_selection.py
```

8 项测试覆盖候选池上限、坐标保真、重叠去重、硬字符预算、来源多样性、中部遗失排序、生成摘要拒绝精确引用和空查询。
</section>

<section id="modify-add-model-adapter" data-learning-context="modify-add-model-adapter" data-context-type="modify" markdown="1">
## 接入一个真实 CrossEncoder adapter

1. 在独立可选依赖中固定模型与库版本，不改默认 CI。
2. 实现 `score(query, candidates)`，输入最多 20 条候选。
3. 保存模型名、模型修订、分数方向和耗时。
4. 用同一固定评估集比较 Recall、nDCG、引用覆盖与延迟。
5. 任何超时或模型错误回退到已声明策略，而不是静默返回空答案。
</section>

<section id="troubleshoot-context-selection" data-learning-context="troubleshoot-context-selection" data-context-type="troubleshoot" markdown="1">
## 从候选、坐标、重复与预算排查

| 现象 | 首先检查 |
| --- | --- |
| 重排很慢 | 候选池是否无上限 |
| 引用无法打开 | 压缩后是否丢了版本和坐标 |
| 上下文全是同一段 | 是否只按文本而非坐标/父块去重 |
| 答案漏掉第二来源 | MMR 多样性惩罚是否过强或过弱 |
| 最相关证据没被模型用到 | 是否被放在长上下文中部 |
| 摘要显示为逐字引用 | 是否错误继承了原文坐标 |
| Prompt 超预算 | 选择器是否执行硬预算而非事后截断 |
</section>

<section id="deepen-rerank-evaluation" data-learning-context="deepen-rerank-evaluation" data-context-type="deepen" markdown="1">
## 分层评估，不用最终答案掩盖中间错误

重排层比较候选池内的 nDCG、MRR 和关键证据排名；压缩层比较句子保留率、压缩率与引用坐标有效率；上下文层比较证据覆盖、多样性、字符利用率和位置分布。最终回答正确不代表压缩安全，回答错误也不一定是生成模型问题。
</section>

<section id="project-learning-assistant-v29" data-learning-context="project-learning-assistant-v29" data-context-type="project" markdown="1">
## 智能学习助手 P5.10 v0.29

- 上一版：v0.28 产出经过 ACL 的有界候选。
- 本课新增：`Reranker`、`ContextCompressor`、抽取坐标、MMR 式多样性、硬预算和 lost-in-the-middle 排序。
- 文件：`context_selection.py` 与 `test_context_selection.py`。
- 保存：候选池大小、重排版本、抽取坐标、淘汰原因、上下文顺序与预算。
- 下一版：把文档管理、检索调试、Prompt、聊天、引用、健康和指标交付成可用应用。
</section>

## 四类学习者入口

- 零基础兴趣：对照固定报告，看候选怎样一步步变成一条证据。
- 有基础兴趣：修改字符预算和多样性权重，观察证据组成变化。
- 零基础求职：用“CrossEncoder 为什么不能扫全库”解释两阶段检索。
- 有基础求职：展示坐标保真、生成摘要边界、预算与 8 项回归测试；只使用本项目证据。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 重排输入池有明确上限。
- 压缩后每条精确引用都能切回原文。
- 重叠证据不重复占用预算。
- 相关性、多样性和位置分布可解释。
- 未安装或下载真实模型，固定 adapter 不被描述为生产效果。

## 来源与版本

- 核查日期：2026-07-31。
- [Sentence Transformers CrossEncoder](https://www.sbert.net/docs/cross_encoder/usage/usage.html)
- [Lost in the Middle](https://arxiv.org/abs/2307.03172)
- [Maximal Marginal Relevance](https://dl.acm.org/doi/10.1145/290941.291025)

## 下一步

进入第 6 课，交付 FastAPI、原生 TypeScript 管理台、聊天页与发布路径。
