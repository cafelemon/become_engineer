---
name: become-engineer-course-authoring
description: Create or refactor official Become Engineer lessons into task-driven learning pages with Xiaoma tutor knowledge cards, search fixtures, and MkDocs integration. Use when adding a course, restructuring an existing lesson, expanding Xiaoma coverage, or validating a lesson's task route and tutor retrieval.
---

# Become Engineer 课程生产

用本 Skill 新建或重构正式课程。课程必须先让学习者完成一个可观察任务，再按需解释知识；小码同学只能给出已审核、可追溯的分层提示。

## 开始前

1. 阅读 `references/course-contract.md`，并读取课程模板、相邻课程、阶段作品和对应课程说明。
2. 确认本次模式：`新建正式课程` 或 `重构既有课程`。既有课程不得改变 URL；新课程必须获得稳定的文件名与 `lesson_id`。
3. 保留已有课程事实、练习、排错、来源和验收；移动到首次需要它们的任务附近，不能用摘要取代。

## 生产流程

1. 定义一条连续成果线和首次可观察结果，设计 5–7 个任务步骤。
2. 在正文顶部放置唯一的 `be-tutor-mount`，并为每个步骤放置匹配的 `be-task-step`、`id` 和 `data-step-id`。
3. 每一步写明当前任务、最少必要知识、命令或操作、预期结果、学习者主动修改和成功证据；其中至少包含一个安全的失败实验与一个不提供完整答案的迁移验收。
4. 为该课创建 `site-src/data/tutor/<lesson_id>.json`：至少 8 张任务专属卡，使用两层提示、局部示例、主动展开的答案和正文锚点来源。不得使用通用或占位提示。
5. 为该课创建 `tests/tutor/<lesson_id>-search.json`：至少 16 条标准问法和自然改写，覆盖当前任务、关键概念、主动修改、典型错误、验收和下一步。
6. 新建正式课程时，同步更新导航、课程说明、上一/下一课、阶段作品关联、学习路线及受影响的进度和验收记录；重构时保持导航与 URL 稳定。
7. 课程包含求职训练、深化挑战或项目证据问答时，阅读 `references/recruiting-reference-v2.md`，通过查询脚本取得脱敏能力信号；不得直接读取 raw 外部素材。
8. 运行本 Skill 的验证清单；失败时先修正文锚点、知识卡或测试问法，再处理视觉细节。

## 助教与内容边界

- 小码同学使用静态 JSON 和浏览器端确定性检索；不引入模型 API、账号、后端或对话保存。
- 卡片必须先帮助学习者诊断，再逐层给提示；完整解释只在学习者主动展开时出现。
- 不执行未定义行为来展示错误。对悬空引用、空指针、权限或资源类风险，使用编译诊断、受控失败、测试或安全替代方案。
- AI 可以协助提出实现与诊断候选；学习者必须解释边界、主动修改代码并运行验证。
- V2 只提供方向、高频证据和教学优先级。任何原创机考或面试任务都必须重新设计场景、失败路径、测试与验收，不能把外部信号改写成近似原题。

## 验证

从仓库根目录执行：

```bash
node scripts/test_tutor_search.cjs
mkdocs build --strict
git diff --check
```

对有阶段作品变更的课程，额外执行该作品的构建、测试和输出契约检查。完成后在桌面和手机检查任务卡、助教面板、键盘焦点、深浅色和禁用 JavaScript 的正文降级。

## 参考资料

- `references/course-contract.md`：课程、助教、数据文件和接入的完整约束。
- `references/recruiting-reference-v2.md`：求职信号查询、频率解释和原创转化边界。
- `templates/course_lesson_template.md`：可复用的正文结构。
- `docs/08_content_standard.md`：课程内容规范与来源要求。
