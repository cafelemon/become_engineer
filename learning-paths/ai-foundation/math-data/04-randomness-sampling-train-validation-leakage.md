<div class="be-tutor-mount" data-tutor-lesson="ai-math-data-04" aria-hidden="true"></div>
<section id="overview-reproducible-split" class="be-page-hero be-lesson-hero" data-learning-context="overview-reproducible-split" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">数学、数据与可复现实验 · 第 4 / 6 课 · 可复现实验与评估系统 v0.4</span>
# 随机性、抽样、训练/验证划分与泄漏
## 种子复现一次抽样，边界保证一次评估可信
```text
seed=20260723
training_ids=a,b,c,e,f,h
validation_ids=d,g
training_label_counts=0:3,1:3
validation_label_counts=0:1,1:1
overlap=0
repeated=identical
duplicate_id=reject
invariants=seeded-local-rng,stratified,no-overlap
```
本课使用局部伪随机生成器和稳定样本 ID，固定一次分层划分，同时明确“可复现”不等于“没有抽样偏差”。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>数学数据实验 · 4 / 6</strong></div>
  <div><span>前置</span><strong>Schema、身份与质量门禁</strong></div>
  <div><span>实现</span><strong>Python 3.11 标准库</strong></div>
  <div><span>完成后留下</span><strong>显式种子、分层划分与无交叉证据</strong></div>
</div>
## 学习目标
- 区分伪随机、随机种子和真正的实验不确定性。
- 用局部 `Random(seed)` 避免修改全局随机状态。
- 在每个标签内部抽取验证样本，保留最小类别覆盖。
- 证明训练集与验证集无交叉、无丢失。
- 识别重复实体、预处理越界和按时间错误划分造成的泄漏。
<section id="concept-seed-local-rng" data-learning-context="concept-seed-local-rng" data-context-type="concept" markdown="1">
## 种子固定伪随机序列，不会让样本天然有代表性
相同算法、输入顺序和种子会产生相同抽样。本实验先按 `sample_id` 排序，再创建 `Random(20260723)`，因此即使输入行顺序改变，划分仍一致。

局部随机生成器不会重置应用其他部分的全局随机状态。种子是复现条件，不是安全随机数，也不是“结果已经稳健”的证明；稳健性仍需多次划分、交叉验证或时间外测试。
</section>
<section id="concept-stratified-partitions" data-learning-context="concept-stratified-partitions" data-context-type="concept" markdown="1">
## 分层先在类别内部抽样，再组合分区
样例中标签 0 和 1 各有 4 个样本。每类抽 1 个进入验证集，因此训练集计数为 `0:3,1:3`，验证集为 `0:1,1:1`。

若少数类只有一个样本，它不能同时支持训练和验证。本课拒绝这种划分，不通过复制同一个样本来伪造类别覆盖。
</section>
<section id="example-no-overlap-leakage" data-learning-context="example-no-overlap-leakage" data-context-type="example" markdown="1">
## 无交叉是最低边界，不是全部泄漏检查
本实验验证：

```text
training_ids ∩ validation_ids = ∅
training_ids ∪ validation_ids = all_ids
```

重复 `sample_id` 在划分前直接拒绝，因为同一实体出现在两边会让验证集不再独立。现实中还要检查同一用户的多条记录、同一次采集的切片、未来信息生成的特征，以及先看全量数据再拟合的标准化或填充规则。
</section>
<section id="reproduce-split-v04" data-learning-context="reproduce-split-v04" data-context-type="reproduce" markdown="1">
## 运行确定性分层划分
```bash
cd site-src/examples/ai-math-data/reproducible-experiment-v04
../../../../.venv/bin/python -m unittest -v test_split_lab.py
../../../../.venv/bin/python split_lab.py
```
6 项测试覆盖同种子稳定性、无交叉无丢失、类别覆盖、全局随机状态隔离、非法输入和固定报告。
</section>
<section id="modify-split-policy" data-learning-context="modify-split-policy" data-context-type="modify" markdown="1">
## 主动改变种子、比例和分组
1. 换三个种子，比较验证 ID，不能只挑结果最好的一次汇报。
2. 把每类验证数从 1 改为 2，预测分区计数。
3. 增加 `entity_id`，保证同一实体的所有记录进入同一分区。
4. 为带时间的数据实现“过去训练、未来验证”，比较它与随机划分的适用边界。
</section>
<section id="troubleshoot-split-leakage" data-learning-context="troubleshoot-split-leakage" data-context-type="troubleshoot" markdown="1">
## 指标过好或不稳定时先审计分区
| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 同种子结果仍变化 | 输入顺序不稳定 | 按稳定 ID 排序后抽样 |
| 验证集没有少数类 | 直接全局随机切片 | 按标签分层或报告限制 |
| 指标异常接近完美 | 同一实体跨分区 | 用实体/组 ID 划分 |
| 线上明显差于离线 | 随机划分掩盖时间漂移 | 使用时间外验证 |
| 改一个模块影响其他随机结果 | 修改了全局随机状态 | 使用局部 `Random` |
| 多个种子只报告最好值 | 选择性汇报 | 预先固定方案并报告分布 |
</section>
<section id="project-reproducible-experiment-v04" data-learning-context="project-reproducible-experiment-v04" data-context-type="project" markdown="1">
## 可复现实验与评估系统 v0.4
- v0.4 新增按标签分层的确定性训练/验证划分。
- 报告保存种子、两边样本 ID、标签计数和交叉数量。
- 重复 ID、非法标签和无法同时覆盖训练/验证的类别会被拒绝。
- 下一版在固定验证集上建立基线、混淆矩阵和阈值比较。
</section>
## 四类学习者入口
- 零基础兴趣：用 8 张纸牌手动完成每类抽 1 张。
- 有基础兴趣：实现按实体分组的分层划分。
- 零基础求职：解释固定种子为什么不等于评估稳定。
- 有基础求职：为时间序列、同用户多记录设计防泄漏策略。
<section id="career-split-leakage" data-learning-context="career-split-leakage" data-context-type="career" markdown="1">
## 求职加练：随机切分通过了，为何生产仍失败
原创追问：同一用户的多张图片被随机分到训练和验证两边，验证分数极高。请指出实体泄漏，设计按用户分组且保留类别覆盖的划分；再说明固定种子、时间外验证和多次重复实验分别解决什么问题。
</section>
## 完成检查
- 6 项测试通过，固定验证 ID 为 `d,g`。
- 相同种子与相同样本集合得到相同划分。
- 训练和验证无交叉、无丢失，两边都有标签 0 与 1。
- 局部随机生成器不改变全局随机状态。
- 能列出 ID 交叉之外至少两种数据泄漏。
## 来源与版本
- Python 3.11 标准库；核查日期 2026-07-23。
- [Python random](https://docs.python.org/3.11/library/random.html)：伪随机生成器、独立实例和复现边界。
- [scikit-learn Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)：数据泄漏与预处理边界。
## 下一步
进入第 5 课《基线、混淆矩阵、阈值与指标选择》，把固定验证集变成可解释的评估证据。
