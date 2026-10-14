<div class="be-tutor-mount" data-tutor-lesson="nlp-transformer-03" aria-hidden="true"></div>
<section id="overview-embedding-result" class="be-page-hero be-lesson-hero" data-learning-context="overview-embedding-result" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">NLP 与 Transformer · 第 3 / 7 课 · 文本分类模型演进 v0.3</span>
# 词表、Embedding 与池化浅层网络
## 一句话长短不同，怎样送进同一个分类器？

```text
40 条原创学习问题；训练 24 条，验证 8 条，测试 8 条暂不查看
文本 → token ID → Embedding → 去 padding 的均值 → 两类 logits
```

v0.2 的字符 bigram TF-IDF 构造稀疏特征；这次让每个训练词元有一个可学习的向量，再把一句话的向量合成固定长度。目标是看懂词表、`<unk>`、`<pad>` 和池化如何影响模型，不从 8 条验证句推断真实业务性能。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>NLP 与 Transformer · 3 / 7</strong></div>
  <div><span>前置</span><strong>v0.1 固定划分、v0.2 TF-IDF 基线、深度学习训练循环</strong></div>
  <div><span>环境</span><strong>Python 3.12 · PyTorch 2.13.0 · CPU · 离线</strong></div>
  <div><span>完成后留下</span><strong>v0.3 浅层分类器、验证报告与 9 项测试</strong></div>
</div>

## 学习目标

- 只用训练集建立词表，说明验证集词汇为什么不能参与 `fit`。
- 解释 token ID、Embedding 行、`<unk>` 和 `<pad>` 的不同作用。
- 用 mask 排除 padding 后做均值池化，得到固定宽度句向量。
- 在同一划分和指标下与 v0.2 基线比较，记录错误而非只报准确率。

<section id="concept-train-only-vocabulary" data-learning-context="concept-train-only-vocabulary" data-context-type="concept" markdown="1">
## 词表是训练得到的工件

本课 tokenizer 把 `Python`、数字等 ASCII 连续字符保留为词元，把汉字拆成单字。它简单、完全离线且可检查，但不是中文词语切分器。`build_vocab(train_rows)` 只读取 24 条训练句，并按词元排序分配稳定 ID：`<pad>=0`、`<unk>=1`。验证句出现未见过的词元时映射为 1，而不是临时扩大词表。

如果用全体 40 句建词表，验证和测试文本已经影响输入表示；即使未读取标签，也破坏了“只在训练数据上拟合”的比较契约。词表大小和语料指纹应随报告保存。这里的“测试集封存”是实验流程规则：v0.1 原始 CSV 含全部标签，并没有访问控制；本课入口只用测试行核对完整语料身份，不用它们拟合、评估或选模。
</section>

<section id="concept-embedding-masked-mean" data-learning-context="concept-embedding-masked-mean" data-context-type="concept" markdown="1">
## Embedding 是可学习的查表，均值必须跳过 padding

`nn.Embedding(V, 8)` 把 `[B,L]` 个整数 ID 查成 `[B,L,8]` 的向量；`V` 是训练词表大小，8 是本实验的向量宽度，不是语言的天然维度。查表行在反向传播中更新，`padding_idx=0` 的行不用于学习。

不同句子补齐到同一长度后，求均值必须除以真实 token 数。如果把 0 号 padding 一起算入分母，短句会因补齐长度而改变表示。代码用 `token_ids.ne(0)` 得到 mask，再对有效位置求和并除以有效个数。池化结果为 `[B,8]`，线性层输出 `[B,2]` logits。
</section>

<section id="example-padding-and-oov" data-learning-context="example-padding-and-oov" data-context-type="example" markdown="1">
## 先预测两种输入会怎样

先想一想：同一条 ID 序列 `[2,3]` 和 `[2,3,0,0]`，分类 logits 应不应该相同？本课的 mask 使它们相同；测试直接比较两次前向结果。再想一想：新句里的训练词表外词元会不会报错？`encode` 把它送到 `<unk>` 行，模型仍可运行，但若整句几乎全是 `<unk>`，输出不应被视为可靠分类。

没有位置编码、RNN 或 Attention 的均值池化不区分词元顺序。这既是易懂的基线，也是不适合需要精确语序任务的限制。
</section>

<section id="reproduce-embedding-v03" data-learning-context="reproduce-embedding-v03" data-context-type="reproduce" markdown="1">
## 运行 v0.3 并查看验证报告

从仓库根目录执行（已安装 Python 3.12 时）：

```bash
python3.12 -m venv .venv-nlp
.venv-nlp/bin/python -m pip install -r site-src/examples/nlp-transformer/text-classification-evolution-v03/requirements.txt
cd site-src/examples/nlp-transformer/text-classification-evolution-v03
../../../../.venv-nlp/bin/python -m unittest -v test_embedding_lab.py
../../../../.venv-nlp/bin/python embedding_lab.py
```

