# 文本分类模型演进 v0.6：Transformer Encoder 与消融

这一版继承 v0.1 的 40 条原创句及固定 train/validation/test 划分、v0.3 的训练集词表与 tokenizer、v0.5 的正弦位置编码。模型是 PyTorch `TransformerEncoderLayer` 的单层、双头、小宽度教学编码器，不是预训练模型，也不是原论文完整翻译系统。

默认 Python 3.12、PyTorch 2.13.0、CPU；不联网、不下载权重。代码读取完整 v0.1 CSV 来核对指纹和划分，但只用 24 条训练句拟合，用 8 条验证句比较。8 条测试句的标签在 CSV 中可见，`sealed` 是实验流程纪律，不是访问控制；本入口不对测试集预测、评估或选模。

从仓库根目录运行：

```bash
python3.12 -m venv .venv-nlp
.venv-nlp/bin/python -m pip install -r site-src/examples/nlp-transformer/text-classification-evolution-v06/requirements.txt
cd site-src/examples/nlp-transformer/text-classification-evolution-v06
../../../../.venv-nlp/bin/python -m unittest -v test_transformer_lab.py
../../../../.venv-nlp/bin/python transformer_lab.py
```

`transformer_lab.py` 在相同词表、划分、种子、训练轮数、优化器、宽度和头数下跑三种变体：完整模型、去位置编码、去 attention 的 key padding mask。三者均保留去 padding 的最终均值池化，避免同时改变池化策略。报告列出语料指纹、训练/验证 ID、三组混淆矩阵、错误 ID、参数量、训练时间和预热后同批次 20 次推理时间中位数。CPU 毫秒数受系统状态影响，只作本机观察，不作跨机器性能承诺。

9 项测试包含位置编码与 v0.5 一致、padding 对完整模型不改变 logits、去 mask 后能观察补齐影响、去位置后词元置换不改变 logits、梯度与输入拒绝、固定种子，以及三组报告不含测试指标。若 `ModuleNotFoundError: torch`，确认使用安装依赖的虚拟环境；若 v0.1/v0.3/v0.5 文件找不到，保留相邻项目目录。若消融指标改变，先检查三组共享的划分、词表和设置；8 条验证句不能证明哪种结构普遍更好。去位置与去 mask 是结构对照，不是因果意义上的单变量结论：不同训练轨迹和小样本误差仍会影响分数。
