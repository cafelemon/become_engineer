# 开始学习

这是一条给初学者使用的默认学习路线。你不需要先理解仓库目录，也不需要自己判断先学哪一门；从上往下走，完成当前部分的练习和验收后，再进入下一部分。

## 学习路线树

```text
工程基础入门
└── Python 起步
    └── Python / C++ 双主修
        └── CS 最小核心
            └── Web 实践 + CS 深化
                └── AI 基础
                    └── LLM / Agent
```

可选分支：

- Java：完成 Python 起步后可以作为补充语言学习，适合后续进入 Java 后端生态。
- 强化学习：完成机器学习和深度学习基础后再进入，不是 LLM/Agent 的必经前置。
- 多模态、Text2SQL、视觉、金融 AI、本地推理：完成对应基础后再选择。

## 使用规则

1. 当前部分的练习和完成标准没有通过，不进入下一部分。
2. 项目只在达到解锁条件后开始，不替代前置课程。
3. 学习中遇到不会的基础知识，回到对应课程补齐。
4. 每次学习都留下可检查的记录，包括命令、输出、错误、问题和下一步。

## 工程基础入门

先建立最基本的学习方法、文件意识、命令行能力、文档记录、版本管理、环境认知和验证习惯。

### 适合谁

- 从零开始学习工程、编程或 AI。
- 会使用电脑，但还不熟悉终端、Git、Markdown 或开发环境。
- 经常遇到“我不知道文件在哪里”“命令为什么不能运行”“学完不知道算不算会”的问题。

### 学习内容

- [课程说明](engineering-foundation/stage-0/README.md)
- [学习方法](engineering-foundation/stage-0/01-learning-method.md)
- [文件系统](engineering-foundation/stage-0/02-filesystem.md)
- [终端与 Shell](engineering-foundation/stage-0/03-terminal-shell.md)
- [编辑器](engineering-foundation/stage-0/04-editor.md)
- [Markdown](engineering-foundation/stage-0/05-markdown.md)
- [Git](engineering-foundation/stage-0/06-git.md)
- [开发环境](engineering-foundation/stage-0/07-development-environment.md)
- [Docker最小认知](engineering-foundation/stage-0/08-docker-basics.md)
- [验证习惯](engineering-foundation/stage-0/09-validation-habit.md)

### 完成标准

- 能创建一个 Git 仓库并完成至少 3 次有意义的提交。
- 能从终端进入项目目录并运行一个给定命令。
- 能写一份包含目标、步骤、结果和问题的 Markdown 学习记录。
- 能解释 Docker 解决的环境一致性问题。
- 能根据错误信息指出失败发生在哪条命令，而不是只说“不能运行”。

### 下一步

完成工程基础入门后，进入 Python 起步。

## Python 起步

用 Python 建立最基本的程序思维，并为后续 C++、数据处理、自动化和 AI 学习打基础。

### 前置要求

- 工程基础入门完成。

### 学习内容

- [课程说明](programming-languages/python-basics/README.md)
- [变量、基本类型、输入输出](programming-languages/python-basics/01-variables-types-io.md)
- [条件、循环、布尔逻辑](programming-languages/python-basics/02-conditions-loops-boolean.md)
- 函数、参数、返回值和作用域。
- 字符串、列表、字典、集合和元组。
- 文件读取、JSON 和简单目录操作。
- 模块、导入和虚拟环境的基本使用。
- 异常信息、基本调试和最小测试意识。

### 完成标准

- 能独立编写一个读取 JSON 或文本文件并输出统计结果的脚本。
- 能把重复代码提取成函数。
- 能解释列表和字典分别适合什么场景。
- 能创建虚拟环境并运行项目命令。
- 能根据 traceback 定位到具体文件和行。

### 项目解锁

完成 Python 起步后，可以进入 [Python 内容分析工具](../projects/python-content-analysis/README.md) 的第一个里程碑。

项目不会替代 Python 起步课程。先完成本部分的变量、条件、循环、函数、数据结构、文件和调试练习，再进入项目里程碑。

## Python / C++ 双主修

Python 用于快速实现、数据处理和自动化；C++ 用于理解类型、编译、内存、性能和系统意识。

### 前置要求

- Python 起步完成。

### Python 方向

- 类型提示、模块组织和包结构。
- 命令行参数、配置、日志和异常设计。
- 单元测试、测试数据和可重复运行。
- NumPy、pandas 和基础数据处理。
- API 与自动化所需的标准库能力。