`embedding_lab.py`、`test_embedding_lab.py` 和依赖文件位于 v0.3 目录；v0.1 的 `corpus.csv` 与 `experiment.py` 必须保留在相邻目录。测试覆盖 tokenizer、训练集词表、OOV、padding、shape/dtype 拒绝、梯度、固定种子、验证 ID 和测试集封存。报告应包含 `train_rows: 24`、`validation_rows: 8`、`test_status: "sealed"`、语料 SHA-256、与 v0.2 相同的划分 ID、`model_validation` 指标、错误 ID、参数量及训练耗时。这里不提供固定准确率作为通过条件：小样本和平台实现差异可能改变数值；固定数据身份、训练协议和边界才是可复查结果。
</section>

<section id="modify-embedding-width" data-learning-context="modify-embedding-width" data-context-type="modify" markdown="1">
## 改宽度并做一个受控对照

先预测把 `embedding_dim=8` 改为 4 后，Embedding 表、池化结果和输出层权重的 shape 会怎样变化。只改这一项，保持 v0.1 划分、训练轮数、学习率与验证指标不变，再运行测试并记录验证混淆矩阵、错误 ID、参数量和训练耗时。不要在看过验证结果后反复调参却只展示最好的一次；也不要为了让分数上升而打开测试集。
</section>

<section id="troubleshoot-embedding" data-learning-context="troubleshoot-embedding" data-context-type="troubleshoot" markdown="1">
## 分数异常时先查数据和表示

| 现象 | 检查位置 | 恢复办法 |
| --- | --- | --- |
| `ModuleNotFoundError: torch` | 运行的 Python 与虚拟环境 | 用 `.venv-nlp/bin/python` 安装并运行 |
| v0.1 路径找不到 | v0.1/v0.3 是否仍是相邻目录 | 恢复原项目目录，不复制语料到新版本 |
| 补齐后同句 logits 变化 | `forward` 的 mask 和分母 | 只除以非 padding 数，跑 padding 不变测试 |
| 大量 `<unk>` | tokenizer 与训练词表覆盖率 | 记录 OOV，先检查输入；不要用验证集扩词表 |
| 验证分数很高或变化很大 | 划分 ID、词表来源、重复调参 | 复核 v0.1 manifest，保留所有对照与错误样本 |
</section>

<section id="project-text-classification-v03" data-learning-context="project-text-classification-v03" data-context-type="project" markdown="1">
## 文本分类模型演进 v0.3

- 上一版：v0.1 固定原创语料、分层划分和评测；v0.2 在同一任务上建立 TF-IDF 线性基线。
- 本课：新增训练集词表、可学习 Embedding、去 padding 均值池化和两类 logits；沿用 v0.1 验证 API，不碰测试集。
- 文件：`text-classification-evolution-v03/embedding_lab.py`、`test_embedding_lab.py`、`README.md`、`requirements.txt`。
- 保存：语料指纹、配置、词表大小、验证混淆矩阵、错误 ID、参数量与测试记录；与 v0.2 对照时说明同一划分和指标。
- 下一版：在相同实验契约上加入 RNN/CNN，检验顺序建模是否值得额外成本。

只比较 8 条教学验证句，不能证明某类模型普遍更好，更不能把它用于真实学习者意图判断。v0.2 到 v0.3 同时改变了 token 表示和分类器，因此结果差异不能单独归因于“用了神经网络”。
</section>

## 四类学习者入口

- 零基础兴趣：拿两条长短不同的句子，手写 token ID 与 padding，解释 mask 为什么让补齐不改变句向量。
- 有基础兴趣：只改 `embedding_dim`，比较参数量、验证错误 ID 和训练耗时；记录这次实验还不能证明什么。
- 零基础求职：整理 v0.1–v0.3 的语料指纹、划分 ID、两版验证指标与测试记录，说明项目是怎样逐步建立可复查比较的；不把小样本分数包装成业务效果。
- 有基础求职：展示 v0.2/v0.3 的不同 tokenizer、模型与错误 ID，解释为什么现有对照不足以单独归因于神经网络，并提出下一次单变量实验。当前没有映射到本课的 V2 求职能力信号，因此这里不制作或声称任何“企业高频”面试题。

## 完成检查

- 9 项测试与离线报告运行通过，报告未包含测试集指标。
- 能解释 `train-only` 词表、`<unk>`、`<pad>`、mask 和均值池化。
- 能手算输入、Embedding、池化、logits 的 shape，并说明顺序信息为何丢失。
- 至少做一次单变量修改，保留预测、实际输出及一次排错记录。
- 与 v0.2 比较时使用同一验证集和指标，并列出至少一个错误样本 ID。

## 来源与版本

- 核查日期：2026-10-13；运行目标：Python 3.12、PyTorch 2.13.0、CPU；本仓库 v0.1 数据契约。
- [PyTorch `nn.Embedding`](https://docs.pytorch.org/docs/stable/generated/torch.nn.Embedding.html)
- [PyTorch `CrossEntropyLoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)
- [PyTorch `inference_mode`](https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html)
- [PyTorch 可复现性说明](https://docs.pytorch.org/docs/stable/notes/randomness.html)
- 验证方式：`test_embedding_lab.py`、`embedding_lab.py` 报告与 v0.1 manifest；教学合成语料结果不外推。

## 下一步

第 4 课在同一语料和划分上加入序列模型，比较均值池化、RNN 与 CNN 在语序、误差和成本上的差异。
