# Become Engineer 课程生产契约

## 正式课程

- 正文位于四个正式课程目录之一；文件名使用两位顺序号。
- 每课包含一个稳定 `lesson_id`、5–7 个 `step-N` 任务锚点和一个顶部助教挂载点。
- 任务路线必须覆盖首次成功、主动修改、失败/排错和迁移验收；正文保留来源、完成标准和下一步。
- 新课接入 `mkdocs.yml`、课程 README、前后课程、阶段作品及受影响的路线、进度与验收文档。

## 小码同学数据

- 知识库：`site-src/data/tutor/<lesson_id>.json`。
- 检索测试：`tests/tutor/<lesson_id>-search.json`。
- 最低门槛：8 张卡、16 条测试问法、5–7 步、Top 3 命中率至少 80%。
- 每张卡包含唯一 ID、课程/步骤 ID、问题、别名、关键词、诊断问题、两层提示、局部示例、可选答案、来源锚点和核查日期。
- 测试问法的步骤和预期卡片必须存在；未知问题必须返回空候选并由界面降级。

## 验证入口

```bash
node scripts/test_tutor_search.cjs
mkdocs build --strict
git diff --check
```

阶段作品有代码变化时，使用该作品 README 中的构建和测试命令，并验证公开输出契约保持稳定。

## 求职训练输入

- 只通过 `scripts/query-recruiting-reference.mjs` 查询 V2 课程生产导出，不读取 raw 缓存或受限平台正文。
- 每道原创题至少使用 3 条信号和 2 个来源族，保留信号 ID、原创变化、测试或评分证据。
- `high-frequency-reference` 只是样本内跨来源重复，不得写成企业官方高频或市场统计。
- 素材信号不能直接成为课程正文；发布前必须完成原创场景、主动修改、失败路径和迁移验收。
