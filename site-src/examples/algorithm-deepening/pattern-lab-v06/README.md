# 可追踪约束模式实验 v0.6

第六版按结束时间选择最多互不重叠半开区间，并用小规模穷举验证选择数量最优。
同一数据同时运行错误的“最早开始”启发式，固定产生 4 对 3 的反例。

```bash
../../../../.venv/bin/python -m unittest -v test_greedy_interval_trace.py
```

Python 与 C++20 使用 `(end,start,label)` 平局顺序并输出一致报告。
