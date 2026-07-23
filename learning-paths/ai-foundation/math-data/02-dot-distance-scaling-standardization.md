<div class="be-tutor-mount" data-tutor-lesson="ai-math-data-02" aria-hidden="true"></div>
<section id="overview-scaling-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-scaling-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">数学、数据与可复现实验 · 第 2 / 6 课 · 可复现实验与评估系统 v0.2</span>
# 点积、距离、缩放与标准化
## 数值能比较，不代表量纲已经公平
```text
rows=2,10;4,20;6,30;8,40
means=5.000,25.000
scales=2.236,11.180
z_first=-1.342,-1.342
z_last=1.342,1.342
raw_distance_first_last=30.594
z_distance_first_last=3.795
constant=reject
invariants=train-fit-only,nonzero-scale
```
本课把“拟合统计量”和“应用变换”拆开：均值和尺度只从训练数据获得，验证与测试数据只能复用它们。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>数学数据实验 · 2 / 6</strong></div>
  <div><span>前置</span><strong>向量、形状、点积与欧氏距离</strong></div>
  <div><span>实现</span><strong>Python 3.11 标准库</strong></div>
  <div><span>完成后留下</span><strong>标准化器、训练集统计量与泄漏防线</strong></div>
</div>
## 学习目标
- 解释特征单位和数值尺度为何会主导距离与点积。
- 用 `z=(x-mean)/scale` 计算标准分数。
- 区分总体标准差与样本标准差，并固定本实验采用的口径。
- 把 `fit` 与 `transform` 分离，阻止验证集参与统计量计算。
- 明确处理零方差列，而不是让除零或隐式替代进入结果。
<section id="concept-scale-dominance" data-learning-context="concept-scale-dominance" data-context-type="concept" markdown="1">
## 距离会放大数值尺度，不理解单位就会误读相似性
同一对象可用“米”或“厘米”表达，语义没有变化，数字却扩大 100 倍。欧氏距离会平方每一维的差，所以取值范围更大的列可能掩盖其他列。

样例首尾两行的原始距离是 `30.594`。这不是“第二个特征更重要”的证明，只说明它的数值跨度更大。点积同样受分量尺度影响：把一列换单位，会改变结果大小。
</section>
<section id="concept-z-score-population" data-learning-context="concept-z-score-population" data-context-type="concept" markdown="1">
## 标准化把中心移到 0，把训练集总体方差缩放到 1
对每一列，本课使用：

```text
mean = sum(x) / n
variance = sum((x - mean)^2) / n
scale = sqrt(variance)
z = (x - mean) / scale
```

分母使用 `n`，所以这是本组训练行的总体标准差口径。统计推断中的样本标准差通常用 `n-1`；两者没有谁永远正确，关键是计算、测试和文档采用同一个契约。

样例两列均值为 `5` 和 `25`，尺度约为 `2.236` 和 `11.180`。变换后训练集每列均值为 0、总体方差为 1，首尾距离变成 `3.795`。
</section>
<section id="example-fit-transform-boundary" data-learning-context="example-fit-transform-boundary" data-context-type="example" markdown="1">
## fit 学规则，transform 只应用规则
```python
fitted = fit_standardizer(training_rows)
training_z = fitted.transform(training_rows)
validation_z = fitted.transform(validation_rows)
```
若把验证行一起放进 `fit_standardizer`，验证集的信息就提前改变了均值和尺度。即使没有标签，这也会让评估不再模拟“模型面对未知数据”的过程，属于数据泄漏。

