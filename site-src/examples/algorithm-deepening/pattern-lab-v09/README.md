# 可追踪约束模式实验 v0.9

本版本用同一组确定性节点演示：

- Kahn 拓扑排序只从零入度前沿取点，处理不完即报告环；
- Kosaraju 把互相可达节点压成 SCC，缩点边形成 DAG；
- 多源 BFS 同时把所有源点以距离 0 入队，首次发现即为最短边数。

运行：`../../../../.venv/bin/python -m unittest -v test_advanced_graph_trace.py`
