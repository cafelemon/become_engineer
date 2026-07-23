# 结构化数据机器学习系统 v0.8

本版本训练完整校准流水线，生成 pickle 模型与 JSON 清单，校验 SHA-256、依赖版本、字段 Schema 和阈值后再推理。

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_delivery_lab.py
.venv/bin/python delivery_lab.py
```

pickle 能执行任意代码，只能加载本机生成、经过审查且校验通过的可信产物。本实验不提供公网服务、模型注册中心或生产部署。
