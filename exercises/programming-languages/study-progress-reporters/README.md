# 双语言学习进度报告器

这是 Python/C++ 双主修的第一个阶段作品。它由多节配对课程形成基础版本，并沿容器、对象、资源与调用边界持续演进。两种语言仍保持相同的数据、业务规则和报告输出。

它不是长期项目。这里关注的是：同一个问题在两种语言中如何表达类型、容器、复制边界、构建和测试，而不是引入数据库、Web界面或第三方框架。

## 关联课程

- [C++：从源文件到可执行程序](../../../learning-paths/programming-languages/cpp-core/01-build-types-io.md)
- [Python：类型提示、接口与静态检查认知](../../../learning-paths/programming-languages/python-core/01-type-hints-interfaces-static-checking.md)
- [C++：函数、声明与程序组织](../../../learning-paths/programming-languages/cpp-core/02-functions-declarations-program-organization.md)
- [Python：可维护函数接口、协议与模块边界](../../../learning-paths/programming-languages/python-core/02-maintainable-function-interfaces-protocols-modules.md)
- [C++：头文件、源文件与最小CMake工程](../../../learning-paths/programming-languages/cpp-core/03-headers-sources-cmake.md)
- [C++：STL容器、迭代器与基础算法](../../../learning-paths/programming-languages/cpp-core/04-stl-containers-iterators-algorithms.md)
- [Python：容器协议、迭代器与生成器](../../../learning-paths/programming-languages/python-core/03-iterables-iterators-generators.md)
- [C++：对象、引用、指针、生命周期与RAII](../../../learning-paths/programming-languages/cpp-core/05-objects-references-pointers-lifetime-raii.md)
- [Python：数据模型、数据类与上下文管理](../../../learning-paths/programming-languages/python-core/04-data-model-dataclasses-context-managers.md)
- [Python：装饰器、闭包与自定义上下文管理器](../../../learning-paths/programming-languages/python-core/05-decorators-closures-custom-context-managers.md)
- [Python：包结构、可安装入口与 CLI](../../../learning-paths/programming-languages/python-core/06-package-structure-installable-cli.md)
- [Python：TOML 配置、日志与可诊断执行契约](../../../learning-paths/programming-languages/python-core/07-toml-configuration-logging-diagnostics.md)

## 统一行为契约

两套实现使用相同的四条内存记录，并提供相同能力：

- 进度限制在`0%`到`100%`之间。
- 完成时间达到或超过计划时间时状态为“已完成”。
- 汇总总计划、总完成、状态数量和唯一标签。
- 按进度降序排列；进度相同时按课程名升序排列。
- 按标签筛选，返回独立记录副本，不修改原始输入。
- Python额外提供惰性的标签筛选和进度行生成器，并在报告边界只物化一次输入。
- C++额外提供按引用更新、可空非拥有查找和作用域内审计文件导出；审计导出不改变主报告标准输出。
- Python 已把 `TypedDict` 记录迁移为数据类对象，并使用 `with` 提供相同格式的审计文件；主报告输出保持稳定。
- Python 提供可选的类型安全调用追踪器，并通过生成器式上下文管理器先写临时文件、成功后再发布审计；追踪事件不进入主报告。
- Python 已迁移为 `src` 布局可安装包，提供 `study-progress` 和 `python -m study_progress_reporter` 等价入口，以及 `report`、`audit` 子命令。
- Python 只读取 `--config` 显式指定的 TOML；命令行覆盖配置、配置覆盖默认值，报告进入 stdout，日志与错误进入 stderr。
- Python 成功返回 0，配置或 I/O 失败返回 1，argparse 参数语法错误返回 2；失败不覆盖旧审计或留下临时文件。
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
│   ├── pyproject.toml
│   ├── config.example.toml
│   ├── src/study_progress_reporter/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── cli.py
│   │   ├── config.py
│   │   ├── logging_setup.py
│   │   └── ...业务模块
│   └── tests/
│       ├── test_reporter.py
│       └── test_cli_config.py
└── README.md
```

## 运行 Python 版本

环境：Python 3.11及以上，运行仅使用标准库；构建与静态检查工具作为开发依赖安装到虚拟环境。

```bash
cd python
python -m pip install -e ".[dev]"
study-progress report
python -m study_progress_reporter report
python -m unittest discover -s tests -v
python -m mypy --strict src tests
python -m build
```

配置不会自动加载。需要时显式运行：

```bash
study-progress --config config.example.toml report
study-progress audit --output build/audit.txt
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
| 记录类型 | `@dataclass` 对象 | 简单聚合`struct` |
| 只读输入意图 | `Iterable[StudyRecord]` | `const std::vector<StudyRecord>&` |
| 排序副本 | `sorted()`处理复制后的记录 | 参数按值复制后`std::sort` |
| 惰性遍历 | `Iterator`与生成器按需产出 | 迭代器表示容器范围中的位置 |
| 唯一标签 | `set`后`sorted` | `std::set` |
| 状态统计 | `dict`并按键排序输出 | `std::map` |
| 对象与资源 | 对象方法、复制边界、`with` 文件上下文 | 引用借用、可空非拥有指针、`ofstream` RAII |
| 调用与发布边界 | `ParamSpec` 装饰器、`contextmanager` 分阶段提交 | 保持既有显式调用与 `ofstream` RAII 对照 |
| 工程入口 | `src` 包、pyproject、模块入口与控制台脚本 | CMake 应用目标与构建产物 |
| 配置与诊断 | 显式 TOML、命名 logger、stdout/stderr、退出码 | 保持现有命令行与 CTest 诊断基线 |
| 自动检查 | mypy、unittest | 编译器、CTest、审计成功与打开失败路径 |

## AI协作边界

AI可以生成容器替换、排序条件和测试候选，学习者必须亲自检查：

- 比较器是否满足严格弱序，不能把`<=`当作排序关系。
- 排序或筛选是否修改了调用者输入。
- C++是否返回悬空引用或失效迭代器。
- Python是否用`Any`或忽略注释绕过类型矛盾。
- Python装饰器是否吞掉异常、丢失返回值或把事件写入全局状态。
- 分阶段审计是否只在成功后替换正式文件，失败时是否保留旧内容并清理临时文件。
- 两种语言的边界数据、输出顺序和测试是否真的一致。

## 验收

- Python严格类型检查和全部unittest通过；审计成功与缺失父目录失败均有测试。
- C++以C++20和严格警告零警告构建，CTest全部通过；审计文件成功与无法打开路径均有测试。
- 两个应用的标准输出逐字一致。
- 空记录、重复标签、同进度、超额完成和筛选无结果均有测试。
- Python测试证明生成器惰性执行、单次消费和一次性输入报告行为。
- Python测试证明装饰器保留签名、返回值与元数据，失败事件不会抑制原异常。
- Python测试证明审计首次发布、覆盖和失败清理路径，旧文件在块内失败时保持不变。
- Python 测试证明包可安装、两个入口等价、帮助文本和标签筛选可用，默认报告不受新增参数影响。
- Python 测试证明 TOML 的合法、缺省、未知、错误类型和优先级路径，以及日志流和退出码 0/1/2 契约。
- 排序、筛选和汇总后原始记录顺序与内容保持不变。
- 没有第三方运行依赖、个人路径、密钥或生成产物进入Git。

## 下一步

Python 的包结构、CLI、配置与日志已形成最小工程化闭环。下一步按总课程表进入四类路线纵向验证和 CS 共同主干；并发、网络、数据库、Web 与真实发布继续留给后续课程和项目里程碑。