### C++ 方向

- 编译、链接、头文件和源文件。
- 类型、引用、指针、const 和作用域。
- 函数、类、对象生命周期和 RAII。
- STL 容器、迭代器和算法。
- 内存、智能指针、错误处理和调试。
- CMake、测试和基础工程组织。

### Java 补充

Java 不是默认必修，但可以作为完整补充路线学习：

- 语法、类型和控制流。
- 面向对象、异常和集合。
- 泛型、IO、并发基础。
- JVM、构建工具和测试。
- Spring 等后端生态在 Web 实践中再展开。

## CS 最小核心

在开始完整 Web 应用前，先补齐解释程序性能、网络请求和数据存储所需的计算机基础。

### 前置要求

- Python 和 C++ 基础完成。

### 学习内容

- 数据结构：数组、链表、栈、队列、哈希表、树。
- 通用算法与复杂度：查找、排序、递归、动态规划、图的基本概念、时间和空间复杂度。
- 计算机运行基础：进程、线程、内存、文件和系统调用概念。
- 网络最小集：客户端/服务端、IP、TCP、DNS、HTTP。
- 数据库最小集：关系模型、表、主键、SQL、索引和事务概念；实践工具以 PostgreSQL 和 `psql` 为主，MySQL 作为常见对照。
- 数据交换：文本、JSON、编码和序列化。

### 完成标准

- 能为常见容器操作给出基本复杂度判断。
- 能描述浏览器或客户端请求 API 的基本过程。
- 能设计一个简单关系表并完成增删改查。
- 能解释进程与线程、内存与磁盘的基本区别。

## Web 实践 + CS 深化

做出可访问的完整应用，同时用 CS 原理解释真实工程问题。

### 前置要求

- CS 最小核心完成。

### Web 实践

- HTML、CSS 和浏览器基础。
- JavaScript，再进入 TypeScript。
- 前端组件、状态、表单和请求。
- Python 后端、FastAPI、数据校验和错误处理。
- REST、OpenAPI、认证和权限。
- PostgreSQL、psql、SQL、迁移、备份和数据访问层；根据项目需要补充 MySQL 差异。
- 测试、日志、部署、监控和回滚。

### CS 深化

- 操作系统：进程线程、同步、内存和文件系统。
- 网络：TCP、HTTP、连接、缓存和代理。
- 数据库：PostgreSQL 优先的事务、索引、查询优化和并发；理解 MySQL 在类型、索引、事务和部署上的常见差异。
- 系统设计：缓存、队列、可用性、一致性和扩展。
- 安全：认证、授权、输入校验、密钥和最小权限。

## AI 基础

理解数据、模型、训练和评估的完整闭环，并能够通过实验判断模型是否有效。

### 前置要求

- Python 工程化和数据处理。
- 数据结构、复杂度和基本实验方法。

### 学习内容

- 数学基础：线性代数、概率统计、微积分、梯度和优化。
- 机器学习：数据清洗、特征工程、训练验证、指标和误差分析。
- 深度学习：张量、神经网络、反向传播、优化器和正则化。
- NLP / Transformer：文本表示、序列模型、注意力机制和预训练模型。
- 强化学习：环境、状态、动作、奖励、价值方法和 DQN，作为独立进阶分支。

### 项目解锁

- [结构化数据机器学习系统](../projects/structured-data-ml-system/README.md)
- [文本分类模型演进](../projects/text-classification-evolution/README.md)
- [强化学习控制实验](../projects/reinforcement-learning-control-lab/README.md)

## LLM / Agent

在 Python 工程能力、Web/API、检索和评估能力具备后，再进入 LLM/Agent。

### 前置要求

- Python 工程化。
- Web/API 基础。
- 检索、评估和基础模型知识。

### 学习内容

- Prompt、结构化输出和工具调用。
- Embedding、检索、RAG 和引用。
- 评估集、自动评估和人工复核。
- Workflow、Agent、状态管理和失败恢复。
- 可观测性、部署和安全边界。

### 项目解锁

- [可评估的智能学习助手](../projects/intelligent-learning-assistant/README.md)

这个项目会使用本学习库的公开内容作为知识来源，逐步加入检索、引用、RAG、评估、工具调用、工作流、Agent、可观测性和部署。
