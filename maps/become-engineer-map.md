# Become Engineer 总地图

## 四层结构

```text
学习地图
  -> 学习路线
    -> 项目实践
      -> 资源评测与公开沉淀
```

## 默认主线

```text
工程基础
  -> 编程语言（Python 起步，Python/C++ 双主修，Java 补充）
    -> CS 最小核心
      -> Web 全栈 / CS 深化并行
        -> AI 基础
          -> LLM/Agent

CS 深化可选分支
  -> 工业控制与实时通信
    -> PLC / Beckhoff / TwinCAT
      -> ADS / DDS
        -> 仿真集成 / 真实设备
```

六条主线用于内容归类。新学习者的唯一默认顺序和阶段验收以 [小白统一学习路线](../learning-paths/beginner-roadmap.md) 为准。

## 三层课程结构

```text
必修主干
  -> 达到阶段验收后进入下一主线

推荐深化
  -> 不阻塞默认路线
  -> 提升工程熟练度、原理理解和机考能力

专业选修
  -> 面向具体职业或技术方向
  -> 可以依赖一个或多个推荐深化模块
```

语言之后的全部模块、前置和跳过影响见[完整课程地图](../learning-paths/curriculum-map.md)。

## 推荐学习节奏

1. 先完成语言前的工程基础：学习方法、文件系统、终端、编辑器、Markdown、Git、环境、Docker最小认知和验证习惯。
2. 用 Python 建立编程概念，随后启动 Python 与 C++ 双主修，并沿核心语言、工程化、并发网络、运行原理与性能、领域应用持续深化。
3. 完成数据结构、通用算法、复杂度、HTTP、网络和数据库的 CS 最小核心。
4. 启动 Web 实践，同时继续学习操作系统、并发、PostgreSQL优先的数据库原理、MySQL差异和系统设计。
5. 在 Python、数学和评估基础上进入 AI，学习机器学习、深度学习、NLP/Transformer和强化学习等模型算法。
6. 在 Python 工程化、Web/API、检索和评估基础上进入 LLM/Agent。

需要工业自动化、设备通信或实时数据系统能力的学习者，可以在C++工程化、操作系统、并发和网络基础完成后进入“工业控制与实时通信”分支。该分支从PLC与TwinCAT仿真推进到ADS/DDS系统集成，再扩展到真实Beckhoff设备；不需要时可以跳过，不影响默认路线。

其他推荐深化和专业选修包括算法与机考、系统编程、网络与数据库深化、前后端工程、MLOps、强化学习、多模态、本地推理、Text2SQL和专业Agent。它们不改变默认顺序，只在前置满足后解锁。

外部素材按统一路线逐阶段加工，不直接决定学习顺序。来源情况见：

- [Python、AI 与 LLM 素材覆盖说明](python-ai-llm-content-coverage.md)
- [外部来源目录](../content-inbox/external-source-catalog.md)
- [项目主干规划](../projects/project-roadmap.md)

## 内容沉淀规则

- 路线放入 `learning-paths/`。
- 原始免费资源放入 `resources/`。
- 资源使用后的判断放入 `reviews/`。
- 可公开知识笔记放入 `notes/`。
- 练习题、聚焦实验和阶段验证放入 `exercises/`。
- 跨章节实践项目放入 `projects/`。
- 从 `个人学习/` 提炼出的阶段成果放入 `publications/`。
