# 结构化数据机器学习系统 v0.4

本版本在同一训练/验证边界上加入决策树，对比不受约束的树和 `max_depth=3, min_samples_leaf=5` 的受约束树。

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_decision_tree_lab.py
.venv/bin/python decision_tree_lab.py
```

固定种子只用于复现当前教学实验，验证结果不等于真实业务泛化证据。
