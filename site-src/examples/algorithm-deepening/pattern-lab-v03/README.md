# 可追踪约束模式实验 v0.3

第三版统一使用半开区间 `[left,right)`：

- 前缀和用 `prefix[right] - prefix[left]` 回答多次区间和。
- 差分在 left 加增量、right 减增量，最后一次扫描还原全部位置。

```bash
../../../../.venv/bin/python -m unittest -v test_range_transform_trace.py
```

Python 与 C++20 固定报告逐字一致；空区间自然为零且空更新无效果。
