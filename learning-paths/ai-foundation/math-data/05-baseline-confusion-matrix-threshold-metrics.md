<div class="be-tutor-mount" data-tutor-lesson="ai-math-data-05" aria-hidden="true"></div>
<section id="overview-evaluation-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-evaluation-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">数学、数据与可复现实验 · 第 5 / 6 课 · 可复现实验与评估系统 v0.5</span>
# 基线、混淆矩阵、阈值与指标选择
## 分数只有放回错误类型与业务代价中才有意义
```text
baseline_negative=tp:0,fp:0,tn:3,fn:3,accuracy:0.500,precision:0.000,recall:0.000,f1:0.000
threshold_0.5=tp:2,fp:1,tn:2,fn:1,accuracy:0.667,precision:0.667,recall:0.667,f1:0.667
threshold_0.7=tp:1,fp:1,tn:2,fn:2,accuracy:0.500,precision:0.500,recall:0.333,f1:0.400
selection=cost-and-validation-contract
invariants=fixed-validation,threshold-declared,zero-division-defined
```
本课在同一固定验证集上比较负类基线和两个声明阈值，不把一个准确率当成完整结论。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>数学数据实验 · 5 / 6</strong></div>
  <div><span>前置</span><strong>固定训练/验证划分</strong></div>
  <div><span>实现</span><strong>Python 3.11 标准库</strong></div>
  <div><span>完成后留下</span><strong>基线、混淆矩阵、指标口径与阈值证据</strong></div>
</div>
## 学习目标
- 用简单基线判断复杂方案是否真的增加价值。
- 从 TP、FP、TN、FN 推导 accuracy、precision、recall 与 F1。
- 固定 `score >= threshold` 的边界语义。
- 为零分母给出明确且可测试的返回规则。
- 用错误成本和独立验证选择阈值，避免在同一验证集上反复追分。
<section id="concept-baseline-confusion" data-learning-context="concept-baseline-confusion" data-context-type="concept" markdown="1">
## 基线给复杂方案一条最低比较线
样例正负各 3 个。始终预测负类的基线准确率仍有 `0.500`，但召回率为 0：三个正类全部漏掉。类别极不平衡时，“全猜多数类”甚至可能得到很高准确率。

混淆矩阵要求每个验证样本恰好进入 TP、FP、TN、FN 中一个格子，四格之和必须等于验证样本数。
</section>
<section id="concept-metrics-denominators" data-learning-context="concept-metrics-denominators" data-context-type="concept" markdown="1">
## 每个指标回答不同问题
```text
accuracy  = (TP + TN) / all
precision = TP / (TP + FP)
recall    = TP / (TP + FN)
F1        = 2 × precision × recall / (precision + recall)
```
精确率关注“报为正的样本里有多少是真的”，召回率关注“真实正类找回多少”。本课把零分母定义为 0，并用测试锁定；其他系统也可能选择未定义或警告，不能混用口径。
</section>
<section id="example-threshold-cost" data-learning-context="example-threshold-cost" data-context-type="example" markdown="1">
## 阈值移动会重新分配误报与漏报
预测规则固定为 `score >= threshold`。阈值从 0.5 提到 0.7 后，样例 TP 从 2 降为 1，FN 从 1 升为 2；召回率由 `0.667` 降为 `0.333`。

这不是“0.5 永远更好”。告警疲劳高时可能更重视少误报，疾病筛查漏诊代价高时可能更重视召回。阈值选择必须写出错误成本和验证契约，并最终在未参与选择的数据上确认。
</section>
<section id="reproduce-evaluation-v05" data-learning-context="reproduce-evaluation-v05" data-context-type="reproduce" markdown="1">
## 运行基线与阈值实验
```bash
cd site-src/examples/ai-math-data/reproducible-experiment-v05
../../../../.venv/bin/python -m unittest -v test_evaluation_lab.py
../../../../.venv/bin/python evaluation_lab.py
```
6 项测试覆盖阈值等号边界、四格守恒、指标公式、零分母、负类基线、非法输入和固定报告。
</section>
<section id="modify-evaluation-policy" data-learning-context="modify-evaluation-policy" data-context-type="modify" markdown="1">
## 主动改变分布、阈值与成本
1. 将正类缩减为 1 个，观察多数类基线准确率怎样误导。
2. 增加阈值 0.3，先预测 TP/FP/TN/FN 再运行。
3. 定义 `cost = 5×FN + FP`，比较三个阈值。
4. 增加“阈值选择集”和“最终测试集”，禁止用最终测试集调参。
</section>
<section id="troubleshoot-evaluation-metrics" data-learning-context="troubleshoot-evaluation-metrics" data-context-type="troubleshoot" markdown="1">
## 指标争议先核对样本、阈值和分母
| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 四格和不等于样本数 | 分支重叠或漏分支 | 每样本只分类一次并断言 total |
| 阈值点归属不一致 | `>` 与 `>=` 混用 | 固定并记录边界规则 |
| 准确率高但业务失败 | 类别不平衡或 FN 代价高 | 同看基线、召回和错误成本 |
| precision 出现除零 | 没有任何正预测 | 明确零分母策略 |
| 验证指标越调越好 | 在同一数据反复选阈值 | 留出最终未见测试集 |
| 两份报告 F1 不同 | 平均方式或正类定义不同 | 固定标签与计算口径 |
</section>
<section id="project-reproducible-experiment-v05" data-learning-context="project-reproducible-experiment-v05" data-context-type="project" markdown="1">
## 可复现实验与评估系统 v0.5
- v0.5 保存固定验证样本、负类基线和不同阈值的同口径结果。
- 所有指标只从同一个 `Confusion` 对象派生。
- 输入拒绝重复 ID、非二分类标签、越界分数和越界阈值。
- 下一版将配置、数据、代码修订、指标与文件哈希汇总为复现清单。
</section>
## 四类学习者入口
- 零基础兴趣：手工把 6 个样本放进四格并计算准确率。
- 有基础兴趣：实现按错误成本排序的阈值表。
- 零基础求职：解释准确率高为什么仍可能漏掉全部正类。
- 有基础求职：设计阈值选择集、最终测试集和指标口径清单。
<section id="career-threshold-metrics" data-learning-context="career-threshold-metrics" data-context-type="career" markdown="1">
## 求职加练：线上误报太多，能否直接提高阈值
原创追问：模型准确率 95%，但运营说告警不可用。请先要求类别分布和混淆矩阵，再解释阈值提高对 precision/recall 的可能影响；设计包含多数类基线、错误成本、阈值选择集和最终测试集的验收。
</section>
## 完成检查
- 6 项测试通过，阈值 0.5 的四格为 `2,1,2,1`。
- 四格和等于 6，四个指标从同一组计数派生。
- 能说明负类基线为什么准确率 0.5、召回率 0。
- 阈值等号边界与零分母策略明确。
- 不用最终测试集反复选择阈值。
## 来源与版本
- Python 3.11 标准库；核查日期 2026-07-23。
- [NIST: Confusion matrix](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/confmatr.htm)
- [scikit-learn Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)：用于核对分类指标术语，本课不依赖 scikit-learn 运行。
## 下一步
进入第 6 课《实验配置、数据指纹、产物清单与复现验收》，把结果和产生它的输入完整绑定。
