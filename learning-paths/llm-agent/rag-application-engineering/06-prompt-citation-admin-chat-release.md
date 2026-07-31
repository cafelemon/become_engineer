<div class="be-tutor-mount" data-tutor-lesson="rag-application-engineering-06" aria-hidden="true"></div>
<section id="overview-rag-application" class="be-page-hero be-lesson-hero" data-learning-context="overview-rag-application" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">RAG 应用工程 · 第 6 / 6 课 · 智能学习助手 P5.11 v0.30</span>
# Prompt、引用、管理台、聊天页与发布
## 从上传文档到带引用回答的可运行应用
```text
application=admin:true,chat:true,prompt-versioned:true
ingestion=job:succeeded,version:active,replayed:false
retrieval=authorized:1,reranked:1,context:1
answer=refused:false,citations:1
citation=source+version+page+block+chunk:true
runtime=models:fixed,network:disabled,secrets:none
```
v0.30 把来源管理、版本接入、ingestion 作业、检索调试、Prompt 版本、上下文包、拒答和引用接进 FastAPI 与原生 TypeScript 页面，并提供健康、指标和真实 PostgreSQL/pgvector schema。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>RAG 应用工程 · 6 / 6</strong></div>
  <div><span>前置</span><strong>接入、切片、pgvector、路由、重排与压缩</strong></div>
  <div><span>环境</span><strong>Python 3.11 · FastAPI · TypeScript · PostgreSQL/pgvector</strong></div>
  <div><span>完成后留下</span><strong>管理台、聊天页、稳定 API、18 项测试与 Compose</strong></div>
</div>

## 学习目标

- 让来源、版本、作业、chunk、检索运行、会话和消息拥有稳定 API。
- 将系统指令、任务指令、证据和用户输入分层，不把文档内容当命令。
- 在管理台查看失败原因、阶段候选、最终上下文与精确引用。
- 区分确定性应用测试、真实 pgvector schema 证据与尚未运行的模型效果。

<section id="concept-prompt-boundaries" data-learning-context="concept-prompt-boundaries" data-context-type="concept" markdown="1">
## Prompt 是有版本的数据装配契约

回答请求依次装配：不可被文档覆盖的系统边界、回答任务、经过 ACL 的证据包、用户问题和输出 Schema。`prompt_version=grounded-answer-v1` 与检索 run 一起保存。来源正文用明确分隔符标记为不可信数据；其中的“忽略规则”“调用工具”等句子不能变成指令。

页面展示 Prompt 版本和上下文包，不展示秘密、Authorization 或隐式思维链。
</section>

<section id="concept-api-resource-boundaries" data-learning-context="concept-api-resource-boundaries" data-context-type="concept" markdown="1">
## API 围绕资源和状态，而不是页面按钮

| 资源 | 稳定操作 |
| --- | --- |
| knowledge source | 创建、停用、查询版本、回滚 |
| document version | 上传 Markdown/HTML/数字文本 PDF |
| ingestion job | 查询状态、失败码和尝试次数 |
| retrieval run | 调试阶段计数、候选与最终上下文 |
| chat session/message | 创建会话、提交问题、返回拒答或引用 |

每个请求都先解析主体；他人来源和会话统一返回 404，未授权内容不会进入候选、Prompt、日志或 trace。
</section>

<section id="example-admin-chat-flow" data-learning-context="example-admin-chat-flow" data-context-type="example" markdown="1">
## 管理台和聊天页共享同一条证据链

```text
POST source → POST version → job:succeeded → version:active
POST retrieval/debug → authorized → lexical → reranked → context
POST chat/session → POST message → answer + prompt_version + citations
```

引用返回 `source_id + version + page/block + chunk_id`。找不到证据时返回明确拒答和空引用，不用模型常识填空。
</section>

<section id="reproduce-rag-application-v30" data-learning-context="reproduce-rag-application-v30" data-context-type="reproduce" markdown="1">
## 运行 API、前端和真实 schema 测试

```bash
cd site-src/examples/rag-application-engineering/intelligent-learning-assistant-v30
../../../../.venv/bin/python -m unittest -v test_knowledge_service.py test_api.py
../../web-engineering/learning-dashboard-v12/node_modules/.bin/tsc -p tsconfig.json
../../../../.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```

