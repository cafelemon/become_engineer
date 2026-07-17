---
name: become-engineer-course-authoring
description: Create, migrate, or maintain official Become Engineer lessons using the V2 semantic learning structure, course-type templates, reproducible examples, continuous projects, and V1/V2-compatible Xiaoma tutor data. Use when adding a formal course, migrating a task-first V1 lesson, maintaining a legacy lesson without forced migration, creating tutor knowledge cards and search fixtures, or validating course content and MkDocs integration.
---

# Become Engineer 课程生产

用本 Skill 新建、迁移或维护正式课程。课程先帮助学习者看懂问题，再通过小例子、复现、修改、排错和连续项目形成能力。

## 开始前

1. 阅读 `references/course-contract.md`、`docs/08_content_standard.md`、公共课程模板、相邻课程和阶段作品。
2. 选择模式：`新建 V2 课程`、`V1 迁移到 V2` 或 `维护 V1`。
3. 选择课型，并读取 `templates/course-types/` 中唯一对应的差异模板。
4. 核对课程 URL、`lesson_id`、前置、下一课、项目线、适用版本和一手来源。
5. 迁移或维护时先记录必须保留的事实、代码输出、测试、锚点、项目接口和公开链接。

## 三种模式

### 新建 V2 课程

- 使用 `lesson + contexts + cards` 协议和语义正文锚点。
- 更新课程登记、导航、相邻链接、课程说明、项目关系、进度和验收记录。
- 不提前创建没有正文、验证和来源的空课程页。

### V1 迁移到 V2

- 保持 URL、`lesson_id`、标题事实、项目契约和既有学习成果。
- 将固定步骤重新组织为语义学习区域，不能用格式替换冒充内容修订。
- 用 V2 知识库和测试集替换该课 V1 数据；迁移前后分别运行全量兼容校验。
- 不迁移同组其他课程，除非用户明确把它们放入同一批次。

### 维护 V1

- 允许修正事实、代码、链接、错误说明和知识卡，不要求同时迁移结构。
- 保留 `steps`、`step_id`、原存储键和 5–7 步页面锚点。
- 不在一次小修中混用 `steps` 与 `contexts`。

## V2 生产流程

1. 从结果、问题、界面或现象设计第一屏，让学习者先知道为什么值得学。
2. 用 `overview`、`concept`、`example`、`reproduce`、`modify`、`troubleshoot`、`project` 组织内容；`deepen`、`career` 按需加入，不固定数量和顺序。
3. 准备可实际运行的源文件、命令、输入、输出、失败恢复和验证；正文引用真实示例，不手工维护第二份代码。
4. 把本课接入一条连续作品线，说明上一版、本课变化、涉及文件、保存结果和下一版。无法接入时给出理由和等价产出。
5. 写成“老师陪练＋简洁教材”：定义短而准，操作交代位置和变化，不写评审报告式正文，不虚构作者经历。
6. 创建 V2 小码知识库：至少 8 张审核卡、两层提示、局部例子、主动展开答案和正文来源。
7. 创建至少 16 条固定问法与自然改写；Top 3 不低于 80%，未知问题必须降级。
8. 完成来源、适用版本、核查日期、安全、隐私、版权、费用、硬件与静态降级检查。

## 求职内容

包含求职训练、深化挑战或项目证据问答时，读取 `references/recruiting-reference-v2.md`，只通过查询脚本取得脱敏能力信号。

- 不直接读取或改写 raw 外部题目。
- 原创题重新设计场景、约束、失败路径、测试与评分证据。
- 平台信号不能写成企业官方高频或真实市场统计。

## 验证

从仓库根目录执行：

```bash
node scripts/validate_course_content_v2.cjs
node scripts/test_tutor_search.cjs
node scripts/validate_curriculum_v2.cjs
mkdocs build --strict
git diff --check
```

阶段作品有代码变化时，额外执行项目自己的构建、测试和输出契约检查。完成后检查桌面、390px 手机、深浅色、键盘、减少动画和禁用 JavaScript。

## 参考资料

- `references/course-contract.md`：V1/V2 正文、助教、迁移与接入契约。
- `references/recruiting-reference-v2.md`：求职信号查询和原创边界。
- `templates/course_lesson_template.md`：V2 共同课程骨架。
- `templates/course-types/`：八类课程的差异要求。
- `docs/08_content_standard.md`：正式内容和语言规范。
