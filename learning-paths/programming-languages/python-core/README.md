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
| 对象与资源 | [数据模型、数据类和上下文管理](04-data-model-dataclasses-context-managers.md) | [对象生命周期、RAII和资源边界](../cpp-core/05-objects-references-pointers-lifetime-raii.md) | 基础配对已完成 |
| 包装与资源边界 | [装饰器、闭包和自定义上下文管理器](05-decorators-closures-custom-context-managers.md) | RAII 边界作为既有对照，不机械映射语法 | 已完成 |
| 工程化 | [包、CLI](06-package-structure-installable-cli.md)、[配置、日志、测试与安装认知](07-toml-configuration-logging-diagnostics.md) | CMake、测试、调试和静态分析 | 最小闭环已完成 |

## 课程顺序

| 课程 | 状态 | 你要掌握什么 |
| --- | --- | --- |
| [类型提示、接口与静态检查认知](01-type-hints-interfaces-static-checking.md) | 已完成 | 区分运行时类型、类型提示和静态检查，为不可信数据建立可验证边界 |
| [C++函数、声明与程序组织](../cpp-core/02-functions-declarations-program-organization.md) | 已完成 | 学习函数接口、参数传递和单文件职责边界 |
| [可维护函数接口、协议与模块边界](02-maintainable-function-interfaces-protocols-modules.md) | 已完成 | 使用关键字参数、协议、公开接口和单向依赖组织多模块程序 |
| [C++头文件、源文件与最小CMake工程](../cpp-core/03-headers-sources-cmake.md) | 已完成 | 把稳定接口迁移到多翻译单元、库目标和CTest构建结构 |
| [C++ STL容器、迭代器与基础算法](../cpp-core/04-stl-containers-iterators-algorithms.md) | 已完成 | 从单条状态卡进入多条记录处理并形成双语言阶段作品 |
| [容器协议、迭代器与生成器](03-iterables-iterators-generators.md) | 已完成 | 理解可迭代协议、单次消费、惰性生成和显式物化边界 |
| [C++ 对象、引用、指针、生命周期与 RAII](../cpp-core/05-objects-references-pointers-lifetime-raii.md) | 已完成 | 建立对象与资源所有权的基本模型 |
| [数据模型、数据类与上下文管理](04-data-model-dataclasses-context-managers.md) | 已完成 | 把结构化字典迁移为对象，并用 `with` 管理审计文件 |
| [装饰器、闭包与自定义上下文管理器](05-decorators-closures-custom-context-managers.md) | 已完成 | 用类型安全包装器复用调用边界，并分阶段提交审计文件 |
| [包结构、可安装入口与 CLI](06-package-structure-installable-cli.md) | 已完成 | 把多模块报告器迁移为 `src` 包，并提供模块入口、控制台脚本和 argparse 子命令 |
| [TOML 配置、日志与可诊断执行契约](07-toml-configuration-logging-diagnostics.md) | 已完成 | 建立显式配置、固定优先级、标准流、命名日志和退出码契约 |

## 工具基线

- Python 3.11或更高版本。
- 类型语法以Python 3.11兼容写法为准。
- 静态检查器使用固定版本的mypy并启用严格模式。
- 测试继续使用标准库`unittest`，静态检查不能替代运行测试。
- 阶段作品使用 `pyproject.toml` 和 `src` 布局；运行依赖仍只有标准库，构建与 mypy 作为开发依赖安装到项目虚拟环境。
- editable install 用于开发，wheel install 用于检查分发内容；课程不上传 PyPI。

## 学习方式

1. 先说明函数和数据的真实运行时边界，再写类型提示。
2. 运行静态检查，阅读每条错误中的期望类型与实际类型。
3. 运行代码和测试，确认类型通过后行为仍然正确。
4. 对JSON、用户输入和网络响应等外部数据继续执行运行时校验。
5. 审查AI是否通过`Any`、`cast()`或`# type: ignore`掩盖问题。
6. 保存静态检查、运行测试和人工判断三类证据。

## 阶段作品边界

Python起步的学习进度报告器保持原样，代表当时已经验收的能力。本课程在正文中提供类型化副本，不反向修改起步作品，也不创建新的独立练习目录。

双主修课程已经形成[双语言学习进度报告器](../../../exercises/programming-languages/study-progress-reporters/README.md)。Python 实现已加入惰性筛选、数据类对象、类型安全调用追踪、分阶段审计、可安装 CLI、显式 TOML 配置和 stderr 日志，C++ 实现已加入借用与 RAII 审计导出；两边继续保持公开主报告契约不变。类型提示、协议、CMake、容器、装饰器或 CLI 本身都不是独立项目。

## 下一步

从[类型提示、接口与静态检查认知](01-type-hints-interfaces-static-checking.md)开始，按表格顺序学习到[TOML 配置、日志与可诊断执行契约](07-toml-configuration-logging-diagnostics.md)。完成后，Python 核心已达到最小工程化离开条件；按总课程表进入四类路线纵向验证与 [CS 核心](../../cs-core/README.md)，并在后续项目中继续深化并发、网络、数据库、Web 与发布。
