<div class="be-tutor-mount" data-tutor-lesson="nlp-transformer-02" aria-hidden="true"></div>
<section id="overview-tfidf-result" class="be-page-hero be-lesson-hero" data-learning-context="overview-tfidf-result" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">NLP 与 Transformer · 第 2 课 · 文本分类模型演进 v0.2</span>
# 分词、TF-IDF 与线性分类基线
## 同一批验证题，模型开始读文本了
```text
vocabulary_size=232
baseline_validation: accuracy=0.500,macro_f1=0.333
model_validation: accuracy=0.875,macro_f1=0.873
validation_errors=P09
test_policy=sealed
```
这 8 条验证短句上，TF-IDF 加线性分类器比“全部猜 code”少错了 3 条。但 0.875 只代表这套小型原创语料的验证结果，不能证明模型已适用于真实提问。先问自己：它是学会了问题含义，还是抓住了少量词形线索？
</section>

<div class="be-lesson-overview">
  <div><span>适合谁</span><strong>已学数据切分与指标，想做第一种文本模型的学习者</strong></div>
  <div><span>前置</span><strong><a href="../01-text-data-contract-splits-metrics/">第 1 课：数据契约与评估</a></strong></div>
  <div><span>环境</span><strong>Python 3.11+ 标准库；CPU；无需联网或下载模型</strong></div>
  <div><span>本课留下</span><strong>P3.2 传统文本基线、验证指标与错误记录</strong></div>
</div>

## 学习目标

- 解释字符二元组、词频、逆文档频率与线性打分各在做什么。
- 只用训练集拟合词表、IDF 和分类器，再用验证集做一次同口径比较。
- 读混淆矩阵和具体错误，不只读一个准确率。
- 改动特征规则，先预测可能受影响的句子，再运行验证。

<section id="concept-token-tfidf" data-learning-context="concept-token-tfidf" data-context-type="concept" markdown="1">
## 先把句子变成可比较的数

这里的“分词”先选一个不依赖中文词典的做法：移除空白、英文字母转小写，再取相邻两个字符。例如 `学习计划` 变成 `学习`、`习计`、`计划`；`A 中 文` 变成 `a中`、`中文`。这种字符二元组能保留短词形，也可能把无关的相邻字符当特征；它不是语言学意义的完整中文切词。

训练集中每个二元组的权重是 `词频 × IDF`。本课的平滑公式为 `IDF=1+ln((1+训练文档数)/(1+包含该组的训练文档数))`，再把每句话的向量缩放到 L2 长度 1。同一二元组出现在许多训练句里时，IDF 相对较低；只出现少数句里时相对较高。词表和 IDF 都是学出来的状态，因此验证句、测试句不能参与 `fit`。
</section>

<section id="concept-linear-score" data-learning-context="concept-linear-score" data-context-type="concept" markdown="1">
## 线性分类器怎样选标签

模型给每个二元组一个权重，计算 `score = bias + 各特征值×对应权重之和`。本课用全批量二元逻辑回归学习权重：`score ≥ 0` 预测 `code`，否则预测 `plan`。训练固定 300 轮、学习率 1.0、L2 系数 0.01；这些是教学配置，不是为验证集反复搜索出的最优值。模型只能利用看到的词形组合，无法保证理解同义表达、否定或新领域用语。

```text
v0.1 固定分区 ── train 24 句 ── 拟合词表/IDF/线性权重
                         validation 8 句 ── 仅变换和预测 ── 指标与错误
                         test 8 句 ── 保持封存
```
</section>

<section id="example-small-tfidf" data-learning-context="example-small-tfidf" data-context-type="example" markdown="1">
## 先猜一个二元组的权重

假设训练集只有 `学习计划`、`学习复盘`、`代码报错` 三句。`学习` 出现在前两句，`代码` 只在第三句；按上面的公式，`学习` 的 IDF 是 `1+ln(4/3)≈1.288`，`代码` 是 `1+ln(4/2)≈1.693`。先预测：若第三句里的 `代码` 出现两次，归一化前它的 TF-IDF 会怎样？答案是词频从 1 到 2，归一化前权重翻倍；归一化后各维还会一起缩放，不能只盯一维读最终向量。

真正分类时不能根据“稀有”直接断言类别。线性权重还需从标签学来。v0.2 在验证集只错了 `P09`：`什么时候回顾错题记录` 被预测为 `code`，实际是 `plan`。`错题`、`记录` 等词形同时可能靠近技术与学习计划语境；单个错误值得读原句，不应为了这 1 条马上改语料或偷看测试集。
</section>

<section id="reproduce-tfidf-v02" data-learning-context="reproduce-tfidf-v02" data-context-type="reproduce" markdown="1">
## 跑出同一份验证结果

从仓库根目录运行，`experiment.py` 会直接加载相邻 v0.1 的 `corpus.csv`、`read_corpus()`、`split_rows()` 和 `evaluate_validation()`。不需要第三方包；下列结果已在 Python 3.11.9 验证：

```bash
python3 -m unittest discover -s site-src/examples/nlp-transformer/text-classification-evolution-v02 -p 'test_*.py' -v
python3 site-src/examples/nlp-transformer/text-classification-evolution-v02/experiment.py
python3 site-src/examples/nlp-transformer/text-classification-evolution-v02/experiment.py --output /tmp/be-nlp-v02-artifacts
```

