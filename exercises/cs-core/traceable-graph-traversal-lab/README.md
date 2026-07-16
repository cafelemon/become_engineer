# 可追踪图遍历实验

本阶段作品用 Python 3.11 与 C++20 实现同一份简单无向图契约，把图表示、无权 BFS、全图 DFS、连通分量和环检测变成可重复验证的输出。

## 运行

Python：

```bash
cd python
python -m pip install -e .
python -m traceable_graph_traversal_lab graph
python -m traceable_graph_traversal_lab bfs
python -m traceable_graph_traversal_lab dfs
```

C++：

```bash
cmake -S cpp -B build
cmake --build build
ctest --test-dir build --output-on-failure
./build/traceable_graph_traversal_lab graph
```

无参数等价于 `graph`；未知模式只写入 `stderr` 并返回 `2`。两种语言的三种标准输出必须逐字一致。

## 公开契约

- 图：`UndirectedGraph`、`Edge`、`describe_graph`、`build_adjacency_matrix`、`degree_sequence`、`has_edge`
- BFS：`breadth_first`、`shortest_path`、`reachable_within`
- DFS：`depth_first_components`、`build_component_labels`
- 输入为顶点 `0..n-1` 的简单无向图；拒绝非法端点、自环和重复边，邻接点升序保存。
- BFS 在入队时标记；无权最短距离按边数计算。DFS 从最小未访问顶点启动，并在无向环判断中排除父边。

## 验证

```bash
cd python
python -m mypy --strict src tests
python -m unittest discover -s tests -v
```

所有计数来自教学实现，不读取标准容器内部状态，也不设置机器相关耗时阈值。
