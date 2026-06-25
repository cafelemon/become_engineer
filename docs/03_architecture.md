# 技术架构

## 当前阶段

当前项目首先以 GitHub 仓库形态建设，优先沉淀 Markdown 文档、学习地图、路线索引、资源评测、公开笔记和实践项目。后续如果内容规模扩大，再考虑静态站点或学习平台应用。

## 信息架构

项目采用四层六线结构。

四层：

- `maps/`：学习地图，负责全局导航和能力关系。
- `learning-paths/`：学习路线，负责阶段拆解和学习顺序。
- `projects/`、`exercises/`：项目实践，负责验证学习成果。
- `resources/`、`reviews/`：资源事实与资源评测，负责筛选、纠错和使用建议。

六线：

- 工程基础
- 编程语言
- Web 全栈
- CS 核心
- AI 基础
- LLM/Agent

## 仓库结构

```text
become_engineer/
├── README.md
├── docs/
├── maps/
│   ├── README.md
│   └── become-engineer-map.md
├── learning-paths/
│   ├── README.md
│   ├── engineering-foundation/
│   ├── programming-languages/
│   ├── web-fullstack/
│   ├── cs-core/
│   ├── ai-foundation/
│   └── llm-agent/
├── resources/
├── reviews/
├── notes/
├── exercises/
├── projects/
├── publications/
├── templates/
└── 个人学习/
```

## 内容模块

- `maps/`：总学习地图和主线关系。
- `learning-paths/`：六条主线的路线入口和阶段规划。
- `resources/`：免费资源清单，记录事实信息。
- `reviews/`：资源评测，记录使用判断和推荐建议。
- `notes/`：公开知识笔记。
- `exercises/`：练习题、实验任务和答案提示。
- `projects/`：阶段项目与综合项目。
- `publications/`：从个人学习资料提炼出的公开输出。
- `templates/`：资源、评测、路线、项目、笔记、练习和公开化模板。

## 私有目录

```text
个人学习/
```

该目录只在本地使用，不进入公开仓库。适合存放个人草稿、下载资料、未整理想法和私人复盘。公开化时必须先删除隐私信息、版权风险内容和私人上下文，再沉淀到公开目录。

## 未来技术选型

如果 Markdown 仓库不足以承载阅读体验，可考虑：

- 静态站点：VitePress、Docusaurus、MkDocs。
- 搜索：本地静态索引或站点搜索服务。
- 数据化资源库：JSON、YAML、SQLite 或轻量 CMS。
- 自动检查：链接检查、Markdown lint、拼写检查、资源字段校验。

## 质量控制

- 每个资源条目保留来源链接。
- 每个资源评测明确适合阶段和验证状态。
- 每个学习路线必须包含可验证产出。
- 不确定内容标记为待验证。
- 明确区分原创总结、引用、翻译和个人理解。
- 对外发布前检查版权、隐私和准确性。
