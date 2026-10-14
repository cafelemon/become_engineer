<div class="be-tutor-mount" data-tutor-lesson="nlp-transformer-06" aria-hidden="true"></div>
<section id="overview-encoder-ablation" class="be-page-hero be-lesson-hero" data-learning-context="overview-encoder-ablation" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">NLP 与 Transformer · 第 6 / 7 课 · 文本分类模型演进 v0.6</span>
# Transformer Encoder 文本分类与消融
## 都叫“去掉 mask”，为什么有的补齐会改变分类结果？

```text
同一 24 条训练句、8 条验证句、同一训练集词表
完整 Encoder：8/8；去位置：6/8；去 attention 键 padding mask：7/8
测试集仍未用于训练、评估或选模
```

这是 Python 3.12、PyTorch 2.13.0、CPU 上一次固定设置的教学结果，不是模型优劣的通用结论。本课把 v0.5 可检查的单头注意力推进到 PyTorch 单层双头 Encoder，再分别关闭位置输入与 attention 的 padding 屏蔽，观察代码、错误和成本一起发生了什么。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>NLP 与 Transformer · 6 / 7</strong></div>
  <div><span>前置</span><strong>v0.1 划分、v0.3 Embedding、v0.5 注意力与位置</strong></div>
  <div><span>环境</span><strong>Python 3.12 · PyTorch 2.13.0 · CPU · 离线</strong></div>
  <div><span>完成后留下</span><strong>v0.6 三组报告与 9 项测试</strong></div>
</div>

## 学习目标

- 说清 Embedding、正弦位置、多头自注意力、前馈层与均值分类头怎样连接。
- 区分 v0.5 `key_valid=True` 表示可看，与 PyTorch `src_key_padding_mask=True` 表示忽略。
- 用相同划分、词表和训练配置做两项结构消融，保留混淆矩阵与错误 ID。
- 解释为什么 8 条验证句和一次训练不能支持“Transformer 一定更好”的结论。

<section id="concept-encoder-flow" data-learning-context="concept-encoder-flow" data-context-type="concept" markdown="1">
## 从 token ID 到两类 logits

v0.6 的输入是 `[B,L]` 整数 ID。训练集词表沿用 v0.3，`nn.Embedding(V,16)` 变成 `[B,L,16]`；v0.5 的固定正弦位置也有 16 维，可直接相加。一个 `TransformerEncoderLayer(d_model=16,nhead=2,dim_feedforward=32,dropout=0,batch_first=True)` 在每个位置组合双头自注意力、残差/归一化与前馈计算；最终只对真实 token 求均值，线性层输出 `[B,2]` logits。

它只是单层教学 Encoder 分类器，不是原论文的完整编码器—解码器，也没有预训练或生成能力。v0.5 的手写单头注意力用于观察权重；v0.6 使用 PyTorch 参考层，重点转到接口、消融和比较。
</section>

<section id="concept-mask-polarity" data-learning-context="concept-mask-polarity" data-context-type="concept" markdown="1">
## 同一个布尔值，两个 API 的意思相反

v0.5 的 `scaled_dot_product_attention(..., key_valid)` 用 `True` 表示这个 key 有效。v0.6 调用 `TransformerEncoder(..., src_key_padding_mask=~valid)`；PyTorch 此处用 `True` 表示忽略这个 padding key。少了 `~` 就可能把有效词全部遮住。

三组实验的最终均值池化始终只统计真实 token。“去 key padding mask”只让 Encoder 的注意力可能看见补齐位，并没有去掉池化 mask。这样才知道改变发生在 attention 入口，而不是同时换了输出汇总规则。
</section>

<section id="example-ablation-observation" data-learning-context="example-ablation-observation" data-context-type="example" markdown="1">
## 补齐和换序先手算，再看模型

先预测同一个模型看到 `[2,3]` 与 `[2,3,0,0]` 时 logits 是否应相同。完整模型屏蔽 0 号 key，测试得到相同结果；去掉 key padding mask 后，同样输入的 logits 在这次固定初始化下发生变化。再把 `[2,3,4]` 换成 `[4,3,2]`：关闭位置编码的 Encoder 加上均值池化，在测试中给出相同 logits，因为输入只有一个置换；这不意味着训练后的两模型验证分数必然相同。

固定设置的一次验证结果：完整模型准确率与 macro-F1 均 1.000，去位置均 0.750（错误 `C06`、`P09`），去 key padding mask 分别为 0.875 与约 0.873（错误 `C01`）。这些只是 8 条原创教学句的观察，不能用“完整模型赢了”代替多种子和更大数据验证。
</section>

<section id="reproduce-transformer-v06" data-learning-context="reproduce-transformer-v06" data-context-type="reproduce" markdown="1">
## 离线运行三组同协议实验

从仓库根目录执行；若前课已经创建 `.venv-nlp`，可复用环境而不重复安装：

```bash
python3.12 -m venv .venv-nlp
.venv-nlp/bin/python -m pip install -r site-src/examples/nlp-transformer/text-classification-evolution-v06/requirements.txt
cd site-src/examples/nlp-transformer/text-classification-evolution-v06
../../../../.venv-nlp/bin/python -m unittest -v test_transformer_lab.py
../../../../.venv-nlp/bin/python transformer_lab.py
```

