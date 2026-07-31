<div class="be-tutor-mount" data-tutor-lesson="llm-rag-eval-01" aria-hidden="true"></div>
<section id="overview-reproducible-corpus" class="be-page-hero be-lesson-hero" data-learning-context="overview-reproducible-corpus" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">检索、RAG 与评估 · 第 1 / 6 课 · 智能学习助手 P5.2 v0.7</span>
# 语料文档契约、来源身份与可复现索引
## 先证明索引里是什么，再讨论如何检索
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
corpus=id:become-engineer-public,schema:1,documents:3
order=http-status,python-venv,sqlite-transaction
fingerprint=8d59f13bd6b74b5d5903adbd065b2635b5ee0f66fabb735f4052d9ded9b22cab
reordered=fingerprint-equal:True
identity=document-id+title+source-uri+updated-at+content+content-sha256
validation=empty:false,duplicate-id:false,duplicate-source:false,extra-fields:false
persistence=utf8-json,canonical:true,temporary-write:true,fsync:true,atomic-replace:true
logs=content:none,source-uri:none,corpus-id:allowed,fingerprint:allowed,count:allowed
invariants=source-before-index,content-hash-verified,input-order-independent,no-rag-generation,no-tools
```
v0.7 只做语料和索引快照：稳定文档 ID、可回到课程锚点的来源、更新时间、内容摘要、Schema 版本和整个语料指纹。相同文档即使输入顺序不同，也生成同一快照身份。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>LLM 应用工程化 · 1 / 6</strong></div>
  <div><span>前置</span><strong>结构化输出、哈希、文件原子替换</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 合成公开语料</strong></div>
  <div><span>完成后留下</span><strong>语料快照、完整性门禁与 8 项测试</strong></div>
</div>

## 学习目标

- 用文档 ID、标题、来源 URI、更新时间和正文建立输入契约。
- 区分内容 SHA-256、语料 fingerprint、来源可信与内容正确。
- 先按稳定 ID 排序，再生成与输入顺序无关的规范快照。
- 拒绝空语料、重复 ID、重复来源、额外字段和不兼容 Schema。
- 用临时文件、flush/fsync 与原子 replace 保存索引 manifest。
- 加载时先核对单文档摘要，再核对整体指纹和规范顺序。

<section id="concept-document-identity" data-learning-context="concept-document-identity" data-context-type="concept" markdown="1">
## 文档身份不是数组下标

数组第 0 项会因导入顺序变化，不能成为持久引用。`document_id` 是稳定 slug，`source_uri` 指向 `course://...#anchor`，让后续 chunk 和 citation 能回到原始课程位置。

标题可以修改，正文也可以更新；只要这些字段变化，内容摘要或语料 fingerprint 就会变化。不要用哈希值代替可读来源。
</section>

<section id="concept-hash-trust-boundary" data-learning-context="concept-hash-trust-boundary" data-context-type="concept" markdown="1">
## 哈希证明一致，不证明可信

`content_sha256` 可以发现保存后的正文被改写，语料 fingerprint 可以标识一次完整快照。它们不能证明课程内容真实、来源拥有授权，或导入前没有恶意文本。

来源准入、许可、隐私检查和内容评审发生在索引之前；本课只对已经选定的合成公开语料建立可复现身份。
</section>

<section id="example-canonical-snapshot" data-learning-context="example-canonical-snapshot" data-context-type="example" markdown="1">
## 规范序列化消除无意义差异

```python
ordered = sorted(documents, key=lambda item: item.document_id)
records = tuple(document_record(item) for item in ordered)
identity = {
    "schema_version": 1,
    "corpus_id": corpus_id,
    "documents": records,
}
fingerprint = sha256(canonical_json(identity))
```

规范 JSON 固定 UTF-8、键排序和分隔符。重新排列输入不会改变结果，但标题、来源、更新时间、正文或 Schema 变化都会进入指纹。
</section>

<section id="reproduce-corpus-v07" data-learning-context="reproduce-corpus-v07" data-context-type="reproduce" markdown="1">
## 保存、重开并篡改一份临时索引

```bash
cd site-src/examples/llm-rag-eval/intelligent-learning-assistant-v07
python3 -m unittest -v test_corpus_index.py
python3 corpus_index.py
```

8 项测试覆盖契约、重排稳定性、重复身份、内容变化、原子保存/重开、正文篡改、额外字段和脱敏固定报告。所有文件只写入测试临时目录。
</section>

<section id="modify-corpus-schema" data-learning-context="modify-corpus-schema" data-context-type="modify" markdown="1">
## 增加许可字段并升级 Schema

1. 给文档增加 `license_id`，只接受事先登记的值。
2. 把 Schema 从 1 升到 2，不让旧 loader 悄悄忽略字段。
3. 决定旧快照是显式迁移还是拒绝，不在读取时猜默认许可。
4. 把字段加入文档摘要和整体 fingerprint。
5. 新增一次 v1 拒绝、一次 v2 成功和一次未知许可失败测试。

