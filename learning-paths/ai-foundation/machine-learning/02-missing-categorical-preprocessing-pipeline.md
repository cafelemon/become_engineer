<div class="be-tutor-mount" data-tutor-lesson="machine-learning-02" aria-hidden="true"></div>
<section id="overview-preprocessing-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-preprocessing-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">机器学习 · 第 2 / 8 课 · 结构化数据机器学习系统 v0.2</span>
# 缺失值、类别编码与预处理流水线
## 只在训练集学习统计量，让验证和推理复用同一条变换链
```text
rows=120,raw_features=5
missing=signal_a:11,signal_b:8,channel:7
train_rows=90,validation_rows=30
fit_scope=train-only,train_median_signal_a=0.378
transformed_features=7,validation_shape=30x7
feature_names=numeric__signal_a,numeric__signal_b,numeric__noise,numeric__redundant_signal,categorical__channel_direct,categorical__channel_organic,categorical__channel_referral
post_transform_missing=0
unknown_category=ignored,raw_validation_unchanged=true
baseline_accuracy=0.667
invariants=target-excluded,fit-train-only,same-pipeline-for-validation
```
本课给 v0.1 加入受控缺失值和类别列，用 `ColumnTransformer` 将两类字段送入不同变换，再用一个 `Pipeline` 固定训练、验证和推理的处理顺序。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>机器学习 · 2 / 8</strong></div>
  <div><span>前置</span><strong>问题定义与多数类基线</strong></div>
  <div><span>依赖</span><strong>NumPy 2.5.1 · pandas 2.3.3 · scikit-learn 1.9.0</strong></div>
  <div><span>完成后留下</span><strong>可复用、无验证泄漏的预处理流水线</strong></div>
</div>

## 学习目标

- 区分缺失、空字符串、未知类别和目标缺失。
- 只用训练数据学习中位数、众数、缩放参数和类别词表。
- 用 `ColumnTransformer` 并行组织数值与类别字段。
- 用 `Pipeline` 保证验证和推理执行与训练相同的预处理。
- 让未知类别可解释地忽略，同时保持输出维度稳定。

<section id="concept-missing-semantics" data-learning-context="concept-missing-semantics" data-context-type="concept" markdown="1">
## 缺失不是一个数字，填补规则必须服从字段语义

数值缺失表示该次观察没有值，本课用训练集的中位数填补，再做标准化；类别缺失表示渠道未知，用训练集众数填补，再做独热编码。目标缺失不能照此填补，因为监督答案不存在时，样本是否可用于训练是任务规则，而不是特征预处理问题。

空字符串也不自动等于缺失。真实系统应在 Schema 中明确哪些原始表示映射为缺失，保留原始字段以便审计，不用一个魔法常数把未知信息伪装成真实测量值。
</section>

<section id="concept-fit-transform-boundary" data-learning-context="concept-fit-transform-boundary" data-context-type="concept" markdown="1">
## fit 学参数，transform 应用参数；验证集只能走后者

`fit` 会学习中位数、均值、标准差、众数和类别词表，这些都属于模型产物的一部分。若先对整表预处理再切分，验证数据已经影响这些参数，评估就不再代表未见数据。

正确顺序是：先冻结训练/验证 ID，再只对训练集 `fit`；验证集和未来推理数据只调用同一已拟合流水线的 `transform` 或 `predict`。本课测试把验证值改成极端大数，确认训练中位数不随之变化。
</section>

<section id="example-column-transformer-pipeline" data-learning-context="example-column-transformer-pipeline" data-context-type="example" markdown="1">
## ColumnTransformer 处理异构列，Pipeline 固定完整执行路径

| 原始字段 | 训练期路径 | 学到的状态 | 输出 |
| --- | --- | --- | --- |
| 4 个数值列 | 中位数填补 → 标准化 | 4 个中位数、均值和尺度 | 4 列连续值 |
| `channel` | 众数填补 → 独热编码 | 众数和 3 个已知类别 | 3 列指示值 |
| `sample_id` | 不进入变换 | 无 | 仅用于追踪 |
| `target` | 不进入变换 | 无 | 只交给分类器 |

最终 5 个原始特征变为 7 个数值特征。`get_feature_names_out()` 固定字段来源，避免只有一个匿名矩阵。分类器仍是多数类基线，让本课只验证数据处理边界，不把模型提升与预处理变化混在一起。
</section>

