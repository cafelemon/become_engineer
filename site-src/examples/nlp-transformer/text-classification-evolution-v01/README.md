# 文本分类模型演进 v0.1

Python 3.12 标准库即可运行；不下载模型、不联网，也不使用真实个人对话。`corpus.csv` 是 40 条原创教学短句，`code` / `plan` 各 20 条。

从仓库根目录运行：

```bash
python3 -m unittest -v site-src/examples/nlp-transformer/text-classification-evolution-v01/test_experiment.py
python3 site-src/examples/nlp-transformer/text-classification-evolution-v01/experiment.py
python3 site-src/examples/nlp-transformer/text-classification-evolution-v01/experiment.py --output /tmp/be-nlp-v01-artifacts
```

最后一条命令写入 `train.csv`、`validation.csv`、`test.csv` 与 `manifest.json`；目标目录须为空，避免意外覆盖。不要在模型选择前读取 `test.csv` 的标签。下一版只在训练集拟合 TF-IDF 与线性分类器，用验证集比较。
