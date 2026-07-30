<div class="be-tutor-mount" data-tutor-lesson="agent-engineering-02" aria-hidden="true"></div>
<section id="overview-bounded-memory-context" class="be-page-hero be-lesson-hero" data-learning-context="overview-bounded-memory-context" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Agent 工程 · 第 2 / 6 课 · 智能学习助手 P5.6 v0.20</span>
# 记忆来源、同意、TTL 与上下文预算
## 四条事实已保存，只有一条可以进入当前上下文
```text
runtime=python:3.11+,dependencies:stdlib-only,storage:sqlite,network:disabled
memory=working:ephemeral,facts:persistent,source-required:true,consent-filter:true,ttl-filter:true,subject-isolation:true
stored=4,eligible=1,assembled=working:working-1,fact:fact-preference
budget=used-chars:29,limit-chars:29,deterministic:true
excluded=unconsented:true,expired:true,other-subject:true,hidden-reasoning:true
invariants=explicit-memory-only,source-bound,consent-before-use,ttl-enforced,subject-scoped,budget-bounded,no-hidden-chain-of-thought,no-network
```
“存过”不等于“现在可以使用”。v0.20 在装配上下文前逐条检查来源、主体、同意、过期时间和预算，工作记忆只属于当前 run，不能悄悄变成长久画像。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 工程 · 2 / 6</strong></div>
  <div><span>前置</span><strong>run snapshot、事件日志、原子 checkpoint</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 临时 SQLite</strong></div>
  <div><span>完成后留下</span><strong>MemoryStore、ContextAssembler、固定报告与 8 项测试</strong></div>
</div>

## 学习目标

- 区分当前 run 的工作记忆与可持久事实。
- 让持久事实携带主体、来源、同意和 TTL。
- 在装配时拒绝过期、未同意和跨主体记忆。
- 用确定性预算选择上下文，并能解释被舍弃项。
- 不保存 prompt、reasoning 或隐式思维链。

<section id="concept-working-persistent-memory" data-learning-context="concept-working-persistent-memory" data-context-type="concept" markdown="1">
## 工作记忆随 run 结束，持久事实必须有使用依据

工作记忆保存“这一轮正在做什么”，例如当前目标和已确认约束，只存在于调用参数或 checkpoint 的允许字段中。持久事实跨 run 使用，因此必须回答：属于谁、从哪里来、是否同意、何时过期。

`MemoryStore` 可以保存未同意记录以等待后续授权，但 `ContextAssembler` 永远不会把它送入模型输入。
</section>

<section id="concept-filter-before-budget" data-learning-context="concept-filter-before-budget" data-context-type="concept" markdown="1">
## 先过滤资格，再按稳定顺序装配

装配顺序固定为：验证当前主体 → 接收显式工作记忆 → 查询同主体且已同意、未过期的事实 → 按优先级和 memory ID 稳定排序 → 在字符预算内选择。

课程使用字符数作为离线预算代理，不把它冒充 provider 的真实 token 计数。生产接入具体 tokenizer 时，应保留相同过滤边界并重新冻结预算测试。
</section>

<section id="example-four-facts-one-eligible" data-learning-context="example-four-facts-one-eligible" data-context-type="example" markdown="1">
## 为什么四条事实只有一条合格

固定示例保存四条记录：

| 记录 | 结果 | 原因 |
| --- | --- | --- |
| `fact-preference` | 进入上下文 | 同主体、有来源、已同意、未过期 |
| `fact-unconsented` | 排除 | 没有使用同意 |
| `fact-expired` | 排除 | `expires_at <= now` |
| `fact-other-subject` | 排除 | 属于另一个学习者 |

当前 run 的 `review arrays` 先进入工作记忆，再装配唯一合格事实，合计正好 29 个字符。
</section>

<section id="reproduce-memory-context-v20" data-learning-context="reproduce-memory-context-v20" data-context-type="reproduce" markdown="1">
## 运行真实 SQLite 和记忆装配

```bash
cd site-src/examples/agent-engineering/intelligent-learning-assistant-v20
python3 -m unittest -v test_memory_context.py
python3 memory_context.py
```

8 项测试覆盖持久读取、来源必填、同意、TTL、主体隔离、稳定预算、工作记忆生命周期和隐藏推理拒绝。
</section>

<section id="modify-memory-priority" data-learning-context="modify-memory-priority" data-context-type="modify" markdown="1">
## 增加一种“用户刚刚确认”的高优先级事实

1. 新增 `fact-current-goal`，来源写为 `goal-confirmation`。
2. 设置较高 priority 和短 TTL。
3. 把预算缩小到只能保留一条事实。
4. 预测稳定排序后哪条保留，再运行测试。
5. 记录为什么短 TTL 比永久保存更符合用途。
</section>

<section id="troubleshoot-memory-context" data-learning-context="troubleshoot-memory-context" data-context-type="troubleshoot" markdown="1">
## 从“为什么没进入上下文”反查门禁

| 现象 | 首先检查 |
| --- | --- |
| `source required` | source ID 是否为空 |
| 已保存但查询为空 | consent、TTL 和 subject 是否同时满足 |
| 预算内结果不稳定 | 是否使用了 priority 与 memory ID 的稳定排序 |
| 其他用户事实出现 | 查询是否把 subject ID 作为条件 |
| `hidden prompt or reasoning fields are forbidden` | 工作记忆是否混入禁止字段 |

不要为了“召回更多”绕过资格过滤；先修正来源、同意或生命周期。
</section>

<section id="deepen-memory-is-not-profile" data-learning-context="deepen-memory-is-not-profile" data-context-type="deepen" markdown="1">
## 记忆系统不是无限期用户画像

长期保存会扩大隐私、误用和过时风险。事实应有明确用途、最短 TTL、删除入口和主体授权；推断性标签不能伪装成用户确认事实。课程只保存合成文本，不保存真实个人数据。

固定报告中的字符预算只是确定性教学机制；真实模型还需计算系统指令、检索证据、工具结果和输出预留。
</section>

<section id="project-learning-assistant-v20" data-learning-context="project-learning-assistant-v20" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.6 v0.20

- 上一版：v0.19 持久化 run、事件和原子 checkpoint。
- 本课新增：工作记忆、带来源/同意/TTL 的事实和确定性上下文装配。
- 文件：`memory_context.py` 与 `test_memory_context.py`。
- 保存：四类排除证据、预算选择结果和 8 项测试。
- 下一版：给 worker 增加 lease、幂等 step 和崩溃后 resume。
</section>

## 四类学习者入口

- 零基础兴趣：用表格解释四条事实为什么只有一条合格。
- 有基础兴趣：修改 priority、TTL 和预算，观察稳定选择。
- 零基础求职：说明“保存”和“允许进入上下文”为什么是两件事。
- 有基础求职：解释主体隔离、同意、数据最小化和 tokenizer 适配边界；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 工作记忆不写入持久事实表。
- 每条持久事实有主体、来源、同意和 TTL。
- 过期、未同意和跨主体事实不会进入上下文。
- 预算选择顺序确定，输出可复现。
- prompt、reasoning 和 chain of thought 被拒绝。

## 来源与版本

- 核查日期：2026-07-30。
- [Python sqlite3](https://docs.python.org/3.11/library/sqlite3.html)
- [NIST Privacy Framework](https://www.nist.gov/privacy-framework)
- [OWASP LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)

## 下一步

进入第 3 课，用 lease 和幂等 step 证明崩溃恢复不会重复已经完成的副作用。
