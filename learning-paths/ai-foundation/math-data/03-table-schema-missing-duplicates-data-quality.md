<div class="be-tutor-mount" data-tutor-lesson="ai-math-data-03" aria-hidden="true"></div>
<section id="overview-data-quality-gate" class="be-page-hero be-lesson-hero" data-learning-context="overview-data-quality-gate" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">数学、数据与可复现实验 · 第 3 / 6 课 · 可复现实验与评估系统 v0.3</span>
# 表格 Schema、缺失值、重复与数据质量
## 清洗不是把问题藏起来，而是把每项决策留下来
```text
schema=sample_id:str,feature_a:number?,feature_b:number?,label:0|1
rows_seen=6
accepted_ids=a,b
missing_cells=1
exact_duplicates=1
conflicting_ids=c
invalid_rows=1
status=reject
invariants=explicit-schema,conflicts-not-silently-deduplicated
```
本课先验证字段、类型、缺失和样本身份，再允许数据进入缩放或建模。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>数学数据实验 · 3 / 6</strong></div>
  <div><span>前置</span><strong>形状契约与标准化边界</strong></div>
  <div><span>实现</span><strong>Python 3.11 标准库</strong></div>
  <div><span>完成后留下</span><strong>显式 Schema、质量报告与冲突隔离</strong></div>
</div>
## 学习目标
- 把表格 Schema 写成字段集合、类型、可空性和值域。
- 区分缺失、无效、完全重复和同 ID 冲突。
- 不用 `0` 或空字符串擅自替代未知特征。
- 让质量报告同时保留输入行数、接受样本和拒绝原因。
- 解释为什么冲突样本不能用“保留第一条”静默消失。
<section id="concept-schema-contract" data-learning-context="concept-schema-contract" data-context-type="concept" markdown="1">
## Schema 是数据进入计算前的接口
本实验每行必须恰好包含：

| 字段 | 契约 | 可缺失 |
| --- | --- | --- |
| `sample_id` | 非空字符串，标识样本身份 | 否 |
| `feature_a` | 数值，但布尔值不算数值特征 | 是，以 `None` 表示 |
| `feature_b` | 数值，但布尔值不算数值特征 | 是，以 `None` 表示 |
| `label` | 整数 0 或 1 | 否 |

“字段存在”不等于“值有效”。Python 中 `bool` 是 `int` 的子类，本课主动拒绝 `True` 作为数值，避免语言实现细节污染数据语义。
</section>
<section id="concept-missing-invalid" data-learning-context="concept-missing-invalid" data-context-type="concept" markdown="1">
## 缺失值和无效值需要不同恢复策略
`feature_a=None` 表示这一格未知，样本仍可能用于后续明确支持缺失值的流程；`label=2` 则违反二分类值域，整行不能进入实验。

不能把缺失特征自动改成 0：0 可能是真实测量值。填充、删除、增加缺失指示列或使用能处理缺失的模型，必须在看过缺失比例和数据产生机制后另行决定。
</section>
<section id="example-duplicate-conflict" data-learning-context="example-duplicate-conflict" data-context-type="example" markdown="1">
## 相同行与身份冲突不是同一种重复
- 同一个 `sample_id=a` 的两行逐字段相同：计为一次完全重复，接受一份。
- 同一个 `sample_id=c` 的两行特征不同：身份已经歧义，两行都不能进入接受集合。
- 无效行 `label=2`：计入 `invalid_rows`，不与合法样本合并。

样例 6 行最终只接受 `a,b`。质量门禁状态为 `reject`，因为存在冲突 ID 和无效行；这比“读取成功”更接近实验是否可继续的真实问题。
</section>
<section id="reproduce-data-quality-v03" data-learning-context="reproduce-data-quality-v03" data-context-type="reproduce" markdown="1">
## 运行数据质量门禁
```bash
cd site-src/examples/ai-math-data/reproducible-experiment-v03
../../../../.venv/bin/python -m unittest -v test_data_quality_lab.py
../../../../.venv/bin/python data_quality_lab.py
```
6 项测试覆盖合法行归一化、缺失计数、完全重复、冲突身份、字段/类型/值域错误和固定报告。报告按 ID 排序，不依赖输入顺序或机器环境。
</section>
<section id="modify-data-quality-policy" data-learning-context="modify-data-quality-policy" data-context-type="modify" markdown="1">
## 主动修改 Schema 和清洗策略
1. 增加 `captured_at` 字段，定义格式、时区和是否允许缺失。
2. 将“额外字段拒绝”改为“允许但记录”，比较兼容性与拼写错误风险。
3. 为每列输出缺失计数，而不只输出总数。
4. 给冲突 ID 生成隔离清单，确认它们仍可追查但不会进入训练。
</section>
<section id="troubleshoot-data-quality" data-learning-context="troubleshoot-data-quality" data-context-type="troubleshoot" markdown="1">
## 清洗结果异常时从身份和口径回查
| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 行数突然减少 | 重复、冲突和无效行被混成一个计数 | 分开报告每类原因 |
| 缺失率变成 0 | 未知值被填成 0 或空字符串 | 保留缺失状态再决定策略 |
| 同一 ID 标签不同仍被保留 | 只执行 `drop_duplicates` | 按身份检测字段冲突 |
| `True` 进入数值列 | 只用了 `isinstance(x, int)` | 在数值判断前排除 bool |
| 新字段导致生产失败 | Schema 演进没有版本策略 | 明确严格或兼容读取模式 |
| 结果每次顺序不同 | 依赖字典或来源顺序 | 按稳定 ID 排序输出 |
</section>
<section id="project-reproducible-experiment-v03" data-learning-context="project-reproducible-experiment-v03" data-context-type="project" markdown="1">
## 可复现实验与评估系统 v0.3
- v0.3 在标准化前增加 `audit_rows`，输出结构化 `QualityReport`。
- 缺失特征被计数并保留为 `None`，没有擅自填充。
- 完全重复只计一次；冲突 ID 从接受集合隔离。
- 下一版只对通过身份检查的数据做训练/验证划分。
</section>
## 四类学习者入口
- 零基础兴趣：为四个字段各写一个合法值和一个非法值。
- 有基础兴趣：增加逐列缺失率与可配置阈值。
- 零基础求职：解释为什么缺失值不能默认填 0。
- 有基础求职：设计可审计的冲突隔离与 Schema 演进方案。
<section id="career-data-quality-gate" data-learning-context="career-data-quality-gate" data-context-type="career" markdown="1">
## 求职加练：去重后样本变少，究竟修好了什么
原创追问：数据脚本对 `sample_id` 使用“保留第一条”，指标随后提高。请区分完全重复与字段冲突，设计不会静默丢证据的质量报告；再说明缺失标签、缺失特征和未知字段各应在哪个门禁处理。
</section>
## 完成检查
- 6 项测试通过，固定报告接受 `a,b` 并隔离冲突 ID `c`。
- 能写出四字段 Schema、可空性和标签值域。
- 缺失、无效、完全重复和冲突分别计数。
- 不把 `None` 擅自转换为 0。
- 质量失败不妨碍留下可复查报告。
## 来源与版本
- Python 3.11 标准库；核查日期 2026-07-23。
- [Python Data model](https://docs.python.org/3.11/reference/datamodel.html)：用于核对布尔值与整数类型关系。
- [NIST/SEMATECH: Data Exploration](https://www.itl.nist.gov/div898/handbook/eda/section1/eda11.htm)：用于数据分析前的结构与质量检查。
## 下一步
进入第 4 课《随机性、抽样、训练/验证划分与泄漏》，让质量合格的样本进入可复现评估边界。
