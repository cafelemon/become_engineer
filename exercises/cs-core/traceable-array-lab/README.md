# 可追踪数组实验

这是 CS 核心的第一条连续成果线。Python 与 C++ 使用相同固定数据和业务契约，先观察安全数组访问与线性查找，再用确定性操作次数解释增长率。

## 关联课程

- [序列接口、数组表示与安全边界](../../../learning-paths/cs-core/01-sequence-interface-array-representation-boundaries.md)
- [操作计数、增长率与渐近复杂度](../../../learning-paths/cs-core/02-operation-count-growth-asymptotic-complexity.md)

## 公开契约

- `checked_at` 主动拒绝负索引和 `index == size`；C++ 不使用未检查的越界访问。
- `replace_at_copy` 返回修改后的副本，调用者输入保持不变。
- `linear_search` 返回第一个匹配位置和精确比较次数；缺失目标比较 `n` 次。
- `build_growth_rows` 生成常量访问、线性扫描和两两比较的确定性步骤数。
- 两个程序的 UTF-8 标准输出逐字一致。

## Python

环境为 Python 3.11+，运行只使用标准库。

```bash
cd python
python -m pip install -e ".[dev]"
python -m traceable_array_lab
python -m unittest discover -s tests -v
python -m mypy --strict src tests
```

## C++

环境为 C++20 与 CMake 3.20+，运行只使用标准库。

```bash
cd cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_array_lab
```

## 输出

```text
可追踪数组实验
数据：7, 3, 9, 3
index=2：9
target=3：index=1，comparisons=2

增长表
n | 常量访问 | 线性扫描 | 两两比较
4 | 1 | 4 | 6
8 | 1 | 8 | 28
16 | 1 | 16 | 120
32 | 1 | 32 | 496
```

计时只能辅助观察环境噪声，不属于正确性测试，也不用于比较语言胜负。
