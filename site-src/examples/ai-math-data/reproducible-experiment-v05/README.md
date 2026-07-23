# 可复现实验与评估系统 v0.5

这一版在固定验证样本上比较负类基线与两个阈值。

```bash
../../../../.venv/bin/python -m unittest -v test_evaluation_lab.py
../../../../.venv/bin/python evaluation_lab.py
```

预测规则固定为 `score >= threshold`。准确率、精确率、召回率和 F1 都从同一组 TP/FP/TN/FN 派生；零分母结果显式定义为 0。阈值必须结合错误成本和独立验证选择，不能在同一验证集上反复挑最好结果后把它当作无偏结论。
