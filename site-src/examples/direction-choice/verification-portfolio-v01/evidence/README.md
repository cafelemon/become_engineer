# 学习时段汇总

`study_summary.py` 汇总非负学习时段，固定输出时段数与总小时。

```bash
cd evidence
python -m unittest -v test_study_summary.py
python study_summary.py
```

输入为空时返回零汇总，负数输入会被拒绝。运行只使用 Python 3.11 标准库。
