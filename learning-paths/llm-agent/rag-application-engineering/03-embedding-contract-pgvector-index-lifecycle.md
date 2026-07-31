<div class="be-tutor-mount" data-tutor-lesson="rag-application-engineering-03" aria-hidden="true"></div>
<section id="overview-pgvector-lifecycle" class="be-page-hero be-lesson-hero" data-learning-context="overview-pgvector-lifecycle" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">RAG 应用工程 · 第 3 / 6 课 · 智能学习助手 P5.9 v0.27</span>
# Embedding 契约、pgvector 与索引生命周期
## 向量先有身份，索引再有 active
```text
runtime=python:3.11+,postgresql:16,pgvector-server:0.8.2,pgvector-python:0.5.0
contract=model+version+dimension+normalized+distance
database=extension:true,exact-cosine:true,hnsw:true,acl-filter:true
lifecycle=building→ready→active→retired
rebuild=active-v1:unchanged,activate-v2:atomic
invariants=no-mixed-model,no-mixed-dimension,owner-before-rank,one-active-index
```
v0.27 用真实 PostgreSQL 16 + pgvector 保存向量。模型名、版本、维度、归一化和距离函数构成不可混用的 embedding 契约；新索引在 building/ready 时不影响线上查询。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>RAG 应用工程 · 3 / 6</strong></div>
  <div><span>前置</span><strong>chunk identity、向量距离、PostgreSQL 事务</strong></div>
  <div><span>环境</span><strong>Docker · PostgreSQL 16 · pgvector 0.8.2 · psycopg 3.3.3</strong></div>
  <div><span>完成后留下</span><strong>VectorStore、迁移、HNSW、索引切换与 8 项集成测试</strong></div>
</div>

## 学习目标

- 保存完整 embedding contract 并拒绝维度混用。
- 在真实 pgvector 上运行余弦精确检索。
- 建立 HNSW 与 ACL 辅助索引，理解近似检索边界。
- 支持同一 index 的增量 upsert。
- 让重建和 active index 原子切换分离。

<section id="concept-embedding-contract" data-learning-context="concept-embedding-contract" data-context-type="concept" markdown="1">
## 向量不是没有来源的数字数组

`model_name + model_version + dimension + normalized + distance` 共同决定向量空间。相同维度不代表相同语义空间，不同模型的向量禁止写入同一 index。查询向量也必须通过 active index 的契约校验。

本课固定 3 维 adapter 只验证数据库和生命周期；真实模型接入必须创建新 index version，不能覆盖旧向量。
</section>

<section id="concept-exact-hnsw-filter" data-learning-context="concept-exact-hnsw-filter" data-context-type="concept" markdown="1">
## 精确检索是基线，HNSW 是可调近似索引

`embedding <=> query` 使用 cosine distance；无近似索引时得到精确排序。HNSW 加速较大数据集，但召回受构建参数、`ef_search`、过滤选择性和候选量影响。课程先用精确结果做正确性基线，再验证 HNSW 索引真实存在，不用小样本执行计划冒充生产性能。

owner 与 index ID 在排序前进入 `WHERE`；其他主体的向量不能先排完再过滤。
</section>

<section id="example-index-rebuild-switch" data-learning-context="example-index-rebuild-switch" data-context-type="example" markdown="1">
## v2 重建不影响 v1 查询

```text
idx-v1:active
idx-v2:building → add chunks → ready
query:still idx-v1
transaction:idx-v1 retired + idx-v2 active
query:now idx-v2
```

唯一部分索引约束数据库中只能有一个 `status='active'`。切换失败则事务回滚。
</section>

<section id="reproduce-pgvector-v27" data-learning-context="reproduce-pgvector-v27" data-context-type="reproduce" markdown="1">
## 启动真实 pgvector 并运行测试