应看到本页开头的 `vocabulary_size=232`、两组准确率和 `validation_errors=P09`。第三条向空目录写 `result.json`，保留语料指纹、分区种子、训练/验证 ID、配置、混淆矩阵和错误句。若目录已非空，程序会拒绝覆盖；换一个目录名即可。验证报告不生成测试集预测，也不把测试标签交给模型。
</section>

<section id="modify-ngram-rule" data-learning-context="modify-ngram-rule" data-context-type="modify" markdown="1">
## 改一处特征规则，再解释变化

先记下原版的 `232` 个特征、`0.875` 准确率和 `P09`。在练习副本里将 `tokens()` 的 `i:i + 2` 改为 `i:i + 3`，预测词表大小和 `P09` 的分类可能怎样变，再跑测试与脚本。恢复原版后，尝试把 `EPOCHS` 从 `300` 改成 `30`，比较验证指标。改动会让固定报告断言失败：这是测试在提醒你已经改变实验配置；练习时先记录新旧结果，不要为了让新结果看起来“通过”而改 v0.1 数据契约或删除断言。

这两次探索都用了同一验证集；若据此决定正式选用某方案，要诚实记录选择过程。不要继续无止境地试参数直到 8 条验证句全对，那会把验证集变成事实上的训练反馈。
</section>

<section id="troubleshoot-tfidf" data-learning-context="troubleshoot-tfidf" data-context-type="troubleshoot" markdown="1">
## 数字不对时查哪一层

| 现象 | 先查 | 恢复 |
| --- | --- | --- |
| 找不到 v0.1 文件 | v0.2 是否仍在相邻目录 | 保持两个版本的相对位置，从仓库根目录运行 |
| 词表不是 232 | `tokens()`、语料指纹、训练 ID | 恢复原版分词和固定划分，不用验证数据补词表 |
| 指标突然很好但无法复现 | 是否先用全部语料算 IDF 或改过训练配置 | 只在 train 拟合，记录参数，重新运行测试 |
| `prediction IDs must exactly match validation IDs` | 预测字典是否漏项或混入测试 ID | 只给 `evaluate_validation()` 完整验证 ID |
| 新句向量为空 | 所有二元组都不在训练词表 | 检查输入归一化；把它作为分布外风险记录，不现场扩词表 |
| 再次写输出报目录非空 | 旧 `result.json` 尚在 | 换新目录，保留旧实验记录 |
</section>

<section id="project-text-v02" data-learning-context="project-text-v02" data-context-type="project" markdown="1">
## 文本分类模型演进：P3.2

上一版 P3.1 已锁定 40 句原创语料、24/8/8 分区、准确率、macro-F1 和混淆矩阵接口。本版没有复制或重切数据，而是在 `text-classification-evolution-v02/experiment.py` 中加入字符二元组、TF-IDF 与线性逻辑回归；`test_experiment.py` 守住训练拟合边界和固定输出。保存 `result.json`、一次特征规则改动前后的比较，以及对 `P09` 的简短解释。下一版 P3.3 在同一分区上加入 Embedding 与浅层网络，再比较效果、错误和计算成本。
</section>

## 四类学习者入口

- 零基础兴趣：拿 `学习计划` 手写三个字符二元组，再在 `result.json` 中找出模型与“全部猜 code”的两组指标，解释为什么不能只看准确率。
- 有基础兴趣：把二元组临时改成三元组，先预测词表大小会怎样变，再记录验证混淆矩阵和 `P09` 是否仍出错；恢复原版后确认 6 项测试通过。
- 零基础求职：把本课当作项目证据整理练习，保存命令、运行环境、`result.json` 和一段不夸大效果的说明：只用 24 条训练句拟合，8 条验证句比较，测试集尚未用于选模。这不是招聘题或岗位频率结论。
- 有基础求职：在个人练习副本中为“验证文本改变不影响训练词表”补一个断言，并说明其防泄漏意义；提交原版与改版测试输出、`P09` 错误分析和仍未验证的真实数据风险。这是可复查的项目记录，不是企业题目复现。

## 完成检查

- [ ] 我能解释为什么 IDF 只由训练句计算，以及字符二元组有什么盲点。
- [ ] 测试通过，脚本显示 `0.500/0.333` 与 `0.875/0.873` 两组验证指标。
- [ ] 我读过 `P09` 原句和混淆矩阵，没有只报告准确率。
- [ ] 我改过一个特征或训练参数，并记录预测、新结果和回退方式。
- [ ] 我没有用测试集选择模型，也没有把教学数据结果说成真实产品表现。

## 来源与版本

- 适用版本：Python 3.11+ 标准库（本地验证 3.11.9）；本课 `experiment.py` 的公式和优化器是可审查的教学实现，不等同于 scikit-learn 的默认实现。
- 核查日期：2026-10-13；输出由本课脚本与测试在本地复现。
- 一手资料：[scikit-learn 的 TF-IDF 定义与平滑公式](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfTransformer.html)、[逻辑回归说明](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)、[数据泄漏与训练/验证边界](https://scikit-learn.org/stable/common_pitfalls.html)。
- 安全与成本：原创教学短句，无个人对话、密钥、付费 API、GPU 或联网要求；换成真实文本前要另做隐私、授权和分布核查。

## 下一步

进入第 3 课《Embedding 与浅层网络》：保留同一分区和指标，看看可学习的连续表示能否改善传统词形特征的盲点。
