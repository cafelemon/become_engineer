<div class="be-tutor-mount" data-tutor-lesson="machine-learning-05" aria-hidden="true"></div>
<section id="overview-selection-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-selection-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">机器学习 · 第 5 / 8 课 · 结构化数据机器学习系统 v0.5</span>
# 交叉验证、超参数选择与最终测试集
## 选择发生在开发集内部，最终测试只在方案冻结后打开
```text
rows=120,development_rows=90,test_rows=30,overlap=0
selection_scope=development-only,cv=stratified-5-fold,scoring=balanced_accuracy
candidates=logistic-regression:C[0.1|1|10];decision-tree:max_depth[2|3|4],min_samples_leaf:5
candidate_count=6,fit_count=30
selected=decision-tree,max_depth=2
cv_balanced_accuracy=0.742,std=0.041
final_test=accuracy:0.600,balanced_accuracy:0.575,recall:0.500
test_access=after-selection-once
invariants=preprocess-inside-cv,test-excluded-from-selection,refit-development-only
```
本课先冻结 30 行最终测试集，再只用 90 行开发集的五折交叉验证比较 6 个候选。预处理放在候选 Pipeline 内，因此每折只学习该折训练部分的统计量。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>机器学习 · 5 / 8</strong></div>
  <div><span>前置</span><strong>线性模型与树模型容量</strong></div>
  <div><span>依赖</span><strong>NumPy 2.5.1 · pandas 2.3.3 · scikit-learn 1.9.0</strong></div>
  <div><span>完成后留下</span><strong>选择协议、CV 结果与一次最终测试</strong></div>
</div>

## 学习目标

- 区分开发集内部的训练折、验证折和外部最终测试集。
- 用分层交叉验证减少单次切分的偶然性。
- 让预处理在每一折内部重新拟合，避免折间泄漏。
- 先固定评分指标和候选空间，再执行选择。
- 正确解释 CV 均值、标准差与最终测试差异。

<section id="concept-cv-fold-roles" data-learning-context="concept-cv-fold-roles" data-context-type="concept" markdown="1">
## 五折交叉验证让每个开发样本轮流承担验证角色

90 行开发集被分成五折；每轮用四折拟合、剩余一折评分，共得到五个分数。分层保持每折的类别比例，`shuffle + random_state` 固定本课分组。交叉验证没有创造新数据，只是更充分地复用有限开发样本。

最终测试集的 30 行不属于任何一折。其 ID 与开发集零交叉，模型家族、参数、评分方式和预处理都不能因测试结果而改变。
</section>

<section id="concept-selection-bias-final-test" data-learning-context="concept-selection-bias-final-test" data-context-type="concept" markdown="1">
## 选择会对验证反馈过拟合，测试集因此必须延迟访问

每比较一个新模型、参数或特征，开发反馈都会影响下一步决策。即使从未调用梯度，这些人工选择也会使开发分数越来越乐观。最终测试集只承担一次独立估计，打开后若继续调参，它就退化成新的验证集。

本课先按 CV 平衡准确率选择候选并在完整开发集重拟合，之后才得到测试平衡准确率 0.575。它低于 CV 均值 0.742，显示有限样本波动和选择乐观性，不能被隐藏。
</section>

<section id="example-grid-search-pipeline" data-learning-context="example-grid-search-pipeline" data-context-type="example" markdown="1">
## 候选空间、指标和预处理都进入可复现选择契约

| 模型家族 | 候选参数 | 数量 |
| --- | --- | ---: |
| 逻辑回归 | `C = 0.1 / 1 / 10` | 3 |
| 决策树 | `max_depth = 2 / 3 / 4`，叶子最少 5 | 3 |

6 个候选 × 5 折产生 30 次折内拟合。`GridSearchCV` 的 estimator 是完整的 `preprocess → classifier` Pipeline，所以中位数、尺度和类别词表不会提前看到验证折。固定评分为平衡准确率，避免多数类占比直接主导选择。
</section>

