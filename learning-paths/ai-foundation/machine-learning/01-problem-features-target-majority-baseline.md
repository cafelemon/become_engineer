<div class="be-tutor-mount" data-tutor-lesson="machine-learning-01" aria-hidden="true"></div>
<section id="overview-ml-baseline-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-ml-baseline-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">机器学习 · 第 1 / 8 课 · 结构化数据机器学习系统 v0.1</span>
# 问题定义、特征目标与多数类基线
## 模型训练之前，先固定样本、目标、切分和最低比较线
```text
rows=120
features=4
target=target,binary=0|1,positive=1
target_rate=0.333
train_rows=90,class_counts=0:60,1:30
validation_rows=30,class_counts=0:20,1:10
overlap=0
baseline_strategy=most_frequent,predicted_label=0
baseline_accuracy=0.667
baseline_recall=0.000
invariants=target-excluded,stratified-split,validation-untouched
```
本课不急着训练复杂模型：先用 pandas 明确表格语义，用分层切分冻结评估边界，再用忽略全部特征的多数类分类器建立基线。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>机器学习 · 1 / 8</strong></div>
  <div><span>前置</span><strong>数学数据实验 6 / 6</strong></div>
  <div><span>依赖</span><strong>NumPy 2.5.1 · pandas 2.3.3 · scikit-learn 1.9.0</strong></div>
  <div><span>完成后留下</span><strong>版本化合成数据、分层切分与多数类基线</strong></div>
</div>
## 学习目标
- 把一个任务写成样本、特征、目标、正类和评估边界。
- 区分 `sample_id`、输入特征和目标列。
- 用固定种子生成可回归的教学合成数据。
- 用 `train_test_split(..., stratify=target)` 保留类别比例。
- 用 `DummyClassifier` 判断后续模型是否超过最低比较线。
<section id="concept-sample-feature-target" data-learning-context="concept-sample-feature-target" data-context-type="concept" markdown="1">
## 一行是一个样本，特征用于预测，目标只提供监督信号
本实验每行有唯一 `sample_id`、四个数值特征和二分类 `target`。正类明确为 1。目标列不能进入特征，否则模型会直接读到答案；样本 ID 也不应成为特征，它只用于追踪切分、错误和产物。

四个特征中包含两个信号列、一个纯噪声列和一个冗余信号列。名字来自生成机制，学习者能够检验模型是否利用有效信息；这些合成数据不代表真实用户或业务。
</section>
<section id="concept-supervised-generalization" data-learning-context="concept-supervised-generalization" data-context-type="concept" markdown="1">
## 监督学习拟合已知标签，评估关心未参与拟合的样本
训练集用于让估计器学习参数，验证集用于比较当前方案。`fit` 只能看到 90 行训练数据；30 行验证数据不能参与生成规则、预处理统计量或模型拟合。

本课保持上组的三个不变量：目标不进入特征、训练/验证 ID 无交叉、验证集保持未触碰。模型能记住训练样本不等于能泛化到新样本。
</section>
<section id="example-stratified-majority-baseline" data-learning-context="example-stratified-majority-baseline" data-context-type="example" markdown="1">
## 分层切分保持类别比例，多数类基线暴露准确率盲点
120 行中有 80 个负类、40 个正类。按 25% 分出验证集后：

| 分区 | 负类 | 正类 | 总数 |
| --- | ---: | ---: | ---: |
| 训练 | 60 | 30 | 90 |
| 验证 | 20 | 10 | 30 |

