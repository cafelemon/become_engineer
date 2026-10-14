<div class="be-tutor-mount" data-tutor-lesson="nlp-transformer-05" aria-hidden="true"></div>
<section id="overview-attention-result" class="be-page-hero be-lesson-hero" data-learning-context="overview-attention-result" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">NLP 与 Transformer · 第 5 / 7 课 · 文本分类模型演进 v0.5</span>
# 缩放点积注意力、Mask 与位置
## 同一句里的两个位置，能否选择看向不同的词？
```text
hand_check: full_first_weights=[0.5,0.5] → output=[1.0,2.0]
hand_check: causal_first_weights=[1.0,0.0] → output=[2.0,0.0]
validation: accuracy=0.875, macro_f1=0.873, errors=[P09]
test_status=sealed
```
上面前两行由两词 PyTorch 张量直接算出：只改“第一个位置能否看见第二个位置”，结果就变了。后两行是本课单头自注意力分类器在原有 8 条验证句上的一次固定实验，不证明注意力普遍优于 GRU、CNN 或均值池化。
</section>

<div class="be-lesson-overview">
  <div><span>适合谁</span><strong>完成前四课，想看懂注意力内部计算的学习者</strong></div>
  <div><span>前置</span><strong>v0.1 固定数据；v0.3 Embedding；v0.4 GRU/CNN 序列基线</strong></div>
  <div><span>环境</span><strong>Python 3.12、PyTorch 2.13.0、CPU</strong></div>
  <div><span>留下</span><strong>手算记录、mask 与位置测试、同口径验证报告</strong></div>
</div>

## 学习目标

- 从 `QKᵀ/√d`、softmax 到加权 `V`，手算两词例子并与 PyTorch 对照。
- 分清 padding mask 和 causal mask 的职责，说明文本分类默认为什么不遮未来。
- 解释没有位置编码时自注意力不能单凭词元内容辨认原始次序。
- 沿用 v0.1 的语料指纹、train/validation ID 和指标；不打开测试集选模型。

<section id="concept-scaled-attention" data-learning-context="concept-scaled-attention" data-context-type="concept" markdown="1">
## 每个位置给其他位置打分，再加权取值

对每个查询位置，先算 `score = QKᵀ / √d`，按可见位置做 softmax 得到权重，再用这些权重求 `V` 的加权和。除以 `√d` 是为避免维度增大时点积幅度随之放大；它不是一个可随意省掉的装饰常数。本课 `attention_lab.py` 显式保留分数、mask、softmax 和权重，便于逐项测试。分类器用学习到的 Q/K/V 线性投影；两词手算例用固定张量，与训练权重无关。

v0.4 的 GRU 逐位置更新隐藏状态，CNN 用固定宽度局部窗口；这里每个位置可直接对所有允许的键位置分配权重。三者是不同计算路径，不能仅凭一次小语料验证分数判断哪种结构普遍更好。
</section>

<section id="concept-mask-position" data-learning-context="concept-mask-position" data-context-type="concept" markdown="1">
## Mask 决定“能看谁”，位置编码补上“在哪里”

`key_valid=True` 表示真实词元，可作为键；padding 键权重必须为 0，padding 查询位置的输出也置 0，池化只统计真实词元。`causal=True` 额外遮住未来键，适合不能读取未来词的自回归场景。本课做整句分类，输入句子本来完整，因此训练和验证默认用双向、仅 padding mask；因果 mask 只作对照实验。PyTorch 的 `scaled_dot_product_attention` 布尔掩码 `True` 也表示允许参与，和 `MultiheadAttention` 的 `key_padding_mask=True` 表示遮蔽正好相反；移植时要检查方向。

单靠词元内容的自注意力不会自动获得原始次序。本课给每个位置加固定正弦／余弦位置向量，再映射成 Q/K/V；同一个词元放到不同位置，输入向量便不同。这个编码本身不保证模型理解语法，只提供可利用的位置信息。
</section>

<section id="example-two-token" data-learning-context="example-two-token" data-context-type="example" markdown="1">
## 两词手算：遮住未来后第一个位置会怎样？

设第一个查询 `q₁=(1,0)`，两个键都是 `(1,0)`，`d=2`；两个值分别是 `v₁=(2,0)`、`v₂=(0,4)`。两个缩放分数都为 `1/√2≈0.707107`，softmax 给 `(0.5,0.5)`，因此第一个位置输出 `0.5v₁+0.5v₂=(1,2)`。

现在打开 causal mask：第一个位置不能看第二个键，权重变成 `(1,0)`，输出 `(2,0)`。第二个位置仍可看前两个键。代码里的 `hand_check()` 输出与上表一致，测试还将手写实现与 PyTorch 官方 SDPA 的无掩码结果对照。

| 第一个查询位置 | 键 1 权重 | 键 2 权重 | 输出 |
| --- | ---: | ---: | --- |
| 双向可见 | 0.5 | 0.5 | (1, 2) |
| 因果遮蔽 | 1.0 | 0.0 | (2, 0) |
</section>

<section id="reproduce-attention-v05" data-learning-context="reproduce-attention-v05" data-context-type="reproduce" markdown="1">
## 运行手算核对与同语料分类实验

从仓库根目录进入本版；需要相邻的 v0.1 与 v0.3 源码。Python 3.12 与 CPU 版 PyTorch 2.13.0 依赖见 `requirements.txt`，无需联网下载数据或预训练模型。依赖未安装时，先在独立虚拟环境安装，再运行：