<section id="reproduce-selection-v05" data-learning-context="reproduce-selection-v05" data-context-type="reproduce" markdown="1">
## 运行 v0.5 并核对最终测试门

```bash
cd site-src/examples/machine-learning/structured-data-ml-system-v05
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_model_selection_lab.py
.venv/bin/python model_selection_lab.py
```

8 项测试覆盖测试集隔离、分层五折、Pipeline 折内预处理、六候选网格、开发集重拟合、测试指标边界、Schema 拒绝和固定报告。
</section>

<section id="modify-selection" data-learning-context="modify-selection" data-context-type="modify" markdown="1">
## 主动修改评分、候选和折数

1. 把评分改为召回率，记录选中候选是否变化，但不要据测试结果反向挑指标。
2. 加入 `C=0.01` 与树深度 1，解释候选空间扩张的计算与选择成本。
3. 比较 3 折、5 折和 10 折的均值、标准差与拟合次数。
4. 故意把预处理放到交叉验证外，说明为什么这段代码应被测试拒绝。
</section>

<section id="troubleshoot-selection" data-learning-context="troubleshoot-selection" data-context-type="troubleshoot" markdown="1">
## 选择结果异常先查测试污染、评分口径和折内 Pipeline

| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| CV 很高、测试明显下降 | 选择乐观、样本少或分布差异 | 报告差异并获取新证据 |
| 每次最佳参数不同 | 分折随机性未固定或差异很小 | 固定折并报告完整排名 |
| 某折没有正类 | 未分层或类别过少 | 使用分层并降低折数 |
| 预处理统计量异常稳定 | 在 CV 外提前拟合 | 将预处理放进 Pipeline |
| 测试分数被反复查看 | 测试集变成选择反馈 | 封存测试并建立访问记录 |
| 搜索耗时暴涨 | 候选、折数或并行度扩大 | 先用小网格和预算 |
</section>

<section id="project-structured-data-ml-v05" data-learning-context="project-structured-data-ml-v05" data-context-type="project" markdown="1">
## 结构化数据机器学习系统 v0.5

- 将原验证边界升级为 90 行开发集和 30 行冻结测试集。
- 在开发集内用固定五折比较逻辑回归与决策树共 6 个候选。
- 选择 `decision-tree, max_depth=2`，CV 平衡准确率 `0.742 ± 0.041`。
- 最终测试只在重拟合后评估一次，保留 0.600 准确率、0.575 平衡准确率和 0.500 召回率。
- 下一版暂时离开标签监督，用聚类和 PCA 建立无监督评估边界。
</section>

## 四类学习者入口

- 零基础兴趣：用五张纸模拟五折轮换，标出每轮训练与验证。
- 有基础兴趣：导出六候选每折分数和排名，不只打印最佳项。
- 零基础求职：解释为什么最终测试集不能反复用于调参。
- 有基础求职：设计候选空间审计、折内预处理、测试访问记录和重训触发规则。

<section id="career-selection-contract" data-learning-context="career-selection-contract" data-context-type="career" markdown="1">
## 求职加练：CV 0.742，最终测试只有 0.575，项目失败了吗

原创追问：请区分均值、方差、选择偏差、样本量和潜在分布差异；检查测试是否被污染、两组置信区间和分组错误，再决定收集新数据、简化候选或重新定义任务。不能删除不理想测试结果，也不能用它继续挑参数后仍称“最终测试”。
</section>

## 完成检查

- 8 项测试通过，开发/测试为 90/30 且 ID 零交叉。
- 6 个候选在五折内完成 30 次真实拟合。
- 预处理属于每个候选 Pipeline，在折内学习状态。
- 选择只使用开发集，最终测试在方案冻结后访问。
- 能如实解释 CV 与测试差距，而不是挑选好看的数字。

## 来源与版本

- 核查日期 2026-07-23；运行依赖见同目录 `requirements.txt`。
- [scikit-learn cross-validation guide](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html)
- [scikit-learn StratifiedKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html)

## 下一步

进入第 6 课《聚类、PCA 与无监督评估》，学习没有目标标签时怎样限制结论。
