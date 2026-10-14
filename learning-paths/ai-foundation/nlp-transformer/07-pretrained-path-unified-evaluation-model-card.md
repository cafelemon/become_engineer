<div class="be-tutor-mount" data-tutor-lesson="nlp-transformer-07" aria-hidden="true"></div>
<section id="overview-final-gap" class="be-page-hero be-lesson-hero" data-learning-context="overview-final-gap" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">NLP 与 Transformer · 第 7 / 7 课 · 文本分类模型演进 v0.7</span>
# 预训练路径、统一评测与模型卡
## 验证集 8/8，最终测试却只有 4/8：还能说“模型做好了”吗？
```text
selection_before_test=v06-encoder-full
validation: accuracy=1.000, macro_f1=1.000
final_test: accuracy=0.500, macro_f1=0.467
final_test_errors=C03,C04,C15,P18
pretrained_model_evidence=not_run
```
不能。六个可发布候选在同一划分上按预先写好的规则比较，完整 Encoder 以验证 macro-F1 最高入选；只对它打开一次最终测试，结果明显下降。本课保留这个不漂亮但重要的发现，不按测试结果回头换模型。预训练模型只是可选人工研究路径，本轮没有权重下载、微调或实测。
</section>

<div class="be-lesson-overview">
  <div><span>适合谁</span><strong>完成本组前六课，准备解释实验结论的学习者</strong></div>
  <div><span>前置</span><strong>v0.1 固定协议；v0.2–v0.6 各模型与错误报告</strong></div>
  <div><span>环境</span><strong>Python 3.12 · PyTorch 2.13.0 · CPU · 离线</strong></div>
  <div><span>留下</span><strong>选择记录、一次性测试收据、最终报告与模型卡</strong></div>
</div>

## 学习目标

- 用同一语料指纹、train/validation ID 和指标核对不同模型报告是否可比较。
- 在碰测试集之前写明候选资格、排序规则和成本解释。
- 只对选中的模型做一次最终测试，看到落差后不反向调参或重选。
- 把用途、指标、失败样本、限制与未做过的预训练实验如实写入模型卡。

<section id="concept-one-protocol" data-learning-context="concept-one-protocol" data-context-type="concept" markdown="1">
## 同一考卷，才能比较不同做法

v0.2 的字符 bigram TF-IDF＋线性分类器、v0.3 的均值 Embedding、v0.4 的 GRU/CNN、v0.5 的单头注意力以及 v0.6 的完整 Encoder，数据都是 40 条原创教学短句；训练 24、验证 8、最终测试 8。`delivery_lab.py` 在汇总前检查语料 SHA-256、切分种子、训练与验证 ID 和“测试仍封存”标志，任一不一致就拒绝合表。

评估固定报告 accuracy、macro-F1、混淆矩阵与错误 ID。成本列出参数量和本机单次运行耗时；计时受启动、系统负载和实现方式影响，不能当成跨架构、跨硬件的严格速度榜。v0.6 的“去位置”“去 key padding mask”是故意拆掉结构的消融对照，不具备发布候选资格，不能因某次分数凑巧好就选它上线。
</section>

<section id="concept-select-once" data-learning-context="concept-select-once" data-context-type="concept" markdown="1">
## 先冻结选择，再开最后一份数据

本课的规则写在最终测试之前：仅六个完整候选入围，先比验证 macro-F1，再比 accuracy；若仍相同，选参数更少者；最后按候选 ID 字典序。测试集分数不在规则中。一次固定环境运行得到：

| 候选 | 验证准确率 | 验证 macro-F1 | 错误 ID | 参数量 |
| --- | ---: | ---: | --- | ---: |
| v02 线性 | 0.875 | 0.873 | P09 | 233 |
| v03 Embedding | 0.875 | 0.873 | P09 | 1,482 |
| v04 GRU | 0.625 | 0.619 | C06、P09、P15 | 1,914 |
| v04 CNN | 0.625 | 0.564 | P01、P09、P15 | 1,682 |
| v05 单头注意力 | 0.875 | 0.873 | P09 | 1,674 |
| v06 完整 Encoder | **1.000** | **1.000** | 无 | 5,186 |

