# 结构化数据机器学习系统 v0.3

本版本复用 v0.2 的训练期预处理流水线，加入带 L2 正则化的逻辑回归，固定概率、0.5 阈值、对数损失和系数范数报告。

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_logistic_regression_lab.py
.venv/bin/python logistic_regression_lab.py
```

输出只解释当前版本化合成数据上的离线行为，不构成真实业务效果或因果结论。
