# 可追踪查找与排序实验

这个阶段作品把有序查找、基础比较排序和自底向上归并实现为一份可安装、可测试、可逐字对照的双语言实验。Python 3.11 与 C++20 只使用标准库，操作次数由教学实现定义，不依赖标准排序函数的内部行为。

## 目录

```text
traceable-search-sort-lab/
├── python/   # src 布局、模块入口、unittest
└── cpp/      # CMake、公开头文件、CTest
```

## 三种模式

| 模式 | 观察重点 | 固定证据 |
| --- | --- | --- |
| `search` | 一次性有序验证、线性查找、左右边界 | 返回位置与键比较次数 |
| `elementary` | 插入排序、选择排序、稳定性 | 比较、右移、交换与标签顺序 |
| `merge` | 宽度 1/2/4 的迭代归并 | 每轮快照、比较与写入次数 |

无参数等价于 `search`。未知模式只写入标准错误并返回退出码 `2`。

## Python

```bash
cd exercises/cs-core/traceable-search-sort-lab/python
python3.11 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m mypy --strict src tests
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m traceable_search_sort_lab search
.venv/bin/python -m traceable_search_sort_lab elementary
.venv/bin/python -m traceable_search_sort_lab merge
```

## C++

```bash
cmake -S exercises/cs-core/traceable-search-sort-lab/cpp -B /tmp/traceable-search-sort-build -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/traceable-search-sort-build
ctest --test-dir /tmp/traceable-search-sort-build --output-on-failure
/tmp/traceable-search-sort-build/traceable_search_sort_lab search
```

## 公开契约

- `SortedValues` 构造时复制并验证非递减顺序；后续查找计数不包含验证成本。
- `lower_bound` 返回第一个大于等于目标的位置，`upper_bound` 返回第一个严格大于目标的位置，两者都允许返回序列长度。
- 插入排序只在严格越过时移动相等键；选择排序保留标准交换产生的不稳定反例。
- `merge_sorted` 在键相等时先取左段；`bottom_up_merge_sort` 返回每轮宽度和完整快照。
- 所有排序返回副本，调用方输入保持不变。

## 课程迁移任务

- 第 12 课：组合左右边界实现 `equal_range`，覆盖存在、缺失与空序列。
- 第 13 课：把稳定插入排序迁移为降序，仍保持相等标签顺序。
- 第 14 课：把迭代归并迁移为稳定降序，不改写输入，也不改用递归。
