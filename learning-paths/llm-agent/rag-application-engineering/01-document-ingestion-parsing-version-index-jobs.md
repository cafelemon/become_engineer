<div class="be-tutor-mount" data-tutor-lesson="rag-application-engineering-01" aria-hidden="true"></div>
<section id="overview-document-ingestion" class="be-page-hero be-lesson-hero" data-learning-context="overview-document-ingestion" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">RAG 应用工程 · 第 1 / 6 课 · 智能学习助手 P5.9 v0.25</span>
# 文档接入、解析、版本与索引作业
## 上传不是可检索，成功激活才是
```text
runtime=python:3.11+,pypdf:6.14.2,storage:sqlite,network:disabled
upload=version:1,replay:false,checksum:true
job=status:indexed,attempts:1,blocks:1
active=source:guide,version:1,atomic:true
formats=markdown:true,html:true,digital-pdf:true,scanned-pdf:ocr_required
invariants=source-owner,checksum-idempotency,version-history,job-state,activate-after-index,tombstone
```
v0.25 把一个文件拆成知识来源、不可变版本、解析块和索引作业。新版本只有解析与索引成功后才能原子激活；失败版本不能替换线上知识。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>RAG 应用工程 · 1 / 6</strong></div>
  <div><span>前置</span><strong>文档契约、来源坐标、SQLite 事务</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · pypdf 6.14.2 · 临时 SQLite</strong></div>
  <div><span>完成后留下</span><strong>IngestionStore、三种解析器、作业状态与 8 项测试</strong></div>
</div>

## 学习目标

- 区分 knowledge source、document version、parsed block 和 ingestion job。
- 用内容 SHA 实现重复上传的幂等 replay。
- 解析 Markdown、HTML 和数字文本 PDF，并保留标题路径或页码。
- 扫描或空文本 PDF 返回 `ocr_required`，不伪造 OCR。
- 失败版本不影响 active 指针，停用后旧内容退出服务。

<section id="concept-source-version-job" data-learning-context="concept-source-version-job" data-context-type="concept" markdown="1">
## 来源、版本、块和作业分开保存

`knowledge_source` 保存主体、名称和 active version；`document_version` 保存 media type、checksum、不可变内容与状态；`document_block` 保存解析文本、标题路径和页码；`ingestion_job` 保存 pending/succeeded/failed、attempts 和稳定错误码。

```text
source
├── version 1 ─ blocks ─ job succeeded ─ active
└── version 2 ─ no blocks ─ job failed:ocr_required
```

查询只读取 enabled source 的 active version，不读取“最新上传序号”。
</section>

<section id="concept-parser-boundaries" data-learning-context="concept-parser-boundaries" data-context-type="concept" markdown="1">
## 解析器只声明它真正看见的内容

Markdown 保存标题路径；HTML 使用标准解析器提取可见文本，不用正则假装理解 DOM；PDF 逐页调用 pypdf 文本提取并保存 1-based 页码。没有文本层时返回 `ocr_required`。pypdf 不是 OCR，也不能保证复杂表格、阅读顺序或图片文字的语义完整。
</section>

<section id="example-version-activation" data-learning-context="example-version-activation" data-context-type="example" markdown="1">
## v1 在线，v2 失败

| 动作 | v1 | v2 | active |
| --- | --- | --- | --- |
| v1 indexed | indexed | — | none |
| activate v1 | active | — | 1 |
| upload scan | active | uploaded | 1 |
| run v2 | active | failed:ocr_required | 1 |
| activate v2 | active | refused | 1 |

失败原因可见，但 v2 的空块不会污染查询。
</section>

<section id="reproduce-document-ingestion-v25" data-learning-context="reproduce-document-ingestion-v25" data-context-type="reproduce" markdown="1">
## 运行真实解析与版本实验

```bash
cd site-src/examples/rag-application-engineering/intelligent-learning-assistant-v25
../../../../.venv/bin/python -m unittest -v test_document_ingestion.py
../../../../.venv/bin/python document_ingestion.py
```

8 项测试覆盖 Markdown、HTML、无文本 PDF、重复上传、成功激活、失败保护、旧版回滚和停用。
</section>

<section id="modify-add-job-retry" data-learning-context="modify-add-job-retry" data-context-type="modify" markdown="1">
## 给失败作业增加有界重试

1. 只允许 transient parser error 自动重试，`ocr_required` 不自动循环。
2. 保存 `max_attempts=3` 与下一次执行时间。
3. 同一 job ID 重试，不能创建重复版本。
4. 成功后清空 error code，但保留 attempts。
5. 超过预算进入 `dead_letter`，等待人工处理。
</section>

<section id="troubleshoot-document-ingestion" data-learning-context="troubleshoot-document-ingestion" data-context-type="troubleshoot" markdown="1">
## 从媒体、checksum、作业和 active 排查

| 错误 | 首先检查 |
| --- | --- |
| `unsupported_media_type` | Content-Type 是否在允许列表 |
| `empty_document` | Markdown/HTML 是否只有标签或空白 |
| `ocr_required` | PDF 是否没有数字文本层 |
| `version_not_ready` | 作业是否真正 indexed |
| 上传两次产生两版 | checksum 幂等查询是否在插入前 |
| 新版失败后知识消失 | 是否错误提前切换 active |
</section>

<section id="deepen-ingestion-api-boundary" data-learning-context="deepen-ingestion-api-boundary" data-context-type="deepen" markdown="1">
## API 返回资源身份，不假装同步完成

稳定接口将采用 `POST /api/knowledge-sources`、`POST /api/knowledge-sources/{id}/versions`、`GET /api/ingestion-jobs/{id}`、`POST /api/knowledge-sources/{id}/versions/{version}/activate` 和停用接口。上传返回 version 与 job ID；客户端轮询作业，不把 HTTP 201 当作索引已可用。

owner、许可和 ACL 在读取内容前校验。普通日志只保存 source/version/job ID、状态、大小和错误码，不保存原文。
</section>

<section id="project-learning-assistant-v25" data-learning-context="project-learning-assistant-v25" data-context-type="project" markdown="1">
## 智能学习助手 P5.9 v0.25

- 上一版：v0.24 已建立 Agent 安全发布门禁。
- 本课新增：来源、版本、解析块、索引作业、幂等上传、激活/停用和扫描 PDF 边界。
- 文件：`document_ingestion.py`、`test_document_ingestion.py` 与固定依赖。
- 保存：source、version、checksum、block coordinates、job state 和 active pointer。
- 下一版：用统一 Chunker 比较五种切片模型与参数。
</section>

## 四类学习者入口

- 零基础兴趣：沿 v1 在线、v2 失败的表格理解“上传不等于可用”。
- 有基础兴趣：实现 transient retry 与 dead letter。
- 零基础求职：解释来源、版本、块和作业为什么要拆表。
- 有基础求职：讨论幂等上传、原子激活、删除传播和 PDF 解析边界；只使用本项目证据，不声称企业高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 三种文档格式走真实解析器。
- 无文本 PDF 稳定返回 `ocr_required`。
- checksum 重放不创建重复版本。
- 失败版本不替换 active，旧验证版本可重新激活。
- 停用后 active 指针清空。

## 来源与版本

- 核查日期：2026-07-31。
- [pypdf text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
- [Python html.parser](https://docs.python.org/3.11/library/html.parser.html)
- [SQLite transactions](https://www.sqlite.org/lang_transaction.html)

## 下一步

进入第 2 课，用同一份解析块对比固定、递归、结构感知、语义断点和父子切片。
