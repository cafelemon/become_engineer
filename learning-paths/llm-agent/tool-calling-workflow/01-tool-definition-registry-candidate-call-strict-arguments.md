<div class="be-tutor-mount" data-tutor-lesson="agent-tool-calling-01" aria-hidden="true"></div>
<section id="overview-tool-proposal" class="be-page-hero be-lesson-hero" data-learning-context="overview-tool-proposal" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Tool Calling 与有界工作流 · 第 1 / 6 课 · 智能学习助手 P5.5 v0.13</span>
# 工具定义、注册表、候选调用与严格参数
## 模型提出调用，应用决定是否执行
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
registry=tools:1,names:get_learning_status,strict:true
manifest=fingerprint:e5c8836eb436,additional-properties:false
candidate=call-id:call_demo1,tool:get_learning_status,arguments:2,executed:false
validation=call-id:true,known-tool:true,json-object:true,required:true,exact-fields:true,strict-types:true
rejection=bad-call-id:true,unknown-tool:true,bad-json:true,array-arguments:true,missing:true,extra:true,type:true,length:true
trust=model-output:proposal-only,application-validates:true,application-executes:false
logs=arguments:none,user-text:none,call-id:allowed,tool-name:allowed,error-code:allowed
invariants=allowlisted-registry,canonical-manifest,immutable-arguments,no-handler,no-side-effects,no-network
```
v0.13 只建立协议边界：应用发布一个允许列表工具 manifest，离线模型提出带 `call_id`、工具名和 JSON 参数的候选调用，注册表完成严格解析。验证成功仍不触发 handler。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 工程 · 1 / 6</strong></div>
  <div><span>前置</span><strong>严格 JSON、RAG 评估、权限默认拒绝</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 完全离线</strong></div>
  <div><span>完成后留下</span><strong>ToolRegistry、规范 manifest、候选解析与 8 项测试</strong></div>
</div>

## 学习目标

- 区分工具定义、模型候选调用、应用执行和工具结果。
- 用允许列表注册表代替任意函数名反射。
- 生成稳定、可指纹化的严格工具 manifest。
- 验证 `call_id`、工具名和 arguments JSON 对象。
- 拒绝缺失、额外字段、错误类型和字符串越界。
- 保持验证结果不可变，并证明本课没有执行副作用。

<section id="concept-tool-flow" data-learning-context="concept-tool-flow" data-context-type="concept" markdown="1">
## Tool Calling 是五步协议，不是模型获得函数权限

```text
应用给出工具定义
  → 模型提出候选调用
  → 应用验证与授权
  → 应用执行并绑定 call_id 回传结果
  → 模型回答或提出下一次调用
