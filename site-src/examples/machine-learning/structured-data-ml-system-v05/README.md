# 结构化数据机器学习系统 v0.5

本版本冻结 30 行最终测试集，只在 90 行开发集内部用 5 折分层交叉验证比较逻辑回归与受约束决策树的 6 个候选。

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_model_selection_lab.py
.venv/bin/python model_selection_lab.py
```

最终测试结果只描述当前教学合成数据；重复查看并据此改模型会破坏它的最终评估角色。
