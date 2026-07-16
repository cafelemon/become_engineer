# 可追踪数组实验

这是 CS 核心的第一条连续成果线。Python 与 C++ 使用相同固定数据和业务契约，先观察安全数组访问与线性查找，再用确定性操作次数解释增长率。

## 关联课程

- [序列接口、数组表示与安全边界](../../../learning-paths/cs-core/01-sequence-interface-array-representation-boundaries.md)
- [操作计数、增长率与渐近复杂度](../../../learning-paths/cs-core/02-operation-count-growth-asymptotic-complexity.md)
- [字符串、UTF-8 字节与码点边界](../../../learning-paths/cs-core/03-string-utf8-byte-code-point-boundaries.md)
- [二维网格、行优先布局与坐标边界](../../../learning-paths/cs-core/04-two-dimensional-grid-row-major-layout.md)
- [动态数组容量、扩容成本与摊还分析](../../../learning-paths/cs-core/05-dynamic-array-capacity-amortized-cost.md)

## 公开契约

- `checked_at` 主动拒绝负索引和 `index == size`；C++ 不使用未检查的越界访问。
- `replace_at_copy` 返回修改后的副本，调用者输入保持不变。
- `linear_search` 返回第一个匹配位置和精确比较次数；缺失目标比较 `n` 次。
- `build_growth_rows` 生成常量访问、线性扫描和两两比较的确定性步骤数。
- `analyze_utf8` 严格验证 UTF-8，并分别统计字节、码点、ASCII 和多字节码点。
- `checked_grid_at` 与 `sum_grid_row` 使用扁平行优先表示，并校验形状和坐标。
- `simulate_growth` 使用公开的确定性倍增规则记录追加、复制和总步骤，不代表标准库实际增长因子。
- 两个程序的 UTF-8 标准输出逐字一致。

## Python

环境为 Python 3.11+，运行只使用标准库。

```bash
cd python
python -m pip install -e ".[dev]"
python -m traceable_array_lab
python -m traceable_array_lab text
python -m traceable_array_lab grid
python -m traceable_array_lab capacity
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
./build/traceable_array_lab text
./build/traceable_array_lab grid
./build/traceable_array_lab capacity
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

无参数与 `baseline` 模式继续输出上面的 V2.1 报告。其余模式各自输出独立、可逐字比较的 UTF-8、二维网格或容量事件报告；未知模式返回退出码 2。
