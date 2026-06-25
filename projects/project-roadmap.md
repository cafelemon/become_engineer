# 项目主干规划

本项目不采用“一篇笔记对应一个项目”。项目是跨章节持续演进的学习主干，笔记负责解释并推进某个里程碑。

新学习者不应从本页选择项目。请先按[小白统一学习路线](../learning-paths/beginner-roadmap.md)完成前置，项目会在对应阶段解锁。

## 核心项目

| 解锁阶段 | 项目 | 主要知识模块 | 定位 |
| --- | --- | --- | --- |
| Python起步完成 | [Python 内容分析工具](python-content-analysis/README.md) | 工程基础、Python、数据处理 | 建立可复用的内容审计工具 |
| AI机器学习阶段 | [结构化数据机器学习系统](structured-data-ml-system/README.md) | Python、数学、机器学习、工程化 | 完成数据到推理的ML闭环 |
| AI深度学习/NLP阶段 | [文本分类模型演进](text-classification-evolution/README.md) | 机器学习、深度学习、NLP/Transformer | 在同一任务上比较模型演进 |
| AI独立进阶分支 | [强化学习控制实验](reinforcement-learning-control-lab/README.md) | Python、数学、机器学习、强化学习 | 独立验证决策学习方法 |
| LLM/Agent阶段 | [可评估的智能学习助手](intelligent-learning-assistant/README.md) | 工程、Web、LLM、RAG、Agent、评估 | 将本仓库内容构建成可验证应用 |

## 关系

- 项目 1 为后续内容生产提供工具，但不是所有项目的强制代码依赖。
- 项目 2 是项目 3 的机器学习基础。
- 项目 4 从机器学习和深度学习分支出去，不要求继续进入 LLM/Agent。
- 项目 5 依赖 Python 工程能力、Web/API 基础和 LLM 知识，不依赖强化学习。

## 高级候选

- 多模态文档理解。
- Text2SQL。
- OpenCV 视觉应用。
- 金融 AI。
- 本地模型推理、量化与 C++/llama.cpp 性能方向。

这些分支暂不进入核心顺序，也不创建空项目目录。
