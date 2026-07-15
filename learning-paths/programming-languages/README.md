# 编程语言

## 定位

编程语言线以 Python 和 C++ 为双主修，Java作为完整补充路线。JavaScript/TypeScript主要在Web阶段学习。目标不是学完语法表，而是从零建立编程能力，再逐步获得阅读代码、设计接口、调试程序、构建项目、分析性能和进入专业领域的能力。

## 适合人群

- 需要选择主力语言的人。
- 想同时覆盖工程开发、系统理解和 AI 应用的人。
- 想把语言学习和项目实践结合起来的人。

## 阶段划分

1. [Python 起步](python-basics/README.md)：从最小脚本推进到包含函数、数据结构、文件、模块、异常和测试的小型程序。
2. 核心语言：沿[Python核心语言](python-core/README.md)和[C++核心语言](cpp-core/README.md)深入类型、接口、数据模型、对象生命周期、STL与泛型；先完成构建与类型配对，再按能力主题继续推进。
3. 工程化：掌握项目结构、依赖、配置、日志、测试、调试、构建和文档。
4. 并发与网络：学习 Python 的线程、进程和异步，以及 C++ 的并发、内存模型、网络和协议处理。
5. 运行原理与性能：理解 Python 解释器、GIL和扩展边界，以及 C++ 内存布局、未定义行为和性能分析。
6. 领域应用：在Web、数据、AI、工业控制、实时通信和系统项目中持续深化。
7. Java 补充：语法、面向对象、集合、JVM、构建、测试和后端生态。
8. Web语言：JavaScript与TypeScript在Web主线中展开。

## 双主修能力阶梯

| 层级 | Python 能力 | C++ 能力 | 主要产出 |
| --- | --- | --- | --- |
| 入门 | 语法、函数、数据结构、文件、模块、异常和最小测试 | 在 Python 建立共同编程概念后开始类型、控制流、函数和编译 | 可独立运行和检查的小程序 |
| 进阶 | 类型提示、数据模型、迭代器、生成器、装饰器和上下文管理 | 类、生命周期、RAII、STL、迭代器、算法、模板和现代 C++ | 职责清楚的多模块程序 |
| 工程化 | 包结构、CLI、配置、日志、测试、依赖管理和发布认知 | CMake、多文件工程、测试、调试、静态分析和错误处理 | 可构建、可测试、可复现的项目 |
| 深入 | 线程、进程、异步、网络、解释器、GIL、性能和扩展边界 | 并发、原子操作、内存模型、网络、系统接口和性能分析 | 有测量证据的并发、网络或性能实验 |
| 领域应用 | 自动化、Web、数据和AI | 系统组件、工业控制、实时通信和本地推理 | 跨课程项目中的真实模块 |

“精通”不作为看完某个章节后的标签。学习者需要在多个项目中反复设计、实现、测试、调试和复盘，才能逐步接近熟练与深入。

## 推荐学习顺序

1. 先用Python掌握变量、控制流、函数、数据结构和调试。
2. 完成Python起步后先用[从源文件到可执行程序](cpp-core/01-build-types-io.md)启动C++，再完成Python[类型提示、接口与静态检查认知](python-core/01-type-hints-interfaces-static-checking.md)、C++[函数、声明与程序组织](cpp-core/02-functions-declarations-program-organization.md)、Python[可维护函数接口、协议与模块边界](python-core/02-maintainable-function-interfaces-protocols-modules.md)、C++[头文件、源文件与最小CMake工程](cpp-core/03-headers-sources-cmake.md)、[STL容器、迭代器与基础算法](cpp-core/04-stl-containers-iterators-algorithms.md)、Python[容器协议、迭代器与生成器](python-core/03-iterables-iterators-generators.md)和C++[对象、引用、指针、生命周期与RAII](cpp-core/05-objects-references-pointers-lifetime-raii.md)，不要求机械轮流。
3. 核心语言和基础工程化达到验收后进入CS最小核心，不等待所有高级主题学完。
4. 在Web、AI和工业控制等项目中继续学习并发、网络、运行原理、性能和领域接口。
5. Java在双主修基础后作为完整补充路线。
6. JavaScript/TypeScript在Web阶段进入，不与前期双主修争抢起步时间。

## 当前项目映射

- Python：[Python 内容分析工具](../../projects/python-content-analysis/README.md)
- Python 数据与 AI：[结构化数据机器学习系统](../../projects/structured-data-ml-system/README.md)
- Python/C++ 工业通信：工业控制与实时通信项目已登记为高级候选，课程和项目目录尚未建设。
- C++本地推理：`llama.cpp` 只作为后期部署与性能方向，不代替C++课程。
- Java：来源已登记，作为补充主流语言建设。

## 进入与离开条件

- 进入条件：工程基础前置验收完成。
- Python 起步入口：[课程说明](python-basics/README.md)。
- Python深化入口：[Python核心语言](python-core/README.md)。
- C++解锁：Python起步完成，能够独立编写、检查和维护一个小型程序；当前入口为[C++核心语言](cpp-core/README.md)。
- CS最小核心解锁：Python可完成带测试和错误处理的小工具，C++可完成CMake多文件程序并使用STL和RAII。
- 工业控制与实时通信解锁：完成C++基础工程化，以及操作系统、并发、网络、数据类型和序列化基础。

详细顺序见[小白统一学习路线](../beginner-roadmap.md)。

## 对应入口

- 资源：../../resources/README.md
- 评测：../../reviews/README.md
- 笔记：../../notes/README.md
- 练习：../../exercises/README.md
- 项目：../../projects/README.md