`DummyClassifier(strategy="most_frequent")` 忽略所有特征，只预测训练集多数类 0，因此验证准确率仍为 `0.667`，但正类召回率为 `0.000`。后续模型不仅要超过基线，还要在任务关心的错误类型上有实际改善。
</section>
<section id="reproduce-ml-baseline-v01" data-learning-context="reproduce-ml-baseline-v01" data-context-type="reproduce" markdown="1">
## 安装隔离依赖并运行第一版
```bash
cd site-src/examples/machine-learning/structured-data-ml-system-v01
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_baseline_lab.py
.venv/bin/python baseline_lab.py
```
7 项测试覆盖 Schema、固定种子、分层且无交叉的切分、目标/ID 排除、基线指标、无效数据拒绝和固定报告。依赖安装应在隔离环境完成；不要复用一个来源不明、已经损坏的全局 Python 环境。
</section>
<section id="modify-ml-baseline" data-learning-context="modify-ml-baseline" data-context-type="modify" markdown="1">
## 主动改变类别比例、种子和基线
1. 把正类从 40 行改为 20 行，预测多数类准确率和召回率。
2. 更换数据生成种子，确认 Schema 与类别计数不变、特征值改变。
3. 将 `test_size` 改为 0.2，先计算两个分区的类别数。
4. 增加 `stratified` 随机基线，并说明它与多数类基线回答的不同问题。
</section>
<section id="troubleshoot-ml-baseline" data-learning-context="troubleshoot-ml-baseline" data-context-type="troubleshoot" markdown="1">
## 指标异常先查任务和切分，不先换模型
| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 准确率接近 1 | 目标列进入特征 | 明确特征白名单并测试 |
| 验证集没有正类 | 未分层或样本过少 | 使用 stratify 或报告限制 |
| 同种子结果变化 | 数据生成或输入顺序未固定 | 统一生成器和随机状态 |
| 基线准确率很高 | 类别不平衡 | 同看召回、错误成本和类别数 |
| 训练验证有相同 ID | 划分前存在重复或拼接错误 | 质量门禁后再划分 |
| 本机导入库失败 | 解释器或二进制依赖损坏 | 新建隔离环境并按锁定版本安装 |
</section>
<section id="project-structured-data-ml-v01" data-learning-context="project-structured-data-ml-v01" data-context-type="project" markdown="1">
## 结构化数据机器学习系统 v0.1
- 第一版冻结 120 行合成数据、4 个特征、二分类正类和固定随机种子。
- pandas DataFrame 保存带标签的异构表格语义；NumPy 只生成受控数值。
- scikit-learn 负责分层切分与多数类基线，不隐藏目标/特征边界。
- 下一版加入缺失值和类别列，并将全部预处理封装在训练期流水线。
</section>
## 四类学习者入口
- 零基础兴趣：画出一行数据中 ID、特征和目标三类字段。
- 有基础兴趣：增加一个纯噪声特征并证明基线不受影响。
- 零基础求职：解释准确率 0.667 为什么不表示模型有预测能力。
- 有基础求职：设计防止目标泄漏、实体交叉和分布漂移的验收清单。
<section id="career-ml-baseline-contract" data-learning-context="career-ml-baseline-contract" data-context-type="career" markdown="1">
## 求职加练：模型 90% 准确，为什么还不能上线
原创追问：数据中 90% 都是负类，模型准确率也是 90%。请要求类别分布、正类定义、切分方式和多数类基线，指出目标泄漏与实体交叉风险；再设计一个能证明模型超过基线且改善关键错误的最小报告。
</section>
## 完成检查
- 7 项测试通过，固定输出为 120 行、4 个特征。
- 训练/验证为 90/30，类别计数分别为 `60/30` 与 `20/10`。
- `sample_id` 和 `target` 都不进入特征矩阵。
- 多数类基线准确率 0.667、正类召回率 0。
- 能解释合成数据、固定种子和真实泛化证据的边界。
## 来源与版本
- 核查日期 2026-07-23；运行依赖见同目录 `requirements.txt`。
- [pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
- [scikit-learn train_test_split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
- [scikit-learn Dummy estimators](https://scikit-learn.org/stable/api/sklearn.dummy.html)
- [scikit-learn installation](https://scikit-learn.org/stable/install.html)
## 下一步
进入第 2 课《缺失值、类别编码与预处理流水线》，确保相同的训练期预处理能被验证和推理复用。
