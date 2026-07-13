# 验收测试清单

## 仓库初始化

- [x] 当前目录已初始化为 git 仓库。
- [x] 已连接远程仓库 `https://github.com/cafelemon/become_engineer.git`。
- [x] 默认分支名称明确。
- [x] README 能说明项目目标、范围和入口。

## 私有内容保护

- [x] `.gitignore` 已包含 `个人学习/`。
- [x] `git status` 中不出现 `个人学习/` 内部文件。
- [x] 公开文档不包含账号、密钥、私人路径或不可公开资料。
- [x] 下载的课程资料、PDF、视频和原始版权材料不进入仓库。

## 文档完整性

- [x] `docs/00_overview.md` 存在。
- [x] `docs/01_prd.md` 存在。
- [x] `docs/02_roadmap.md` 存在。
- [x] `docs/03_architecture.md` 存在。
- [x] `docs/04_acceptance_checklist.md` 存在。
- [x] `docs/05_ai_coding_agent_guide.md` 存在。
- [x] `docs/06_progress.md` 存在。
- [x] `docs/07_decisions.md` 存在。

## 四层六线结构

- [x] `maps/README.md` 存在。
- [x] `maps/become-engineer-map.md` 存在。
- [x] `content-inbox/README.md` 存在。
- [x] `content-inbox/llm-agent.md` 存在。
- [x] `source-materials/README.md` 存在。
- [x] `source-materials/raw/` 被 `.gitignore` 排除。
- [x] `source-materials/working/` 被 `.gitignore` 排除。
- [x] `source-materials/exports/` 被 `.gitignore` 排除。
- [x] `learning-paths/engineering-foundation/README.md` 存在。
- [x] `learning-paths/programming-languages/README.md` 存在。
- [x] `learning-paths/web-fullstack/README.md` 存在。
- [x] `learning-paths/cs-core/README.md` 存在。
- [x] `learning-paths/ai-foundation/README.md` 存在。
- [x] `learning-paths/llm-agent/README.md` 存在。
- [x] `reviews/README.md` 存在。
- [x] `publications/README.md` 存在。

## 模板完整性

- [x] `templates/learning_path_template.md` 存在。
- [x] `templates/track_readme_template.md` 存在。
- [x] `templates/project_template.md` 存在。
- [x] `templates/review_template.md` 存在。
- [x] `templates/personal_to_public_template.md` 存在。

## 内容质量

- [x] 每个学习主题有清晰定位。
- [x] 首个 Tool Calling 样品能追溯到内部来源清单。
- [x] 首个 Tool Calling 样品已标记所属主线和适用阶段。
- [x] 首个 Tool Calling 样品已记录待验证事实及核查结论。
- [x] 公开内容可被他人独立阅读。
- [x] 资源事实记录和资源评测判断分开存放。
- [x] 个人学习资料公开化前经过去隐私和版权检查。
- [x] Inbox 素材不保存账号、密码、token 或原始版权资料。
- [x] Source materials 原始抓取内容不进入公开仓库。

## 内容审计与项目主干

- [x] 2519 个 Markdown 页面全部分类，未分类数为 0。
- [x] 每页至少标记一个内容角色或明确暂缓。
- [x] 重复、过时和广告风险与内容角色分开记录。
- [x] 已抽样核对 `llama.cpp`、Git、RAG、OpenCV、金融和 Tool Calling 等边界案例。
- [x] 工程、数学、CS、Web 和 C++ 的来源状态与加工进度已公开说明。
- [x] 当前六条主线名称和边界保持不变。
- [x] 五个核心项目均横跨至少三个知识模块。
- [x] 项目使用里程碑关联多篇笔记，不采用一篇笔记一个项目。
- [x] 强化学习项目不是 LLM/Agent 前置。
- [x] Dify、Coze、LangChain 和 LangGraph 不分别建立项目。

## 小白统一路线