规则选出 v06 完整 Encoder。参数多不意味着好；这里它只是先在主要验证指标上领先。验证集仅 8 条，满分尤其容易让人误以为能力已经稳固。最终测试得到 4/8，macro-F1 约 0.467，错误为 `C03`、`C04`、`C15`、`P18`。这提示数据与模型的泛化风险，不能据此重新挑 v02，也不能偷偷调参后仍称这轮测试“独立”。
</section>

<section id="example-selection-trace" data-learning-context="example-selection-trace" data-context-type="example" markdown="1">
## 手工走一次规则，再看测试收据

先不看测试：v02、v03、v05 都是 macro-F1 约 0.873；若只有三者，它们准确率也相同，规则会选参数更少的 v02。现在加入 v06 完整 Encoder，macro-F1=1.000，第一层就胜出，无需比较参数量。两个消融变体纵使接近，也因结构不完整被排除。

执行 `--finalize` 时先写 `selection.json` 和 `test-opened.json`，后者记录唯一获选候选和 8 个测试 ID；之后才训练该候选并评估测试。输出目录非空时拒绝运行。收据不能阻止别人复制语料另做实验，它防止的是这条示例工作流无声地用同一目录反复打开测试。
</section>

<section id="reproduce-delivery-v07" data-learning-context="reproduce-delivery-v07" data-context-type="reproduce" markdown="1">
## 先看计划，再一次性生成模型卡

从仓库根目录准备 Python 3.12 与 PyTorch 2.13.0，然后进入项目；首次安装依赖可能下载 PyTorch wheel，之后的测试和实验不需要模型账号、网络或外部语料：

```bash
python3.12 -m venv .venv-nlp
.venv-nlp/bin/python -m pip install -r site-src/examples/nlp-transformer/text-classification-evolution-v07/requirements.txt
cd site-src/examples/nlp-transformer/text-classification-evolution-v07
../../../../.venv-nlp/bin/python -m unittest -v test_delivery_lab.py
../../../../.venv-nlp/bin/python delivery_lab.py
```

应看到 `Ran 10 tests`、`OK`，以及 `selected_before_test=v06-encoder-full`、`test_status=sealed_before_selection`。检查六个候选、两项排除的消融和选择规则后，才在新空目录运行一次：

```bash
../../../../.venv-nlp/bin/python delivery_lab.py --finalize --output /tmp/be-nlp-v07-my-final
```

输出包括 `selection.json`、`test-opened.json`、`final-report.json` 与 `model-card.md`。本课已经完成一次正式教学实验，固定结果也保存于本项目 `MODEL_CARD.md`；再练习命令应视作另一轮复现，不可把多次测试中最好的一次当成首次独立结果。若中途失败，先查看收据和已写文件，不直接换目录连试。
</section>

<section id="modify-policy-v07" data-learning-context="modify-policy-v07" data-context-type="modify" markdown="1">
## 修改选择规则，但只在验证计划里练习

在一份练习副本中，先写下“如果 macro-F1 与 accuracy 同分，优先小模型”的预测，再用 `select_candidate()` 的玩具候选单测验证。也可以试着把消融变体放入候选列表，观察规则为何必须有资格门禁；练习结束后恢复原门禁。此练习只操作验证计划或合成玩具数据，**不**重新打开本轮真实测试集以挑一个更好看的赢家。
</section>

<section id="troubleshoot-delivery-v07" data-learning-context="troubleshoot-delivery-v07" data-context-type="troubleshoot" markdown="1">
## 结果不一致时先保护最后一份数据

