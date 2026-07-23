<div class="be-tutor-mount" data-tutor-lesson="machine-learning-07" aria-hidden="true"></div>
<section id="overview-calibration-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-calibration-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">机器学习 · 第 7 / 8 课 · 结构化数据机器学习系统 v0.7</span>
# 概率校准、阈值、分组误差与模型比较
## 比较完整概率证据，再用预声明阈值审计不同分组的错误
```text
model=logistic-regression,calibration=sigmoid,cv=stratified-5-fold
development_rows=90,test_rows=30,test_access=single-analysis
raw_probability=brier:0.206,log_loss:0.590,ece5:0.187
calibrated_probability=brier:0.194,log_loss:0.563,ece5:0.129
decision_threshold=0.35,policy=recall-oriented-predeclared
group_errors=direct:n=8,pos=3,recall=0.000,fpr=0.200;missing:n=2,pos=1,recall=0.000,fpr=1.000;organic:n=9,pos=3,recall=0.333,fpr=0.167;referral:n=11,pos=3,recall=0.667,fpr=0.250
minimum_group_samples=2,small_groups_descriptive_only=true
comparison=report-all-metrics-no-cherry-picking
invariants=calibration-development-only,threshold-predeclared,test-not-retuned
```
本课只在 90 行开发集内拟合 sigmoid 校准器，在一次最终分析中比较原始与校准概率；0.35 阈值在看测试结果前声明，不用最终测试反向调参。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>机器学习 · 7 / 8</strong></div>
  <div><span>前置</span><strong>选择协议与最终测试隔离</strong></div>
  <div><span>依赖</span><strong>NumPy 2.5.1 · pandas 2.3.3 · scikit-learn 1.9.0</strong></div>
  <div><span>完成后留下</span><strong>概率、阈值和分组错误审计</strong></div>
</div>

## 学习目标

- 区分排序能力、概率质量和阈值后的决策质量。
- 用 Brier、对数损失和固定分箱 ECE 比较概率。
- 让校准器只接触开发集内部的折外预测关系。
- 用预声明阈值把概率映射为动作。
- 按分组同时报告样本量、正类数、召回和假阳性率。

<section id="concept-calibration-metrics" data-learning-context="concept-calibration-metrics" data-context-type="concept" markdown="1">
## 概率校准关心“预测 0.7 的样本是否约有七成为正类”

校准不等于准确率，也不等于排序。Brier 是预测概率与二元标签的平方误差；对数损失更重罚对错误答案的极端自信；本课 ECE 把概率分成五箱，汇总每箱平均概率与实际正类率的加权差。

开发集五折 sigmoid 校准后，最终测试 Brier 从 0.206 降到 0.194、对数损失从 0.590 降到 0.563、ECE5 从 0.187 降到 0.129。三个指标都保留，但 30 行样本仍不足以证明长期稳定。
</section>

<section id="concept-threshold-policy" data-learning-context="concept-threshold-policy" data-context-type="concept" markdown="1">
## 阈值是一条决策政策，不会改变模型输出的概率

同一组概率可用 0.35、0.5 或 0.7 转为不同动作。阈值降低通常增加正类召回，也可能增加假阳性；选择应由漏报、误报、人工复核容量和安全要求共同决定。

本课把 0.35 预声明为偏召回的教学政策，然后只做一次测试分析。若看到分组结果后改阈值，就必须把测试集降级为开发数据并取得新的独立测试证据。
</section>

<section id="example-group-error-audit" data-learning-context="example-group-error-audit" data-context-type="example" markdown="1">
## 分组指标必须携带分母，小样本只用于发现问题

| 渠道 | 样本 | 正类 | 召回 | 假阳性率 |
| --- | ---: | ---: | ---: | ---: |
| direct | 8 | 3 | 0.000 | 0.200 |
| missing | 2 | 1 | 0.000 | 1.000 |
| organic | 9 | 3 | 0.333 | 0.167 |
| referral | 11 | 3 | 0.667 | 0.250 |

最小组只有 2 行，单个样本就会让比例巨变，因此这些数值只能指向“需要更多数据和输入质量检查”，不能排名渠道、宣称公平或推断真实群体差异。`channel` 也是合成教学字段，不是受保护身份。
</section>

