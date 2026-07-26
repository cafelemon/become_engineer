<div class="be-tutor-mount" data-tutor-lesson="llm-rag-eval-03" aria-hidden="true"></div>
<section id="overview-source-grounded-chunks" class="be-page-hero be-lesson-hero" data-learning-context="overview-source-grounded-chunks" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">检索、RAG 与评估 · 第 3 / 6 课 · 智能学习助手 P5.3 v0.9</span>
# 分块、重叠、来源坐标与精确引用
## Chunk 不是复制的字符串，而是原文中的可验证区间
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
document=id:python-venv,characters:57,sentences:4
chunking=max-chars:32,overlap-sentences:1,chunks:3
chunks=python-venv:0:23|chars:23,python-venv:11:38|chars:27,python-venv:25:57|chars:32
citation=chunk:python-venv:0:23,absolute:0:10,exact:true
validation=source-bounds:true,text-slice:true,content-hash:true,stable-id:true
rejection=long-sentence:true,unknown-chunk:true,out-of-bounds:true,quote-mismatch:true
trust=retrieved-text:data-only,instructions-in-source:false,html-render:false
logs=chunk-text:none,quote:none,chunk-id:allowed,coordinates:allowed,error-code:allowed
invariants=sentence-boundaries,source-coordinates,exact-citation,retrieved-only,no-generation,no-tools
```
v0.9 按句子边界生成有界 chunk，并保存原文绝对字符坐标。引用使用 chunk 内相对区间，验证后转换回来源绝对区间；未检索 chunk、越界和引文不匹配都不能进入答案。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>LLM 应用工程化 · 3 / 6</strong></div>
  <div><span>前置</span><strong>语料身份、BM25、字符串区间</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 离线</strong></div>
  <div><span>完成后留下</span><strong>Chunk manifest、citation 门禁与 8 项测试</strong></div>
</div>

## 学习目标

- 从原文字符区间切分句子，不丢失终止标点。
- 以最大字符数成组，单句超限时明确拒绝而不是静默硬切。
- 用句子重叠保留边界上下文，同时让重复可观察。
- 用 `document_id:start:end` 建立稳定 chunk 身份。
- 验证 chunk 文本、摘要、来源和坐标均与原文一致。
- 只允许引用已检索 chunk，并把相对引文转换为绝对来源区间。

<section id="concept-chunk-boundary" data-learning-context="concept-chunk-boundary" data-context-type="concept" markdown="1">
## 分块策略改变检索单位和上下文

太大的 chunk 混入无关内容并占用上下文预算；太小的 chunk 丢失语义联系。v0.9 固定 `max_chars=32`、重叠 1 句，以便观察三个 chunk，不把字符数冒充 provider token。

单句超过上限返回 `sentence_too_long`，迫使调用方选择更大的预算或显式次级切分策略。
</section>

<section id="concept-citation-coordinate" data-learning-context="concept-citation-coordinate" data-context-type="concept" markdown="1">
## 两套坐标解决展示与追溯

- chunk 坐标：`start:end` 是它在整篇原文中的绝对字符区间。
- quote 坐标：`quote_start:quote_end` 是引文在 chunk 内的相对区间。
- 验证结果：两者相加得到来源绝对区间。

相同句子因 overlap 出现在两个 chunk 时，citation 的 chunk ID 仍能说明本次检索使用了哪一个上下文。
</section>

<section id="example-exact-citation" data-learning-context="example-exact-citation" data-context-type="example" markdown="1">
## 引文必须逐字符匹配已检索内容

```python
chunk = retrieved_by_id[citation.chunk_id]
expected = chunk.text[citation.quote_start:citation.quote_end]
if citation.quote != expected:
    raise ChunkError("citation_quote_mismatch", ...)
