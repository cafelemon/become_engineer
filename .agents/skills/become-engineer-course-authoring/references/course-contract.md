# Become Engineer 课程生产契约

## 目录

1. 正式课程模式
2. V2 正文结构
3. 小码数据协议
4. 迁移与兼容
5. 站点接入
6. 验证与求职输入

## 正式课程模式

| 模式 | 正文协议 | 使用条件 |
| --- | --- | --- |
| 新建 V2 | `contexts` | 新增正式课程或已明确采用新规范的内容 |
| V1 迁移到 V2 | 从 `steps` 改为 `contexts` | 连续迁移批次已经确定并完成前后回归 |
| 维护 V1 | 保留 `steps` | 修正现有课程，不扩大为结构迁移 |

知识库必须且只能包含 `steps` 或 `contexts` 之一。页面、知识库和测试集不得混用两种范围字段。

## V2 正文结构

- 顶部保留一个稳定挂载点：`<div class="be-tutor-mount" data-tutor-lesson="lesson-id" aria-hidden="true"></div>`。
- 每个语义区域同时包含相同的 `id` 与 `data-learning-context`，并使用 `data-context-type` 标记类型。
- 必需类型：`overview`、`concept`、`example`、`reproduce`、`modify`、`troubleshoot`、`project`。
- 可选类型：`deepen`、`career`。类型可以重复，不规定数量和顺序。
- 正文还必须包含完成检查、来源与版本、下一步。
- 第一屏从真实结果、问题、界面或现象进入，不使用连续任务路线开场。

## 小码数据协议

知识库位于 `site-src/data/tutor/<lesson_id>.json`，检索测试位于 `tests/tutor/<lesson_id>-search.json`。

### V1

- 知识库：`lesson + steps + cards`，卡片使用 `step_id`。
- 测试集：数组形式，条目包含 `query`、`step_id`、`expected`。
- 正式页面使用 `.be-task-step[data-step-id]`。
- 现有课程继续要求 5–7 步、至少 8 张卡、16 条问法。

### V2

- 知识库：`lesson + contexts + cards`。
- `lesson` 包含 `id`、`title`、`path`。
- `contexts[]` 包含 `id`、`type`、`title`、`anchor`，其中 `anchor` 必须为 `#<id>`。
- `cards[]` 包含 `id`、`lesson_id`、`context_id`、`question`、`aliases`、`keywords`、`diagnostic`、`hints`、`example`、`answer`、`source`、`updated_at`、`recommended`。
- `source.href` 必须指向卡片所属上下文；`hints` 至少两层。
- 测试集为 `{lesson_id, cases, unknown}`；`cases[]` 使用 `query` 和 `expected_card`。
- 每课至少 8 张审核卡、16 条问法，Top 3 不低于 80%，未知问题返回空候选。

## 迁移与兼容

- URL、`lesson_id`、导航位置和公开项目契约默认不变。
- V1 状态继续保存在 `be:tutor:v1:<lessonId>`；V2 使用 `be:tutor:v2:<lessonId>`，不复制旧提示进度。
- 浏览器只保存 `{open, levels}`，不保存原始提问。
- 迁移一课时同时替换该课页面、知识库和测试集；提交中不得留下页面与数据协议不一致的中间状态。
- 全量校验必须同时覆盖课程登记中的 V1 正式课和冻结的 V2 样板，直到正式课程全部迁移完成。

## 站点接入

- 新课更新 `site-src/data/curriculum/v2.json`、`mkdocs.yml`、课程说明、前后链接、项目线和治理状态。
- 迁移课不改变课程登记 ID、URL 和导航顺序。
- JavaScript、外部服务、硬件或浏览器运行器失效时，正文、静态图表、命令和本地复现路径仍完整。
- 外部模型调用必须离线优先、环境变量取密钥、自动测试禁用真实 API。

## 验证与求职输入

```bash
node scripts/validate_course_content_v2.cjs
node scripts/test_tutor_search.cjs
node scripts/validate_curriculum_v2.cjs
mkdocs build --strict
git diff --check
```

- 只通过 `scripts/query-recruiting-reference.mjs` 查询 V2 课程生产导出。
- 每道原创题至少使用 3 条信号和 2 个来源族，并保留原创变化、测试或评分证据。
- `high-frequency-reference` 只代表样本内跨来源重复，不代表企业官方频率或市场统计。
