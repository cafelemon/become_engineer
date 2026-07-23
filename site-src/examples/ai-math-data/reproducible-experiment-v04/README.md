# 可复现实验与评估系统 v0.4

这一版用局部伪随机生成器完成确定性分层划分。

```bash
../../../../.venv/bin/python -m unittest -v test_split_lab.py
../../../../.venv/bin/python split_lab.py
```

输入先按稳定样本 ID 排序，再用显式种子抽取每个标签的验证样本；训练集和验证集必须无交叉且无丢失。种子用于复现实验，不代表一次划分足以证明模型稳定。
