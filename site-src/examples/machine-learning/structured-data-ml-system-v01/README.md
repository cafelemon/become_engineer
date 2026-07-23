# 结构化数据机器学习系统 v0.1

第一版使用固定种子生成 120 行教学合成数据，明确样本 ID、4 个数值特征和二分类目标，再执行分层训练/验证划分和多数类基线。

```bash
python -m pip install -r requirements.txt
python -m unittest -v test_baseline_lab.py
python baseline_lab.py
```

合成数据只用于离线学习和自动验收，不代表真实业务分布。目标列与样本 ID 不进入特征；验证集只用于评估，不能参与拟合。多数类基线刻意忽略特征，用来判断后续模型是否真正带来增益。
