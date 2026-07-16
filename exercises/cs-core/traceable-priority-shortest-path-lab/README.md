# 可追踪优先队列与最短路实验

本阶段作品用 Python 3.11 与 C++20 实现同一最小堆、稳定优先队列和非负权 Dijkstra 契约。只使用标准库，不修改前六个 CS 实验。

## 运行模式

- `heap`：逐次插入、删除堆顶与精确比较/交换计数；无参数时默认运行。
- `queue`：用 `(priority, sequence)` 保证同优先级 FIFO。
- `dijkstra`：在确定性简单无向非负权图上追踪松弛、过期项和路径。

```bash
cd python
python -m unittest discover -s tests -v
python -m traceable_priority_shortest_path_lab heap
python -m traceable_priority_shortest_path_lab queue
python -m traceable_priority_shortest_path_lab dijkstra
```

```bash
cmake -S cpp -B /tmp/traceable-priority-build -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/traceable-priority-build
ctest --test-dir /tmp/traceable-priority-build --output-on-failure
```

未知模式只写标准错误并返回 `2`。Python 与 C++ 三种标准输出必须逐字一致；构建目录、wheel、虚拟环境和缓存不得提交。
