# 算法演练运行器 v0.2

v0.2 在 v0.1 固定判题状态之外增加可回放的限时策略日志。示例时间是学习者声明的逻辑分钟，不是机器性能测量。

```bash
../../../../.venv/bin/python -m unittest -v test_timed_rehearsal.py
../../../../.venv/bin/python timed_rehearsal.py
```

日志要求时间单调、任务不重叠、每次决策有证据说明，并拒绝超过总预算的事件。
