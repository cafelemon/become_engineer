# 练习库

这里存放题目、聚焦实验和阶段作品。单节课只验证一个知识点的微练习保留在课程正文，不在这里重复建目录；跨课程长期项目继续放在 `projects/`。

练习应尽量说明：

- 目标
- 输入
- 输出
- 约束
- 验收标准
- 关联的连续课程、起始状态和最终产出
- 环境、文件、依赖、运行命令和预期结果
- AI协作边界、人工修改、手动检查点和验证证据
- 常见失败、离线或低成本替代方案
- 提示
- 延伸任务

阶段作品默认由连续3-6节相关课程形成。若它推进已有长期项目，则直接写入项目里程碑，不在本目录重复创建。具体要求见[课程内容规范](https://github.com/cafelemon/become_engineer/blob/main/docs/08_content_standard.md)和[练习模板](https://github.com/cafelemon/become_engineer/blob/main/templates/exercise_template.md)。

## 主线映射

每个练习应标注所属主线和适合阶段，方便从学习路线直接跳转到练习。

新学习者不要从本页任选练习，应先按[面向小白的统一学习路线](../learning-paths/beginner-roadmap.md)完成对应前置阶段。

## 已公开练习

### 通用软件工程求职训练样板

- [Python 起步机考与限时模拟](career-readiness/python-entry-machine-test.md)：原创分级题、混合题、固定输入和本地限时验收。
- [学习进度报告器项目证据问答](career-readiness/study-progress-reporter-evidence.md)：用代码、测试、失败记录和设计取舍组织项目表达。

这两项只在求职路线主动推荐，兴趣路线仍可自由访问。它们是纵向样板，不代表 AI、后端或 C++ 岗位专项已经完成。

### Python 起步

- [学习进度报告器](python-basics/study-progress-reporter/README.md)：连续整合函数、数据结构、文件与JSON、模块、异常和测试；用于验收一个可运行、可排错、可回归的小型Python程序，不作为长期项目。

### Python / C++ 双主修

- [双语言学习进度报告器](programming-languages/study-progress-reporters/README.md)：使用同一数据和行为契约对照Python类型化模块与C++ STL/CMake实现，验收容器、算法、复制边界和双语言一致性。

### CS 核心

- [可追踪数组实验](cs-core/traceable-array-lab/README.md)：使用双语言确定性契约验证数组、字符串、网格和动态容量。
- [可追踪线性结构实验](cs-core/traceable-linear-structures-lab/README.md)：使用节点所有权、LIFO、FIFO 和受控下溢验证链表、栈与队列。
- [可追踪哈希实验](cs-core/traceable-hash-lab/README.md)：使用确定性教学哈希、分离链接、负载扩容和稳定输出验证哈希与集合应用。
- [可追踪查找与排序实验](cs-core/traceable-search-sort-lab/README.md)：使用有序输入契约、确定性操作计数和带标签元素验证二分边界、基础排序与稳定归并。
- [可追踪树与遍历实验](cs-core/traceable-tree-traversal-lab/README.md)：使用槽位表示、链接所有权和确定性前沿验证递归与迭代树遍历。
- [可追踪图遍历实验](cs-core/traceable-graph-traversal-lab/README.md)：使用规范简单无向图验证邻接表示、BFS、DFS、连通分量和无向环。
- [可追踪优先队列与最短路实验](cs-core/traceable-priority-shortest-path-lab/README.md)：使用最小堆、稳定序号和懒惰重复项验证非负权 Dijkstra。
- [可追踪生成森林实验](cs-core/traceable-spanning-forest-lab/README.md)：使用路径压缩、确定性边序和割边前沿验证 DSU、Kruskal 与 Lazy Prim。

### LLM/Agent

- [安全销售查询 Tool Calling](llm-agent/safe-sales-tool-calling/README.md)：后期 LLM/Agent 阶段的加工样品；需先具备Python工程化、Web/API与数据库最小核心，再用于验证Tool Calling、参数校验、只读SQLite和错误处理。
