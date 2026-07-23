# 结构化数据机器学习系统 v0.6

本版本从拟合输入中排除 `target`，对四个数值特征执行中位数填补、标准化、PCA 二维投影和 KMeans 聚类。

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_unsupervised_lab.py
.venv/bin/python unsupervised_lab.py
```

簇是当前特征空间和算法下的描述性分组，不是自动发现的真实类别、用户身份或因果机制。
