# 文本分类模型演进 v0.4：GRU 与 CNN

本版复用 v0.1 的原创语料、24/8/8 固定分区和验证指标，以及 v0.3 的训练集词表与 tokenizer。只在训练集拟合，验证集用于模型比较，测试集仍封存。

在仓库根目录运行（Python 3.12、PyTorch 2.13.0、CPU）：

```bash
python3.12 -m venv .venv-nlp
.venv-nlp/bin/python -m pip install -r site-src/examples/nlp-transformer/text-classification-evolution-v04/requirements.txt
cd site-src/examples/nlp-transformer/text-classification-evolution-v04
../../../../.venv-nlp/bin/python -m unittest -v test_sequence_lab.py
../../../../.venv-nlp/bin/python sequence_lab.py
```

GRU 通过 packed sequence 跳过 padding；CNN 在卷积后遮蔽 padding 位置，再做最大池化。固定报告记录验证混淆矩阵、错误 ID、参数量、训练与推理耗时。耗时随机器变化，不作为精确快照。小型合成语料的分数不能外推到真实业务；两种结构只说明序列归纳偏置和成本如何被测量，不证明普遍优劣。
