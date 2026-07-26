<div class="be-tutor-mount" data-tutor-lesson="llm-use-02" aria-hidden="true"></div>
<section id="overview-prompt-snapshot" class="be-page-hero be-lesson-hero" data-learning-context="overview-prompt-snapshot" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">模型使用与结构化输出 · 第 2 / 6 课 · 智能学习助手 P5.1 v0.2</span>
# Prompt 角色、版本、参数与上下文预算
## “同一个问题”只有连同 Prompt 配置一起保存才可追踪
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
prompt=id:public-course-guide,version:2.0.0,roles:system|user
parameters=temperature:0.0,max_output_units:80
budget=input:139/240,estimator:utf8-bytes-not-provider-tokens
snapshot=fingerprint:64-hex,raw_content:excluded-from-audit
user_instruction=role:user,system_unchanged:true
version_change=fingerprint_changed:true
empty_question=rejected
oversized_question=rejected-before-adapter
invalid_prompt_spec=rejected
invariants=roles-preserved,version-explicit,parameters-recorded,budget-before-call,no-secrets
```
只记“用户问了什么”无法解释结果为何变化。系统规则、模板版本、模型名、生成参数和预算都属于一次请求；v0.2 把它们冻结为可比较快照。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>LLM 应用起步 · 2 / 6</strong></div>
  <div><span>前置</span><strong>模型边界、消息角色与离线 adapter</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 离线</strong></div>
  <div><span>完成后留下</span><strong>PromptSpec、请求快照与 8 项测试</strong></div>
</div>

## 学习目标

- 把 system 规则和 user 数据保留在不同 role。
- 为 Prompt 声明稳定 ID 和语义版本。
- 同时记录模型、temperature、输出上限与输入预算。
- 在调用前拒绝超预算输入。
- 用规范 JSON 的 SHA-256 指纹比较配置变化。
- 只将必要元数据写入审计记录，不保存原始内容。

<section id="concept-prompt-as-config" data-learning-context="concept-prompt-as-config" data-context-type="concept" markdown="1">
## Prompt 是版本化配置，不是散落的字符串

`PromptSpec` 包含 ID、版本、system instruction、输入预算、输出上限和 temperature。修改其中任一项都可能改变行为，因此必须进入变更记录和测试。

语义版本不自动证明兼容：它只是让团队能指出“哪个版本产生了这次请求”。真正的兼容性仍由固定用例与后续结构化输出测试证明。
</section>

<section id="concept-role-budget" data-learning-context="concept-role-budget" data-context-type="concept" markdown="1">
## 用户写“忽略规则”仍然只是 user 数据

消息结构决定角色，不靠字符串内容猜测。用户文本可以讨论 system，但不能在请求构造阶段改变首条 system message。

v0.2 用 UTF-8 字节数建立离线教学预算。它稳定、无需 tokenizer，却不是 provider token 数。生产 adapter 必须使用对应模型的计量或官方 usage，不能把这里的 139 字节写成 139 tokens。
</section>

<section id="example-canonical-fingerprint" data-learning-context="example-canonical-fingerprint" data-context-type="example" markdown="1">
## 指纹覆盖影响请求的字段

```python
canonical = {
    "prompt_id": spec.prompt_id,
    "prompt_version": spec.version,
    "model": model,
    "messages": [asdict(message) for message in messages],
    "max_output_units": spec.max_output_units,
    "temperature": spec.temperature,
}
fingerprint = sha256(canonical_json(canonical)).hexdigest()
```

规范序列化固定 key 顺序和分隔符。同一请求得到同一指纹，版本或参数变化会改变指纹。SHA-256 不是加密保密方案：短 Prompt 可能被猜测，所以审计记录只保存指纹不等于原文永远不可恢复。
</section>

<section id="reproduce-prompt-v02" data-learning-context="reproduce-prompt-v02" data-context-type="reproduce" markdown="1">
## 运行 Prompt 快照实验

```bash
cd site-src/examples/llm-use/intelligent-learning-assistant-v02
python3 -m unittest -v test_prompt_contract.py
python3 prompt_contract.py
```

8 项测试覆盖 role、用户越权文本、确定性指纹、版本/参数变化、预算、空输入/坏配置、审计脱敏和固定报告。全程不会调用 adapter 或网络。
</section>

<section id="modify-prompt-contract" data-learning-context="modify-prompt-contract" data-context-type="modify" markdown="1">
## 修改 Prompt 时同时修改版本和测试

1. 把 system 规则增加“不确定时明确说明”。
2. 将版本从 `2.0.0` 改为 `2.1.0`。
3. 保留同一用户问题，确认指纹改变。
4. 增加一个固定用例，证明“不确定”路径不会编造答案。

不要只改字符串而保留旧版本；也不要因为指纹变化就声称质量改善，质量判断需要后续固定评估集。
</section>

<section id="troubleshoot-prompt-contract" data-learning-context="troubleshoot-prompt-contract" data-context-type="troubleshoot" markdown="1">
## 结果漂移先比较快照，不先猜模型

| 现象 | 先查 | 恢复 |
| --- | --- | --- |
| 同问题结果不同 | Prompt 版本、模型和参数 | 比较完整快照 |
| 用户文本覆盖规则 | role 构造 | 规则只从可信配置进入 system |
| 请求尚未发送就失败 | 输入预算 | 缩短输入或明确分段，不静默截断 |
| 指纹每次不同 | JSON 规范化 | 固定 key 排序和分隔符 |
| 日志出现问题原文 | audit record | 只记 ID、版本、计量和指纹 |
| 字节预算与账单不符 | 估算器边界 | 使用 provider usage，不混称 token |
</section>

<section id="deepen-prompt-limits" data-learning-context="deepen-prompt-limits" data-context-type="deepen" markdown="1">
## Prompt 版本化仍不能消除模型不确定性

相同快照可能因模型更新、采样、服务实现或安全策略得到不同输出。temperature 为 0 也不等于跨时间绝对确定。快照解决“应用提交了什么配置”，不单独证明 provider 执行环境和结果一致。

真实系统还要记录 provider 返回的模型版本、usage、request ID 和状态；它们与 v0.1 的归一化结果结合，才形成完整调用证据。
</section>

<section id="project-learning-assistant-v02" data-learning-context="project-learning-assistant-v02" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.1 v0.2

- 上一版：v0.1 有稳定请求/结果与离线 adapter。
- 本课新增：`PromptSpec`、role 门禁、预算、规范指纹和脱敏审计记录。
- 文件：`prompt_contract.py` 与 `test_prompt_contract.py`。
- 保存：一份版本变更前后快照、8 项测试和一次预算排错。
- 下一版：解析 JSON，并分别处理语法、对象形状、字段、类型、范围和缺失信息。
</section>

## 四类学习者入口

- 零基础兴趣：把一条请求拆成规则、问题、参数和预算四部分。
- 有基础兴趣：实现不同估算器，并说明它与 provider tokens 的差异。
- 零基础求职：用版本、参数和测试描述自己的 Prompt 变更，不说“调了几句效果更好”。
- 有基础求职：解释快照能证明什么、不能证明什么；本组没有脱敏招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- system/user role 不因用户字符串而改变。
- Prompt ID、版本、模型、参数和预算进入快照。
- 超预算输入在调用前拒绝，不静默截断。
- 同配置指纹相同，版本或参数变化后指纹改变。
- 审计记录不含原始消息，并说明哈希不是保密承诺。

## 来源与版本

- 核查日期：2026-07-26。
- 适用环境：Python 3.11+ 标准库；自动测试离线。
- [OpenAI text generation and message roles](https://platform.openai.com/docs/guides/text)
- [OpenAI Responses API reference](https://platform.openai.com/docs/api-reference/responses)
- [Python hashlib](https://docs.python.org/3.11/library/hashlib.html)

## 下一步

进入第 3 课，让模型提出的 JSON 依次通过语法、对象、字段、类型、范围和缺失信息校验。
