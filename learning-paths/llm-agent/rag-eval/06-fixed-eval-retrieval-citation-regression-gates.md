<div class="be-tutor-mount" data-tutor-lesson="llm-rag-eval-06" aria-hidden="true"></div>
<section id="overview-rag-evaluation" class="be-page-hero be-lesson-hero" data-learning-context="overview-rag-evaluation" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">检索、RAG 与评估 · 第 6 / 6 课 · 智能学习助手 P5.4 v0.12</span>
# 固定评估集、检索指标、引用质量与回归门禁
## 改进必须在同一协议上量化，安全退化直接阻止交付
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
dataset=cases:4,answerable:3,unanswerable:1,fingerprint:1dfb11add9b5
baseline=recall@3:0.666667,mrr:0.750000,citation-validity:1.000000,abstention-accuracy:1.000000
candidate=recall@3:1.000000,mrr:1.000000,citation-validity:1.000000,abstention-accuracy:1.000000
gate=allowed:true,reasons:none
denominators=recall:answerable-cases,mrr:answerable-cases,citations:emitted-citations,abstention:all-cases
rejection=empty-set:true,coverage-mismatch:true,duplicate-rank:true,unknown-rank:true,no-citations:true,incomparable:true
artifacts=dataset-fingerprint:true,baseline:true,candidate:true,gate:true,deterministic-json:true
logs=query:none,answer:none,citation-text:none,case-id:allowed,metrics:allowed,reason:allowed
invariants=fixed-eval,recall-at-k,mrr,citation-validity,abstention-accuracy,no-regression,no-generation,no-tools
```
v0.12 冻结四个合成案例和语料 ID，分别计算检索覆盖、首个相关结果位置、引用门禁结果与拒答决策。候选必须在同一 fingerprint 和 Top-k 下比较；检索指标不得退化，引用与拒答安全指标必须为 1。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>LLM 应用工程化 · 6 / 6</strong></div>
  <div><span>前置</span><strong>Top-k、相关性标注、citation 门禁、拒答状态</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 固定离线案例</strong></div>
  <div><span>完成后留下</span><strong>评估集指纹、四项指标、基线对比与 8 项测试</strong></div>
</div>

## 学习目标

- 冻结 case ID、query、相关 chunk 和 answerable 标签。
- 明确 Recall@k、MRR、引用有效率与拒答准确率的分母。
- 区分“找到了证据”“证据排得靠前”“引用有效”“该答时答/该拒时拒”。
- 校验输出完整覆盖评估集且排名不含重复或语料外 ID。
- 只比较同一数据 fingerprint、Top-k 和案例数量的报告。
- 用可解释原因阻止检索退化或安全指标不满分的候选。

<section id="concept-fixed-eval-set" data-learning-context="concept-fixed-eval-set" data-context-type="concept" markdown="1">
## 评估集本身也是版本化产物

每个 `EvalCase` 固定 ID、query、相关 chunk 集与 answerable。按 case ID 规范排序后生成 SHA-256 fingerprint，因此文件重排不改变身份，问题或标注变化会形成新协议。

四个案例只用于教学计算，不代表真实用户分布。真实交付还要增加边界、长尾、语言、权限和对抗分层，并由人工复核相关性标签。
</section>

<section id="concept-rag-metrics" data-learning-context="concept-rag-metrics" data-context-type="concept" markdown="1">
## 四个指标回答四个问题

- `Recall@k`：answerable 案例的相关 chunk 有多少进入前 k。
- `MRR`：每个 answerable 案例首个相关结果的倒数名次，再取平均。
- `citation validity`：所有已发出 citation 中，通过第 5 课门禁的比例。
- `abstention accuracy`：全部案例中，answered/abstained 是否匹配 answerable 标签。

Recall 能处理一个问题多个相关 chunk；MRR 更关心第一个相关结果是否靠前。引用有效不代表 claim 事实正确，拒答准确也不代表答案内容质量完整。
</section>

<section id="example-regression-gate" data-learning-context="example-regression-gate" data-context-type="example" markdown="1">
## 候选先与基线比较，再过安全底线

```python
if candidate.recall_at_k < baseline.recall_at_k:
    reasons.append("recall_at_k_regressed")
if candidate.mrr < baseline.mrr:
    reasons.append("mrr_regressed")
if candidate.citation_validity < 1:
    reasons.append("citation_validity_below_1")
if candidate.abstention_accuracy < 1:
    reasons.append("abstention_accuracy_below_1")
