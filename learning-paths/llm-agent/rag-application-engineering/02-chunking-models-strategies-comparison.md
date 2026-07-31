<div class="be-tutor-mount" data-tutor-lesson="rag-application-engineering-02" aria-hidden="true"></div>
<section id="overview-chunking-comparison" class="be-page-hero be-lesson-hero" data-learning-context="overview-chunking-comparison" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">RAG 应用工程 · 第 2 / 6 课 · 智能学习助手 P5.9 v0.26</span>
# 切片模型、切片策略与对照实验
## 同一份解析块，用五种边界模型比较
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
strategies:5,models=fixed,recursive,structure,semantic,parent-child
coordinates=block-id+start+end+heading+page
metrics=boundary-coverage,context-precision,size-distribution,duplicate-rate
claim=fixture-adapter:true,real-semantic-model:false
invariants=shared-interface,stable-strategy-version,exact-source-slice,parent-link
```
v0.26 用统一 `Chunker` 比较固定窗口、递归分隔、标题/页码感知、语义断点和父子切片。切片模型决定边界，参数只控制尺度；选择必须来自同一评估集。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>RAG 应用工程 · 2 / 6</strong></div>
  <div><span>前置</span><strong>解析块、来源坐标、固定评估集</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 固定 embedding adapter</strong></div>
  <div><span>完成后留下</span><strong>五种 Chunker、策略指标与 8 项测试</strong></div>
</div>

## 学习目标

- 用同一接口输出稳定 chunk identity 与原文坐标。
- 比较五种切片模型的适用边界。
- 把模型版本与 size、overlap、threshold 一起登记。
- 用四类指标选择策略，不只看平均长度。
- 让父子切片的小块召回仍能回到完整父块。

<section id="concept-five-chunkers" data-learning-context="concept-five-chunkers" data-context-type="concept" markdown="1">
## 五种模型解决不同边界问题

| 模型 | 优势 | 主要风险 |
| --- | --- | --- |
| fixed window | 简单、稳定、易基线 | 截断语义 |
| recursive | 优先段落、句子与空格 | 分隔符规则依语言变化 |
| heading/page aware | 保留文档结构和引用位置 | 超长章节需二次切分 |
| semantic breakpoint | 相邻语义变化处断开 | 依赖 adapter、阈值和成本 |
| parent-child | 小块召回、大块回答 | 身份、去重和预算更复杂 |

不存在脱离文档类型和查询集的“最佳切片”。
</section>

<section id="concept-strategy-identity-metrics" data-learning-context="concept-strategy-identity-metrics" data-context-type="concept" markdown="1">
## 策略身份和指标必须一起保存

`fixed-v1:size=18:overlap=4` 与 `fixed-v1:size=20:overlap=4` 是不同策略。语义切片还要记录 adapter、维度、归一化和 threshold。对照指标至少包括：

- boundary coverage：金标准边界被保留的比例；
- context precision：进入候选的文本中相关证据占比；
- size distribution：均值、最大值和分位数；
- duplicate rate：overlap 或父子回填造成的重复比例。
</section>

<section id="example-parent-child-citation" data-learning-context="example-parent-child-citation" data-context-type="example" markdown="1">
## Child 命中，Parent 回填，引用仍指原文

child 保存 `block_id + start + end + parent_id`。检索命中 child 后可按 parent ID 取较完整上下文，但 citation 仍引用 child 的精确区间；不能把整段 parent 都声明为支持证据。
</section>

<section id="reproduce-chunking-lab-v26" data-learning-context="reproduce-chunking-lab-v26" data-context-type="reproduce" markdown="1">
## 运行五策略对照

```bash
cd site-src/examples/rag-application-engineering/intelligent-learning-assistant-v26
python3 -m unittest -v test_chunking_lab.py
python3 chunking_lab.py
```

8 项测试覆盖固定窗口坐标、坏参数、递归边界、结构元数据、语义 adapter、父子身份、四类指标和策略版本。
</section>

<section id="modify-add-chinese-separators" data-learning-context="modify-add-chinese-separators" data-context-type="modify" markdown="1">
## 给递归切片增加中文分隔优先级

1. 比较 `。！？；` 与英文句号、空格的优先级。
2. 固定 max chars，不同时调整 overlap。
3. 增加标题后短段、列表和代码块 case。
4. 比较 boundary coverage 与 duplicate rate。
5. 若协议变化，更新 strategy version 而不是覆盖旧报告。
</section>

<section id="troubleshoot-chunking-strategy" data-learning-context="troubleshoot-chunking-strategy" data-context-type="troubleshoot" markdown="1">
## 从模型、参数、坐标和指标排查

| 现象 | 首先检查 |
| --- | --- |
| 答案跨 chunk 丢失 | 边界模型是否破坏结构 |
| 候选大量重复 | overlap 或 parent 回填是否去重 |
| PDF 引用错页 | chunk 是否继承 block page |
| 语义切片每次变化 | adapter/version/threshold 是否固定 |
| 调大 size 仍失败 | 是否选错模型而非参数 |
| 指标变好但答案变差 | 评估集是否覆盖真实查询 |
</section>

<section id="deepen-real-model-adapter" data-learning-context="deepen-real-model-adapter" data-context-type="deepen" markdown="1">
## 真实语义模型只替换 adapter

本课固定 adapter 只验证向量维度、距离、阈值和坐标协议，不声明真实语义质量。用户自行运行 SentenceTransformer 时，应在独立可选环境保存模型名、revision、维度和归一化；也可接 OpenAI-compatible embedding API。两者都不能改变 `Chunker` 输出契约，且本机 CI 不下载模型。
</section>

<section id="project-learning-assistant-v26" data-learning-context="project-learning-assistant-v26" data-context-type="project" markdown="1">
## 智能学习助手 P5.9 v0.26

- 上一版：v0.25 能接入三种文档并激活验证版本。
- 本课新增：统一 Chunker、五种边界模型、策略身份、父子关联和四类指标。
- 文件：`chunking_lab.py` 与 `test_chunking_lab.py`。
- 保存：chunk ID、block coordinates、heading/page、strategy version 与 parent ID。
- 下一版：把 embedding 契约、精确检索和 HNSW 接到 PostgreSQL/pgvector。
</section>

## 四类学习者入口

- 零基础兴趣：先比较固定窗口和标题感知的切片外观。
- 有基础兴趣：加入中文分隔符并重跑四类指标。
- 零基础求职：解释切片模型与切片参数的区别。
- 有基础求职：讨论父子召回、语义断点、评估偏差和引用保真；只使用本项目证据。

## 完成检查

- 8 项 unittest 与五策略报告通过。
- 每个 chunk 都能切回原 block 文本。
- heading、page 和 parent identity 不丢失。
- 参数变化形成不同 strategy version。
- 四类指标在同一输入与查询集比较。
- 固定 adapter 不冒充真实语义模型。

## 来源与版本

- 核查日期：2026-07-31。
- [Sentence Transformers semantic textual similarity](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)
- [pypdf text extraction limitations](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)

## 下一步

进入第 3 课，使用真实 PostgreSQL 16 + pgvector 管理向量与索引版本。
