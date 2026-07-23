# 可追踪约束模式实验 v1.0

最终版本比较两种字符串信息复用：

- Trie 让多个词共享前缀路径，终止标记区分完整词和普通前缀；
- KMP 的 prefix function 保存最长真前后缀，失配时回退而不重扫文本；
- 补全、重复插入、重叠匹配和空输入均有固定契约。

运行：`../../../../.venv/bin/python -m unittest -v test_string_matching_trace.py`
