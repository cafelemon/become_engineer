# Source Materials

这里是素材二次加工区，用来保存外部原始资料的本地抓取结果、清洗中间产物和导出文件。

这个目录不是个人学习区，也不是公开展示区。它服务于内容生产流程：先把原素材拉下来，再去广告、去重、纠错、筛选项目，最后把二次加工后的内容沉淀到正式公开目录。

## 子目录

```text
source-materials/
├── raw/      # 原始抓取内容，本地保留，不入库
├── working/  # 清洗、去重、纠错过程文件，本地保留，不入库
└── exports/  # 临时导出文件，本地保留，不入库
```

## 入库规则

- `README.md` 入库，用于说明边界。
- `raw/`、`working/`、`exports/` 全部被 `.gitignore` 排除。
- 不保存账号、密码、token 或访问凭证。
- 不把广告、重复内容、未核对旧内容直接放入公开目录。
- 最终公开内容应进入 `notes/`、`projects/`、`reviews/`、`resources/` 或 `publications/`。

## 当前素材

- 《大模型全部学习笔记》2025：已完整拉取到 `raw/llm-notes-2025/`，共 2533 个节点、2519 个 Markdown 页面，失败数为 0。该目录被 `.gitignore` 排除，只作为二次加工来源。
- 完整内容审计：2519 页逐项分类、覆盖矩阵、缺口分析和抽样复核位于 `working/llm-notes-2025/content-audit/`。
- Tool Calling 样品：加工记录位于 `working/llm-notes-2025/tool-calling-sample/`，公开产物已进入 `notes/llm-agent/` 和 `exercises/llm-agent/`。
