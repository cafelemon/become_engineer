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

### Python 起步

- [学习进度报告器](python-basics/study-progress-reporter/README.md)：连续整合函数、数据结构、文件与JSON、模块、异常和测试；用于验收一个可运行、可排错、可回归的小型Python程序，不作为长期项目。

### LLM/Agent

- [安全销售查询 Tool Calling](llm-agent/safe-sales-tool-calling/README.md)：后期 LLM/Agent 阶段的加工样品；需先具备Python工程化、Web/API与数据库最小核心，再用于验证Tool Calling、参数校验、只读SQLite和错误处理。
