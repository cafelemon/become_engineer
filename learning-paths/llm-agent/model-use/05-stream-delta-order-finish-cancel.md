<div class="be-tutor-mount" data-tutor-lesson="llm-use-05" aria-hidden="true"></div>
<section id="overview-stream-lifecycle" class="be-page-hero be-lesson-hero" data-learning-context="overview-stream-lifecycle" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">模型使用与结构化输出 · 第 5 / 6 课 · 智能学习助手 P5.1 v0.5</span>
# 流事件、Delta 顺序、终止原因与取消
## 屏幕已经有字，不代表响应已经完成
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
completed=status:completed,text:学习计划,finish:stop,events:4
incomplete=status:incomplete,partial:未完,finish:max_output
cancelled=status:cancelled,partial:部分,finish:client_cancelled
ordering=sequence:start-zero,strict-contiguous,duplicate:false,gap:false
terminal=completed|refused|incomplete|cancelled,required:true,event-after-terminal:false
assembly=delta-order:preserved,empty-delta:false,max-chars:bounded,partial-is-complete:false
rendering=plain-text-first,html-trust:false,json-parse:after-terminal-only
logs=delta:none,assembled-text:none,event-kind:allowed,sequence:allowed,status:allowed
invariants=created-first,one-terminal,cancel-stops-consumption,no-rag,no-tools
```
v0.5 把流式响应建模为有序事件协议。只有 `response.completed` 加 `finish_reason=stop` 才能产生完成结果；截断和取消可以保留部分文本，但绝不能进入完成路径。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>LLM 应用起步 · 5 / 6</strong></div>
  <div><span>前置</span><strong>模型状态、有界失败恢复</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 离线事件流</strong></div>
  <div><span>完成后留下</span><strong>流组装器、取消边界与 8 项测试</strong></div>
</div>

## 学习目标

- 用 created、delta 和唯一终止事件表达响应生命周期。
- 用从 0 开始的连续序号拒绝重复、缺口和乱序。
- 区分 completed、refused、incomplete 与 cancelled。
- 保留截断和取消时的部分文本，但不把它当作完整业务结果。
- 给累积内容设置上限，并在终止后才解析 JSON。
- 取消后停止消费；日志只记录事件类型、序号和状态。

<section id="concept-stream-protocol" data-learning-context="concept-stream-protocol" data-context-type="concept" markdown="1">
## 流是一份协议，不是一串随意字符串

```text
response.created
  -> output_text.delta*
  -> exactly one terminal
```

第一条必须创建响应，delta 只能追加，最后必须有 completed、refused 或 incomplete。客户端主动取消形成第四种本地终止状态。没有终止事件的连接关闭属于 `missing_terminal`。
</section>

<section id="concept-partial-not-complete" data-learning-context="concept-partial-not-complete" data-context-type="concept" markdown="1">
## 部分文本可以展示，不能提交

`max_output` 截断前可能已经产生“未完”，取消前也可能已有“部分”。界面可以标记为未完成后展示，但业务层不能保存为完整学习计划，更不能在每个 delta 到达时尝试解析 JSON。

流式结构化输出应先收齐并确认完成，再运行第 3 课的严格解析器。
</section>

<section id="example-stream-state-machine" data-learning-context="example-stream-state-machine" data-context-type="example" markdown="1">
## 序号和终止状态共同守住边界

```python
if event.sequence != expected_sequence:
    raise StreamProtocolError("sequence_mismatch", ...)
if terminal is not None:
    raise StreamProtocolError("event_after_terminal", ...)
if event.kind == "output_text.delta":
    append_with_bound(event.delta)
elif event.kind == "response.completed":
    require_finish_reason_stop()
