<div class="be-page-hero be-map-hero" markdown>

<span class="be-page-eyebrow">唯一公开课程控制面 · V2</span>

# 完整课程地图

四类学习者共享同一棵能力树：**小白／有基础决定从哪里开始和补什么，兴趣／求职决定是否叠加机考、项目证据与面试训练**。本页同时展示目标架构、当前建设状态和衔接缺口；标记为“规划”的模块并不代表已经开放。

<div class="be-page-actions" markdown>

[开始学习](beginner-roadmap.md){ .md-button .md-button--primary }
[让小码规划路线](../README.md#learning-assessment){ .md-button }
[直接看 55 节明细](#opened-lessons){ .md-button }

</div>

</div>

## 怎样读这张地图

<div class="be-curriculum-legend" aria-label="课程地图图例">
  <div><strong>六级深度</strong><span>起步 → 基础 → 核心 → 工程化 → 深化 → 专业/求职</span></div>
  <div><strong>模块角色</strong><span>共同基座 · 方向主干 · 能力深化 · 求职叠加</span></div>
  <div><strong>内容状态</strong><span class="be-status" data-status="open">已开放</span><span class="be-status" data-status="relevel">已开放待重分层</span><span class="be-status" data-status="building">建设中</span><span class="be-status" data-status="planned">已规划未建设</span></div>
  <div><strong>衔接状态</strong><span>可顺序进入 · 缺少起步层 · 等待前置 · 方向可选</span></div>
</div>

当前正式课程共 **55 节**：工程基础 10 节、Python 起步 7 节、CS 起步 4 节、Python 核心与工程化 7 节、C++ 起步 2 节、C++ 核心 3 节、算法基础与核心 22 节。课程 URL 没有改变；目录已经按目标层级重排，正文按迁移台账分批升级。

## 四类用户共用一棵能力树

<div class="be-profile-route-table" markdown>

| 用户画像 | 起点与补修 | 共同内容 | 兴趣／方向内容 | 求职叠加 |
| --- | --- | --- | --- | --- |
| 小白 · 兴趣学习 | 从工程基础开始 | 完成共同基座 | 按兴趣选择应用、系统、算法、AI、LLM/Agent 或设备方向 | 默认不加入 |
| 有基础 · 兴趣学习 | 从首个未证明掌握的缺口开始 | 已掌握内容可以收起，缺口必须补 | 优先进入方向核心、深化和兴趣项目 | 默认不加入 |
| 小白 · 转行求职 | 从工程基础开始 | 完成共同基座 | 先建立方向能力和可验证项目 | 阶段验收后逐步加入机考、项目证据和面试训练 |
| 有基础 · 强化求职 | 补具体缺口，不按一个总分退回起点 | 保留必要前置 | 进入方向核心与深化 | 同步加入限时题、故障复盘、项目追问和岗位专项 |

</div>

个性化只改变推荐、显示顺序和训练包，不复制课程正文，也不限制搜索或直接访问。现有测评 V1 暂不消费本页的新关系；导航迁移会在地图验收后单独规划。

## 可点击状态流程图

流程按“共同基座 → 方向分流 → 跨线汇合”阅读。每个节点都可跳到下方总表；手机端自动改为纵向分组。

<div class="be-architecture-flow">
  <section class="be-flow-foundation" aria-labelledby="flow-foundation-title">
    <h3 id="flow-foundation-title">所有学习者的共同基座</h3>
    <div class="be-flow-sequence">
      <a href="#module-engineering-start" data-status="open"><strong>工程基础起步</strong><small>已开放 · 可顺序进入</small></a>
      <span aria-hidden="true">→</span>
      <a href="#module-python-start" data-status="open"><strong>Python 编程起步</strong><small>已开放 · 可顺序进入</small></a>
      <span aria-hidden="true">→</span>
      <a href="#module-cs-start" data-status="relevel"><strong>CS 起步</strong><small>现有内容待重分层 · 缺起步层</small></a>
      <span aria-hidden="true">→</span>
      <a href="#module-direction-choice" data-status="building"><strong>首个可验证项目</strong><small>建设中 · 完成后选择方向</small></a>
    </div>
  </section>

  <div class="be-flow-branch-label"><span>满足共同前置后分流</span></div>

  <div class="be-flow-branches">
    <section>
      <h3>应用工程</h3>
      <a href="#module-python-core" data-status="open">Python 核心</a>
      <a href="#module-python-engineering" data-status="open">Python 工程化</a>
      <a href="#module-web-start" data-status="planned">Web 起步</a>
      <a href="#module-web-core" data-status="planned">Web 核心</a>
      <a href="#module-web-engineering" data-status="planned">Web 工程化</a>
    </section>
    <section>
      <h3>系统工程</h3>
      <a href="#module-cpp-start" data-status="relevel">C++ 起步 · 待迁移</a>
      <a href="#module-cpp-core" data-status="relevel">C++ 核心 · 待重分层</a>
      <a href="#module-cs-systems-core" data-status="planned">CS 系统核心</a>
      <a href="#module-systems-engineering" data-status="planned">并发、网络与性能</a>
    </section>
    <section>
      <h3>算法</h3>
      <a href="#module-algorithm-foundation" data-status="relevel">共同算法基础</a>
      <a href="#module-algorithm-core" data-status="relevel">算法核心</a>
      <a href="#module-algorithm-deepening" data-status="planned">算法深化</a>
      <a href="#module-career-algorithm" data-status="building">求职：机考与复盘</a>
    </section>
    <section>
      <h3>AI 模型</h3>
      <a href="#module-ai-math-data" data-status="planned">数学、数据与实验</a>
      <a href="#module-machine-learning" data-status="planned">机器学习</a>
      <a href="#module-deep-learning" data-status="planned">深度学习</a>
      <a href="#module-reinforcement-learning" data-status="planned">强化学习</a>
      <a href="#module-vision" data-status="planned">视觉 / NLP / 多模态</a>
    </section>
    <section>
      <h3>LLM 应用</h3>
      <a href="#module-llm-use" data-status="planned">模型使用与结构化输出</a>
      <a href="#module-llm-rag-eval" data-status="planned">检索、RAG 与评估</a>
      <small>不要求先完成完整机器学习与深度学习</small>
    </section>
    <section>
      <h3>Agent 工程</h3>
      <a href="#module-agent-tool-calling" data-status="planned">Tool Calling 与有界工作流</a>
      <a href="#module-agent-engineering" data-status="planned">状态、恢复、评估与安全</a>
      <a href="#module-agent-specialized" data-status="planned">专业 Agent</a>
      <small>微调、本地推理、多模态 Agent 再追加模型或系统前置</small>
    </section>
    <section>
      <h3>设备系统</h3>
      <a href="#module-c-start" data-status="planned">C 语言起步</a>
      <a href="#module-device-foundation" data-status="planned">设备共同基础</a>
      <a href="#module-mcu-rtos" data-status="planned">MCU / RTOS</a>
      <a href="#module-linux-bsp" data-status="planned">Linux / BSP</a>
      <a href="#module-industrial-control" data-status="planned">工业控制</a>
    </section>
  </div>

  <section class="be-flow-merges" aria-labelledby="flow-merges-title">
    <h3 id="flow-merges-title">跨方向汇合</h3>
    <a href="#module-edge-ai" data-status="planned"><strong>设备平台 + AI 模型 → 边缘智能</strong><small>AI 基础与 MCU/RTOS 或 Linux/BSP 同时满足</small></a>
    <a href="#module-intelligent-control" data-status="planned"><strong>设备平台 + 强化学习 → 智能控制</strong><small>强化学习不是边缘智能的通用前置</small></a>
    <a href="#module-agent-advanced" data-status="planned"><strong>Agent 工程 + 模型／系统能力 → 高级 Agent</strong><small>微调、本地推理和多模态按实际方向追加前置</small></a>
  </section>
</div>

## 阶段总表

表中“关键产出”描述验收方向，不代表已经存在对应课程。`A`=小白兴趣，`B`=有基础兴趣，`C`=小白求职，`D`=有基础求职。

<div class="be-curriculum-v2-table" markdown>

| 模块 | 深度 | 角色 | 关键产出 | 前置 → 解锁 | 四类用户规则 | 内容状态 | 衔接状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <span id="module-engineering-start">工程基础起步</span> | 起步 | 共同基座 | 可复现本地学习工作区 | 无 → Python 起步 | A/C 完整；B/D 按缺口补修 | 已开放 | 可顺序进入 |
| <span id="module-python-start">Python 编程起步</span> | 起步 | 共同基座 | 可运行、可测试的小程序 | 工程基础 → CS 起步、Python 核心 | 四类共用；有基础者可测评跳过 | 已开放 | 可顺序进入 |
| <span id="module-cs-start">CS 起步</span> | 起步 | 共同基座 | 能描述表示、复杂度与边界 | Python 起步 → 算法基础、方向选择 | 四类共用；当前课程需重组出真正起步层 | 已开放待重分层 | 缺少起步层 |
| <span id="module-direction-choice">首个可验证项目与方向选择</span> | 基础 | 共同基座 | 第一份代码、测试、说明和复盘证据 | CS 起步 → 各方向 | 四类都完成；求职画像追加项目表达 | 建设中 | 等待前置 |
| <span id="module-python-core">Python 核心</span> | 核心 | 方向主干 | 类型、协议、数据模型与资源边界 | Python 起步 → Python 工程化 | 应用、AI、LLM 方向优先 | 已开放 | 方向可选 |
| <span id="module-python-engineering">Python 工程化</span> | 工程化 | 方向主干 | 可安装包、CLI、配置和诊断 | Python 核心 → Web、LLM 应用 | 应用、AI、LLM 方向优先；求职追加证据问答 | 已开放 | 可顺序进入 |
| <span id="module-web-start">Web 起步</span> | 起步 | 方向主干 | 浏览器到本地 API 的首次闭环 | Python 起步 → Web 核心 | 应用与 LLM 路线进入 | 已规划未建设 | 方向可选 |
| <span id="module-web-core">Web 核心</span> | 核心 | 方向主干 | 前后端、数据库与 API 契约 | Web 起步 + Python 工程化 → Web 工程化 | 应用与 LLM 路线进入 | 已规划未建设 | 等待前置 |
| <span id="module-web-engineering">Web 工程化</span> | 工程化 | 能力深化 | 测试、认证、发布与可观测应用 | Web 核心 → RAG/Agent | 兴趣按项目选；求职路线重点 | 已规划未建设 | 等待前置 |
| <span id="module-cpp-start">C++ 起步</span> | 起步 | 方向主干 | 从源码、编译到首次运行和函数组织 | 方向选择 → C++ 核心 | 系统、性能、设备方向进入 | 已开放待重分层 | 可顺序进入 |
| <span id="module-cpp-core">C++ 核心</span> | 核心 | 方向主干 | 多文件构建、STL、生命周期与 RAII | C++ 起步 → 系统工程、设备基础 | 系统方向主干；其他方向可选 | 已开放待重分层 | 等待前置 |
| <span id="module-systems-engineering">系统编程、并发、网络与性能</span> | 工程化 | 能力深化 | 可诊断的系统程序与性能证据 | C++ 核心 + CS 系统核心 → 设备／高级 Agent | 系统和设备路线重点；求职叠加故障题 | 已规划未建设 | 等待前置 |
| <span id="module-algorithm-foundation">共同算法基础</span> | 基础 | 共同基座 | 常用结构、查找排序、递归、BFS/DFS 与边界测试 | CS 起步 → 算法核心 | 四类共用，深度可按测评调整 | 已开放待重分层 | 可顺序进入 |
| <span id="module-algorithm-core">算法核心</span> | 核心 | 方向主干 | 动态结构、堆、最短路、并查集和生成树 | 算法基础 → 深化／机考 | 算法兴趣或求职进入 | 已开放待重分层 | 方向可选 |
| <span id="module-algorithm-deepening">算法深化</span> | 深化 | 能力深化 | 双指针、窗口、前缀和、单调结构、回溯、贪心、DP、高阶图与字符串 | 算法核心 → 专项 | 兴趣按方向选；求职按岗位权重选 | 已规划未建设 | 方向可选 |
| <span id="module-career-algorithm">机考、限时模拟与复盘</span> | 专业/求职 | 求职叠加 | 固定输入输出、测试、限时记录和错因复盘 | 算法基础／核心 → 岗位专项 | 仅 C/D 默认叠加 | 建设中 | 方向可选 |
| <span id="module-cs-systems-core">操作系统、网络与数据库核心</span> | 核心 | 方向主干 | 进程、内存、协议、关系模型与事务实验 | CS 起步 → 系统工程、Web 核心 | 四类按方向进入；不是算法起步前置 | 已规划未建设 | 等待前置 |
| <span id="module-ai-math-data">数学、数据与可复现实验</span> | 基础 | 方向主干 | 数据处理、实验设计、指标与基线 | Python 工程化 + 算法基础 → ML | AI 模型路线共用 | 已规划未建设 | 等待前置 |
| <span id="module-machine-learning">机器学习</span> | 核心 | 方向主干 | 可复现训练、验证和误差分析 | 数学数据实验 → 深度学习 | AI 模型路线共用 | 已规划未建设 | 等待前置 |
| <span id="module-deep-learning">深度学习</span> | 核心 | 方向主干 | 神经网络训练、调试和评估 | 机器学习 → RL／视觉／NLP／多模态 | AI 模型路线进入；LLM 应用不强制 | 已规划未建设 | 等待前置 |
| <span id="module-reinforcement-learning">强化学习</span> | 专业/求职 | 能力深化 | 策略、价值、环境与控制实验 | 深度学习 → 智能控制 | 专业方向可选 | 已规划未建设 | 方向可选 |
| <span id="module-vision">计算机视觉</span> | 专业/求职 | 能力深化 | 视觉数据、模型、评估与部署证据 | 深度学习 → 边缘视觉／多模态 Agent | 专业方向可选 | 已规划未建设 | 方向可选 |
| <span id="module-nlp-transformer">NLP 与 Transformer</span> | 深化 | 能力深化 | 文本任务、Transformer 与评估 | 深度学习 → 模型型 Agent | 模型方向可选；不是应用 Agent 通用前置 | 已规划未建设 | 方向可选 |
| <span id="module-multimodal">多模态与其他 AI 专业方向</span> | 专业/求职 | 能力深化 | 多模态或专项模型项目 | 深度学习 → 高级 Agent | 专业方向可选 | 已规划未建设 | 方向可选 |
| <span id="module-llm-use">模型使用与结构化输出</span> | 基础 | 方向主干 | 可验证的模型调用、Schema 与失败处理 | Python 工程化 + Web/API → RAG | LLM 应用路线进入；不强制 ML/DL | 已规划未建设 | 等待前置 |
| <span id="module-llm-rag-eval">检索、RAG 与评估</span> | 工程化 | 方向主干 | 有引用、固定评估集和可观测失败的 RAG | 模型使用 + Web 工程化 → Agent | LLM/Agent 路线共用 | 已规划未建设 | 等待前置 |
| <span id="module-agent-tool-calling">Tool Calling 与有界工作流</span> | 基础 | 方向主干 | 可停止、可验收的工具工作流 | RAG 与评估 → Agent 工程 | Agent 路线进入 | 已规划未建设 | 等待前置 |
| <span id="module-agent-engineering">状态、记忆、上下文、恢复、评估、可观测性与安全</span> | 工程化 | 方向主干 | 可恢复、可评估、可观测的 Agent | Tool Calling → 专业 Agent | Agent 路线共用；求职追加系统设计追问 | 已规划未建设 | 等待前置 |
| <span id="module-agent-specialized">专业 Agent</span> | 专业/求职 | 能力深化 | Coding、Research、Text2SQL 等领域项目 | Agent 工程 → 领域交付 | 按兴趣或岗位选择 | 已规划未建设 | 方向可选 |
| <span id="module-agent-advanced">微调、本地推理与多模态 Agent</span> | 专业/求职 | 能力深化 | 模型或系统边界明确的高级 Agent | Agent 工程 + DL／Transformer／系统能力 | 只在实际需求满足时进入 | 已规划未建设 | 等待前置 |
| <span id="module-c-start">C 语言起步</span> | 起步 | 方向主干 | 编译、指针、内存与硬件接口基础 | 方向选择 → 设备共同基础 | 仅设备方向进入 | 已规划未建设 | 方向可选 |
| <span id="module-device-foundation">设备系统共同基础</span> | 基础 | 方向主干 | 交叉编译、链接、接口、调试、实时性与可靠性 | C 起步 + C++ 核心 + CS 系统核心 → 三平台线 | 设备方向共用 | 已规划未建设 | 等待前置 |
| <span id="module-mcu-rtos">MCU / RTOS</span> | 核心 | 能力深化 | 外设、任务、同步、内存、看门狗与功耗证据 | 设备基础 → 边缘 AI／智能控制 | 设备专业可选 | 已规划未建设 | 方向可选 |
| <span id="module-linux-bsp">嵌入式 Linux / BSP</span> | 核心 | 能力深化 | 启动链、设备树、驱动、移植与性能证据 | 设备基础 → 边缘 AI／智能控制 | 设备专业可选 | 已规划未建设 | 方向可选 |
| <span id="module-industrial-control">工业控制与实时通信</span> | 专业/求职 | 能力深化 | 实时通信、控制链路和故障恢复证据 | 设备基础 → 智能控制 | 设备专业可选 | 已规划未建设 | 方向可选 |
| <span id="module-edge-ai">边缘智能 / 嵌入式 AI</span> | 专业/求职 | 能力深化 | 板端推理的延迟、内存、功耗、精度与恢复证据 | ML + MCU/RTOS 或 Linux/BSP | AI 与设备交叉方向 | 已规划未建设 | 等待前置 |
| <span id="module-intelligent-control">智能控制实验</span> | 专业/求职 | 能力深化 | 强化学习策略与真实／仿真设备闭环证据 | RL + 任一设备平台 | 控制交叉方向 | 已规划未建设 | 等待前置 |

</div>

## 已开放课程明细 { #opened-lessons }

以下 **55 节课程各出现一次**。`待重分层` 表示正文可以访问，但它在新能力树中的层级或前置尚需调整，不表示课程被删除。

### 工程基础起步 · 10 节

1. [学习方法](engineering-foundation/stage-0/01-learning-method.md) · 已开放
2. [文件系统](engineering-foundation/stage-0/02-filesystem.md) · 已开放
3. [终端与 Shell](engineering-foundation/stage-0/03-terminal-shell.md) · 已开放
4. [编辑器：从安装 VS Code 开始](engineering-foundation/stage-0/04-editor.md) · 已开放
5. [Markdown](engineering-foundation/stage-0/05-markdown.md) · 已开放
6. [本地 Git 与 .gitignore](engineering-foundation/stage-0/06-git.md) · 已开放
7. [GitHub 远程协作：remote、push 与 clone](engineering-foundation/stage-0/06-github-remote.md) · 已开放
8. [开发环境](engineering-foundation/stage-0/07-development-environment.md) · 已开放
9. [Docker最小认知](engineering-foundation/stage-0/08-docker-basics.md) · 已开放
10. [验证习惯](engineering-foundation/stage-0/09-validation-habit.md) · 已开放

### Python 编程起步 · 7 节

1. [变量、基本类型、输入输出](programming-languages/python-basics/01-variables-types-io.md) · 已开放
2. [条件、循环、布尔逻辑](programming-languages/python-basics/02-conditions-loops-boolean.md) · 已开放
3. [函数、参数、返回值和作用域](programming-languages/python-basics/03-functions-parameters-returns-scope.md) · 已开放
4. [字符串、列表、字典、集合和元组](programming-languages/python-basics/04-strings-collections.md) · 已开放
5. [文件、路径、JSON 和简单目录操作](programming-languages/python-basics/05-files-json-paths.md) · 已开放
6. [模块、导入和虚拟环境](programming-languages/python-basics/06-modules-imports-venv.md) · 已开放
7. [异常、基本调试和最小自动化测试](programming-languages/python-basics/07-errors-debugging-tests.md) · 已开放

### Python 核心与工程化 · 7 节

1. [类型提示、接口与静态检查认知](programming-languages/python-core/01-type-hints-interfaces-static-checking.md) · 核心 · 已开放
2. [可维护函数接口、协议与模块边界](programming-languages/python-core/02-maintainable-function-interfaces-protocols-modules.md) · 核心 · 已开放
3. [Python 容器协议、迭代器与生成器](programming-languages/python-core/03-iterables-iterators-generators.md) · 核心 · 已开放
4. [Python 数据模型、数据类与上下文管理](programming-languages/python-core/04-data-model-dataclasses-context-managers.md) · 核心 · 已开放
5. [Python 装饰器、闭包与自定义上下文管理器](programming-languages/python-core/05-decorators-closures-custom-context-managers.md) · 核心 · 已开放
6. [Python 包结构、可安装入口与 CLI](programming-languages/python-core/06-package-structure-installable-cli.md) · 工程化 · 已开放
7. [Python TOML 配置、日志与可诊断执行契约](programming-languages/python-core/07-toml-configuration-logging-diagnostics.md) · 工程化 · 已开放

### C++ 起步 · 2 节

> 现有前两课正式归入 C++ 起步。页面可以访问，正文仍按 V2 迁移台账升级，因此标为“已开放待重分层”。

1. [从源文件到可执行程序：编译、类型与输入输出](programming-languages/cpp-core/01-build-types-io.md) · 待重分层
2. [函数、声明与程序组织](programming-languages/cpp-core/02-functions-declarations-program-organization.md) · 待重分层

### C++ 核心 · 3 节

1. [头文件、源文件与最小 CMake 工程](programming-languages/cpp-core/03-headers-sources-cmake.md) · 待重分层
2. [C++ STL 容器、迭代器与基础算法](programming-languages/cpp-core/04-stl-containers-iterators-algorithms.md) · 待重分层
3. [C++ 对象、引用、指针、生命周期与 RAII](programming-languages/cpp-core/05-objects-references-pointers-lifetime-raii.md) · 待重分层

### CS 起步 · 4 节

> 这四课已经归入 CS 起步。当前正文仍更接近“用实现理解表示与边界”，迁移后会从 Python 学习者已经见过的数据和操作开始。

1. [序列接口、数组表示与安全边界](cs-core/01-sequence-interface-array-representation-boundaries.md) · 待重分层
2. [操作计数、增长率与渐近复杂度](cs-core/02-operation-count-growth-asymptotic-complexity.md) · 待重分层
3. [字符串、UTF-8 字节与码点边界](cs-core/03-string-utf8-byte-code-point-boundaries.md) · 待重分层
4. [二维网格、行优先布局与坐标边界](cs-core/04-two-dimensional-grid-row-major-layout.md) · 待重分层

### 共同算法与数据结构基础 · 16 节

1. [动态数组容量、扩容成本与摊还分析](cs-core/05-dynamic-array-capacity-amortized-cost.md) · 待重分层
2. [单链表、节点链接与所有权](cs-core/06-singly-linked-list-nodes-ownership.md) · 待重分层
3. [栈、LIFO 接口与空栈边界](cs-core/07-stack-lifo-interface-underflow.md) · 待重分层
4. [队列、FIFO 与首尾不变量](cs-core/08-queue-fifo-head-tail-invariants.md) · 待重分层
5. [哈希函数、键相等与冲突](cs-core/09-hash-function-key-equality-collisions.md) · 待重分层
6. [分离链接、负载因子与扩容](cs-core/10-separate-chaining-load-factor-rehash.md) · 待重分层
7. [集合去重、频次映射与稳定输出](cs-core/11-set-frequency-map-deterministic-output.md) · 待重分层
8. [有序查找、半开区间与左右边界](cs-core/12-ordered-search-half-open-boundaries.md) · 待重分层
9. [插入排序、选择排序与稳定性](cs-core/13-insertion-selection-sort-stability.md) · 待重分层
10. [自底向上归并排序与稳定复杂度](cs-core/14-bottom-up-merge-sort-stable-complexity.md) · 待重分层
11. [二叉树形状、链接所有权与槽位表示](cs-core/15-binary-tree-shape-linked-ownership.md) · 待重分层
12. [递归深度优先遍历、基线条件与调用深度](cs-core/16-recursive-dfs-traversal-call-frames.md) · 待重分层
13. [迭代 DFS、BFS 与层级前沿](cs-core/17-iterative-dfs-bfs-frontier-levels.md) · 待重分层
14. [简单无向图、邻接表示与输入边界](cs-core/18-undirected-graph-adjacency-representations.md) · 待重分层
15. [BFS、无权距离与最短路径](cs-core/19-bfs-unweighted-distances-shortest-paths.md) · 待重分层
16. [DFS、连通分量与无向环检测](cs-core/20-dfs-connected-components-undirected-cycles.md) · 待重分层

### 算法核心 · 6 节

1. [二叉最小堆、隐式树与堆不变量](cs-core/21-binary-min-heap-implicit-tree-invariant.md) · 待重分层
2. [稳定优先队列、同优先级顺序与下溢](cs-core/22-stable-priority-queue-tie-order-underflow.md) · 待重分层
3. [带权图松弛、Dijkstra 与过期队列项](cs-core/23-weighted-relaxation-dijkstra-stale-entries.md) · 待重分层
4. [并查集、按大小合并与路径压缩](cs-core/24-disjoint-set-union-path-compression.md) · 待重分层
5. [Kruskal、环检测与最小生成森林](cs-core/25-kruskal-minimum-spanning-forest.md) · 待重分层
6. [Lazy Prim、割边前沿与过期边](cs-core/26-lazy-prim-cut-frontier-stale-edges.md) · 待重分层

## 规划模块边界

以下只登记稳定模块，不提前虚构课名和课数：

- **共同基座缺口**：CS 起步正文迁移、首个可验证项目与方向选择。
- **应用工程**：Web 起步、Web 核心、Web 工程化。
- **系统工程**：C++ 起步与核心正文迁移，操作系统／网络／数据库核心，系统编程、并发、网络与性能。
- **算法**：算法深化，以及只对求职画像默认叠加的机考、限时模拟与复盘。
- **AI 模型**：数学数据实验、机器学习、深度学习，再分强化学习、视觉、NLP/Transformer、多模态等方向。
- **LLM 应用**：模型使用与结构化输出、检索、RAG 与评估；它与 AI 模型相邻但不是同一条线。
- **Agent 工程**：Tool Calling、有界工作流、状态／记忆／上下文／恢复／评估／可观测性／安全，再进入专业 Agent。
- **设备系统**：C 起步、设备共同基础、MCU/RTOS、Linux/BSP、工业控制；与 AI 或强化学习汇合后进入边缘智能或智能控制。

## 接下来怎么推进

1. 目录和逐课迁移台账已经采用同一分层，课程 URL 保持不变。
2. 先迁移工程基础与 Python 起步，再把 CS 前四课改成真正的小白入口。
3. 完成共同基座和首个方向项目后，分别进入 Python、C++、算法及后续方向。
4. 每迁移一节正式课程，同时更新正文、知识库、测试、项目关系、课程登记和公开状态；禁止只改页面标题。

设备方向的硬件门槛与三级出口见[设备系统与边缘智能](device-edge-systems/README.md)。公开课程登记的机器可校验版本位于 `site-src/data/curriculum/v2.json`，但学习者只需要使用本页。
