# Python 核心语言

Python 核心语言承接已经完成的 Python 起步。目标不再是认识更多语法，而是学会设计可维护接口、表达数据契约、理解 Python 数据模型，并逐步进入迭代器、生成器、装饰器、上下文管理、包结构和工程化。

本课程与 C++ 核心语言按能力主题配对。两门语言会处理相似问题，但不会强行使用相同语法或实现方式；学习者需要比较它们在类型检查、运行模型、资源管理和工程工具上的真实差异。

## 前置要求

- 完成 [Python 起步](../python-basics/README.md)和学习进度报告器阶段作品。
- 完成 C++ [从源文件到可执行程序：编译、类型与输入输出](../cpp-core/01-build-types-io.md)。
- 能创建虚拟环境、安装项目开发依赖、运行测试并阅读失败信息。
- 能说明运行时校验与自动化测试各自解决什么问题。

## 能力顺序

| 能力主题 | Python 重点 | C++ 配对主题 | 状态 |
| --- | --- | --- | --- |
| 类型与接口 | 类型提示、静态检查、TypedDict、边界校验 | 编译、静态类型、初始化和转换 | 已完成 |
| 函数与程序组织 | 可维护签名、模块接口、协议和依赖方向 | [声明、定义、参数、返回和单文件职责拆分](../cpp-core/02-functions-declarations-program-organization.md) | 已完成 |
| 容器与迭代 | [抽象容器接口、迭代器和生成器](03-iterables-iterators-generators.md) | [STL容器、迭代器和算法](../cpp-core/04-stl-containers-iterators-algorithms.md) | 已完成 |
| 对象与资源 | 数据模型、类、装饰器和上下文管理 | 对象生命周期、RAII和智能指针 | 待建设 |
| 工程化 | 包、CLI、配置、日志、测试、依赖和发布认知 | CMake、测试、调试和静态分析 | 待建设 |

## 课程顺序

| 课程 | 状态 | 你要掌握什么 |
| --- | --- | --- |
| [类型提示、接口与静态检查认知](01-type-hints-interfaces-static-checking.md) | 已完成 | 区分运行时类型、类型提示和静态检查，为不可信数据建立可验证边界 |
| [C++函数、声明与程序组织](../cpp-core/02-functions-declarations-program-organization.md) | 已完成 | 学习函数接口、参数传递和单文件职责边界 |
| [可维护函数接口、协议与模块边界](02-maintainable-function-interfaces-protocols-modules.md) | 已完成 | 使用关键字参数、协议、公开接口和单向依赖组织多模块程序 |
| [C++头文件、源文件与最小CMake工程](../cpp-core/03-headers-sources-cmake.md) | 已完成 | 把稳定接口迁移到多翻译单元、库目标和CTest构建结构 |
| [C++ STL容器、迭代器与基础算法](../cpp-core/04-stl-containers-iterators-algorithms.md) | 已完成 | 从单条状态卡进入多条记录处理并形成双语言阶段作品 |
| [容器协议、迭代器与生成器](03-iterables-iterators-generators.md) | 已完成 | 理解可迭代协议、单次消费、惰性生成和显式物化边界 |
| C++ 对象、引用、指针、生命周期与 RAII | 下一节 | 建立对象与资源所有权的基本模型 |

## 工具基线

- Python 3.11或更高版本。
- 类型语法以Python 3.11兼容写法为准。
- 静态检查器使用固定版本的mypy并启用严格模式。
- 测试继续使用标准库`unittest`，静态检查不能替代运行测试。
- 第三方工具只安装到项目虚拟环境，不进入全局Python。

## 学习方式

1. 先说明函数和数据的真实运行时边界，再写类型提示。
2. 运行静态检查，阅读每条错误中的期望类型与实际类型。
3. 运行代码和测试，确认类型通过后行为仍然正确。
4. 对JSON、用户输入和网络响应等外部数据继续执行运行时校验。
5. 审查AI是否通过`Any`、`cast()`或`# type: ignore`掩盖问题。
6. 保存静态检查、运行测试和人工判断三类证据。

## 阶段作品边界

Python起步的学习进度报告器保持原样，代表当时已经验收的能力。本课程在正文中提供类型化副本，不反向修改起步作品，也不创建新的独立练习目录。

双主修累计六节基础内容已经形成[双语言学习进度报告器](../../../exercises/programming-languages/study-progress-reporters/README.md)。本节继续演进其中的Python实现，加入惰性筛选、一次遍历汇总和显式物化边界，同时保持C++实现与公开报告契约不变。类型提示、协议、CMake或容器本身都不是独立项目。

## 下一步

从[类型提示、接口与静态检查认知](01-type-hints-interfaces-static-checking.md)开始，按表格顺序学习到[容器协议、迭代器与生成器](03-iterables-iterators-generators.md)。完成后进入C++[对象、引用、指针、生命周期与RAII](../cpp-core/05-objects-references-pointers-lifetime-raii.md)，继续建立双语言的对象与资源能力对照。