```

重复序号和跳号都返回同一稳定代码，但错误信息保留期望值与实际值。终止后任何新事件都被拒绝。
</section>

<section id="reproduce-stream-v05" data-learning-context="reproduce-stream-v05" data-context-type="reproduce" markdown="1">
## 回放完成、截断、拒绝与取消

```bash
cd site-src/examples/llm-use/intelligent-learning-assistant-v05
python3 -m unittest -v test_stream_assembler.py
python3 stream_assembler.py
```

8 项测试覆盖精确拼接、乱序/重复、created 生命周期、截断、拒绝、取消、累积上限、缺终止和固定脱敏报告。它验证事件消费者，不虚构真实 provider 网络。
</section>

<section id="modify-stream-renderer" data-learning-context="modify-stream-renderer" data-context-type="modify" markdown="1">
## 给界面增加明确的四态渲染

1. completed 显示“完成”，允许进入 Schema 校验。
2. incomplete 显示“内容被截断”，保留部分文本但禁用提交。
3. refused 显示拒绝原因类别，不展示伪造正文。
4. cancelled 显示“已取消”，停止 spinner 与后续消费。
5. 所有文本先按 plain text 渲染；若以后支持 Markdown，单独设计可信边界。

为每种状态写一个视图测试，不能只测试成功颜色。
</section>

<section id="troubleshoot-stream-events" data-learning-context="troubleshoot-stream-events" data-context-type="troubleshoot" markdown="1">
## 从首个违反协议的事件定位

| 错误代码 | 常见原因 |
| --- | --- |
| `missing_created` | 订阅从中间开始或事件映射漏掉 created |
| `sequence_mismatch` | 重复投递、事件丢失或并发消费乱序 |
| `missing_terminal` | 连接断开却被当作正常结束 |
| `event_after_terminal` | 取消/完成后仍继续读取 |
| `output_too_large` | 没有累计上限或 provider 输出失控 |
| `partial_before_refusal` | 事件映射把拒绝与文本混成一个成功流 |
</section>

<section id="deepen-provider-stream-map" data-learning-context="deepen-provider-stream-map" data-context-type="deepen" markdown="1">
## Provider 事件名可以不同，领域状态要稳定

不同接口可能使用 SSE、不同事件名、不同 finish reason 或不同取消机制。provider adapter 负责把它们映射成这套内部协议；业务代码不应到处判断某家供应商的原始字符串。

序号若由应用生成，只能证明本地观察顺序；若协议提供原始 event ID，还应另行保存用于断线恢复和去重。本课不实现自动续流。
</section>

<section id="project-learning-assistant-v05" data-learning-context="project-learning-assistant-v05" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.1 v0.5

- 上一版：v0.4 能在三层预算内恢复瞬时故障。
- 本课新增：严格事件序号、delta 组装、四种终止状态、取消和内容上限。
- 文件：`stream_assembler.py` 与 `test_stream_assembler.py`。
- 保存：三条固定流轨迹、8 项测试和一次四态界面修改。
- 下一版：接入环境配置、短期进程秘密、脱敏审计和可选真实 provider 验收。
</section>

## 四类学习者入口

- 零基础兴趣：拿四张事件卡按顺序拼出“学习计划”。
- 有基础兴趣：增加 adapter，把另一种事件名映射到稳定领域协议。
- 零基础求职：解释为何“页面有字”仍可能是 incomplete。
- 有基础求职：说明取消、序号、终止事件和结构化解析的边界；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- created 必须第一且唯一，序号从 0 连续增长。
- 完成、拒绝、截断和取消不会互相冒充。
- 取消后与终止后都不再接受事件。
- 部分文本有累积上限，只有 completed 才能进入结构化解析。
- 界面按 plain text 处理内容，日志不保存 delta 或拼接正文。

## 来源与版本

- 核查日期：2026-07-26。
- 适用环境：Python 3.11+ 标准库；自动测试使用离线事件。
- [OpenAI Streaming API responses](https://platform.openai.com/docs/api-reference/responses-streaming)
- [OpenAI Streaming guide](https://platform.openai.com/docs/guides/streaming-responses)
- [HTML Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html)

## 下一步

进入第 6 课，完成 provider 配置、秘密边界、脱敏日志、CLI 交付和整组六课验收。