`transformer_lab.py` 依赖相邻 v0.1、v0.3、v0.5 的真实源文件，不复制语料、词表或位置算法。报告应列出同一 `corpus_sha256`、train/validation ID、三组配置、混淆矩阵、错误 ID、参数量、训练耗时与预热后同批次 20 次推理时间中位数；`test_status` 必须是 `sealed`，不得出现测试指标。9 项测试检查 mask 极性、位置接口、补齐不变/变动、无位置换序、梯度、坏输入、固定种子及报告契约。
</section>

<section id="modify-ablation-run" data-learning-context="modify-ablation-run" data-context-type="modify" markdown="1">
## 只改一个因素，再写下证据

先选一个改动：把两头改成四头（16 维仍可整除），或把最大长度 48 缩为 12。改前预测输入 shape、参数量和可能的截断/错误 ID 变化，改后重跑 9 项测试与三组报告。若改头数，参数量可能不变，但每头宽度会变；若改最大长度，请检查哪些句子实际被截断，不能只报准确率。保存完整配置、三组结果和至少一个错误样本，不挑最好的一次替代全部尝试。
</section>

<section id="troubleshoot-encoder" data-learning-context="troubleshoot-encoder" data-context-type="troubleshoot" markdown="1">
## 三类常见故障先查哪儿

| 现象 | 检查 | 恢复 |
| --- | --- | --- |
| `embed_dim must be divisible by num_heads` | `width` 与 `heads` | 选可整除组合，重算每头宽度 |
| 补齐后完整模型 logits 变化 | `valid=ids.ne(0)`、`src_key_padding_mask=~valid`、最终池化 mask | 保持 PyTorch 的 `True=忽略` 极性，跑补齐测试 |
| 结果每次不同 | seed、dropout、CPU 线程、版本和输入顺序 | 恢复固定设置；跨设备不承诺逐位一致 |
| 指标变好但错误样本没看 | v0.1 划分与每组 `validation_errors` | 对照相同 ID 和混淆矩阵，保留失败实例 |
| 首组训练耗时异常高 | 首次 PyTorch 初始化与系统负载 | 看预热后同批次推理中位数；不把一次墙钟时间当性能结论 |
</section>

<section id="project-text-classification-v06" data-learning-context="project-text-classification-v06" data-context-type="project" markdown="1">
## 文本分类模型演进 v0.6

- 上一版：v0.1 固定数据与划分，v0.3 提供训练词表，v0.5 已能检查单头注意力、padding 和位置。
- 本课：把注意力接成单层双头 Encoder 分类器，在相同训练/验证协议下做位置与 key padding mask 两项消融。
- 文件：`text-classification-evolution-v06/transformer_lab.py`、`test_transformer_lab.py`、`README.md`、`requirements.txt`。
- 保存：完整三组 JSON、混淆矩阵和错误 ID、参数量与本机成本、一次修改前后的预测与排错记录。
- 下一版：讨论预训练表示与可选微调，再用统一模型卡解释本组从传统模型到 Transformer 的得失。

完整模型验证 8/8 不等于项目完成了真实世界意图识别。三组分别训练，结果同时受优化轨迹和小样本影响；只能把本次现象当成继续检验的线索。
</section>

## 四类学习者入口

- 零基础兴趣：画出 `[B,L] → [B,L,16] → [B,16] → [B,2]`，用两条补齐序列解释 `True` 为什么在两个 API 中方向相反。
- 有基础兴趣：运行无位置换序测试，再改头数并记录参数量与验证错误，不把一个分数当机制证明。
- 零基础求职：把 v0.1 数据契约、v0.3 词表、v0.5 手工注意力和 v0.6 三组报告整理成可复查的项目演进记录。
- 有基础求职：展示同划分、多配置和错误 ID，明确单次 8 条验证的局限，提出多种子/更大数据复验。当前没有映射到本课的 V2 求职能力信号，不编造企业高频题。

## 完成检查

- 9 项 unittest 与三组离线报告通过；报告中没有测试集指标。
- 能解释 Encoder 的主要部件，以及 `key_valid` 与 `src_key_padding_mask` 的布尔极性。
- 能预测并复核补齐不变、去 mask 变化和去位置换序不变三项微型实验。
- 保留三组固定配置、混淆矩阵、错误 ID、参数量及成本；说明训练时间为什么不能跨机器直接比较。
- 完成一次单因素修改、预测、运行和错误恢复，不宣称 8 条验证句代表真实业务。

## 来源与版本

- 核查日期：2026-10-14；本机验证环境：Python 3.12、PyTorch 2.13.0、CPU；v0.1 原创语料与 v0.3/v0.5 项目接口。
- [PyTorch TransformerEncoderLayer 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html)
- [PyTorch TransformerEncoder 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoder.html)
- [PyTorch Transformer mask 语义](https://docs.pytorch.org/docs/stable/generated/torch.nn.Transformer.html)
- [Attention Is All You Need 原论文](https://arxiv.org/abs/1706.03762)
- 代码与数值由 `test_transformer_lab.py` 和 `transformer_lab.py` 实测；教学数据、单次种子和本机时间不外推。

## 下一步

第 7 课在保留本组评测协议的前提下看预训练表示与可选微调，再完成统一误差、资源和模型卡。
