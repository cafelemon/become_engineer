<div class="be-tutor-mount" data-tutor-lesson="nlp-transformer-04" aria-hidden="true"></div>
<section id="overview-sequence-baselines" class="be-page-hero be-lesson-hero" data-learning-context="overview-sequence-baselines" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">NLP 与 Transformer · 第 4 / 7 课 · 文本分类模型演进 v0.4</span>
# GRU、CNN 序列基线与公平比较
## 更复杂的结构不保证在八条验证句上更好

```text
same_corpus=true  train=24  validation=8  test=sealed
v0.3 masked_mean: accuracy=0.875  errors=P09
v0.4 GRU:         accuracy=0.625  errors=C06,P09,P15
v0.4 CNN:         accuracy=0.625  errors=P01,P09,P15
```

这不是“GRU/CNN 比浅层模型差”的普遍结论。它只说明在同一份极小教学语料和固定配置上，结构变化必须连同错误与成本一起读。
</section>

<div class="be-lesson-overview">
  <div><span>前置</span><strong>第 3 课的 train-only 词表、Embedding 与 padding mask</strong></div>
  <div><span>环境</span><strong>Python 3.12 · PyTorch 2.13.0 · CPU · 离线</strong></div>
  <div><span>本课留下</span><strong>同一验证协议下的 GRU/CNN 对照和成本记录</strong></div>
</div>

## 学习目标

- 说清均值池化为什么没有顺序信息，GRU 与 CNN 分别怎样引入顺序或局部模式。
- 正确处理变长句和 padding，不让补齐位置改变句子预测。
- 用同一语料、划分、指标、错误 ID 和资源成本比较模型，不只挑最高分。
- 解释小样本实验不能证明模型族普遍优劣，测试集仍不参与选模。

<section id="concept-gru-order" data-learning-context="concept-gru-order" data-context-type="concept" markdown="1">
## GRU：状态沿 token 顺序更新

v0.3 对 token 向量求均值，交换顺序后和不变。GRU 依次把当前向量与先前状态组合，最后状态可携带顺序信息。本课使用 PyTorch `nn.GRU(batch_first=True)`：输入 `[B,L,8]`，最后状态 `[1,B,8]`，线性层输出 `[B,2]`。这不是语言理解的证明，只是模型结构能够表达顺序差异。

batch 中的句子长短不同。若直接把尾部 `<pad>` 送入 GRU，最后状态可能多走若干“空 token”步骤。本课先计算非零 token 数，再使用 `pack_padded_sequence(..., enforce_sorted=False)`，让状态停在真实句尾。`lengths.cpu()` 是该 PyTorch API 的输入要求；不能用原始 CSV 的字符数冒充 token 数。
</section>

<section id="concept-cnn-local" data-learning-context="concept-cnn-local" data-context-type="concept" markdown="1">
## CNN：局部窗口与最大响应

一维卷积的宽度 3 让相邻三个位置共同产生一个特征。输入 `[B,L,8]` 转成 `[B,8,L]` 后经过 `Conv1d(8,8,kernel_size=3,padding=1)`，再转回 `[B,L,8]`；对真实 token 位置取最大响应，最后映射到两类。卷积共享同一组局部规则，但最大池化会丢失“这个模式在第几处出现”的精确信息。

`padding=1` 只是让卷积输出长度与输入相同，不等于自动排除 `<pad>`。本课在池化前把补齐位置遮为极小值，防止它们成为最大响应；测试比较 `[2,3]` 与 `[2,3,0,0]` 的 logits，证明额外补齐不改变结果。
</section>

<section id="example-sequence-boundary" data-learning-context="example-sequence-boundary" data-context-type="example" markdown="1">
## 先手算一个边界，再看固定结果

假设句 A 编码为 `[2,3]`，句 B 为 `[4,5,6,7]`。同一个 batch 补齐后 A 变成 `[2,3,0,0]`，真实长度仍为 2。GRU 的 packed sequence 只走前两步；CNN 虽然计算四个位置，但只在前两处选最大值。请先画出两条路径的 shape，并预测如果删去 mask，短句结果为什么可能随 batch 中最长句变化。

真实脚本的固定验证输出：GRU 误判 `C06,P09,P15`，CNN 误判 `P01,P09,P15`；两者准确率都为 `0.625`，但错误集合不同。GRU 参数量 `1914`，CNN 为 `1682`；耗时字段每次运行会变，不能将一次 CPU 计时当性能基准。对照 v0.3 的 `0.875` 时还应记住：三个模型的词表与分割一致，但架构、参数量和优化轨迹不同。
</section>

<section id="reproduce-sequence-v04" data-learning-context="reproduce-sequence-v04" data-context-type="reproduce" markdown="1">
## 真实运行两类模型

在仓库根目录安装 Python 3.12 与本课依赖，然后运行：