14 项离线测试覆盖幂等上传、版本切换/回滚、ACL、停用、拒答、引用、会话隔离、Prompt/上下文、指标与 API。真实容器另运行 4 项 schema 测试，验证 vector 扩展、11 张表、唯一约束和维度约束。
</section>

<section id="modify-add-ingestion-failure" data-learning-context="modify-add-ingestion-failure" data-context-type="modify" markdown="1">
## 给解析失败增加可恢复入口

1. 为 `ingestion_jobs` 增加 `failed` 与稳定 `error_code`。
2. 数字文本为空的 PDF 标记 `ocr_required`，不要假装成功。
3. 管理台显示失败原因和“按同一幂等键重试”。
4. 新作业成功前不替换 active version。
5. 为失败、重试、重复点击和旧版本仍可查询增加测试。
</section>

<section id="troubleshoot-rag-application" data-learning-context="troubleshoot-rag-application" data-context-type="troubleshoot" markdown="1">
## 沿应用链路定位，不只看最终回答

| 现象 | 首先检查 |
| --- | --- |
| 上传后搜不到 | job、active version、chunk 数与 active index |
| 调试有候选但回答拒绝 | 重排/压缩后 context 是否为 0 |
| 引用打开错误版本 | citation 是否携带 version 而非只带 source |
| 他人文档出现在调试台 | ACL 是否在召回前执行 |
| 页面刷新内容丢失 | 是否误用教学内存 adapter；生产 adapter 是否持久化 |
| `/health/live` 正常但不能检索 | `/health/ready` 是否检查数据库与 active index |
| 指标基数暴涨 | 是否把 source、query 或 session 当 label |
</section>

<section id="deepen-delivery-boundary" data-learning-context="deepen-delivery-boundary" data-context-type="deepen" markdown="1">
## 三类证据必须分开陈述

- 固定 adapter：证明流程、状态、权限、引用和失败边界可回归，不证明模型效果。
- 真实 PostgreSQL/pgvector：证明 schema、约束、精确/HNSW、增量重建和 active index 切换，不等于生产容量。
- 浏览器与 Compose：证明应用可启动、可操作和可观察，不等于公网 TLS、高可用或真实用户验收。

本课默认服务为离线内存 adapter，Compose 应用真实 schema；替换为持久化 repository 后才可声称重启不丢数据。
</section>

<section id="project-learning-assistant-v30" data-learning-context="project-learning-assistant-v30" data-context-type="project" markdown="1">
## 智能学习助手 P5.11 v0.30

- 上一版：v0.29 产出可引用的上下文包。
- 本课新增：FastAPI、原生 TypeScript 管理台/聊天页、版本化 Prompt、稳定资源 API、拒答、健康、指标、Compose 和最终 RAG schema。
- 文件：`app.py`、`knowledge_service.py`、`src/app.ts`、`schema.sql`、`compose.yml` 与测试。
- 组级验收：六课 58 项代码/数据库测试、72 卡/144 问、真实 pgvector、18 个浏览器模式、严格构建和站内链接。
- 下一组：用显式状态图把 RAG、工具、审批和恢复编排成 Agent 应用。
</section>

## 四类学习者入口

- 零基础兴趣：按“上传 → 搜索 → 回答 → 点引用”完成一条路径。
- 有基础兴趣：增加 ingestion 失败状态并在管理台恢复。
- 零基础求职：解释为什么健康、指标和拒答也是 RAG 产品能力。
- 有基础求职：展示 API、ACL、真实 schema、引用契约和浏览器证据；不编造面试题频率。

## 完成检查

- 14 项离线测试、4 项真实 PostgreSQL/pgvector schema 测试和 TypeScript 编译通过。
- 管理台能显示来源、版本、作业；聊天页能显示阶段、上下文、Prompt 版本和引用。
- 无证据时拒答，跨主体资源为 404。
- 指标保持低基数，健康端点分离。
- 无 JavaScript 时仍可读 API 与启动说明。
- 固定 adapter、真实数据库和生产能力边界写清楚。

## 来源与版本

- 核查日期：2026-07-31。
- [FastAPI](https://fastapi.tiangolo.com/)
- [pgvector](https://github.com/pgvector/pgvector)
- [OWASP LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)

## 下一步

进入 Agent 应用编排与交付第 1 课：工作流、路由器与 Agent 的边界。
