# 可追踪约束模式实验 v0.4

第四版用下标候选维护两种单调结构：

- 单调栈为每个位置寻找右侧第一个严格更大值。
- 单调队列维护固定窗口最大值，并区分过期淘汰与尾部支配淘汰。

```bash
../../../../.venv/bin/python -m unittest -v test_monotonic_structures_trace.py
```

每个下标至多进入和离开结构一次，Python 与 C++20 固定报告逐字一致。
