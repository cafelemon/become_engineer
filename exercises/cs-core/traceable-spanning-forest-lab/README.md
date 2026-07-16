# 可追踪生成森林实验

本阶段作品服务 CS 核心第 24—26 课，用同一组确定性契约比较 Python 3.11 与 C++20 的并查集、Kruskal 和 Lazy Prim。它不修改已经验收的数组、线性结构、哈希、查找排序、树遍历、图遍历及最短路实验。

## 运行 Python

```bash
cd python
python -m pip install -e .
python -m traceable_spanning_forest_lab dsu
python -m traceable_spanning_forest_lab kruskal
python -m traceable_spanning_forest_lab prim
python -m unittest discover -s tests -v
python -m mypy --strict src tests
```

## 运行 C++

```bash
cmake -S cpp -B build/spanning-forest -DCMAKE_BUILD_TYPE=Release
cmake --build build/spanning-forest
ctest --test-dir build/spanning-forest --output-on-failure
./build/spanning-forest/traceable_spanning_forest_lab dsu
```

## 公开契约

- 无参数等价于 `dsu`；显式模式为 `dsu|kruskal|prim`，未知模式只写标准错误并返回 2。
- DSU 采用完整路径压缩和按大小合并；同大小时编号较小的根保留代表身份。
- 图为零基简单无向图，允许负权、零权和相同权重，拒绝越界、自环与重复无向边。
- Kruskal 按 `(weight,u,v)` 排序；Lazy Prim 的前沿也使用同一键，但接受顺序只受当前割约束。
- 断开图返回最小生成森林；两算法只要求总权重、分量数和 `V-C` 边数一致。
- 总权重执行有符号 64 位安全加法；失败时不返回半成品结果。

课程入口：[并查集](../../../learning-paths/cs-core/24-disjoint-set-union-path-compression.md) · [Kruskal](../../../learning-paths/cs-core/25-kruskal-minimum-spanning-forest.md) · [Lazy Prim](../../../learning-paths/cs-core/26-lazy-prim-cut-frontier-stale-edges.md)