```bash
cd site-src/examples/nlp-transformer/text-classification-evolution-v05
python3.12 -m unittest -v test_attention_lab.py
python3.12 attention_lab.py
```

测试应显示 `Ran 10 tests` 与 `OK`。JSON 报告应保留 v0.1 语料 SHA-256 `8973927ed683f32cf92bb4a1483b960f3b8c09b0b8497bd0c5176891252b713c`、训练 24 条、验证 8 条与 `test_status=sealed`。本次固定种子 CPU 运行得到准确率 `0.875`、macro-F1 约 `0.873`，唯一错误 ID `P09`；训练耗时随机器而变，不应断言固定秒数。运行器不读取测试标签做选择。
</section>

<section id="modify-attention-v05" data-learning-context="modify-attention-v05" data-context-type="modify" markdown="1">
## 改一个开关，先预测再运行

1. 在两词实验中预测 `causal=True` 后第一个位置的两个权重，再用 `hand_check()` 核对。
2. 在一个练习副本里把第三个词元改成 padding，预测它作为键的权重、作为查询的输出；运行 `test_padding_key_and_query_do_not_contribute`。
3. 对同一小 batch 比较 `use_position=True/False` 的输出；先写下为什么改变位置编码可能改变分数，但不从一组分数外推业务收益。
4. 若要比较分类实验，保持语料、划分与指标不变，只改一个训练超参数并记录新报告。测试集仍不参与调整。
</section>

<section id="troubleshoot-attention-v05" data-learning-context="troubleshoot-attention-v05" data-context-type="troubleshoot" markdown="1">
## 数值异常先检查 mask 与形状

| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| padding 词获得权重 | `True/False` 方向反了 | 确认本函数 `True=有效`，并运行 padding 单测 |
| 出现 NaN | 某一查询没有可见键 | 确保序列首词有效；本实现主动拒绝首键无效 |
| 第一个因果位置读到后词 | 下三角遮蔽方向错误 | 对照两词手算和 `test_causal_mask_excludes_future_keys` |
| 交换词序却输出完全不变 | 没有注入位置信息或只看均值 | 检查 `use_position` 与编码矩阵的两个位置 |
| `ModuleNotFoundError: torch` | 解释器不是安装 PyTorch 的环境 | 检查 `python3.12 -c "import torch; print(torch.__version__)"` |
| 模型分数波动或低于旧版 | 超参数、种子、实现与 8 条验证句敏感 | 核对语料指纹、train/validation ID、混淆矩阵；不要动测试集救分 |
</section>

<section id="project-attention-v05" data-learning-context="project-attention-v05" data-context-type="project" markdown="1">
## 文本分类模型演进 v0.5

v0.1 固定原创文本与切分，v0.3 建立训练集词表和 Embedding，v0.4 用 GRU/CNN 检查有序序列建模；本课在 `text-classification-evolution-v05/attention_lab.py` 增加单头缩放点积注意力、两类 mask、固定位置编码和分类头。报告仍复用 v0.1 的 `evaluate_validation()`，保存手算表、10 项测试、语料/分区 ID、验证混淆矩阵、错误 ID 与配置。v0.4 的 GRU/CNN 本轮同口径各得 0.625，本课 0.875，v0.3 也是 0.875；8 条验证句和不同参数配置不足以把差异归因于架构。下一课将把这些基本件放进完整 Transformer Encoder 层，而不是把本课单头实验冒充完整 Transformer。
</section>

## 四类学习者入口

- 零基础兴趣：用两枚纸片代表两个键，手算遮蔽前后的第一个输出。
- 有基础兴趣：比较 `use_position` 开关和 padding 单测，解释权重矩阵的行列。
- 零基础求职：保留同一切分与混淆矩阵，练习说明“0.875 不等于上线可用”。
- 有基础求职：复查 v0.3／v0.4／v0.5 的配置、参数量与错误 ID，写出还不能归因于架构的因素；不引用外部题库频率。

## 完成检查

- [ ] 两词手算与 `hand_check()` 一致，能解释 `1/√2`、softmax 和加权值。
- [ ] 10 项 PyTorch 测试通过，padding、causal、位置、梯度与官方 SDPA 对照均覆盖。
- [ ] 改动一处开关并先写预测，记录实际结果与差异。
- [ ] 报告保留原语料指纹、固定 train/validation ID 和封存测试状态。
- [ ] 能说明单头注意力与 v0.4 序列基线、下一课完整 Encoder 的区别。

## 来源与版本

- 适用环境：Python 3.12、PyTorch 2.13.0、CPU；核查日期：2026-10-14。语料是原创教学短句，不能代表真实用户、长文本或生产表现；不使用付费 API。
- [Attention Is All You Need 原论文](https://arxiv.org/abs/1706.03762)：缩放点积注意力与位置编码的原始描述。
- [PyTorch scaled_dot_product_attention 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)：分数、布尔 mask 与 dropout 契约。
- [PyTorch MultiheadAttention 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html)：`key_padding_mask` 与 SDPA 的布尔方向差异。
- 代码、手算输出和固定验证报告由 `test_attention_lab.py` 与 `attention_lab.py` 在指定 CPU 环境核查；跨设备逐位相同未证明。

## 下一步

进入第 6 课《Transformer Encoder 与文本分类》：将位置、注意力、残差和前馈网络放入完整层，仍在同一验证协议下比较；最终测试集继续封存。
