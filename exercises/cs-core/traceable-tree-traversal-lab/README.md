# 可追踪树与遍历实验

这个阶段作品把二叉树槽位、链接节点、递归深度和显式遍历前沿实现为一份可安装、可测试、可逐字对照的双语言实验。Python 3.11 与 C++20 只使用标准库，所有计数来自教学实现。

## 目录

```text
traceable-tree-traversal-lab/
├── python/   # src 布局、模块入口、unittest
└── cpp/      # CMake、公开头文件、CTest
```

## 三种模式

| 模式 | 观察重点 | 固定证据 |
| --- | --- | --- |
| `shape` | 零基槽位、链接节点、树形指标 | 大小、高度、叶子数与根子节点 |
| `recursive` | 前中后序、递归帧和深度保护 | 访问顺序、访问数与最大深度 |
| `frontier` | 显式栈、队列与层级边界 | DFS/BFS 顺序与最大前沿 |

无参数等价于 `shape`。未知模式只写标准错误并返回退出码 `2`。

## Python

```bash
cd exercises/cs-core/traceable-tree-traversal-lab/python
python3.11 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m mypy --strict src tests
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m traceable_tree_traversal_lab shape
.venv/bin/python -m traceable_tree_traversal_lab recursive
.venv/bin/python -m traceable_tree_traversal_lab frontier
```

## C++

```bash
cmake -S exercises/cs-core/traceable-tree-traversal-lab/cpp -B /tmp/traceable-tree-traversal-build -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/traceable-tree-traversal-build
ctest --test-dir /tmp/traceable-tree-traversal-build --output-on-failure
/tmp/traceable-tree-traversal-build/traceable_tree_traversal_lab shape
```

## 公开契约

- `BinaryTree` 复制并规范化零基层序槽位；非空输入拒绝空根和孤儿节点。
- 空树高度为 `-1`，根深度为 `0`，叶子高度为 `0`。
- 递归遍历提供显式 `max_depth` 教学保护，不通过真实栈溢出演示失败。
- 迭代 DFS 先压右后压左；BFS 先左后右入队；最大前沿包含初始根节点。
- C++ 树节点由 `std::unique_ptr` 单一拥有，树可移动但不可复制；两种语言都不公开节点引用。

## 课程迁移任务

- 第 15 课：实现并验证 `path_to_slot`，区分空槽、越界和合法根路径。
- 第 16 课：实现 `count_at_depth`，到达目标层后不继续进入更深子树。
- 第 17 课：实现 `widest_level`，宽度并列时选择更浅的层。
