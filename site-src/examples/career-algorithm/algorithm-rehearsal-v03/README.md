# 算法演练运行器 v0.3

v0.3 把判题状态和策略事件整理为五类错因记录。每条记录必须包含反例候选、更小探针、原因、修复、唯一回归测试和时间线链接。

```bash
../../../../.venv/bin/python -m unittest -v test_regression_cases.py test_retrospective.py
../../../../.venv/bin/python retrospective.py
```

工具不会声称自动证明反例在数学意义上全局最小；学习者必须写出尝试过的更小探针和搜索边界。
