# 结构化数据机器学习系统 v0.2

本版本在 v0.1 的任务、切分和多数类基线上加入数值缺失值、类别特征和训练期预处理流水线。

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_preprocessing_lab.py
.venv/bin/python preprocessing_lab.py
```

数据是固定种子生成的教学合成数据，不包含个人信息，也不能外推真实业务分布。
