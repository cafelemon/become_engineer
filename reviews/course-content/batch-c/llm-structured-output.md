# LLM：把一句话变成可靠数据

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-llm-structured-output" aria-hidden="true"></div>

<section id="overview-llm-json" class="be-sample-hero" data-learning-context="overview-llm-json" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">LLM 应用起步 · 智能学习助手 P5.1</span>

## 一句话，先整理成四个字段

> 我想转行学 Python，每周能学 8 小时，目前刚起步。

```json
{
  "goal": "job",
  "topic": "Python",
  "weekly_hours": 8,
  "current_level": "beginner"
}
```

人读第一句话很自然，程序却很难稳定地从中取值。LLM 可以提出一份 JSON，但这份 JSON 还不能直接进入业务代码。它可能少字段、写错类型，甚至返回空内容。

<div class="be-sample-actions" markdown="1">
[先看谁负责哪一段](#concept-llm-boundary){ .md-button .md-button--primary }
[试几种模型回复](#reproduce-llm-fixtures){ .md-button }
</div>

</section>

<section id="concept-llm-boundary" class="be-sample-learning-unit" data-learning-context="concept-llm-boundary" data-context-type="concept" markdown="1">

## 模型提出，程序检查

<div class="be-data-flow" role="img" aria-label="自然语言经过模型生成 JSON，再由程序解析和校验">
  <div><strong>自然语言</strong><span>学习者按自己的方式表达</span></div>
  <div><strong>LLM</strong><span>尝试整理成 JSON</span></div>
  <div><strong>解析与校验</strong><span>检查语法、字段和取值</span></div>
  <div><strong>业务对象</strong><span>只有合格数据才能进入下一步</span></div>
</div>

这条分工很关键：LLM 不是数据库，也不是类型检查器。即使开启 JSON 模式，应用仍然要处理空响应和不合格字段。

</section>

<section id="example-llm-schema" class="be-sample-learning-unit" data-learning-context="example-llm-schema" data-context-type="example" markdown="1">

## 用 Schema 把约定写进代码

```python
class LearningRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal: Literal["interest", "job"]
    topic: str = Field(min_length=1, max_length=60)
    weekly_hours: int = Field(ge=1, le=40)
    current_level: Literal["beginner", "basic"]
```

`extra="forbid"` 会拒绝未约定字段。这样模型即使额外返回电话号码、备注或其他内容，也不会被程序悄悄接收。

`weekly_hours` 限制在 1 到 40，不是说任何人最多只能学 40 小时，而是这个样板先给输入一个清楚、可解释的范围。

</section>

<section id="reproduce-llm-fixtures" class="be-sample-learning-unit" data-learning-context="reproduce-llm-fixtures" data-context-type="reproduce" markdown="1">

## 不用密钥，也能把失败跑全

```bash
.venv/bin/python \
  reviews/course-content/batch-c/examples/llm-structured-output/structured_output.py \
  --case valid

.venv/bin/python \
  reviews/course-content/batch-c/examples/llm-structured-output/structured_output.py \
  --case wrong-type
```

下面这些内容都是固定样本，不会访问网络：

<div class="be-fixture-demo" data-fixture-demo>
  <div class="be-fixture-demo__controls">
    <button type="button" data-fixture="valid">正确 JSON</button>
    <button type="button" data-fixture="wrong">类型错误</button>
    <button type="button" data-fixture="extra">多余字段</button>
    <button type="button" data-fixture="empty">空响应</button>
  </div>
  <div class="be-fixture-result" data-fixture-result aria-live="polite">
    <strong>先选一个回复</strong><p>观察应用接受还是拒绝，以及理由是否说得清楚。</p>
  </div>
  <script type="application/json">{
    "valid":{"title":"通过校验","message":"四个字段都符合约定，可以生成 LearningRequest。","content":"{\"goal\":\"job\",\"topic\":\"Python\",\"weekly_hours\":8,\"current_level\":\"beginner\"}"},
    "wrong":{"title":"拒绝：weekly_hours 类型不对","message":"程序需要整数，不能把“很多”直接当作小时数。","content":"{\"weekly_hours\":\"很多\"}"},
    "extra":{"title":"拒绝：出现未约定字段","message":"phone 不属于 LearningRequest，不会被悄悄保存。","content":"{\"phone\":\"13800000000\"}"},
    "empty":{"title":"拒绝：模型没有返回内容","message":"空响应是一次正常失败，应用需要提示重试或补充信息。","content":""}
  }</script>
</div>

</section>

<section id="modify-llm-request" class="be-sample-learning-unit" data-learning-context="modify-llm-request" data-context-type="modify" markdown="1">

## 换一种说法，再补一条规则

把输入改成：“我会一点 C++，想按兴趣学算法，每周 4 小时。”先自己写出期望 JSON，再修改固定样本验证：

```json
{
  "goal": "interest",
  "topic": "算法",
  "weekly_hours": 4,
  "current_level": "basic"
}
```

接着把 `topic` 改成空字符串，确认程序拒绝它。提示词可以提醒模型，但最终约束仍然在 Schema 里。

</section>

<section id="troubleshoot-llm-output" class="be-sample-learning-unit" data-learning-context="troubleshoot-llm-output" data-context-type="troubleshoot" markdown="1">

## JSON 看起来像，不代表真的能用

| 模型返回 | 应用怎样处理 |
| --- | --- |
| 空字符串 | 提示没有内容，可以重试 |
| 少一个右花括号 | JSON 解析失败，不进入字段校验 |
| `weekly_hours: "8"` | 类型不符合严格约定，拒绝 |
| 多出 `phone` | 未约定字段，拒绝 |
| 缺少 `current_level` | 信息不足，回到用户补问 |

这里先别急着做“自动修复所有错误”。有些错误可以重试，有些需要向学习者补问。应用必须知道自己为什么继续，而不是把坏数据改得看似合理。

</section>

<section id="project-llm-p51" class="be-sample-project-panel" data-learning-context="project-llm-p51" data-context-type="project" markdown="1">

## 智能学习助手先学会可靠地收资料

这是 P5.1 的起点：助手还没有检索知识，也不会调用工具。它先把学习需求整理成程序能检查的对象。

真实 DeepSeek 调用是可选的：安装 `requirements-deepseek.txt`，在本机设置新生成的 `DEEPSEEK_API_KEY`、`DEEPSEEK_MODEL`，再增加 `--use-deepseek`。密钥不要写进 `.env.example`、页面或日志。

```bash
.venv/bin/python reviews/course-content/batch-c/examples/llm-structured-output/structured_output.py \
  --use-deepseek \
  --prompt "我想转行学 Python，每周能学 8 小时，目前刚起步。"
```

</section>

## 完成检查

- [ ] 能说清模型和应用各自负责什么。
- [ ] 能用固定样本复现五种失败。
- [ ] 能解释为什么 JSON 模式以后仍要校验。
- [ ] 能修改一条学习需求，并写出期望 JSON。
- [ ] 知道密钥只能从本机环境变量读取。

下一页：[Agent：安全查询一门课程](agent-read-only-tool.md)。

参考：[DeepSeek JSON Output](https://api-docs.deepseek.com/guides/json_mode/) · [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)