<section id="reproduce-preprocessing-v02" data-learning-context="reproduce-preprocessing-v02" data-context-type="reproduce" markdown="1">
## 运行 v0.2 并核对变换契约

```bash
cd site-src/examples/machine-learning/structured-data-ml-system-v02
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_preprocessing_lab.py
.venv/bin/python preprocessing_lab.py
```

8 项测试覆盖受控缺失 Schema、错误输入拒绝、数值/类别分支、训练集统计量、无原地修改、未知类别、目标与 ID 排除、固定报告。测试使用真实 scikit-learn 变换器，不用伪造矩阵代替流水线。
</section>

<section id="modify-preprocessing" data-learning-context="modify-preprocessing" data-context-type="modify" markdown="1">
## 主动修改填补、类别和输出契约

1. 把数值填补从中位数改为均值，记录训练统计量和输出变化。
2. 在训练集加入第四个合法类别，预测变换后列数和字段名。
3. 将 `handle_unknown` 改为 `error`，用 `partner` 类别复现失败，再恢复为 `ignore`。
4. 增加缺失指示器，解释它为什么可能有信息，也为什么可能放大数据采集偏差。
</section>

<section id="troubleshoot-preprocessing" data-learning-context="troubleshoot-preprocessing" data-context-type="troubleshoot" markdown="1">
## 预处理出错先查拟合边界、字段路由和产物一致性

| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 交叉验证分数异常高 | 切分前对全表 `fit_transform` | 把预处理放进 Pipeline |
| 线上出现新类别即崩溃 | 编码器默认拒绝未知值 | 明确未知类别策略并测试 |
| 训练和推理列数不同 | 手写 `get_dummies` 或词表漂移 | 持久化同一已拟合变换器 |
| 填补后仍有 NaN | 某列全缺失或路由遗漏 | Schema 拒绝全缺失并检查列选择 |
| 数值列被当作文本 | 原始 dtype 漂移 | 入口校验并给出字段级错误 |
| 原始验证数据被覆盖 | 原地填充或共享引用 | 保留原始快照，变换输出另存 |
</section>

<section id="project-structured-data-ml-v02" data-learning-context="project-structured-data-ml-v02" data-context-type="project" markdown="1">
## 结构化数据机器学习系统 v0.2

- 数据仍为 120 行版本化合成样本，新增长度明确的 `channel` 类别列。
- 固定注入 11 个 `signal_a`、8 个 `signal_b` 和 7 个 `channel` 缺失值。
- `ColumnTransformer` 产生 4 个数值列和 3 个类别列，变换后没有缺失。
- `Pipeline` 将预处理与多数类分类器绑定，验证和未知类别复用同一拟合状态。
- 下一版替换为逻辑回归，观察损失、概率、系数和正则化。
</section>

## 四类学习者入口

- 零基础兴趣：把“学习填补值”和“使用填补值”分别标在训练、验证流程图上。
- 有基础兴趣：加入缺失指示器，比较字段名和变换后宽度。
- 零基础求职：解释为什么先填补全表再切分属于数据泄漏。
- 有基础求职：设计未知类别、全缺失列、Schema 漂移和流水线版本不一致的验收测试。

<section id="career-preprocessing-contract" data-learning-context="career-preprocessing-contract" data-context-type="career" markdown="1">
## 求职加练：离线没问题，线上新渠道让预测接口报错

原创追问：团队训练时用 `get_dummies`，推理时重新从请求生成列。请定位训练/推理不一致、未知类别和列顺序风险；给出基于已拟合 `ColumnTransformer + Pipeline` 的修复方案，并设计不记录原始敏感字段也能定位 Schema 漂移的日志证据。
</section>

## 完成检查

- 8 项测试通过，固定缺失计数为 `11 / 8 / 7`。
- 预处理只在 90 行训练集拟合，验证集不改变训练中位数。
- 5 个原始特征稳定变换成 7 个有名字的数值特征。
- 未知 `partner` 类别不会崩溃，类别分支输出全零。
- 原始验证表不被修改，目标与 ID 不进入预处理。

## 来源与版本

- 核查日期 2026-07-23；运行依赖见同目录 `requirements.txt`。
- [scikit-learn Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html)
- [scikit-learn ColumnTransformer](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html)
- [scikit-learn SimpleImputer](https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html)
- [scikit-learn OneHotEncoder](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html)

## 下一步

进入第 3 课《逻辑回归、损失、概率与正则化》，让第一个可学习模型接入同一预处理流水线。
