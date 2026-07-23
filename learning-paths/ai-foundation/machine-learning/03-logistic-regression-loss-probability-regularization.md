<div class="be-tutor-mount" data-tutor-lesson="machine-learning-03" aria-hidden="true"></div>
<section id="overview-logistic-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-logistic-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">机器学习 · 第 3 / 8 课 · 结构化数据机器学习系统 v0.3</span>
# 逻辑回归、损失、概率与正则化
## 从线性分数得到概率，再把概率和决策阈值分开验收
```text
model=logistic-regression,penalty=l2,solver=lbfgs,threshold=0.500
train_rows=90,validation_rows=30,transformed_features=7
validation_accuracy=0.667,recall=0.300,log_loss=0.590
probability_range=0.006..0.885
intercept=-0.981,coefficient_l2=1.294
strongest_absolute_coefficient=numeric__redundant_signal:1.021
regularization=C:0.1,l2:0.798;C:10.0,l2:1.511
weaker_regularization_larger_norm=true
invariants=train-only-preprocessing,probabilities-not-decisions,validation-not-fit
```
本课把 v0.2 的预处理接到逻辑回归。模型输出正类概率，`0.5` 只是本课固定的决策阈值；对数损失评估概率质量，L2 正则化限制系数规模。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>机器学习 · 3 / 8</strong></div>
  <div><span>前置</span><strong>无泄漏预处理流水线</strong></div>
  <div><span>依赖</span><strong>NumPy 2.5.1 · pandas 2.3.3 · scikit-learn 1.9.0</strong></div>
  <div><span>完成后留下</span><strong>概率模型、损失与正则化证据</strong></div>
</div>

## 学习目标

- 从线性分数、sigmoid、正类概率到阈值决策建立完整链路。
- 区分分类标签指标和概率损失。
- 解释 `C` 与 L2 正则强度的反向关系。
- 把预处理与逻辑回归放进同一训练流水线。
- 谨慎解读系数，不把相关性权重写成因果结论。

<section id="concept-score-sigmoid-probability" data-learning-context="concept-score-sigmoid-probability" data-context-type="concept" markdown="1">
## 逻辑回归先算线性分数，再用 sigmoid 映射到 0 到 1

对变换后的特征 \(x\)，模型计算 \(z=w^Tx+b\)，再得到 \(p=1/(1+e^{-z})\)。`p` 是模型在当前数据、特征和拟合假设下给出的正类概率估计，不等于事实频率已经被证明。

本课二分类 `predict_proba` 每行输出两列，二者之和为 1。截距是全部特征为零时的线性分数起点；标准化后的数值零通常对应训练均值附近，但类别独热列仍需结合参考组合解释。
</section>

<section id="concept-loss-threshold" data-learning-context="concept-loss-threshold" data-context-type="concept" markdown="1">
## 对数损失看概率有多自信，阈值才把概率变成动作

同样预测正确，给正确类 0.99 比 0.51 的对数损失更小；对错误答案极度自信会受到更大惩罚。准确率和召回率只在选定阈值后观察离散决策，不能替代概率质量。

固定阈值 0.5 后，本课准确率仍为 0.667，与多数类基线相同，但正类召回率从 0 提升到 0.300、对数损失为 0.590。这不是上线结论，而是提醒：必须同时比较基线、错误类型、概率与业务成本。
</section>

<section id="example-l2-regularization" data-learning-context="example-l2-regularization" data-context-type="example" markdown="1">
## L2 正则化惩罚大系数，C 越小约束越强

| `C` | 正则强度 | 系数 L2 范数 | 本课观察 |
| ---: | --- | ---: | --- |
| 0.1 | 强 | 0.798 | 权重更收缩 |
| 1.0 | 中 | 1.294 | 默认实验 |
| 10.0 | 弱 | 1.511 | 权重更自由 |

`C` 是正则强度的倒数式控制量，不是“正则越大 C 越大”。系数绝对值需要在相同预处理尺度下比较；独热列、相关特征和正则化会共同改变权重分配，所以最大系数只提供调试线索，不证明因果。
</section>

<section id="reproduce-logistic-v03" data-learning-context="reproduce-logistic-v03" data-context-type="reproduce" markdown="1">
## 运行 v0.3 并核对概率与权重

