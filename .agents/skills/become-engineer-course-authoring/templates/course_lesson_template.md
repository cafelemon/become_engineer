# V2 正式课程共同骨架

创建正文时以仓库根目录 `templates/course_lesson_template.md` 为完整起点，并遵守以下不可省略项：

- 顶部唯一 `be-tutor-mount` 和稳定 `lesson_id`。
- `overview`、`concept`、`example`、`reproduce`、`modify`、`troubleshoot`、`project` 七类语义区域。
- 第一屏从结果、问题、界面或现象进入。
- 可实际复现的源文件、环境、命令、输入、输出和失败恢复。
- 学习者主动修改，而不是只复制示例。
- 连续项目关系；无法接入时提供理由和等价产出。
- 完成检查、来源、适用版本、核查日期和下一步。

然后只读取一个课型差异模板：

- `course-types/tool-operation.md`
- `course-types/programming-start.md`
- `course-types/cs-concept.md`
- `course-types/algorithm-data-structure.md`
- `course-types/system-device.md`
- `course-types/ai-experiment.md`
- `course-types/web-llm-agent.md`
- `course-types/project-integration.md`

不要把课型模板复制成八份完整正文。共同骨架负责一致性，课型模板只决定开场、视觉、运行方式、失败设计和项目结果。
