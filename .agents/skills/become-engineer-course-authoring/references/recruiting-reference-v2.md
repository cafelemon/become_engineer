# 求职参考素材 V2 接口

只有在课程包含求职训练、深化挑战、项目证据问答或机考迁移任务时读取本参考。

## 查询入口

从仓库根目录执行：

```bash
node .agents/skills/become-engineer-course-authoring/scripts/query-recruiting-reference.mjs \
  --course python-core-07 \
  --type interview \
  --limit 12
```

也可以使用 `--stage planned-cs-core`、`--ability algorithms`、`--frequency high-frequency-reference` 组合过滤。
脚本默认把当前工作目录视为仓库根目录；从其他目录调用时使用 `--repo /absolute/path/to/become_engineer`。

查询脚本只读取本地 ignored 的 `source-materials/exports/recruiting-reference-v2/authoring-input.json`。如果文件不存在，停止求职题生产并说明需要先构建 V2；不得回退读取 raw 缓存、受限平台页面或自行猜测企业频率。

## 使用规则

- `direction-signal` 只决定是否关注，不得称为高频。
- `repeated-signal` 表示至少两个独立来源族重复。
- `high-frequency-reference` 表示至少三个独立来源族重复且包含 A 级来源，但仍不代表真实招聘市场统计。
- `core`、`recommended-deepening`、`optional-observation` 是教学优先级，不是题目出现概率。
- 每道原创题至少引用 3 条信号、覆盖 2 个来源族，并重新设计场景、输入或追问、失败路径、测试和验收证据。
- 不使用企业名称，不复制外部题面、答案、题解代码、用户面经或外部答案结构。
- 外部来源只保留在本地素材库；公开课程只写原创题、必要引用和可复现证据。

## 产出选择

- 兴趣路线：使用基础课程与深化挑战，不主动加入机考和面试训练。
- 求职路线：在课程验收之后加入机考迁移题、项目追问、故障排查或技术表达任务。
- 课程尚无足够 V2 信号时，在内容计划中登记缺口，不用通用占位题填充。
