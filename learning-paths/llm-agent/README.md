# LLM/Agent

## 定位

LLM/Agent 线用于学习大模型应用和智能体系统，包括 Prompt、RAG、工具调用、评估、微调、Agent 框架和真实项目交付。

本主线位于统一路线后段，不能用“会调用模型API”替代Python工程、Web/API、NLP/Transformer、评估和安全前置。

## 适合人群

- 已完成Python工程化与Web/API基础，想做LLM应用的人。
- 想理解 Agent 系统如何规划、调用工具和处理上下文的人。
- 想把 AI 能力接入真实业务或个人效率工具的人。

## 阶段划分

1. LLM 使用基础：模型能力、上下文、Prompt、结构化输出。
2. 检索与 RAG：文档加载、分块、向量检索、重排和引用。
3. 评估：检索质量、忠实度、答案质量和固定评估集。
4. 工具调用：函数调用、外部 API、权限、错误恢复。
5. Agent：状态、工作流、规划、记忆和人工确认。
6. 工程化：日志、成本、延迟、安全、部署和回滚。

## 推荐学习顺序

1. 先做简单 Prompt 和结构化输出实验。
2. 建立关键词检索基线，再做带引用的 RAG。
3. 在增加复杂能力前建立固定评估集。
4. 加入 Tool Calling、参数校验和权限边界。
5. 最后进入有界 Agent 工作流、可观测性和真实交付。

## 进入条件

- Python工程化与测试。
- HTTP、API、数据库、认证和权限。
- NLP/Transformer基本理解。
- 机器学习阶段形成的实验评估和安全意识。
- 进入本阶段后先完成检索基线、引用和固定评估集，再解锁RAG、Tool Calling与Agent项目里程碑。

详细顺序见[小白统一学习路线](../beginner-roadmap.md)。

## 项目主干

- [可评估的智能学习助手](../../projects/intelligent-learning-assistant/README.md)

当前已完成的 Tool Calling 知识单元：

- 笔记：[Tool Calling：让模型安全地使用外部能力](../../notes/llm-agent/tool-calling.md)
- 练习：[安全销售查询 Tool Calling](../../exercises/llm-agent/safe-sales-tool-calling/README.md)
- 对应项目里程碑：P5.5 Tool Calling

## 对应入口

- 资源：../../resources/README.md
- 评测：../../reviews/README.md
- 笔记：../../notes/README.md
- 练习：../../exercises/README.md
- 项目：../../projects/README.md
