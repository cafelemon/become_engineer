# 可追踪约束模式实验 v0.2

第二版用可伸缩窗口寻找包含需求频次的最短子串。右端只向前加入字符，满足全部
种类后左端只向前收缩；每个位置最多被两个边界各处理一次。

```bash
../../../../.venv/bin/python -m unittest -v test_sliding_window_trace.py
```

需求以频次而非集合表示，因此 `need=AAC` 必须真的包含两个 `A`。Python 与
C++20 固定报告逐字一致。
