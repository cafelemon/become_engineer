# Agent：安全查询一门课程

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-agent-read-only-tool" aria-hidden="true"></div>

<section id="overview-agent-answer" class="be-sample-hero" data-learning-context="overview-agent-answer" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">Agent 工程起步 · 智能学习助手 P5.5</span>

## “Python 变量课开放了吗？”

```text
找到课程《变量、基本类型与输入输出》，状态：已开放。
```

这句话不是模型凭记忆猜的。模型先提出调用 `get_course_summary`，程序检查工具名和参数，再从固定课程目录读取结果。只有这一步成功，模型才能据此回答。

<div class="be-sample-actions" markdown="1">
[单步看一次调用](#concept-agent-loop){ .md-button .md-button--primary }
[运行离线版本](#reproduce-agent-offline){ .md-button }
</div>

</section>

<section id="concept-agent-loop" class="be-sample-learning-unit" data-learning-context="concept-agent-loop" data-context-type="concept" markdown="1">

## 模型没有直接执行工具

<div class="be-tool-flow" role="img" aria-label="模型提出工具调用，应用校验后执行只读查询，再把结果交回模型">
  <div><strong>用户提问</strong><span>查询课程状态</span></div>
  <div><strong>模型提出调用</strong><span>工具名与 JSON 参数</span></div>
  <div><strong>应用校验并执行</strong><span>只读固定课程目录</span></div>
  <div><strong>结果回给模型</strong><span>依据真实数据回答</span></div>
</div>

<div class="be-live-demo" data-trace-demo>
  <div class="be-trace-stage" data-trace-stage></div>
  <div class="be-trace-controls">
    <button type="button" data-trace-previous>上一步</button>
    <button type="button" data-trace-next>下一步</button>
    <button type="button" data-trace-reset>重置</button>
    <span data-trace-position aria-live="polite"></span>
  </div>
  <script type="application/json">[
    {"title":"1. 用户提问","body":"帮我查 Python 变量课现在是否开放。","code":"role=user"},
    {"title":"2. 模型提出调用","body":"模型只提出意图，不直接读取文件。","code":"get_course_summary({\"course_id\":\"python-basics-01\"})"},
    {"title":"3. 应用检查并查询","body":"工具名在白名单里，参数只有 course_id，ID 格式正确。","code":"status=已开放"},
    {"title":"4. 结果关联原调用","body":"tool_call_id 让模型知道这份结果回答的是哪次调用。","code":"tool_call_id=call_offline_001"},
    {"title":"5. 生成最后回答","body":"模型依据工具结果组织自然语言，不再猜课程状态。","code":"找到课程《变量、基本类型与输入输出》，状态：已开放。"}
  ]</script>
</div>

<noscript>

| 顺序 | 发生什么 |
| --- | --- |
| 1 | 用户询问课程状态 |
| 2 | 模型提出 `get_course_summary` 调用 |
| 3 | 应用校验工具名、参数和课程 ID |
| 4 | 固定课程目录返回只读结果 |
| 5 | 模型依据结果回答 |

</noscript>

</section>

<section id="example-agent-tool" class="be-sample-learning-unit" data-learning-context="example-agent-tool" data-context-type="example" markdown="1">

## 工具只接受一个字段

```json
{
  "name": "get_course_summary",
  "arguments": {
    "course_id": "python-basics-01"
  }
}
```

课程目录路径写在程序里，模型不能传入 `path`，也不能要求执行 SQL 或终端命令。查询返回标题、状态、前置和公开 URL，不修改任何数据。

这是一种刻意做小的能力。工具越少、参数越明确，权限和错误越容易检查。

</section>

<section id="reproduce-agent-offline" class="be-sample-learning-unit" data-learning-context="reproduce-agent-offline" data-context-type="reproduce" markdown="1">

## 先跑离线调用记录

```bash
.venv/bin/python \
  reviews/course-content/batch-c/examples/agent-read-only-tool/agent_tool.py \
  --course-id python-basics-01
```

离线模式会打印三段内容：`tool_call`、`tool_result` 和最后回答。它不需要 API Key，也不会访问网络。

再换成 BFS：

```bash
.venv/bin/python \
  reviews/course-content/batch-c/examples/agent-read-only-tool/agent_tool.py \
  --course-id cs-core-19
```

</section>

<section id="modify-agent-catalog" class="be-sample-learning-unit" data-learning-context="modify-agent-catalog" data-context-type="modify" markdown="1">

## 给目录增加一门课

打开 `data/course_catalog.json`，增加一条使用新 `course_id` 的记录，再用离线命令查询。修改前先确认：

- ID 只含小写字母、数字和连字符。
- URL 指向公开页面，不指向本机文件。
- 状态与页面实际情况一致。

如果模型传入课程标题而不是课程 ID，当前工具会拒绝。模糊搜索应该以后作为另一个单独工具设计，不塞进这一课。

</section>

<section id="troubleshoot-agent-safety" class="be-sample-learning-unit" data-learning-context="troubleshoot-agent-safety" data-context-type="troubleshoot" markdown="1">

## 四种输入都应该停下来

| 提出的调用 | 为什么拒绝 |
| --- | --- |
| `read_file(...)` | 工具没有注册 |
| `get_course_summary({"path":"/etc/passwd"})` | 参数字段不在 Schema 中 |
| `course_id="../secret"` | ID 格式不合法 |
| `course_id="not-built-99"` | 固定目录里没有这门课 |

拒绝不是系统“笨”，而是权限设计正在工作。如果一个工具允许模型传任意文件路径，它就已经超出了查询课程的职责。

</section>

<section id="project-agent-p55" class="be-sample-project-panel" data-learning-context="project-agent-p55" data-context-type="project" markdown="1">

## 智能学习助手第一次使用外部能力

LLM 样板只整理输入；这一页让助手查询固定课程目录。它仍然没有自由规划、长期记忆或写入权限。

真实 DeepSeek 调用沿用同一份白名单和校验。设置新的本机 Key 并安装可选依赖后运行：

```bash
.venv/bin/python reviews/course-content/batch-c/examples/agent-read-only-tool/agent_tool.py \
  --use-deepseek \
  --prompt "请查询 course_id 为 python-basics-01 的课程状态"
```

这页只处理“按课程 ID 查状态”这一种请求。系统提示会明确要求模型先查目录；如果模型绕过工具直接回答，应用就拒绝继续。模型即使提出了调用，参数也仍然不可信，程序照样检查字段、格式和课程是否存在。

真实调用最多进行两轮模型交互、执行一次工具。自动测试永远使用离线记录，不产生 API 费用，也不依赖模型状态。

</section>

## 完成检查

- [ ] 能复述用户、模型、应用和工具的职责。
- [ ] 能运行离线调用并找到 `tool_call_id`。
- [ ] 能解释为什么不能提供任意文件读取工具。
- [ ] 能增加一条课程记录并成功查询。
- [ ] 能确认四类危险或错误输入都被拒绝。

回到：[批次 C 评审说明](README.md)。

参考：[DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/) · [OpenAI 兼容 API 入门](https://api-docs.deepseek.com/)
