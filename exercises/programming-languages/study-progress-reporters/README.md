# 双语言学习进度报告器

这是 Python/C++ 双主修的第一个阶段作品。它由六节课程形成基础版本，并在Python“容器协议、迭代器与生成器”课程中继续演进惰性遍历能力。两种语言仍保持相同的数据、业务规则和报告输出。

它不是长期项目。这里关注的是：同一个问题在两种语言中如何表达类型、容器、复制边界、构建和测试，而不是引入数据库、Web界面或第三方框架。

## 关联课程

- [C++：从源文件到可执行程序](../../../learning-paths/programming-languages/cpp-core/01-build-types-io.md)
- [Python：类型提示、接口与静态检查认知](../../../learning-paths/programming-languages/python-core/01-type-hints-interfaces-static-checking.md)
- [C++：函数、声明与程序组织](../../../learning-paths/programming-languages/cpp-core/02-functions-declarations-program-organization.md)
- [Python：可维护函数接口、协议与模块边界](../../../learning-paths/programming-languages/python-core/02-maintainable-function-interfaces-protocols-modules.md)
- [C++：头文件、源文件与最小CMake工程](../../../learning-paths/programming-languages/cpp-core/03-headers-sources-cmake.md)
- [C++：STL容器、迭代器与基础算法](../../../learning-paths/programming-languages/cpp-core/04-stl-containers-iterators-algorithms.md)
- [Python：容器协议、迭代器与生成器](../../../learning-paths/programming-languages/python-core/03-iterables-iterators-generators.md)

## 统一行为契约

两套实现使用相同的四条内存记录，并提供相同能力：

- 进度限制在`0%`到`100%`之间。
- 完成时间达到或超过计划时间时状态为“已完成”。
- 汇总总计划、总完成、状态数量和唯一标签。
- 按进度降序排列；进度相同时按课程名升序排列。
- 按标签筛选，返回独立记录副本，不修改原始输入。
- Python额外提供惰性的标签筛选和进度行生成器，并在报告边界只物化一次输入。
- 生成完全相同的UTF-8报告文本。

本作品故意不读取JSON或CSV。C++标准库没有JSON解析器，而文件格式不是本次容器对照的学习目标；两边都使用代码内固定样例，避免额外依赖干扰比较。

## 目录结构

```text
study-progress-reporters/
├── cpp/
│   ├── include/study/study_report.hpp
│   ├── src/main.cpp
│   ├── src/study_report.cpp
│   ├── tests/study_report_tests.cpp
│   ├── .gitignore
│   └── CMakeLists.txt
├── python/
│   ├── tests/test_reporter.py
│   ├── analysis.py
│   ├── fixtures.py
│   ├── main.py
│   ├── models.py
│   └── reporting.py
└── README.md
```

## 运行 Python 版本

环境：Python 3.11及以上，仅使用标准库；静态检查使用仓库开发环境中的mypy。

```bash
cd python
python main.py
python -m unittest discover -s tests -v
python -m mypy --strict .
```

## 运行 C++ 版本

环境：C++20、CMake 3.20及以上，仅使用标准库。

```bash
cd cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/study_report_app
```

Visual Studio等多配置生成器通常从`build/Debug/study_report_app.exe`运行应用。

## 预期报告

```text
学习进度报告
总计划：35.0 小时
总完成：30.5 小时
总体进度：87.1%

按进度排序：
- C++ 核心：100.0%（已完成）
- 工程复盘：100.0%（已完成）
- Python 起步：75.0%（进行中）
- 算法练习：50.0%（进行中）

状态统计：
- 已完成：2
- 进行中：2
唯一标签：cpp, python, 基础, 复盘, 工程, 算法
标签[基础]：Python 起步, C++ 核心, 算法练习
```

## Python与C++对照

| 能力 | Python | C++ |
| --- | --- | --- |
| 记录类型 | `TypedDict` | 简单聚合`struct` |
| 只读输入意图 | `Iterable[StudyRecord]` | `const std::vector<StudyRecord>&` |
| 排序副本 | `sorted()`处理复制后的记录 | 参数按值复制后`std::sort` |
| 惰性遍历 | `Iterator`与生成器按需产出 | 迭代器表示容器范围中的位置 |
| 唯一标签 | `set`后`sorted` | `std::set` |
| 状态统计 | `dict`并按键排序输出 | `std::map` |
| 自动检查 | mypy、unittest | 编译器、CTest |

## AI协作边界

AI可以生成容器替换、排序条件和测试候选，学习者必须亲自检查：

- 比较器是否满足严格弱序，不能把`<=`当作排序关系。
- 排序或筛选是否修改了调用者输入。
- C++是否返回悬空引用或失效迭代器。
- Python是否用`Any`或忽略注释绕过类型矛盾。
- 两种语言的边界数据、输出顺序和测试是否真的一致。

## 验收

- Python严格类型检查和全部unittest通过。
- C++以C++20和严格警告零警告构建，CTest全部通过。
- 两个应用的标准输出逐字一致。
- 空记录、重复标签、同进度、超额完成和筛选无结果均有测试。
- Python测试证明生成器惰性执行、单次消费和一次性输入报告行为。
- 排序、筛选和汇总后原始记录顺序与内容保持不变。
- 没有第三方运行依赖、个人路径、密钥或生成产物进入Git。

## 下一步

继续学习Python的“容器协议、迭代器与生成器”，从Python侧进一步理解惰性遍历和能力型接口。对象生命周期与资源管理会在后续C++课程中继续深化。