本课用不可变的 `Standardizer(means, scales)` 保存训练统计量。验证行 `(10,50)` 必须用训练均值 `(5,25)` 和训练尺度变换，不能为它重新计算一组“更好看”的统计量。
</section>
<section id="reproduce-scaling-v02" data-learning-context="reproduce-scaling-v02" data-context-type="reproduce" markdown="1">
## 运行缩放实验
```bash
cd site-src/examples/ai-math-data/reproducible-experiment-v02
../../../../.venv/bin/python -m unittest -v test_scaling_lab.py
../../../../.venv/bin/python scaling_lab.py
```
6 项测试覆盖总体均值与尺度、训练列的 0 均值和单位方差、验证集复用训练统计量、常数列拒绝、形状失败和固定报告。报告不写入耗时、随机数或机器路径。
</section>
<section id="modify-scaling-policy" data-learning-context="modify-scaling-policy" data-context-type="modify" markdown="1">
## 主动改变单位、口径与边界
1. 把第二列从“厘米”改成“米”，比较原始距离与标准化距离。
2. 将方差分母改为 `n-1`，先预测尺度与 z 值怎样变化，再同步测试。
3. 给验证集加入极端值，确认训练期 `means` 和 `scales` 完全不变。
4. 把常数列策略改为“删除并记录列名”，不要只把尺度偷偷改成 1。
</section>
<section id="troubleshoot-scaling-leakage" data-learning-context="troubleshoot-scaling-leakage" data-context-type="troubleshoot" markdown="1">
## 指标异常先查拟合边界，再查公式
| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 验证结果异常乐观 | 验证行参与均值或尺度计算 | 只在训练集 fit |
| 某列产生除零 | 训练列所有值相同 | 删除、保留并标记，或定义专门策略 |
| 训练列方差不是 1 | `n` 与 `n-1` 口径混用 | 固定总体或样本标准差 |
| 新数据变换失败 | 列数或顺序与训练时不同 | 先校验 Schema 与形状 |
| 缩放后距离仍不合理 | 标准化不能修复错误特征 | 回查单位、异常值和业务含义 |
| 线上结果无法复现 | 重新拟合而未保存统计量 | 保存训练统计量和版本 |
</section>
<section id="project-reproducible-experiment-v02" data-learning-context="project-reproducible-experiment-v02" data-context-type="project" markdown="1">
## 可复现实验与评估系统 v0.2
- v0.2 新增训练期 `fit_standardizer` 和可复用的 `transform`。
- 固定报告同时保留原始距离和标准化距离，避免只展示处理后的结论。
- 失败契约明确拒绝空表、锯齿表、列数错配和零方差列。
- 下一版先建立表格 Schema 和数据质量报告，再允许数据进入变换。
</section>
## 四类学习者入口
- 零基础兴趣：手算第一列的均值、尺度与首行 z 值。
- 有基础兴趣：实现 min-max 缩放，比较它对极端值的敏感度。
- 零基础求职：解释为什么验证集不能参与标准化器拟合。
- 有基础求职：设计保存列顺序、均值、尺度和版本的数据契约。
<section id="career-scaling-leakage" data-learning-context="career-scaling-leakage" data-context-type="career" markdown="1">
## 求职加练：同一份数据为何离线很好、上线失真
原创追问：团队先合并全量数据做标准化，再划分训练集与验证集，离线指标很好。请指出泄漏路径，设计只在训练集拟合的流水线和回归测试；若生产输入出现训练期常数列或列顺序漂移，系统应怎样拒绝并留下证据？
</section>
## 完成检查
- 6 项测试通过，固定输出中的均值、尺度和两种距离一致。
- 能说明本课使用总体标准差，分母是 `n`。
- 训练数据变换后每列均值为 0、总体方差为 1。
- 验证数据只复用训练统计量，不参与 `fit`。
- 常数列和形状错配在计算前被拒绝。
## 来源与版本
- Python 3.11 标准库；核查日期 2026-07-23。
- [Python statistics](https://docs.python.org/3.11/library/statistics.html)：总体标准差与样本标准差的口径。
- [scikit-learn StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)：用于核对 fit/transform 和特征缩放术语，本课不依赖 scikit-learn 运行。
- [scikit-learn Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)：训练/测试预处理一致性与数据泄漏边界。
## 下一步
进入第 3 课《表格 Schema、缺失值、重复与数据质量》，先判断输入是否可信，再继续数值处理。
