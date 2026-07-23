# 可复现实验与评估系统 v0.3

这一版在数值变换前增加表格 Schema 与质量门禁。

```bash
../../../../.venv/bin/python -m unittest -v test_data_quality_lab.py
../../../../.venv/bin/python data_quality_lab.py
```

缺失特征只计数而不擅自填充；完全相同的重复行折叠并计数；同一 `sample_id` 内容冲突时整组样本不进入已接受数据。错误标签、字段缺失、额外字段和错误类型都计入无效行。
