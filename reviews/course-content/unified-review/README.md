# 十三个样板统一评审

<section class="be-unified-hero" markdown="1">

<span class="be-unified-kicker">跨方向统一评审 · 已通过</span>

## 十三个样板已经成为同一套课程生产基线

共同入口、系统算法设备、Web 与智能方向已经完成统一检查：共同语义骨架写入正式规范，课型差异保留，生产链缺口进入 V2 固化结果。

<div class="be-unified-actions" markdown="1">
[查看候选统一基线](baseline-candidate.md){ .md-button .md-button--primary }
[查看差异与后续修订](gap-register.md){ .md-button }
</div>

</section>

## 先看三个结论

<div class="be-unified-summary-grid">
  <article>
    <span>01</span>
    <strong>共同骨架已经稳定</strong>
    <p>十三页都能找到理解、例子、复现、修改、排错和项目连接，但不需要固定章节数量。</p>
  </article>
  <article>
    <span>02</span>
    <strong>八类课不能写成一种课</strong>
    <p>工具课看界面，算法课看状态，设备课看时序，AI 课看数据和评估；统一的是学习闭环，不是排版。</p>
  </article>
  <article>
    <span>03</span>
    <strong>生产链已经收口</strong>
    <p>正式运行时同时兼容旧步骤课程和新语义课程，统一校验覆盖两类内容。</p>
  </article>
</div>

## 八类课型，十三个样板

| 课型 | 本轮代表样板 | 主要观察点 |
| --- | --- | --- |
| 工具操作 | [VS Code](../batch-a/vscode-workspace.md) | 能否看见入口、界面变化和走错后的恢复方式 |
| 编程起步 | [Python](../batch-a/python-variables.md) · [C++](../batch-b/cpp-build.md) · [C](../batch-b/c-memory.md) | 小例子是否足够短，第一次运行是否顺畅 |
| CS 概念 | [数据表示](../batch-a/cs-data-representation.md) | 是否从具体值和操作进入抽象，而不是先背定义 |
| 算法与数据结构 | [BFS](../batch-b/bfs-shortest-path.md) | 人工推理、状态轨迹、实现和复杂度是否接得起来 |
| 系统与设备 | [RAII](../batch-b/cpp-raii.md) · [GPIO](../batch-b/gpio-interrupts.md) | 生命周期、时序、失败和仿真／真机边界是否清楚 |
| AI 实验 | [训练与验证](../batch-c/ai-reproducible-experiment.md) | 数据、基线、指标、错误样本和复现是否完整 |
| Web／LLM／Agent 应用 | [本地 API](../batch-c/web-local-api.md) · [结构化输出](../batch-c/llm-structured-output.md) · [只读工具](../batch-c/agent-read-only-tool.md) | 输入输出契约、错误状态、评估和权限是否可信 |
| 项目整合 | [学习进度报告器](../batch-a/study-progress-reporter.md) | 多节课是否真的形成版本演进和可讲述的证据 |

## 六条连续作品线

<div class="be-unified-project-grid">
  <article><strong>共同基座</strong><span>学习进度报告器</span><p>从单条学习档案走向可测试、可配置的程序。</p></article>
  <article><strong>应用与 Web</strong><span>工程学习工作台</span><p>把命令行报告接入 API、数据库和前端。</p></article>
  <article><strong>C++ 与系统</strong><span>跨语言可追踪数据引擎</span><p>对照类型、构建、资源、性能和测试。</p></article>
  <article><strong>AI 模型</strong><span>可复现实验与评估系统</span><p>保留数据、基线、训练、验证和误差记录。</p></article>
  <article><strong>LLM 与 Agent</strong><span>可评估的智能学习助手</span><p>逐步加入结构化输出、工具、恢复、评估和安全。</p></article>
  <article><strong>设备与边缘智能</strong><span>设备状态监测与告警系统</span><p>演进采集、通信、系统调试、推理和故障恢复。</p></article>
</div>

算法课程保留可追踪阶段实验，再把能力迁移进方向项目；它不需要被硬塞进一条“超级项目”。

## 评审结果怎样继续使用

1. [候选统一基线](baseline-candidate.md)已经成为内容规范 V2 的来源记录。
2. 八类样板继续作为课型与语言回归基线，不修改冻结正文。
3. 小码同学通过正式双协议运行时加载十三套语义知识库。
4. [差异与后续修订](gap-register.md)记录本轮已经解决与延后的项目。

!!! info "当前边界"
    十三页正文保持冻结。内容规范、模板、双协议运行时和 Skill 已固化；55 节正式课程、导航、URL 和知识库尚未迁移。
