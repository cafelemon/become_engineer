<div class="be-tutor-mount" data-tutor-lesson="nlp-transformer-01" aria-hidden="true"></div>
<section id="overview-text-task" class="be-page-hero be-lesson-hero" data-learning-context="overview-text-task" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">NLP 与 Transformer · 第 1 课 · 文本分类模型演进 v0.1</span>
# 文本任务、数据契约、切分与指标
## 模型还没训练，先让每次比较用同一张考卷
```text
rows=40,labels=code:20,plan:20
train_rows=24,class_counts=code:12,plan:12
validation_rows=8,class_counts=code:4,plan:4
test_rows=8,class_counts=code:4,plan:4
overlap=0
test_policy=sealed_until_final_selection
```
这些是离线原创教学短句，不是用户聊天记录。即使下一课换成 TF-IDF、以后再换神经网络，也必须在同一任务、同一划分和同一指标上比较。本课输出的是可复查的实验边界，不宣称已经得到可用分类器。
</section>

<div class="be-lesson-overview">
  <div><span>适合谁</span><strong>完成机器学习与深度学习基础、想理解文本模型比较的学习者</strong></div>
  <div><span>前置</span><strong>数据划分、混淆矩阵、训练与验证</strong></div>
  <div><span>环境</span><strong>Python 3.12 标准库；CPU；无需网络或模型下载</strong></div>
  <div><span>本课留下</span><strong>文本分类任务、固定切分、语料指纹和评估接口</strong></div>
</div>

## 学习目标

- 把文本分类说清为输入短句、输出标签，而不是把“会聊天”当目标。
- 区分训练、验证和最终测试的用途，检查样本 ID 与文本重复。
- 用准确率、混淆矩阵和 macro-F1 读出多数类预测的局限。
- 保存可复现的切分与数据指纹，让后续模型只替换模型部分。

<section id="concept-text-contract" data-learning-context="concept-text-contract" data-context-type="concept" markdown="1">
## 一条文本是一个样本，标签不是模型输入

`corpus.csv` 每行只有 `sample_id,label,text`。`text` 是预测时可见输入；`label` 是训练与评估时使用的正确答案；`sample_id` 用于追踪样本，不应被当成语言特征。任务固定为区分编程排错问题 `code` 与学习计划问题 `plan`，不是判断提问者身份、意图强弱或真实业务价值。

数据集是 40 条原创短句，两个标签各 20 条。程序会拒绝未知标签、重复 ID、空文本和规范化后相同的文本。它不能自动发现所有“换几个字但实质相同”的近重复；扩展语料时仍须人工检查来源、版权、隐私及语义重复。
</section>

<section id="concept-split-boundary" data-learning-context="concept-split-boundary" data-context-type="concept" markdown="1">
## 三份数据各做一件事

| 分区 | 每类 | 用途 | 不能做的事 |
| --- | ---: | --- | --- |
| 训练 | 12 | 拟合词表、IDF 和模型参数 | 偷看验证或测试统计量 |
| 验证 | 4 | 比较候选方案、查错误类型 | 反过来参与拟合 |
| 测试 | 4 | 方案冻结后的最后一次独立检查 | 反复查看并据此调参 |

划分对每个标签独立进行：固定种子与 `sample_id` 算出 SHA-256 排序键，再取前 12／中间 4／最后 4。输入 CSV 的行顺序变了，分区 ID 不变。SHA-256 在这里只是确定性排序工具，不是匿名化；语料仍是明文，不能靠哈希规避隐私要求。
</section>

<section id="example-confusion-baseline" data-learning-context="example-confusion-baseline" data-context-type="example" markdown="1">
## 先预测：全部回答 `code` 会得几分？

验证集有 4 条 `code`、4 条 `plan`。如果不读文本、全部预测 `code`，你会得到：

| 实际 \ 预测 | code | plan |
| --- | ---: | ---: |
| code | 4 | 0 |
| plan | 4 | 0 |

准确率是 `4/8 = 0.500`。`code` 的 F1 是 `2×4/(2×4+4+0)=0.667`，`plan` 的 F1 是 0，因此 macro-F1 是约 `0.333`。准确率看起来并非零，但这个方案完全不会识别学习计划问题。后续模型要同时报告类别错误和代价，不能只挑一个好看的数字。
</section>

<section id="reproduce-text-v01" data-learning-context="reproduce-text-v01" data-context-type="reproduce" markdown="1">
## 在本地生成第一版实验记录

从仓库根目录运行；只需 Python 3.12 标准库，不安装额外依赖：

```bash
cd site-src/examples/nlp-transformer/text-classification-evolution-v01
python3 -m unittest -v test_experiment.py
python3 experiment.py
python3 experiment.py --output /tmp/be-nlp-v01-artifacts
```

