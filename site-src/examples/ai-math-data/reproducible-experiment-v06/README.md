# 可复现实验与评估系统 v0.6

最终版将实验配置、稳定排序后的数据、代码修订、指标与产物摘要绑定到清单。

```bash
../../../../.venv/bin/python -m unittest -v test_reproducibility_lab.py
../../../../.venv/bin/python reproducibility_lab.py
```

SHA-256 用于发现内容是否变化，不证明数据来源可信，也不替代代码仓库、环境锁定或访问控制。清单刻意不包含当前时间、绝对路径等机器相关值；验证会明确指出配置、数据或产物哪一类发生变化。
