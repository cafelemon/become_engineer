# 结构化数据机器学习系统 v0.7

本版本在开发集内用五折 sigmoid 校准逻辑回归概率，并在一次最终分析中比较原始/校准 Brier、对数损失、ECE 及预声明阈值下的分组错误。

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_calibration_error_lab.py
.venv/bin/python calibration_error_lab.py
```

分组结果来自很小的教学测试集，只用于演示审计方法，不用于描述真实群体或作公平性结论。
