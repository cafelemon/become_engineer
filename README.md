# Become Engineer

Become Engineer 是一个公开学习平台项目，目标是把免费、可信、可复用的工程与 AI 学习资源整理成一套可长期维护的学习体系。

这个仓库面向公众开放，但也服务于我自己的学习。公开部分沉淀学习地图、路线、项目、资源评测、公开笔记和阶段性成果；个人学习资料放在本地 `个人学习/` 目录中，并已加入 `.gitignore`，不会进入公开仓库。

新学习者请从 [小白统一学习路线](learning-paths/beginner-roadmap.md) 开始，按阶段顺序完成前置、练习和验收。

公开网站入口规划为：https://cafelemon.github.io/become_engineer/

本仓库继续以 Markdown 作为内容源，网站由 MkDocs Material 自动生成。

## 四层结构

1. 学习地图：给出全局方向、先后顺序和能力关系。
2. 学习路线：把每条主线拆成阶段目标、前置知识和推荐路径。
3. 项目实践：用练习和项目验证是否真的掌握。
4. 资源评测：对免费资源做筛选、纠错、适用阶段和使用建议。

## 六条主线

六条主线用于组织内容，不是六条任选路线。统一顺序是：

**工程基础前置 → Python 起步 → Python/C++ 双主修 → CS 最小核心 → Web 与 CS 深化并行 → AI 基础 → LLM/Agent**

- [工程基础](learning-paths/engineering-foundation/README.md)：Git、命令行、环境、Docker最小认知、调试、测试、工程习惯、学习方法。
- [编程语言](learning-paths/programming-languages/README.md)：Python、C++ 双主修，Java 补充；JavaScript/TypeScript 在 Web 阶段进入。
- [Web 全栈](learning-paths/web-fullstack/README.md)：前端、后端、PostgreSQL/psql、MySQL对照、API、部署。
- [CS 核心](learning-paths/cs-core/README.md)：数据结构、通用算法、操作系统、网络、数据库原理、系统设计。
- [AI 基础](learning-paths/ai-foundation/README.md)：机器学习、深度学习、NLP/Transformer、强化学习等模型算法。
- [LLM/Agent](learning-paths/llm-agent/README.md)：Prompt、RAG、评估、工具调用、Agent 框架和项目实战。

## 主要入口

- [小白统一学习路线](learning-paths/beginner-roadmap.md)
- [总学习地图](maps/README.md)
- [项目主干规划](projects/project-roadmap.md)
- [素材收纳](content-inbox/README.md)
- [素材加工区](source-materials/README.md)
- [学习路线](learning-paths/README.md)
- [资源库](resources/README.md)
- [资源评测](reviews/README.md)
- [公开笔记](notes/README.md)
- [练习库](exercises/README.md)
- [项目实践](projects/README.md)
- [公开输出](publications/README.md)
- [模板库](https://github.com/cafelemon/become_engineer/tree/main/templates)

## 本地预览网站

安装文档站依赖：

```bash
pip install -r requirements.txt
```

启动本地预览：

```bash
mkdocs serve
```

生成静态网站：

```bash
mkdocs build
```

推送到 `main` 后，GitHub Actions 会自动发布到 GitHub Pages。

## 项目文档

- [项目总览](docs/00_overview.md)
- [产品需求文档](docs/01_prd.md)
- [版本规划](docs/02_roadmap.md)
- [技术架构](docs/03_architecture.md)
- [验收测试清单](docs/04_acceptance_checklist.md)
- [AI Coding 工作协议](docs/05_ai_coding_agent_guide.md)
- [进度记录](docs/06_progress.md)
- [决策记录](docs/07_decisions.md)

## 公开与私有边界

公开仓库只存放可以被他人阅读、引用、复用的内容。私人笔记、未整理草稿、账号信息、下载资料原件、带版权风险的材料和个人复盘记录都应保留在本地私有目录。

当前私有目录：

```text
个人学习/
```

从私有目录提炼出的内容，需要经过整理、去隐私、版权检查和结构化重写后，再进入 `publications/`、`notes/`、`projects/` 或 `reviews/`。