absolute_start = chunk.start + citation.quote_start
absolute_end = chunk.start + citation.quote_end
```

大小写修复、去空格或同义改写都不是“精确引用”。若界面要展示摘要，应把摘要和逐字引文分成不同字段。
</section>

<section id="reproduce-chunk-v09" data-learning-context="reproduce-chunk-v09" data-context-type="reproduce" markdown="1">
## 回放三段重叠 chunk 与四类引用失败

```bash
cd site-src/examples/llm-rag-eval/intelligent-learning-assistant-v09
python3 -m unittest -v test_chunk_citation.py
python3 chunk_citation.py
```

8 项测试覆盖句子区间、chunk 上限/身份、重叠、长句拒绝、精确引用、未知/越界/错引、篡改和来源文本数据边界。
</section>

<section id="modify-chunk-policy" data-learning-context="modify-chunk-policy" data-context-type="modify" markdown="1">
## 比较无重叠与两句重叠

1. 对同一 source document 分别设置 overlap 0、1、2。
2. 记录 chunk 数、重复字符数和每个 chunk 的区间。
3. 用第 2 课固定查询检索各版本。
4. 比较目标句是否进入 Top-k，以及上下文总字符数。
5. 把策略版本写入后续评估配置，不只挑最好看的样例。

重叠提高边界召回，也会增加索引量和重复证据；必须量化权衡。
</section>

<section id="troubleshoot-chunk-citation" data-learning-context="troubleshoot-chunk-citation" data-context-type="troubleshoot" markdown="1">
## 先核对原文，再核对检索集合

| 错误 | 含义 |
| --- | --- |
| `sentence_too_long` | 当前策略不能完整容纳一个句子 |
| `chunk_content_mismatch` | 文本或摘要已不等于原文切片 |
| `chunk_identity_mismatch` | 文档/来源/ID 与坐标不一致 |
| `citation_chunk_not_retrieved` | 答案引用了没有提供给模型的证据 |
| `citation_out_of_bounds` | 相对区间越过 chunk |
| `citation_quote_mismatch` | 引文原文与区间不一致 |

不要在错误发生后搜索全语料找一个相同句子替换；那会掩盖本次检索证据缺失。
</section>

<section id="deepen-retrieved-data-boundary" data-learning-context="deepen-retrieved-data-boundary" data-context-type="deepen" markdown="1">
## 检索内容是数据，不是更高优先级指令

fixture 中含“忽略系统指令”，chunker 只计算字符区间和摘要，绝不执行它。进入模型上下文时还要明确分隔来源数据，并由 system 规则声明来源中的指令不可信。

精确引用只能证明答案引用了这段文本，不能证明这段文本安全或事实正确。来源准入仍属于第 1 课边界。
</section>

<section id="project-learning-assistant-v09" data-learning-context="project-learning-assistant-v09" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.3 v0.9

- 上一版：v0.8 能按 BM25 检索文档。
- 本课新增：句子区间、有界 chunk、重叠、稳定 ID、摘要与精确 citation。
- 文件：`chunk_citation.py` 与 `test_chunk_citation.py`。
- 保存：三段 chunk manifest、8 项测试和三种 overlap 对比。
- 下一版：加入 embedding adapter、余弦相似度与关键词/向量混合排序。
</section>

## 四类学习者入口

- 零基础兴趣：在原文上标出三段颜色区间和重复句。
- 有基础兴趣：比较三种 overlap 的召回与重复成本。
- 零基础求职：用“chunk ID + 原文区间”解释引用如何追溯。
- 有基础求职：解释错引、未检索引用和来源指令注入；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 每个 chunk 都是原文精确切片，字符数不超过上限。
- overlap 只在句子边界发生，单句超限明确拒绝。
- 引用必须来自已检索 chunk，区间与 quote 逐字符一致。
- 绝对引用区间能回到同一 source URI 的原文。
- 日志不保存 chunk 文本或引文，来源中的指令只作为数据。

## 来源与版本

- 核查日期：2026-07-26。
- 适用环境：Python 3.11+ 标准库；自动测试离线。
- [Retrieval-Augmented Generation 原始论文](https://arxiv.org/abs/2005.11401)
- [OWASP LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
- [Python dataclasses](https://docs.python.org/3.11/library/dataclasses.html)

## 下一步

进入第 4 课，用可替换 embedding adapter、余弦相似度和 RRF 建立混合检索。