- [x] 全仓库存在唯一默认学习顺序。
- [x] 工程基础位于语言之前，并区分前置必修与项目深化。
- [x] Docker纳入工程基础最小认知，Dockerfile、compose和部署放到项目中深化。
- [x] Python先短暂起步，再与C++双主修。
- [x] Java明确为完整补充路线。
- [x] JavaScript/TypeScript主要在Web阶段进入。
- [x] CS最小核心位于Web之前。
- [x] CS算法明确为通用算法和复杂度，AI算法明确为模型算法。
- [x] 数据库路线明确PostgreSQL/psql优先、MySQL对照、SQLite仅作轻量练习或样例。
- [x] Web与CS深化明确并行。
- [x] AI位于Python、数学和评估基础之后。
- [x] LLM/Agent位于Python工程化、Web/API、检索和评估之后。
- [x] 项目入口注明解锁阶段，不向小白提前分配后期项目。
- [x] 专项素材地图不再承担学习顺序职责。
- [x] 工程基础阶段0单元1/2已作为独立课程正文落地，并包含前置、顺序、练习、错误排查、完成标准和下一步。
- [x] 工程基础阶段0单元3/4已作为独立课程正文落地，并包含前置、顺序、练习、错误排查、完成标准和下一步。
- [x] 工程基础阶段0单元5/6已作为独立课程正文落地，并包含前置、顺序、练习、错误排查、完成标准和下一步。
- [x] 工程基础阶段0单元7/8已作为独立课程正文落地，并包含前置、顺序、练习、错误排查、完成标准和下一步。
- [x] 工程基础阶段0单元9已作为独立课程正文落地，并包含前置、顺序、练习、错误排查、完成标准和下一步。
- [x] 工程基础阶段0已完成结构和连贯性检查，9个单元形成学习记录、文件、终端、编辑器、Markdown、Git、环境、Docker和验证闭环。
- [x] 工程基础阶段0已完成机器验收：课程契约、相对链接、MkDocs导航、线上页面关键内容和公开信息边界检查通过。
- [x] Python 起步入口和前两节正文已落地，并包含前置、顺序、练习、错误排查、完成标准和下一步。
- [x] Python 起步已接入开始学习和 MkDocs 导航，公开标题不使用内部编号口径。

## Tool Calling 练习

- [x] 四篇输入素材已建立来源清单和重复矩阵。
- [x] 广告、二维码、旧模型宣传和硬编码凭据未进入公开内容。
- [x] 公开笔记以当前官方文档为事实基线。
- [x] 离线模式不需要 API Key。
- [x] SQLite 查询使用只读连接和参数化 SQL。
- [x] 未提供任意 SQL 执行工具。
- [x] 正常查询、筛选、空结果、非法参数、未知工具和恶意参数测试通过。
- [x] 工具调用输出与原始 `call_id` 正确关联。
- [x] 练习已关联智能学习助手 P5.5，而不是独立项目主干。

## 发布前检查

- [x] 运行 `git status --short` 检查待提交文件。
- [x] 检查 `.gitignore` 是否正确保护私有目录。
- [x] 检查 README 链接是否有效。
- [x] 检查 docs 链接是否有效。
- [x] 检查新增地图、主线、评测、公开输出链接是否有效。
- [x] 提交前人工审阅一次公开内容。
- [ ] 工程基础阶段0正文完成后，按小白文档契约进行真实学习者实操验收。

## 文档站

- [x] 使用 MkDocs Material 作为 Markdown 公开网站外壳。
- [x] 网站配置不把 `个人学习/` 和 `source-materials/raw|working|exports/` 纳入构建。
- [x] GitHub Actions 发布到 GitHub Pages。
- [x] 首次推送后检查 `https://cafelemon.github.io/become_engineer/` 可访问。
- [x] 公开站点主导航收敛为首页、开始学习、项目、项目文档。
- [x] 页面目录已整合到左侧导航，不再作为右侧独立目录展示。
- [x] 首页和公开学习入口不再展示素材库、笔记库、资源库和内部编号口径。
