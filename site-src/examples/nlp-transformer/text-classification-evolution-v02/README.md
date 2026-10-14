# 文本分类模型演进 v0.2

沿用相邻 v0.1 的 `corpus.csv`、稳定划分和 `evaluate_validation`，不复制语料、不重新切分。Python 3.11+ 标准库即可运行（本地以 3.11.9 验证），无网络、密钥或下载。数据是 40 条原创教学短句，不代表真实用户分布。

从仓库根目录运行：

```bash
python3 -m unittest discover -s site-src/examples/nlp-transformer/text-classification-evolution-v02 -p 'test_*.py' -v
python3 site-src/examples/nlp-transformer/text-classification-evolution-v02/experiment.py
python3 site-src/examples/nlp-transformer/text-classification-evolution-v02/experiment.py --output /tmp/be-nlp-v02-artifacts
```

第三条只向空目录写 `result.json`，再次运行需选择另一个目录。结果包含训练语料指纹、配置、验证集基线、模型指标与错误样本，不包含测试集预测。不要在选定最终模型前使用测试集标签。

实现步骤：移除空白并转小写 → 字符二元组 → 只在 train 学词表和 IDF → 原始词频 × 平滑 IDF → L2 归一化 → 全批量二元逻辑回归 → validation 比较。教学实现不是 scikit-learn 的完整替代品；40 句的小样本结果也不能外推到真实业务。
