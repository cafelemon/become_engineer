<div class="be-tutor-mount" data-tutor-lesson="rag-application-engineering-04" aria-hidden="true"></div>
<section id="overview-retrieval-routing" class="be-page-hero be-lesson-hero" data-learning-context="overview-retrieval-routing" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">RAG 应用工程 · 第 4 / 6 课 · 智能学习助手 P5.9 v0.28</span>
# 查询理解、过滤、混合检索与策略路由
## 模型给受限计划，应用执行受控检索
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
plan=strategy:hybrid,lexical:8,vector:8,max:12
filter=authorized:1,private-candidate:false
candidates=lexical:1,vector:1,fused:1
result=python-1,budget-ok:true,sql-from-model:false
invariants=normalized-query,strict-plan,acl-first,rrf,dedupe,bounded-decomposition
```
v0.28 把查询规范化、元数据/ACL、关键词、向量、RRF、多查询、问题分解和父子召回组织成严格计划。模型不能输出 SQL，也不能扩大服务端预算。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>RAG 应用工程 · 4 / 6</strong></div>
  <div><span>前置</span><strong>BM25、向量索引、ACL、父子 chunk</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 固定向量 adapter</strong></div>
  <div><span>完成后留下</span><strong>RetrievalPlan、路由器、RRF 与 8 项测试</strong></div>
</div>

## 学习目标

- 规范化查询但保留原始输入的审计边界。
- 只允许白名单过滤字段和固定预算。
- 按查询类型选择 lexical、vector、hybrid、multi-query 或 decomposition。
- 在召回前执行主体与元数据过滤。
- 融合、去重、父块映射和候选预算都有阶段计数。

<section id="concept-strict-retrieval-plan" data-learning-context="concept-strict-retrieval-plan" data-context-type="concept" markdown="1">
## RetrievalPlan 是数据，不是任意查询语言

计划只含 `strategy`、`lexical_k`、`vector_k`、`max_candidates`、白名单 filters 和有界 rewrites。未知策略、负数、超过 40 的预算或 `raw_sql` 过滤字段立即拒绝。应用把计划映射到预定义查询，模型没有数据库连接和 SQL 拼接权。
</section>

<section id="concept-route-and-budget" data-learning-context="concept-route-and-budget" data-context-type="concept" markdown="1">
## 路由按问题特征选择成本

| 查询 | 策略 |
| --- | --- |
| 课程 ID、错误码、精确术语 | lexical |
| 自然语言同义表达 | vector/hybrid |
| 显式“换句话”或改写 | bounded multi-query |
| “比较 A 与 B” | bounded decomposition |
| 带 course/owner 条件 | ACL + metadata before recall |

分解最多三条子查询；多路结果经 RRF 后仍受最终 max candidates 约束。
</section>

<section id="example-acl-first-pipeline" data-learning-context="example-acl-first-pipeline" data-context-type="example" markdown="1">
## 私有文档从未成为候选

```text
documents:4
subject+course filter:2
lexical:2
vector:2
rrf+dedupe:2
context candidate:2
private-other-owner:0
```

ACL 不是生成前提示，而是检索数据入口条件。
</section>

<section id="reproduce-retrieval-router-v28" data-learning-context="reproduce-retrieval-router-v28" data-context-type="reproduce" markdown="1">
## 运行路由、过滤与融合

```bash
cd site-src/examples/rag-application-engineering/intelligent-learning-assistant-v28
python3 -m unittest -v test_retrieval_router.py
python3 retrieval_router.py
```

8 项测试覆盖默认路由、精确 ID、分解预算、坏过滤、ACL、RRF、候选预算和父块去重。
</section>

<section id="modify-add-time-filter" data-learning-context="modify-add-time-filter" data-context-type="modify" markdown="1">
## 增加受控版本时间过滤

1. 在 Schema 增加 `updated_after` ISO 日期字段。
2. 严格解析日期，拒绝任意表达式。
3. 由服务端参数化 SQL 实现。
4. 保证 owner ACL 仍在同一查询中。
5. 给无权内容和错误日期分别加测试。
</section>

<section id="troubleshoot-retrieval-router" data-learning-context="troubleshoot-retrieval-router" data-context-type="troubleshoot" markdown="1">
## 从计划、过滤、分路和预算排查

| 现象 | 首先检查 |
| --- | --- |
| 精确 ID 排名低 | 是否错误只走 vector |
| 私有内容出现在 debug | ACL 是否晚于召回 |
| 多查询延迟暴涨 | rewrite 数和各路 k 是否有界 |
| RRF 后重复 | 是否按 chunk ID 去重 |
| parent 重复占满 | 是否按 parent ID 再去重 |
| 模型可改变 SQL | 是否把计划字段错误直拼查询 |
</section>

<section id="deepen-routing-evaluation" data-learning-context="deepen-routing-evaluation" data-context-type="deepen" markdown="1">
## 路由也要单独评估

固定查询集应标注预期策略、允许过滤、相关 chunk 和候选预算。分别统计 route accuracy、filtered Recall@k、RRF 后 MRR、重复率与各阶段候选数。路由错误与检索器错误不能混成“答案不好”。
</section>

<section id="project-learning-assistant-v28" data-learning-context="project-learning-assistant-v28" data-context-type="project" markdown="1">
## 智能学习助手 P5.9 v0.28

- 上一版：v0.27 提供 active pgvector index。
- 本课新增：严格 RetrievalPlan、查询路由、ACL/metadata、关键词/向量、RRF、多查询、分解和父块去重。
- 文件：`retrieval_router.py` 与 `test_retrieval_router.py`。
- 保存：计划、各阶段候选计数、淘汰原因与最终 chunk/parent ID。
- 下一版：对有界候选做二阶段重排、抽取式压缩和上下文选择。
</section>

## 四类学习者入口

- 零基础兴趣：沿私有文档为 0 的流水线理解 ACL 前置。
- 有基础兴趣：增加日期过滤并维持参数化执行。
- 零基础求职：解释为什么不能所有查询都固定混合检索。
- 有基础求职：讨论路由 Schema、RRF、分解、预算和过滤召回；只使用本项目证据。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 未授权内容不进入任何候选列表。
- 未知过滤和超预算计划拒绝。
- RRF 稳定去重，父 ID 不重复占位。
- 分解和多查询有明确上限。
- 模型不能输出或执行任意 SQL。

## 来源与版本

- 核查日期：2026-07-31。
- [pgvector hybrid search notes](https://github.com/pgvector/pgvector)
- [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

## 下一步

进入第 5 课，建立 Reranker 与 ContextCompressor 接口。
