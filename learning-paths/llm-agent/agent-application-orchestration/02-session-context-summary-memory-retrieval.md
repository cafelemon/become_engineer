<div class="be-tutor-mount" data-tutor-lesson="agent-application-orchestration-02" aria-hidden="true"></div>
<section id="overview-context-memory" class="be-page-hero be-lesson-hero" data-learning-context="overview-context-memory" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Agent 应用编排与交付 · 第 2 / 6 课 · 智能学习助手 P5.13 v0.32</span>
# 会话上下文、摘要与记忆召回
## 四类信息分开治理，再装入同一预算
```text
context=summary:true,messages:2,memory:1,knowledge:1
budget=used:16,limit:30,within:true
memory=owner-filtered:true,consent:true,ttl:true,instruction:false
summary=structured:true,raw-chain-of-thought:false
```
v0.32 把消息窗口、结构化摘要、用户事实和知识检索分成不同来源，逐项执行主体、同意、过期和预算检查。
</section>
<div class="be-lesson-overview"><div><span>课程位置</span><strong>Agent 应用编排与交付 · 2 / 6</strong></div><div><span>前置</span><strong>状态图、记忆来源与 RAG 上下文</strong></div><div><span>环境</span><strong>Python 3.11+ · 标准库 · 固定时钟</strong></div><div><span>完成后留下</span><strong>ContextPackage、结构化摘要与 8 项测试</strong></div></div>

## 学习目标

- 区分短期消息、会话摘要、长期用户事实和外部知识。
- 为长期记忆保存主体、来源、同意和 TTL，跨主体永不召回。
- 在装配时执行硬预算，并记录被丢弃内容的类别和原因。
- 把记忆与检索文本标成数据，抵抗历史内容中的提示注入。

<section id="concept-four-context-sources" data-learning-context="concept-four-context-sources" data-context-type="concept" markdown="1">
## 上下文不是一段无限增长的聊天记录

| 类型 | 生命周期 | 典型用途 |
| --- | --- | --- |
| message window | 最近若干轮 | 保持局部连贯 |
| structured summary | 当前会话 | 保存目标、决定、未决问题 |
| user memory | 跨会话且有 TTL | 经同意保存偏好或事实 |
| knowledge retrieval | 跟随来源版本 | 提供可引用外部证据 |

四类数据不能合并成一个无来源字符串，否则无法分别删除、过期、授权、评估或解释。
</section>

<section id="concept-memory-governance" data-learning-context="concept-memory-governance" data-context-type="concept" markdown="1">
## 记住之前先回答“谁的、从哪来、能存多久”

长期 `Memory` 保存 `owner_id`、`kind`、`source`、`consent` 和 `expires_at`。只有主体匹配、已同意且未过期的事实才有资格进入上下文。即使内容写着“忽略系统规则”，渲染时也标记 `instruction=false`，不能提升为系统指令。
</section>

<section id="example-budgeted-context-package" data-learning-context="example-budgeted-context-package" data-context-type="example" markdown="1">
## 预算是装配规则，不是最后截断

本课先放压缩后的结构化摘要，再放合格用户事实、知识证据和从新到旧的消息。每放一项先计算单位；放不下就记录 `memory:...:budget`、`knowledge:budget` 或 `message:window`。这是一种可测试的教学策略，不是所有产品的唯一顺序。
</section>

<section id="reproduce-context-memory-v32" data-learning-context="reproduce-context-memory-v32" data-context-type="reproduce" markdown="1">
## 运行上下文装配
```bash
cd site-src/examples/agent-application-orchestration/intelligent-learning-assistant-v32
python3 -m unittest -v test_context_memory.py
python3 context_memory.py
```
8 项测试覆盖结构化摘要、最近消息、同意、TTL、跨主体隔离、注入标记、硬预算和用户记忆/知识分离。
</section>

<section id="modify-add-memory-delete" data-learning-context="modify-add-memory-delete" data-context-type="modify" markdown="1">
## 增加“查看并忘记”入口

1. 列出当前主体可见的记忆及来源、用途和过期时间。
2. 删除使用稳定 memory ID，先校验 owner。
3. 写入审计事件但不复制敏感原文。
4. 下一次上下文装配必须立即不再出现。
5. 增加跨主体删除 404 与重复删除幂等测试。
</section>

<section id="troubleshoot-context-memory" data-learning-context="troubleshoot-context-memory" data-context-type="troubleshoot" markdown="1">
## 从来源、主体、过期和预算排查

| 现象 | 首先检查 |
| --- | --- |
| 记忆突然消失 | TTL、同意或预算是否淘汰 |
| 回答引用了旧决定 | 摘要是否随确认事件更新 |
| 用户 A 看到 B 的偏好 | owner filter 是否在召回前 |
| 历史消息覆盖系统规则 | 数据块是否错误当作指令 |
| 上下文仍超限 | 是否事后截断而非逐项装配 |
| 摘要不可解释 | 是否保存了自由文本推理而非结构字段 |
</section>

<section id="deepen-memory-evaluation" data-learning-context="deepen-memory-evaluation" data-context-type="deepen" markdown="1">
## 记忆质量要同时看命中和误用

固定案例标注应该记住、应该忘记、属于哪个主体和何时过期。统计正确召回、漏召回、错误主体召回、过期误用和注入服从率。记忆召回越多并不越好；错误记忆会比没有记忆更危险。
</section>

<section id="project-learning-assistant-v32" data-learning-context="project-learning-assistant-v32" data-context-type="project" markdown="1">
## 智能学习助手 P5.13 v0.32

- 上一版：v0.31 决定运行模式和状态图。
- 本课新增：四类上下文来源、结构化摘要、记忆同意/TTL/主体、硬预算和丢弃原因。
- 文件：`context_memory.py` 与 `test_context_memory.py`。
- 保存：摘要字段、记忆来源与期限、知识引用、消息窗口和预算决策；不保存隐式思维链。
- 下一版：将复杂目标拆成有依赖、有预算、可重规划的子任务。
</section>

## 四类学习者入口

- 零基础兴趣：用四列表格区分聊天记录、摘要、偏好和课程知识。
- 有基础兴趣：实现“查看并忘记”并补隔离测试。
- 零基础求职：解释上下文窗口和长期记忆为什么不是一回事。
- 有基础求职：展示 TTL、同意、跨主体、注入和预算证据；不编造岗位频率。

## 完成检查

- 8 项 unittest 和固定报告通过。
- 记忆必须主体匹配、已同意且未过期。
- 知识与用户事实保持不同类型和来源。
- 上下文使用量不超过硬预算。
- 摘要是结构字段，不保存隐式思维链。

## 来源与版本

- 核查日期：2026-07-31。
- [NIST Privacy Framework](https://www.nist.gov/privacy-framework)
- [OWASP LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)

## 下一步

进入第 3 课：任务拆解、子任务预算与重规划。
