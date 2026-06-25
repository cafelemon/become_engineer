# 技术架构

## 当前阶段

当前项目首先以 GitHub 仓库形态建设，优先沉淀 Markdown 文档、资源索引、学习路线和实践任务。后续如果内容规模扩大，再考虑静态站点或学习平台应用。

## 仓库结构草案

```text
become_engineer/
├── README.md
├── docs/
│   ├── 00_overview.md
│   ├── 01_prd.md
│   ├── 02_roadmap.md
│   ├── 03_architecture.md
│   ├── 04_acceptance_checklist.md
│   ├── 05_ai_coding_agent_guide.md
│   ├── 06_progress.md
│   └── 07_decisions.md
├── learning-paths/
├── resources/
├── notes/
├── exercises/
├── projects/
└── templates/
```

## 内容模块

- `learning-paths/`：学习路线，按方向和阶段组织。
- `resources/`：免费资源清单与评估。
- `notes/`：公开知识笔记。
- `exercises/`：练习题、实验任务和答案提示。
- `projects/`：阶段项目与综合项目。
- `templates/`：资源条目、笔记、练习、复盘等模板。

## 私有目录

```text
个人学习/
```

该目录只在本地使用，不进入公开仓库。适合存放个人草稿、下载资料、未整理想法和私人复盘。

## 未来技术选型

如果 Markdown 仓库不足以承载阅读体验，可考虑：

- 静态站点：VitePress、Docusaurus、MkDocs。
- 搜索：本地静态索引或站点搜索服务。
- 数据化资源库：JSON、YAML、SQLite 或轻量 CMS。
- 自动检查：链接检查、Markdown lint、拼写检查、资源字段校验。

## 质量控制

- 每个资源条目保留来源链接。
- 每个结论尽量标注依据。
- 不确定内容标记为待验证。
- 明确区分原创总结、引用、翻译和个人理解。
- 对外发布前检查版权、隐私和准确性。
