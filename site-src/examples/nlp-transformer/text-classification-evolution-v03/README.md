# 文本分类模型演进 v0.3：Embedding 与掩码均值池化

沿用 v0.1 的 40 条原创学习问题、固定 train/validation/test 划分和验证指标。v0.3 只在 24 条训练句上建词表、训练模型；验证集 8 条只用于比较，测试集 8 条保持封存。

默认环境为 Python 3.12、PyTorch 2.13.0、CPU。代码不下载语料、词表或预训练权重，也不访问外部 API。

从仓库根目录运行：

```bash
python3.12 -m venv .venv-nlp
.venv-nlp/bin/python -m pip install -r site-src/examples/nlp-transformer/text-classification-evolution-v03/requirements.txt
cd site-src/examples/nlp-transformer/text-classification-evolution-v03
../../../../.venv-nlp/bin/python -m unittest -v test_embedding_lab.py
../../../../.venv-nlp/bin/python embedding_lab.py
```

报告 JSON 包括与 v0.2 一致的语料指纹、划分种子与 train/validation ID，以及词表大小、配置、验证指标、错误 ID、参数量、训练耗时和 `test_status=sealed`。这里的 tokenizer 把 ASCII 字母数字组成的词保留成一个 token、汉字拆为单字；它不是中文分词器，也不宣称适合真实业务文本。`<unk>` 承接训练词表外输入；`<pad>` 只补齐 batch，均值池化时不计入分母。

常见失败：若 `ModuleNotFoundError: torch`，先确认运行的是安装依赖的虚拟环境；若 v0.1 路径缺失，必须保留项目相邻目录结构；若新文本都变成 `<unk>`，检查 tokenizer 与训练词表覆盖率，不能把验证集词汇偷加到词表。v0.2 使用字符 bigram TF-IDF，v0.3 使用单汉字/ASCII 词元 Embedding，表示方法与模型都变了，因此差异不能单独归因于神经网络。小样本准确率波动不能解释为某类模型普遍更好；比较需沿用 v0.2 的同一验证协议，最终选模后才能打开测试集。