```

本课停在第 2 步与参数门禁之间。`executed:false` 是刻意的验收结果：模型生成正确 JSON 只能证明“候选形状合法”，不能证明主体有权限、业务值合理或副作用已获确认。
</section>

<section id="concept-registry-manifest" data-learning-context="concept-registry-manifest" data-context-type="concept" markdown="1">
## 注册表把能力面缩到明确业务工具

唯一工具是 `get_learning_status`，参数为 `learner_id: string` 与 `include_recent: boolean`。它表达一个只读业务能力，而不是 `execute_sql`、`run_shell` 或“按名字调用任意 Python 函数”。

manifest 按工具名和参数名规范排序后做 SHA-256。指纹用于识别本次模型看到了哪组定义，不证明定义安全；安全性仍来自工具设计、实现、权限和测试。
</section>

<section id="example-strict-candidate" data-learning-context="example-strict-candidate" data-context-type="example" markdown="1">
## 候选参数不做隐式纠正

```python
candidate = ToolCall(
    "call_demo1",
    "get_learning_status",
    '{"learner_id":"learner-001","include_recent":true}',
)
validated = registry.validate_call(candidate)
```

`"true"` 不转换为 `true`，整数 `1` 不转换为布尔值，数组顶层不转换为对象，额外 `admin` 字段不会被忽略。严格失败让模型或上游状态机获得稳定错误码，而不是把猜测送到执行器。
</section>

<section id="reproduce-tool-v13" data-learning-context="reproduce-tool-v13" data-context-type="reproduce" markdown="1">
## 回放一个合法候选与八类拒绝

```bash
cd site-src/examples/agent-tool-calling/intelligent-learning-assistant-v13
python3 -m unittest -v test_tool_protocol.py
python3 tool_protocol.py
```

8 项测试覆盖 manifest/指纹、不可变候选、call ID/未知工具、坏 JSON/非对象、缺失/额外字段、严格类型、长度/重复注册和固定报告。
</section>

<section id="modify-tool-schema" data-learning-context="modify-tool-schema" data-context-type="modify" markdown="1">
## 增加一个可选 `course_id`

1. 给 definition 增加非必填字符串 `course_id`，长度 3–48。
2. 比较修改前后 manifest 指纹。
3. 验证省略字段与提供合法字段都通过。
4. 验证空字符串、超长字符串、数字和未知字段失败。
5. 仍不增加 handler；下一课才建立执行边界。

如果新字段只是为了让模型“更灵活”而没有明确业务用途，不应加入工具面。
</section>

<section id="troubleshoot-tool-protocol" data-learning-context="troubleshoot-tool-protocol" data-context-type="troubleshoot" markdown="1">
## 先查候选结构，不要直接调业务函数

| 错误 | 含义 |
| --- | --- |
| `invalid_call_id` | 关联 ID 不符合稳定格式 |
| `unknown_tool` | 工具名不在允许列表 |
| `arguments_json_invalid` | 参数不是合法 JSON |
| `arguments_not_object` | 顶层不是对象 |
| `arguments_missing` | 必填字段缺失 |
| `arguments_extra` | 出现 manifest 未声明字段 |
| `argument_type_invalid` | 严格 JSON 类型不符 |
| `argument_value_invalid` | 字符串长度等局部约束不符 |

日志只记录 call ID、工具名和错误码，不写完整 arguments 或用户原文。
</section>

<section id="deepen-schema-security-boundary" data-learning-context="deepen-schema-security-boundary" data-context-type="deepen" markdown="1">
## Strict Schema 不是授权或业务安全

严格 Schema 能阻止形状漂移，却不能判断 `learner_id` 是否属于当前主体、一次查询是否超出数据范围，或一个写工具是否需要人工确认。合法字符串也可能携带路径、SQL 或 Prompt Injection 风格文本。

因此执行前至少还有业务校验、身份授权、风险分类、预算和实现隔离。本课不把“strict:true”描述成完整安全边界。
</section>

<section id="project-learning-assistant-v13" data-learning-context="project-learning-assistant-v13" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.5 v0.13

- 上一版：v0.12 能用固定评估门禁验证 RAG。
- 本课新增：受控工具 definition、注册表、manifest 指纹与候选调用解析。
- 文件：`tool_protocol.py` 与 `test_tool_protocol.py`。
- 保存：固定报告、8 项测试、工具定义与日志允许字段。
- 下一版：把已验证候选交给只读、按主体授权的学习状态 handler。
</section>

## 四类学习者入口

- 零基础兴趣：画出“模型提议”和“应用执行”之间的门。
- 有基础兴趣：给 manifest 增加可选字段并观察指纹。
- 零基础求职：解释为什么正确 JSON 不等于可以执行。
- 有基础求职：说明 Schema、授权、最小权限和副作用确认边界；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 注册表只有明确业务工具，不提供任意 SQL/Shell/反射入口。
- manifest 规范稳定，额外字段关闭。
- call ID、工具名、JSON 对象、必填、字段集合、类型和长度逐层验证。
- 验证参数不可变，固定报告明确 `executed:false`。
- 日志不保存 arguments 或用户原文。

## 来源与版本

- 核查日期：2026-07-26。
- 适用环境：Python 3.11+ 标准库；自动测试离线。
- [OpenAI Function Calling 指南](https://developers.openai.com/api/docs/guides/function-calling)
- [OpenAI Tools 指南](https://developers.openai.com/api/docs/guides/tools)
- [OWASP LLM Excessive Agency](https://genai.owasp.org/llmrisk/llm06-excessive-agency/)
- [Python json](https://docs.python.org/3.11/library/json.html)

## 下一步

进入第 2 课，加入业务值校验、主体权限、只读 handler 与结构化结果 envelope。
