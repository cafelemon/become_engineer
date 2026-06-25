# 技术架构

## 当前阶段

当前项目以 GitHub 仓库和 MkDocs Material 文档站并行建设。Markdown 仍是唯一内容源；MkDocs 负责把公开内容生成可搜索、可导航的静态网站。

## 信息架构

项目采用四层六线结构。

四层六线负责组织内容，[小白统一学习路线](../learning-paths/beginner-roadmap.md)负责定义唯一默认学习顺序。任何专项地图、素材目录和项目清单都不能覆盖这条顺序。

四层：

- `maps/`：学习地图，负责全局导航和能力关系。
- `content-inbox/`：素材收纳，负责登记未整理资料、处理状态和下一步动作。
- `source-materials/`：素材加工区，负责本地保存原始抓取、清洗中间产物和临时导出。
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

默认顺序：

```text
工程基础前置
  -> Python 起步
    -> Python/C++ 双主修（Java 补充）
      -> CS 最小核心
        -> Web / CS 深化并行
          -> AI 基础
            -> LLM/Agent
```

路线口径：

- 工程基础中的 Docker 先作为最小认知进入语言前阶段，复杂 Dockerfile、docker compose 和部署在项目中深化。
- CS 核心中的算法指通用算法和复杂度，不替代 AI 阶段的模型算法。
- AI 基础中的算法指机器学习、深度学习、NLP/Transformer、强化学习等模型算法。
- 数据库实践优先使用 PostgreSQL 和 `psql`，MySQL作为常见生产数据库对照；SQLite只用于轻量本地练习或特定样例。

## 仓库结构

```text
become_engineer/
├── README.md
├── docs/
├── maps/
│   ├── README.md
│   └── become-engineer-map.md
├── content-inbox/
├── source-materials/
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
- `content-inbox/`：待整理素材索引和处理队列。
- `source-materials/`：本地素材加工区；只有说明文件入库，原始内容和中间产物不入库。
- `learning-paths/`：六条主线的路线入口和阶段规划。
- `resources/`：免费资源清单，记录事实信息。
- `reviews/`：资源评测，记录使用判断和推荐建议。
- `notes/`：公开知识笔记。
- `exercises/`：练习题、聚焦实验、阶段验证和答案提示。
- `projects/`：跨多篇笔记持续演进的项目主干。
- `publications/`：从个人学习资料提炼出的公开输出。
- `templates/`：资源、评测、路线、项目、笔记、练习和公开化模板。

## 私有目录

```text
个人学习/
```

该目录只在本地使用，不进入公开仓库。适合存放个人草稿、下载资料、未整理想法和私人复盘。公开化时必须先删除隐私信息、版权风险内容和私人上下文，再沉淀到公开目录。

## 未来技术选型

当前已采用：

- 静态站点：MkDocs + Material for MkDocs。
- 部署：GitHub Actions 发布到 GitHub Pages。

后续如果内容规模继续扩大，可考虑：

- 搜索：本地静态索引或站点搜索服务。
- 数据化资源库：JSON、YAML、SQLite 或轻量 CMS。
- 自动检查：链接检查、Markdown lint、拼写检查、资源字段校验。

## 质量控制

- 每个资源条目保留来源链接。
- 每个资源评测明确适合阶段和验证状态。
- 每个学习路线必须包含可验证产出。
- 项目不得与单篇笔记机械一一对应。
- 项目通过里程碑关联多篇笔记、代码产出和验收结果。
- 项目型笔记必须说明前置知识、关联项目、当前里程碑、实际产出和基础课回链。
- 纯理论笔记可以不关联项目，但必须说明能力去向。
- 框架、平台和部署教程优先作为项目阶段或对照实验，不自动成为项目。
- 每个 inbox 素材必须标注状态、主线和下一步动作。
- 不确定内容标记为待验证。
- 明确区分原创总结、引用、翻译和个人理解。
- 对外发布前检查版权、隐私和准确性。
- 每个课程单元必须提供前置、顺序、操作、错误排查、客观验收和下一步。
- 入口文档必须引用统一路线，不能让小白自行拼装学习顺序。

## 素材与课程边界

当前来源按统一路线逐阶段加工：

- 逐页分类明细、重复候选和风险标签保存在 ignored 加工区。
- 公开端只发布能力依赖图、覆盖说明和重组后的内容。
- CS DIY、FastAPI和大模型笔记均已登记为候选来源。
- 来源已登记不等于公开课程已经完成。
- `llama.cpp`、FastAPI 部署案例或 Codex Git 案例不能替代对应基础课程。