| 现象 | 检查 | 恢复 |
| --- | --- | --- |
| 汇总拒绝语料指纹或 ID | v0.1 文件、seed、各报告字段 | 停止横比，另立新数据协议，不改现有测试结果 |
| 消融进入候选 | `eligible_for_release` | 把故意去结构的变体留在诊断附录 |
| 输出目录非空 | `selection.json` 与 `test-opened.json` | 人工审阅旧审计记录；不要清目录或换目录重刷分 |
| 验证满分、测试显著下降 | 混淆矩阵、错误 ID、样本量 | 记录泛化落差，规划独立新数据；不回头用测试调参 |
| PyTorch 导入失败 | 当前 Python 与依赖版本 | 在隔离环境按 `requirements.txt` 安装，保留旧结果 |
| 本机秒数波动 | 启动、预热、系统负载 | 只把时间作观察记录，不当成通用性能排名 |
</section>

<section id="project-model-card-v07" data-learning-context="project-model-card-v07" data-context-type="project" markdown="1">
## 文本分类模型演进 v0.7：把失败也交付

前六版已经有固定语料、传统模型、Embedding、序列模型、注意力和完整 Encoder；本课不再加一个更复杂的网络，而是在 `text-classification-evolution-v07/delivery_lab.py` 汇总可比的验证指标、错误与成本，生成选择记录和一次性测试收据。保留项目 `MODEL_CARD.md`、测试输出、六候选表、最终混淆矩阵与错误 ID。下一阶段若需要真实文本或预训练模型，必须先另立数据许可、独立评估和资源预算；不能把本轮离线结果包装成可上线模型。
</section>

## 可选人工路径：预训练表示与微调

预训练模型可能提供不同起点，但本课没有下载权重、运行微调或测到预训练分数。若以后手动研究，先审阅拟用模型卡的来源、许可、适用范围和训练数据说明；固定模型 revision、权重与 tokenizer 版本，记录硬件、费用、依赖和输入数据许可。仅在明确允许下载、具备计算资源时，保留同一任务与划分做特征抽取或微调实验，并新建模型卡与独立验收。`local_files_only` 一类离线配置只表示不尝试下载，不等于已经完成预训练评估。

## 四类学习者入口

- 零基础兴趣：按表格找出谁先在验证集胜出，再说出测试分数为何不参与选择。
- 有基础兴趣：复算 v02/v03/v05 同分时的参数量决胜，解释耗时为何只作本机观察。
- 零基础求职：用模型卡说明“验证满分但测试仅半数正确”，不把它包装成优势。
- 有基础求职：审查候选资格、收据与四个最终错误 ID，指出还缺哪些独立数据证据。

## 完成检查

- [ ] 10 项单测通过，六候选与两项非候选消融都在计划中。
- [ ] 能不看测试结果独立复述规则，选出 `v06-encoder-full`。
- [ ] 一次性收据和最终报告一致：测试 4/8、macro-F1≈0.467、四个错误 ID。
- [ ] 能解释验证 8/8 与最终测试 4/8 的落差，以及为什么不能回头重选。
- [ ] 模型卡明确用途、限制、成本观察和“预训练未实测”。

## 来源与版本

- 适用环境：Python 3.12、PyTorch 2.13.0、CPU；核查日期：2026-10-14。所有数据为原创教学短句，无真实用户记录、付费 API 或硬件实测。
- [PyTorch TransformerEncoderLayer 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html)：本组完整 Encoder 的接口边界。
- [Hugging Face 模型卡官方说明](https://huggingface.co/docs/hub/en/model-cards)：用途、数据、评估与限制等报告项目。
- [Hugging Face Auto Classes 官方文档](https://huggingface.co/docs/transformers/model_doc/auto)：模型 revision 与 `local_files_only` 参数；这里只说明可选路径，未调用。
- 本课结果由 `test_delivery_lab.py`、`delivery_lab.py` 的验证计划和一次性最终测试产物核查；8 条测试句不足以支持真实部署结论。

## 下一步

本组七课结束。回看 [文本分类模型演进项目](../../../projects/text-classification-evolution/README.md) 的各里程碑，并先为下一轮独立数据与许可做方案；不要把更多测试集试错藏进这一轮模型卡。