```bash
cd site-src/examples/rag-application-engineering/intelligent-learning-assistant-v27
docker compose up -d --wait
docker compose port postgres 5432
RAG_PGVECTOR_URL=postgresql://rag:rag-local-only@127.0.0.1:PORT/rag_lab \
  ../../../../.venv/bin/python -m unittest -v test_vector_store.py
docker compose down -v
```

8 项集成测试覆盖扩展迁移、维度、精确检索、ACL、HNSW、增量 upsert、building 隔离与原子切换。
</section>

<section id="modify-add-index-rebuild" data-learning-context="modify-add-index-rebuild" data-context-type="modify" markdown="1">
## 增加可恢复索引重建

1. 创建 `idx-v3` 为 building，记录目标契约和 chunk 总数。
2. 按稳定 chunk ID 批量写入并记录游标。
3. 中断后从未完成批次恢复。
4. 核对计数、空向量、维度与固定查询集。
5. 标记 ready 后才允许在事务中 activate。
</section>

<section id="troubleshoot-pgvector-index" data-learning-context="troubleshoot-pgvector-index" data-context-type="troubleshoot" markdown="1">
## 从扩展、适配器、契约和状态排查

| 现象 | 首先检查 |
| --- | --- |
| `vector type not found` | 是否先 `CREATE EXTENSION vector` 再注册 psycopg |
| vector 文本格式错误 | 是否使用 pgvector `Vector` adapter |
| dimension mismatch | 查询与 index contract 是否一致 |
| HNSW 没进入计划 | 数据量、过滤、统计与 planner 成本 |
| 重建时结果变化 | 查询是否错误读取 building index |
| 两个 active | 唯一部分索引与切换事务是否存在 |
</section>

<section id="deepen-provider-index-boundary" data-learning-context="deepen-provider-index-boundary" data-context-type="deepen" markdown="1">
## 模型供应方与索引生命周期解耦

可选 SentenceTransformer 或 OpenAI-compatible API 只实现 `embed(texts) -> vectors`。服务端仍验证批次数、维度、有限值、模型身份和响应顺序。换供应方或模型必须建立新 index，运行固定查询比较后再切换。本机不安装 `sentence-transformers`、不下载权重，CI 使用固定 adapter。
</section>

<section id="project-learning-assistant-v27" data-learning-context="project-learning-assistant-v27" data-context-type="project" markdown="1">
## 智能学习助手 P5.9 v0.27

- 上一版：v0.26 产出带稳定坐标与策略版本的 chunks。
- 本课新增：embedding contract、pgvector 迁移、精确/HNSW、ACL、增量写入与 active index 切换。
- 文件：`migration.sql`、`vector_store.py`、`compose.yml` 与 `test_vector_store.py`。
- 保存：index identity、模型契约、chunk vectors 和生命周期状态。
- 下一版：加入查询理解、过滤、多路召回、RRF 和策略路由。
</section>

## 四类学习者入口

- 零基础兴趣：沿 building → ready → active 理解为什么重建不应影响查询。
- 有基础兴趣：增加批量重建 checkpoint。
- 零基础求职：解释同维度向量为什么仍不能混用。
- 有基础求职：讨论精确/HNSW、过滤、索引切换和线上回滚；只使用本项目证据。

## 完成检查

- 8 项真实 PostgreSQL/pgvector 集成测试通过。
- vector 扩展、HNSW 和 ACL 索引由迁移创建。
- 维度错误在写入前拒绝。
- owner 过滤在向量排序前执行。
- building/ready 不影响 active 查询。
- 切换事务保证只有一个 active index。

## 来源与版本

- 核查日期：2026-07-31。
- [pgvector](https://github.com/pgvector/pgvector)
- [PostgreSQL partial indexes](https://www.postgresql.org/docs/16/indexes-partial.html)
- [psycopg transactions](https://www.psycopg.org/psycopg3/docs/basic/transactions.html)

## 下一步

进入第 4 课，把关键词、向量、过滤、改写与多查询组织成严格检索计划。
