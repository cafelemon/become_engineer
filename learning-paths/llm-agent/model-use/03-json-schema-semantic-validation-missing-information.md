<div class="be-tutor-mount" data-tutor-lesson="llm-use-03" aria-hidden="true"></div>
<section id="overview-structured-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-structured-output" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">模型使用与结构化输出 · 第 3 / 6 课 · 智能学习助手 P5.1 v0.3</span>
# JSON、严格 Schema、语义校验与缺失信息
## 合法 JSON 只是第一道门
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
valid=goal:job,topic:Python,weekly_hours:8,level:beginner
pipeline=nonempty->json-syntax->object->field-set->types->enums-and-ranges->domain-object
failures=empty:empty_response,invalid-json:invalid_json,array:not_object,extra:extra_fields,missing:missing_fields,wrong-type:wrong_type,bool-hours:wrong_type,out-of-range:out_of_range,invalid-enum:invalid_enum
coercion=string-to-int:false,bool-to-int:false,extra-fields:false
missing_information=recovery:ask_user
malformed_output=recovery:reject_or_regenerate,budget:not-yet-implemented
schema_prompt=helpful-but-application-validation-required
logs=raw_content:none,validation_code:allowed
invariants=model-proposes,application-validates,no-silent-repair,no-rag,no-tools
```
模型提出数据，应用决定它是否能成为业务对象。v0.3 不把字符串 `"8"` 转成整数，也不把缺字段偷偷补默认值；每一层失败都有稳定代码和不同恢复方向。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>LLM 应用起步 · 3 / 6</strong></div>
  <div><span>前置</span><strong>Prompt 快照、JSON 与 Python 类型</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 离线</strong></div>
  <div><span>完成后留下</span><strong>严格解析器、错误代码与 8 项测试</strong></div>
</div>

## 学习目标

- 按非空、JSON、对象、字段、类型、枚举/范围顺序校验。
- 拒绝额外字段、缺失字段、隐式类型转换和 bool/int 混淆。
- 只在全部门禁通过后构造不可变业务对象。
- 区分需要向用户补问与可以重新生成的失败。
- 说明 provider 结构化模式之后仍要应用校验。
- 日志只保存失败代码，不默认记录模型原文。

<section id="concept-validation-layers" data-learning-context="concept-validation-layers" data-context-type="concept" markdown="1">
## 每层只回答一个问题

| 层 | 问题 | 失败代码 |
| --- | --- | --- |
| 内容 | 是否有内容 | `empty_response` |
| 语法 | 是否为 JSON | `invalid_json` |
| 形状 | 顶层是否为对象 | `not_object` |
| 字段 | 是否恰好四个字段 | `extra_fields` / `missing_fields` |
| 类型 | 字符串与整数是否严格 | `wrong_type` |
| 语义 | 枚举、长度和范围是否合法 | `invalid_enum` / `out_of_range` |

分层让排错和恢复可解释。把所有异常压成“解析失败”，会失去补问、重试和修复依据。
</section>

<section id="concept-no-silent-repair" data-learning-context="concept-no-silent-repair" data-context-type="concept" markdown="1">
## 自动修复可能改写用户意思

`"weekly_hours": "8"` 看似容易转换，但 `"很多"`、`true` 或 `"8h"` 又怎么办？v0.3 统一拒绝非整数，避免一部分输入被悄悄猜测。

缺 `current_level` 不是格式噪声，而是业务信息不足，应回到用户补问。模型重新生成也不能凭空知道用户水平。
</section>

<section id="example-learning-request" data-learning-context="example-learning-request" data-context-type="example" markdown="1">
## 只有合格 payload 才进入 dataclass

```python
payload = json.loads(content)
require_exact_fields(payload)
goal = require_string(payload, "goal")
hours = require_strict_int(payload, "weekly_hours")
validate_enums_and_ranges(...)
return LearningRequest(goal, topic, hours, level)
```

Python 的 `bool` 是 `int` 子类，所以要先显式排除 bool。额外字段采用默认拒绝，避免模型把电话、备注或未审查内容带入业务对象。
</section>

<section id="reproduce-structured-v03" data-learning-context="reproduce-structured-v03" data-context-type="reproduce" markdown="1">
## 运行十组固定模型回复

```bash
cd site-src/examples/llm-use/intelligent-learning-assistant-v03
python3 -m unittest -v test_structured_output.py
python3 structured_output.py
```

8 项测试覆盖一个成功对象和九种失败 fixture。测试只验证应用解析器，不宣称离线 fixture 代表真实模型质量。
</section>

<section id="modify-structured-schema" data-learning-context="modify-structured-schema" data-context-type="modify" markdown="1">
## 新增可选字段前先决定兼容规则

1. 设计 `preferred_language`，只允许 `zh` 或 `en`。
2. 决定旧 payload 缺少它时是拒绝还是显式使用默认值。
3. 修改 `EXPECTED_FIELDS`、dataclass、校验和测试。
4. 给 Schema 升版本，并记录旧、新行为是否兼容。

“可选”也必须有明确含义，不能因为模型偶尔不返回就临时补值。
</section>

<section id="troubleshoot-structured-output" data-learning-context="troubleshoot-structured-output" data-context-type="troubleshoot" markdown="1">
## 先看错误层，再选恢复动作

| 失败 | 恢复 |
| --- | --- |
| 空、坏 JSON、数组、额外字段 | 拒绝；在有预算时可按同一 Schema 重新生成 |
| 缺少用户事实 | 向用户补问 |
| 字符串代替整数 | 拒绝，不静默转换 |
| 枚举或范围错误 | 检查 Prompt 与 Schema，必要时重新生成 |
| 多次失败 | 停止并返回可解释错误，不无限重试 |

第 4 课才会加入尝试预算和 deadline；v0.3 的 `reject_or_regenerate` 不是授权无限重试。
</section>

<section id="deepen-provider-schema" data-learning-context="deepen-provider-schema" data-context-type="deepen" markdown="1">
## Provider 保证 Schema 仍不等于业务事实正确

结构化输出功能可以提高字段和类型符合度，但支持的 JSON Schema 子集、拒绝和不完整状态会因接口而异。应用仍要处理空响应、拒绝、截断、语义范围和用户事实缺失。

即使 `weekly_hours` 是合法整数 8，也不能证明用户真的每周有 8 小时；输入事实的真实性属于业务确认，不属于 JSON 校验。
</section>

<section id="project-learning-assistant-v03" data-learning-context="project-learning-assistant-v03" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.1 v0.3

- 上一版：v0.2 能审计 Prompt 配置与预算。
- 本课新增：严格解析流水线、不可变 `LearningRequest`、错误代码和恢复分类。
- 文件：`structured_output.py` 与 `test_structured_output.py`。
- 保存：十组 fixture、8 项测试和一次 Schema 演进记录。
- 下一版：给瞬时失败增加 deadline、错误分类、退避与尝试预算。
</section>

## 四类学习者入口

- 零基础兴趣：按七道门逐个判断一个坏 JSON。
- 有基础兴趣：实现 Schema 版本演进并写兼容测试。
- 零基础求职：用“模型提出、程序校验、缺失补问”讲清项目职责。
- 有基础求职：解释为何不静默转换、为何结构化模式后仍校验；无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 九种坏输出都有稳定失败代码，不能进入业务对象。
- 字符串和 bool 不转换成整数，额外字段默认拒绝。
- 缺失用户事实返回补问方向，不让模型猜。
- 日志只允许验证代码，不默认记录原始回复。
- 能说明 Schema 合规、业务语义和事实真实性的区别。

## 来源与版本

- 核查日期：2026-07-26。
- 适用环境：Python 3.11+ 标准库；自动测试离线。
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [DeepSeek JSON Output](https://api-docs.deepseek.com/guides/json_mode)
- [Python json](https://docs.python.org/3.11/library/json.html)

## 下一步

进入第 4 课，用错误分类、deadline、退避和尝试预算建立有限失败恢复。