测试应显示 `Ran 10 tests` 和 `OK`。第二条命令会输出本页顶部的计数，以及语料 SHA-256 `8973927ed683f32cf92bb4a1483b960f3b8c09b0b8497bd0c5176891252b713c`。第三条在空目录中写出 `train.csv`、`validation.csv`、`test.csv` 和 `manifest.json`；若目录已有文件，程序拒绝覆盖。`manifest.json` 保存数据指纹、固定种子、分区 ID、类别数和测试集封存策略。

`experiment.py` 暴露 `read_corpus()`、`split_rows()`、`build_manifest()` 与 `evaluate_validation()`。最后一个函数只接受验证集完整 ID 的预测标签，拒绝测试 ID、缺项和未知标签，返回准确率、macro-F1 与混淆矩阵。下一课直接复用该评估口径。
</section>

<section id="modify-text-v01" data-learning-context="modify-text-v01" data-context-type="modify" markdown="1">
## 改一处数据，观察契约是否保护了比较

先预测：交换 `corpus.csv` 中两行的顺序后，分区会变吗？实际试一次，应该不变。再复制一条文本或 ID，运行测试或脚本，观察它怎样拒绝重复。最后在一份练习副本中改变一条短句，比较语料指纹；若要正式采用改动，应把它视作新的数据版本，重新记录实验，而不是与旧指标直接横比。不要把私人聊天、真实姓名或受版权限制的语料放进公开仓库。
</section>

<section id="troubleshoot-text-v01" data-learning-context="troubleshoot-text-v01" data-context-type="troubleshoot" markdown="1">
## 数字或运行结果不对时，从数据边界查起

| 现象 | 检查位置 | 恢复办法 |
| --- | --- | --- |
| `duplicate sample_id` 或 `duplicate text` | `corpus.csv` | 保留唯一且有明确来源的样本，不靠改 ID 掩盖相同文本 |
| 类别数不是 20/20 | `label` 列 | 找到漏行或错误标签；不要临时改切分比例蒙混过关 |
| 换行序后分区改变 | 是否沿用 `split_rows()` | 不按 CSV 物理顺序切分，核对固定种子与 ID 排序键 |
| 评估拒绝预测 ID | `evaluate_validation()` 输入 | 只传完整验证集 ID；测试集不用于选模 |
| 第二次输出报目录非空 | `--output` 路径 | 换一个新目录，或先人工审阅旧产物后另存；程序不会覆盖 |
| 指标看起来很高 | 混淆矩阵与样本来源 | 检查类别偏斜、数据泄漏与近重复，不急着宣布模型有效 |
</section>

<section id="project-text-v01" data-learning-context="project-text-v01" data-context-type="project" markdown="1">
## 文本分类模型演进 v0.1

此前已有结构化数据机器学习中的划分、指标与防泄漏方法，以及深度学习的训练循环；文本项目本身还没有可比较的第一版。本课在 `text-classification-evolution-v01/` 固定 `corpus.csv`、`experiment.py`、`test_experiment.py`，运行后保存 `manifest.json`、三份分区 CSV、测试输出和一段对多数类基线的解释。下一版只在训练集拟合 TF-IDF 与线性分类器，用相同验证集和 `evaluate_validation()` 比较，不改变任务与切分。
</section>

## 四类学习者入口

- 零基础兴趣：读三条样本，说出哪个字段是输入、哪个字段是答案。
- 有基础兴趣：解释为什么换 CSV 行序不应影响划分。
- 零基础求职：用上面的混淆矩阵说明准确率 0.5 的盲点。
- 有基础求职：写出一个防止近重复、目标泄漏与测试集反复使用的实验审查清单。

## 完成检查

- [ ] 10 项 Python 测试通过，能复述 40 条样本与 24/8/8 分区。
- [ ] 能解释 `text`、`label`、`sample_id` 的不同职责。
- [ ] 能算出全部预测 `code` 时的准确率、macro-F1 与混淆矩阵。
- [ ] 改过数据顺序或样本副本，观察稳定性或拒绝行为。
- [ ] 保存 manifest 与自己的实验说明；没有用测试集挑模型。

## 来源与版本

- 适用环境：Python 3.12 标准库；核查日期：2026-10-13。语料为本课原创教学短句，不代表真实用户分布或部署效果。
- [Python `csv` 文档](https://docs.python.org/3.12/library/csv.html)：CSV 读写行为。
- [Python `hashlib` 文档](https://docs.python.org/3.12/library/hashlib.html)：SHA-256 接口。
- [scikit-learn 分类指标说明](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)：混淆矩阵、F1 与宏平均概念；本课评估实现只用标准库。
- 代码与输出由 `python3 -m unittest -v test_experiment.py` 和 `python3 experiment.py` 核查；跨 Python 版本与不同语料须重新核验指纹。

## 下一步

进入第 2 课《TF-IDF、线性分类器与可比较基线》：只让训练集决定词表与 IDF，验证集衡量是否真的超过不读文本的基线。