```bash
python3.12 -m venv .venv-nlp
.venv-nlp/bin/python -m pip install -r site-src/examples/nlp-transformer/text-classification-evolution-v04/requirements.txt
cd site-src/examples/nlp-transformer/text-classification-evolution-v04
../../../../.venv-nlp/bin/python -m unittest -v test_sequence_lab.py
../../../../.venv-nlp/bin/python sequence_lab.py
```

九项测试覆盖 v0.1 划分复用、train-only 词表、shape/dtype、GRU/CNN 补齐不变、梯度、验证 ID 和测试集封存。报告含语料指纹、训练/验证 ID、混淆矩阵、错误 ID、参数量及训练/推理秒数。它不打印测试集指标；v0.1 的 `sealed` 是选模纪律，不是技术访问控制。
</section>

<section id="modify-sequence-window" data-learning-context="modify-sequence-window" data-context-type="modify" markdown="1">
## 改一个窗口宽度，保留失败结果

在练习副本里只把 CNN 的 `kernel_size=3,padding=1` 改成 `kernel_size=5,padding=2`。先预测 shape 与参数量如何变化，再运行 `test_sequence_lab.py` 和 `sequence_lab.py`，记录验证错误 ID、参数量与耗时。若误差变好或变差，都保留记录；不要同时改语料、训练轮数或学习率，也不要为挑配置打开测试集。恢复原值后，说明“窗口更宽”不等于“模型必然更准确”。
</section>

<section id="troubleshoot-sequence" data-learning-context="troubleshoot-sequence" data-context-type="troubleshoot" markdown="1">
## 结果不一致时逐层排查

| 现象 | 定位 | 恢复 |
| --- | --- | --- |
| `ModuleNotFoundError: torch` | Python 是否为安装依赖的虚拟环境 | 用 `.venv-nlp/bin/python` 运行 |
| 补齐后 logits 变化 | GRU 是否 packed，CNN 池化前是否遮蔽 padding | 先跑 `test_padding_does_not_change_logits` |
| 词表大小或验证 ID 变化 | 是否重新切分或用验证句建词表 | 复用 v0.1 分区和 v0.3 train-only tokenizer |
| 分数低于 v0.3 | 读错误 ID、参数量与训练配置 | 不删低分；保留对照并分析模型偏置 |
| 耗时不稳定 | CPU 负载、首次导入、线程数 | 只记录环境与多次测量，不写死秒数 |
</section>

<section id="project-sequence-v04" data-learning-context="project-sequence-v04" data-context-type="project" markdown="1">
## 文本分类模型演进 v0.4

P3.1 固定任务和考卷，P3.2 建立字符 TF-IDF 线性基线，P3.3 用 Embedding 与均值池化建立神经网络基线。本课只加入序列编码器：`sequence_lab.py` 复用 v0.1/v0.3 接口，输出可比较的验证指标和成本。下一课会在同一文本任务上拆开注意力计算与 mask；在看清权重、位置和引用边界前，不直接调用大型预训练模型。
</section>

## 四类学习者入口

- 零基础兴趣：手画 `[2,3]` 与 `[2,3,0,0]` 的真实长度与输出 shape，运行补齐不变测试。
- 有基础兴趣：比较 GRU 的 packed sequence 与 CNN 的遮蔽池化，解释各自忽略 padding 的位置。
- 零基础求职：保存固定验证混淆矩阵、错误 ID 和复现命令，用真实项目证据说明一次模型对照。
- 有基础求职：把 v0.3/v0.4 的语料指纹、参数量、错误集合与成本整理成可审查表，主动说明小样本和单次计时的限制；不编造招聘高频结论。

## 完成检查

- [ ] 九项测试与两模型报告通过；测试集仍显示 `sealed`。
- [ ] 能解释 GRU/CNN 的输入输出 shape、padding 处理与顺序信息差异。
- [ ] 改过一个窗口参数，记录预测、结果和回退。
- [ ] 报告不仅列准确率，还列混淆矩阵、错误 ID、参数量和计时边界。

## 来源与版本

- 核查日期：2026-10-14；运行目标：Python 3.12、PyTorch 2.13.0、CPU；固定语料来自本仓库 P3.1。
- [PyTorch GRU](https://docs.pytorch.org/docs/stable/generated/torch.nn.GRU.html)、[Packed sequence](https://docs.pytorch.org/docs/stable/generated/torch.nn.utils.rnn.pack_padded_sequence.html)、[Conv1d](https://docs.pytorch.org/docs/stable/generated/torch.nn.Conv1d.html) 官方文档。
- 合成语料只验证教学链路；真实文本需重新审查来源授权、隐私、类分布与错误成本。

## 下一步

第 5 课拆开缩放点积注意力、padding/causal mask 与位置，继续用同一语料和验证协议观察“看哪里”不等于“答对了”。
