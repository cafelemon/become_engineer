# 文本分类模型演进 v0.5：可审查的注意力

沿用 v0.1 原创语料、24/8/8 固定切分、验证评估接口，以及 v0.3 的训练集词表与字符 tokenizer。默认 Python 3.12、PyTorch 2.13.0、CPU；无外部服务、预训练权重或真实个人数据。

从仓库根目录执行：

```bash
cd site-src/examples/nlp-transformer/text-classification-evolution-v05
python3.12 -m unittest -v test_attention_lab.py
python3.12 attention_lab.py
```

`scaled_dot_product_attention()` 返回上下文和可检查的权重矩阵。布尔 `key_valid=True` 表示允许参与；无效 padding key 权重为零，无效 query 输出归零。`causal=True` 只用于单独的未来遮蔽实验；文本分类默认双向注意力。`sinusoidal_position_encoding(length, dim)` 为固定位置编码，`dim` 必须是偶数。`run_validation()` 只拟合训练集、只评估验证集；测试集仍封存。报告记录同一语料指纹、切分 ID、参数量、训练配置、混淆矩阵和错误样本 ID。

小语料分数不说明注意力普遍优于 v0.3 或 v0.4；表示方式、参数量与训练程序的差异均可能影响结果。下一版将用完整 Encoder 层与同一验证协议比较。
