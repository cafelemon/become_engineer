<div class="be-tutor-mount" data-tutor-lesson="llm-use-01" aria-hidden="true"></div>
<section id="overview-model-boundary" class="be-page-hero be-lesson-hero" data-learning-context="overview-model-boundary" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">模型使用与结构化输出 · 第 1 / 6 课 · 智能学习助手 P5.1 v0.1</span>
# 模型边界、消息与离线适配器
## 同一次调用，不只有“成功”或“报错”
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
request=model:offline-learning-assistant-v01,messages:system|user,max_output_units:80
completed=status:completed,finish:stop,usage:18|14,text:present
refused=status:refused,finish:safety,text:present
incomplete=status:incomplete,finish:max_output_units,text:partial
empty_completed=rejected
invalid_request=rejected-before-adapter
normalized_result=status+text+usage+finish_reason+request_id
logs=authorization:none,raw_prompt:none,raw_response:none
invariants=model-is-untrusted-adapter,application-validates,offline-first,no-rag,no-tools
```
模型可能完成、拒绝或只返回一部分。应用若只取一段文本，就会把拒绝当答案、把截断当完整结果。v0.1 先把请求和结果写成稳定契约，再用离线 adapter 跑全分支。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>LLM 应用起步 · 1 / 6</strong></div>
  <div><span>前置</span><strong>Python dataclass、Protocol、HTTP 请求响应</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 离线</strong></div>
  <div><span>完成后留下</span><strong>统一调用边界与 8 项测试</strong></div>
</div>

## 学习目标

- 区分模型、provider adapter 与应用业务逻辑。
- 把 system、user、assistant 消息角色写进数据结构。
- 在调用 adapter 前验证模型名、消息顺序与输出上限。
- 把 completed、refused、incomplete 归一化为一套结果。
- 保留 usage、finish reason 和 request ID，不只取文本。
- 用离线 fixture 验收所有路径，不让 CI 调用真实模型。

<section id="concept-model-call-chain" data-learning-context="concept-model-call-chain" data-context-type="concept" markdown="1">
## 应用不直接依赖某家响应 JSON

```text
学习问题
  ↓ build + validate
ModelRequest
  ↓ ModelAdapter
provider 特有请求/响应
  ↓ normalize + validate
ModelResult
  ↓
界面、CLI 或后续业务
```

adapter 负责翻译 provider 协议，应用只认识自己的 `ModelRequest` 和 `ModelResult`。这样切换服务时，不必让业务代码到处判断某家字段名。模型输出仍是不可信输入：即使 HTTP 200，应用也要检查状态、文本、usage 和结束原因。
</section>

<section id="concept-message-status" data-learning-context="concept-message-status" data-context-type="concept" markdown="1">
## 角色和状态表达不同问题

消息角色说明“这段内容是谁提供的”：

| role | 本课含义 |
| --- | --- |
| system | 应用给出的稳定职责和限制 |
| user | 学习者本次问题 |
| assistant | 历史模型回复；v0.1 暂不构造多轮历史 |

结果状态说明“这次生成怎样结束”：

| status | 应用能否当完整答案 |
| --- | --- |
| completed | 还要确认文本非空，再进入下一层 |
| refused | 不能伪装成普通答案，应保留拒绝语义 |
| incomplete | 可以展示为部分结果，但不能标记完成 |

`finish_reason` 进一步解释停止、策略拒绝或输出上限。不同 provider 名称可能不同，adapter 应映射到应用自己的有限集合。
</section>

<section id="example-offline-adapter" data-learning-context="example-offline-adapter" data-context-type="example" markdown="1">
## Protocol 约束能力，不绑定实现

```python
class ModelAdapter(Protocol):
    def complete(self, request: ModelRequest) -> ProviderResponse:
        ...

def call_model(adapter: ModelAdapter, request: ModelRequest) -> ModelResult:
    validate_request(request)
    response = adapter.complete(request)
    return normalize_and_validate(response)