```bash
cd site-src/examples/machine-learning/structured-data-ml-system-v03
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_logistic_regression_lab.py
.venv/bin/python logistic_regression_lab.py
```

8 项测试覆盖 v0.2 特征边界、流水线组成、概率和系数形状、0.5 阈值、对数损失与召回、正则化趋势、非法 `C` 拒绝和固定报告。
</section>

<section id="modify-logistic" data-learning-context="modify-logistic" data-context-type="modify" markdown="1">
## 主动修改阈值、正则化和特征

1. 将阈值改为 0.3，记录准确率、召回率与假阳性数量变化。
2. 比较 `C=0.01 / 0.1 / 1 / 10 / 100` 的系数范数和验证损失。
3. 删除冗余特征，观察最大绝对系数是否转移到 `signal_a`。
4. 打乱目标后重训，确认结果不能继续被当作有效信号。
</section>

<section id="troubleshoot-logistic" data-learning-context="troubleshoot-logistic" data-context-type="troubleshoot" markdown="1">
## 逻辑回归异常先查尺度、收敛、阈值和数据边界

| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 优化器不收敛 | 尺度差异大或迭代不足 | 保留标准化并检查收敛提示 |
| 概率接近 0/1 且损失很差 | 过拟合或分布变化 | 加强正则并检查切分 |
| 准确率不变但召回变化 | 阈值或错误分布变化 | 同看混淆矩阵和任务成本 |
| 系数数量对不上 | 编码后字段宽度变化 | 对齐 `get_feature_names_out()` |
| 系数符号反直觉 | 相关特征、编码或混杂 | 做消融，不写因果结论 |
| 验证分数过好 | 预处理或选择泄漏 | 整条 Pipeline 只在训练折拟合 |
</section>

<section id="project-structured-data-ml-v03" data-learning-context="project-structured-data-ml-v03" data-context-type="project" markdown="1">
## 结构化数据机器学习系统 v0.3

- 保留 v0.2 的 5 个原始特征、7 个变换特征和训练期预处理边界。
- 用逻辑回归替换多数类分类器，固定 L2、`lbfgs`、最大迭代和随机状态。
- 输出准确率、召回率、对数损失、概率范围、截距、系数范数和最大绝对系数。
- 比较 `C=0.1` 与 `C=10.0`，只断言更弱正则对应更大系数范数。
- 下一版引入决策树，观察非线性切分、训练深度和过拟合。
</section>

## 四类学习者入口

- 零基础兴趣：用数轴画出分数经过 sigmoid 后如何跨过 0.5 阈值。
- 有基础兴趣：画出五个 `C` 对应的系数范数与验证损失。
- 零基础求职：解释为什么概率、阈值、准确率和召回率不是同一个概念。
- 有基础求职：设计概率漂移、阈值变更、收敛失败和训练/推理预处理不一致的监控与回归。

<section id="career-logistic-contract" data-learning-context="career-logistic-contract" data-context-type="career" markdown="1">
## 求职加练：准确率没超过基线，逻辑回归还有没有价值

原创追问：当前模型准确率与多数类基线同为 0.667，但召回从 0 到 0.3、对数损失为 0.590。请说明不能只凭一个数字接受或否决模型；提出错误成本、阈值曲线、概率校准、样本量和独立测试集证据，并解释为什么本课仍不能宣布业务收益。
</section>

## 完成检查

- 8 项测试通过，30 行验证数据得到两列和为 1 的概率。
- 0.5 阈值生成的标签与流水线 `predict` 一致。
- 固定结果为准确率 0.667、召回率 0.300、对数损失 0.590。
- `C=0.1` 的系数范数小于 `C=10.0`。
- 能说明系数是当前模型关联权重，不是因果效应。

## 来源与版本

- 核查日期 2026-07-23；运行依赖见同目录 `requirements.txt`。
- [scikit-learn LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
- [scikit-learn log_loss](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.log_loss.html)
- [scikit-learn probability calibration guide](https://scikit-learn.org/stable/modules/calibration.html)

## 下一步

进入第 4 课《决策树、切分、过拟合与复杂度约束》，用另一类模型检验非线性表达和容量控制。