<section id="reproduce-calibration-v07" data-learning-context="reproduce-calibration-v07" data-context-type="reproduce" markdown="1">
## 运行 v0.7 并核对开发集校准边界

```bash
cd site-src/examples/machine-learning/structured-data-ml-system-v07
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_calibration_error_lab.py
.venv/bin/python calibration_error_lab.py
```

8 项测试覆盖测试边界、五折校准、ECE 定义、概率指标、分组覆盖、阈值行为、非法输入和小样本披露。
</section>

<section id="modify-calibration" data-learning-context="modify-calibration" data-context-type="modify" markdown="1">
## 主动修改分箱、阈值和分组

1. 比较 ECE 的 3、5、10 个分箱，说明小样本下为何波动很大。
2. 在开发集上预先评估 0.2–0.8 阈值曲线，不触碰最终测试。
3. 为每个分组增加混淆矩阵原始计数，不只打印比例。
4. 将 `channel` 从特征中删除但仍用于审计，比较结果变化。
</section>

<section id="troubleshoot-calibration" data-learning-context="troubleshoot-calibration" data-context-type="troubleshoot" markdown="1">
## 概率与分组分析异常先查校准边界、分箱和分母

| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 校准后指标更差 | 样本少、方法不匹配或过拟合 | 如实保留并用独立数据比较 |
| ECE 随分箱剧烈变化 | 每箱样本太少 | 同报分箱、计数和其他指标 |
| 阈值越调测试越好 | 测试集参与选择 | 停止并获取新测试集 |
| 某组 FPR 为 1 | 分母可能只有一个样本 | 先看原始计数和区间 |
| 某组没有正类 | 召回无定义 | 输出 `na`，不要写 0 |
| 总体好、分组差异大 | 数据或错误分布不均 | 增加样本并审查影响 |
</section>

<section id="project-structured-data-ml-v07" data-learning-context="project-structured-data-ml-v07" data-context-type="project" markdown="1">
## 结构化数据机器学习系统 v0.7

- 保留 90/30 开发/测试边界，校准器在开发集五折内拟合。
- 同时报告原始和 sigmoid 校准后的 Brier、对数损失和 ECE5。
- 固定 0.35 预声明阈值，并按四个渠道值输出样本、正类、召回和 FPR。
- 最小组只有 2 行，固定输出明确 `small_groups_descriptive_only=true`。
- 下一版持久化完整流水线和契约，建立加载、推理、拒绝和交付验收。
</section>

## 四类学习者入口

- 零基础兴趣：用 10 张卡模拟“预测 0.7，实际 7 张为正”的校准含义。
- 有基础兴趣：绘制可靠性图，并在每个点旁标注样本量。
- 零基础求职：解释为什么降低阈值不等于模型概率变高。
- 有基础求职：设计测试访问、分组分母、无定义指标和校准漂移的审计协议。

<section id="career-calibration-contract" data-learning-context="career-calibration-contract" data-context-type="career" markdown="1">
## 求职加练：某渠道召回为零，是否证明模型歧视该渠道

原创追问：先核对该组只有 8 行、3 个正类，检查渠道是否进入特征、是否是敏感属性代理、阈值是否预声明以及数据采集是否一致；要求置信区间、新时段样本和影响分析。零召回是严重诊断信号，但当前证据不足以给出群体公平性结论。
</section>

## 完成检查

- 8 项测试通过，校准只使用开发集五折。
- 原始和校准概率同时报告三类指标，不挑选单个好结果。
- 阈值 0.35 在测试前声明，测试结果不用于重调。
- 四组共覆盖全部 30 行，并携带样本量和正类分母。
- 能解释小样本分组指标为何只能用于诊断。

## 来源与版本

- 核查日期 2026-07-23；运行依赖见同目录 `requirements.txt`。
- [scikit-learn calibration guide](https://scikit-learn.org/stable/modules/calibration.html)
- [scikit-learn CalibratedClassifierCV](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html)
- [scikit-learn brier_score_loss](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html)

## 下一步

进入第 8 课《模型持久化、推理契约与交付验收》，完成机器学习组闭环。