```

固定候选把 SQLite 相关 chunk 从第 4 名移到第 1 名，所以 Recall@3 从 2/3 到 1、MRR 从 0.75 到 1。安全指标保持满分，门禁通过。
</section>

<section id="reproduce-eval-v12" data-learning-context="reproduce-eval-v12" data-context-type="reproduce" markdown="1">
## 回放指标、协议错误和四类退化

```bash
cd site-src/examples/llm-rag-eval/intelligent-learning-assistant-v12
python3 -m unittest -v test_rag_evaluation.py
python3 rag_evaluation.py
```

8 项测试覆盖固定指标、多相关项 Recall、指纹稳定/敏感、Top-k/覆盖、坏排名/输出形状、通过门禁、四类退化与固定报告。
</section>

<section id="modify-eval-case" data-learning-context="modify-eval-case" data-context-type="modify" markdown="1">
## 加一个“两条都相关”的案例

1. 新增一个 answerable case，相关 chunk 为 Python 与 HTTP 两条。
2. 让候选 Top-1 只命中一条，分别计算 Recall@1 与 Recall@3。
3. 把第一条相关项从第 1 名移到第 3 名，观察 MRR。
4. 制造一条无效 citation，确认即使 Recall 上升仍被门禁阻止。
5. 保存新 fingerprint；不要把新报告与旧 fingerprint 直接比较。
</section>

<section id="troubleshoot-evaluation" data-learning-context="troubleshoot-evaluation" data-context-type="troubleshoot" markdown="1">
## 先确认可比性，再解释指标

| 错误 | 含义 |
| --- | --- |
| `output_coverage_mismatch` | 少了案例或混入评估集外输出 |
| `invalid_eval_case` | ID/query/相关性与 answerable 契约冲突 |
| `duplicate_ranked_chunk` | 一条 ranking 重复同一 chunk |
| `unknown_ranked_chunk` | 结果不属于固定语料 |
| `missing_citations` | 无法定义引用有效率 |
| `incomparable_reports` | fingerprint、Top-k 或案例数不同 |

不要在候选结果出来后修改相关标签来“修好”分数；标注变化要走新版本和独立复核。
</section>

<section id="deepen-metric-limits" data-learning-context="deepen-metric-limits" data-context-type="deepen" markdown="1">
## 满分只说明通过当前有限协议

四例满分不能证明生产质量。它没有测延迟、成本、真实 embedding、事实时效、完整性、语气、用户满意度或对抗鲁棒性。门禁是最低回归保护，不是发布充分条件。

日志只保留 case ID、聚合指标和门禁原因；教学 query、答案和 citation 文本也不需要进入运行日志。评估产物保留数据 fingerprint、代码版本、配置、基线、候选和失败原因。
</section>

<section id="project-learning-assistant-v12" data-learning-context="project-learning-assistant-v12" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.4 v0.12

- 上一版：v0.11 能输出逐 claim 证据或稳定拒答。
- 本课新增：固定评估集、Recall@k、MRR、引用有效率、拒答准确率和回归门禁。
- 文件：`rag_evaluation.py` 与 `test_rag_evaluation.py`。
- 保存：数据 fingerprint、基线/候选报告、门禁决定与 8 项测试。
- 本组边界：不加入 Tool Calling、Agent、框架、微调或真实 provider；这些在后续模块另建权限和评估契约。
</section>

## 四类学习者入口

- 零基础兴趣：手算四个案例的首个相关名次。
- 有基础兴趣：新增多相关项，比较 Recall@k 与 MRR。
- 零基础求职：用“同一试卷、同一分母、基线对比”解释回归测试。
- 有基础求职：说明离线集偏差、指标盲区和安全门禁；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 评估集 fingerprint 对重排稳定、对内容变化敏感。
- 四项指标的范围、对象和分母固定。
- 候选与基线使用相同 fingerprint、Top-k 与案例数。
- Recall/MRR 不退化，引用和拒答指标为 1 才允许交付。
- 报告明确有限协议边界，不把四例满分写成生产效果。

## 来源与版本

- 核查日期：2026-07-26。
- 适用环境：Python 3.11+ 标准库；自动测试离线。
- [Stanford IR Book：Evaluation](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-unranked-retrieval-sets-1.html)
- [Stanford IR Book：Ranked Retrieval Evaluation](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)
- [Retrieval-Augmented Generation 原始论文](https://arxiv.org/abs/2005.11401)

## 下一步

先完成六课组级验收；通过后再进入 Tool Calling 与 Agent，不在 RAG 课程里提前混入工具权限。