```

`ScriptedAdapter` 不是“假装真实模型效果”，它只替代不可重复、可能收费的网络边界，用固定 provider response 验证应用状态机。课程不会用离线文本宣称模型质量；真实 provider 也不能替代这些确定性契约测试。
</section>

<section id="reproduce-model-boundary-v01" data-learning-context="reproduce-model-boundary-v01" data-context-type="reproduce" markdown="1">
## 运行四条离线路径

```bash
cd site-src/examples/llm-use/intelligent-learning-assistant-v01
python3 -m unittest -v test_model_boundary.py
python3 model_boundary.py
```

不需要安装包、设置环境变量或联网。8 项测试覆盖消息分层、成功归一化、拒绝、不完整、调用前拒绝、空成功响应、未知状态/负 usage 和固定报告。
</section>

<section id="modify-model-boundary" data-learning-context="modify-model-boundary" data-context-type="modify" markdown="1">
## 主动增加一个“服务失败”状态

1. 给 `ScriptedAdapter` 增加一次 provider 超时。
2. 不要把超时塞进 `ModelResult.text`；先设计异常或失败类型。
3. 写测试证明失败不会被显示为模型答案。
4. 记录这个失败能否重试、由谁决定、最多重试几次。

本课只发现边界，不立即实现重试。第 4 课会用 deadline、错误类别和尝试预算完成有界恢复。
</section>

<section id="troubleshoot-model-boundary" data-learning-context="troubleshoot-model-boundary" data-context-type="troubleshoot" markdown="1">
## 先判断坏在调用前、provider 还是归一化

| 现象 | 检查位置 | 恢复 |
| --- | --- | --- |
| adapter 根本没有调用 | `validate_request` | 检查消息顺序、空内容和输出上限 |
| HTTP 成功但界面空白 | completed 文本门禁 | 空文本拒绝，不标记成功 |
| 截断内容被保存为答案 | status / finish reason | 保留 incomplete，不进入完成态 |
| 拒绝文字像普通建议 | refusal 映射 | 使用独立状态与界面分支 |
| usage 为负或缺失 | provider 映射 | 拒绝不可能的计量数据 |
| 调试日志出现用户问题 | 日志字段 | 只记状态、计量和内部 request ID |
</section>

<section id="deepen-provider-differences" data-learning-context="deepen-provider-differences" data-context-type="deepen" markdown="1">
## 归一化不能抹掉重要差异

统一接口不是把所有 provider 压成一个字符串。应用真正依赖的状态、usage、结束原因和 request ID 必须保留；provider 独有但暂时不用的字段，应留在 adapter 内而不是泄漏到业务层。

官方接口会演进，课程不把某个云端字段名固化为永恒事实。v0.1 的固定单位叫 `input_units/output_units`，后续真实 adapter 才明确怎样映射 token 计量。
</section>

<section id="project-learning-assistant-v01" data-learning-context="project-learning-assistant-v01" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.1 v0.1

- 上一版：只有项目路线，没有正式模型调用边界。
- 本课新增：消息、请求、provider response、归一化结果、离线 adapter 和 8 项测试。
- 文件：`model_boundary.py` 与 `test_model_boundary.py`。
- 保存：固定报告、一次新增失败状态的设计和测试。
- 下一版：冻结 Prompt role、模板版本、生成参数与上下文预算，让同一请求可审计。
</section>

## 四类学习者入口

- 零基础兴趣：先沿请求链标出“谁负责验证、谁负责生成”。
- 有基础兴趣：实现第二个 adapter，并证明业务函数无须修改。
- 零基础求职：只陈述自己能证明的项目事实：状态分层、调用前校验和离线回归。
- 有基础求职：解释统一接口保留哪些差异，以及为什么不把 provider JSON 直接传遍业务层；本组没有招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 和固定报告通过。
- system/user 消息分开，非法请求在 adapter 调用前拒绝。
- completed、refused、incomplete 均有独立结果。
- completed 空文本、未知状态和负 usage 被拒绝。
- 日志契约不记录 Authorization、原始 Prompt 或原始回复。
- 能解释离线 adapter 证明的是应用逻辑，不是模型质量。

## 来源与版本

- 核查日期：2026-07-26。
- 适用环境：Python 3.11+ 标准库；自动测试离线。
- [OpenAI Responses API reference](https://platform.openai.com/docs/api-reference/responses)
- [DeepSeek Create Chat Completion](https://api-docs.deepseek.com/api/create-chat-completion)
- [Python typing.Protocol](https://docs.python.org/3.11/library/typing.html#typing.Protocol)

## 下一步

进入第 2 课，把 Prompt 角色、模板版本、生成参数和上下文预算冻结成可审计请求快照。