许可元数据不能证明实际授权，但能让审核决策进入可追溯快照。
</section>

<section id="troubleshoot-corpus-index" data-learning-context="troubleshoot-corpus-index" data-context-type="troubleshoot" markdown="1">
## 从单文档到整份快照逐层定位

| 错误 | 先检查 |
| --- | --- |
| `invalid_document` | ID、来源锚点、时区、标题或正文 |
| `duplicate_document_id` | 同一稳定身份是否被重复导入 |
| `duplicate_source_uri` | 两个 ID 是否指向同一来源位置 |
| `content_hash_mismatch` | 保存后正文是否被篡改或编码变化 |
| `snapshot_fingerprint_mismatch` | 标题、来源、时间或 manifest 是否变化 |
| `noncanonical_order` | 文件是否绕过 builder 手工重排 |
| 临时文件残留 | replace 前是否异常，finally 是否清理 |
</section>

<section id="deepen-corpus-versioning" data-learning-context="deepen-corpus-versioning" data-context-type="deepen" markdown="1">
## 版本要能回答“评估用的是哪一批知识”

模型版本固定而语料变化，也会改变检索和回答结果。因此评估报告至少关联 corpus fingerprint、检索配置、查询集版本和代码版本。

真实站点还要处理删除、重命名、重定向、抓取失败和访问控制。本课使用三个明确课程 URI，不实现爬虫，也不把本地快照描述成知识库服务。
</section>

<section id="deepen-document-lifecycle-map" data-learning-context="deepen-document-lifecycle-map" data-context-type="deepen" markdown="1">
## 从语料快照走向文档生命周期

真实知识库不能把“上传一个文件”直接等同于“检索已经可用”。一份来源至少要经过 `registered → parsing → indexed → active`，失败时进入 `failed`，被新版本替代后进入 `superseded`，删除则先标记 `tombstoned`，再从活动索引中撤出。这样管理台才能解释用户看到的是哪一版知识，而不是靠文件名猜测。

| 对象 | 负责回答 | 不应该混在一起的字段 |
| --- | --- | --- |
| knowledge source | 谁拥有、从哪里来、谁能访问 | 解析结果、向量 |
| document version | 本次内容 SHA、解析器版本、创建时间 | 当前是否对所有用户可见 |
| ingestion job | 解析、切片、embedding、建索引进行到哪一步 | 文档永久身份 |
| active index | 哪组文档版本正在服务查询 | 历史失败详情 |

同一内容 SHA 的重复请求应返回同一个已完成版本或幂等 replay；新内容生成新版本，在解析和索引全部成功前不能替换 active version。回滚只切换到已经验证过的版本，不重新猜测旧文件。权限、许可和 owner 在解析前检查，删除也必须让旧 chunk、embedding 和缓存退出可检索集合。

后续“RAG 应用工程”会把这些对象落到 PostgreSQL、异步 ingestion 状态和管理台。本课先保留最小快照实验，因为生命周期服务最终仍要依赖这里的稳定身份、内容摘要和规范 fingerprint。
</section>

<section id="project-learning-assistant-v07" data-learning-context="project-learning-assistant-v07" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.2 v0.7

- 上一组：P5.1 v0.6 完成可验证模型调用与安全交付。
- 本课新增：文档契约、来源身份、摘要、规范快照、原子保存和加载门禁。
- 文件：`corpus_index.py` 与 `test_corpus_index.py`。
- 保存：固定语料 fingerprint、8 项测试和一次 Schema v2 修改记录。
- 下一版：在同一文档快照上建立倒排索引和 BM25 关键词基线。
- 应用承接：后续把快照扩成 source、version、ingestion job 与 active index，不让上传成功冒充索引可用。
</section>

## 四类学习者入口

- 零基础兴趣：比较同三张文档卡不同排列为何指纹相同。
- 有基础兴趣：实现许可字段与显式 Schema 迁移。
- 零基础求职：用“来源—文档—索引快照”讲清 RAG 输入边界。
- 有基础求职：解释内容哈希、语料版本和来源信任的区别；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 相同文档的不同输入顺序产生同一 fingerprint。
- 重复 ID、重复来源、空语料和额外字段默认拒绝。
- 加载时先发现正文摘要不符，再检查整体指纹。
- 写入采用同目录临时文件、fsync 与原子 replace，异常后无临时残留。
- 日志不保存正文或来源 URI，只允许 corpus ID、指纹和计数。

## 来源与版本

- 核查日期：2026-07-26。
- 适用环境：Python 3.11+ 标准库；合成公开语料，自动测试离线。
- [Retrieval-Augmented Generation 原始论文](https://arxiv.org/abs/2005.11401)
- [Python hashlib](https://docs.python.org/3.11/library/hashlib.html)
- [Python json](https://docs.python.org/3.11/library/json.html)
- [Python os.replace](https://docs.python.org/3.11/library/os.html#os.replace)

## 下一步

进入第 2 课，在同一快照上建立可解释的倒排索引、BM25 分数和稳定 Top-k。
