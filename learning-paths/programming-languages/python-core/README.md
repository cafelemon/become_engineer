# Python：核心与工程化

Python 起步解决“把程序写出来并修到能运行”。这里继续解决两个问题：怎样让代码的接口和数据关系更清楚，以及怎样把多文件程序做成可安装、可配置、可诊断的工程。

这条路线适合应用开发、自动化、数据、AI、Web 和 LLM/Agent。C++ 不再是进入 Python 核心的强制前置；想比较静态类型、对象生命周期和构建方式时，可以并行进入 [C++ 起步与核心](../cpp-core/README.md)。

## 开始前

- 完成 [Python 起步](../python-basics/README.md)和学习进度报告器。
- 能创建虚拟环境，运行程序和 `unittest`，并阅读失败信息。
- 能说明输入校验、异常和自动化测试分别解决什么问题。
- 建议先完成 [CS 起步](../../cs-core/README.md)，建立表示和操作成本的基本直觉。

## Python 核心 · 5 节

| 课程 | 重点 | 项目变化 |
| --- | --- | --- |
| [类型提示、接口与静态检查](01-type-hints-interfaces-static-checking.md) | 区分运行时类型、类型提示和静态检查 | 给报告器补充可信的数据契约 |
| [可维护函数接口、协议与模块边界](02-maintainable-function-interfaces-protocols-modules.md) | 设计签名、协议、公开接口和依赖方向 | 让输出边界可以替换 |
| [容器协议、迭代器与生成器](03-iterables-iterators-generators.md) | 理解迭代、单次消费、惰性生成和物化 | 增加惰性筛选与报告行 |
| [数据模型、数据类与上下文管理](04-data-model-dataclasses-context-managers.md) | 从字典迁移到对象，用 `with` 管理文件 | 建立对象方法与审计快照 |
| [装饰器、闭包与自定义上下文管理器](05-decorators-closures-custom-context-managers.md) | 复用调用边界并安全提交文件 | 增加类型安全追踪和分阶段审计 |

这些课程属于核心层，不是“再学一些语法”。学习者需要解释接口、对象和资源为什么这样设计，并用静态检查、运行测试和失败路径共同验证。

## Python 工程化 · 2 节

| 课程 | 重点 | 项目变化 |
| --- | --- | --- |
| [包结构、可安装入口与 CLI](06-package-structure-installable-cli.md) | `src` 布局、`pyproject.toml`、模块入口、控制台脚本和子命令 | 报告器成为可安装命令行包 |
| [TOML 配置、日志与可诊断执行](07-toml-configuration-logging-diagnostics.md) | 配置优先级、标准流、命名日志和退出码 | 报告器可以配置并留下诊断信息 |

完成工程化后，程序应能在干净环境安装，命令入口和配置行为稳定，日志与业务输出分开，失败退出码可以由测试证明。

## 工具基线

- Python 3.11 或更高版本。
- 类型检查使用固定版本的 mypy 严格模式。
- 测试继续使用标准库 `unittest`。
- 项目使用 `pyproject.toml` 和 `src` 布局；运行依赖仍只有标准库。
- editable install 用于开发，wheel install 用于检查分发内容；课程不要求上传 PyPI。

类型检查不能替代运行测试，测试也不能证明外部 JSON、用户输入或网络响应天然可信。每个边界都要选择合适的验证方式。

## 连续作品

课程持续演进[双语言学习进度报告器](../../../exercises/programming-languages/study-progress-reporters/README.md)。Python 版本从多模块脚本逐步变为类型清楚、对象化、可安装、可配置和可诊断的工程；公开主报告契约保持稳定。

每节课都应保存本次修改、静态检查、测试结果、一次失败排查和下一版准备解决的问题。装饰器、数据类或 CLI 是作品里的能力，不单独包装成虚构的大型项目。

## 下一步

从[类型提示、接口与静态检查](01-type-hints-interfaces-static-checking.md)开始，按顺序完成核心与工程化。之后可以进入 Web、AI 数据实验、LLM 应用，或回到 C++ 与系统方向；完整前置见[课程地图](../../curriculum-map.md)。
