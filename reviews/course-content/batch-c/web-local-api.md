# Web：浏览器怎样拿到学习数据

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-web-local-api" aria-hidden="true"></div>

<section id="overview-web-card" class="be-sample-hero" data-learning-context="overview-web-card" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">Web 起步 · 学习进度报告器 Web v0.1</span>

## 先让浏览器拿到这份报告

```json
{
  "learner_name": "小码",
  "completed_lessons": 4,
  "planned_lessons": 7,
  "completed_hours": 6.5,
  "status": "按计划推进"
}
```

之前的学习进度报告器只能在终端里打印。现在我们把同一份信息交给 FastAPI，再让浏览器来取。页面不会直接碰 Python 变量，它只认识一次 HTTP 响应。

<div class="be-sample-actions" markdown="1">
[先看数据走了哪条路](#concept-web-flow){ .md-button .md-button--primary }
[启动本地 API](#reproduce-web-api){ .md-button }
</div>

</section>

<section id="concept-web-flow" class="be-sample-learning-unit" data-learning-context="concept-web-flow" data-context-type="concept" markdown="1">

## 浏览器和 Python 中间隔着 HTTP

<div class="be-data-flow" role="img" aria-label="浏览器通过 HTTP 请求 FastAPI，再由 Python 返回 JSON">
  <div><strong>浏览器</strong><span>发出 GET 请求</span></div>
  <div><strong>HTTP</strong><span>带着路径和状态码</span></div>
  <div><strong>FastAPI</strong><span>找到对应 Python 函数</span></div>
  <div><strong>JSON</strong><span>把结果送回浏览器</span></div>
</div>

这条请求是：

```http
GET /api/learning-summary/xiaoma
```

路径告诉服务“要做什么”和“查谁”。返回的 `200` 表示成功；找不到学习者时返回 `404`。浏览器不能只看 JSON，也要先看状态码。

</section>

<section id="example-web-contract" class="be-sample-learning-unit" data-learning-context="example-web-contract" data-context-type="example" markdown="1">

## API 先约好返回哪些字段

```python
class LearningSummary(BaseModel):
    learner_id: str
    learner_name: str
    completed_lessons: int
    planned_lessons: int
    completed_hours: float
    status: Literal["起步中", "按计划推进", "本周已完成"]
```

这个类既是 Python 类型，也是接口契约。假如代码把 `completed_lessons` 错写成一段文字，FastAPI 会在结果离开服务前发现问题。

浏览器侧不需要知道 `LearningSummary` 怎样实现，只要按约定读取字段：

```javascript
const response = await fetch("http://127.0.0.1:8780/api/learning-summary/xiaoma");
const summary = await response.json();
console.log(summary.status);
```

</section>

<section id="reproduce-web-api" class="be-sample-learning-unit" data-learning-context="reproduce-web-api" data-context-type="reproduce" markdown="1">

## 在本地把两端都启动

先安装批次 C 的离线依赖：

```bash
.venv/bin/pip install -r reviews/course-content/batch-c/requirements.txt
```

另开一个终端启动 API：

```bash
.venv/bin/uvicorn app:app \
  --app-dir reviews/course-content/batch-c/examples/web-api \
  --host 127.0.0.1 --port 8780
```

看到 `Uvicorn running on http://127.0.0.1:8780` 后，先打开健康检查：

```text
http://127.0.0.1:8780/api/health
```

再回到本页点按钮：

<div class="be-live-demo" data-api-demo>
  <div class="be-live-demo__controls">
    <button type="button" data-learner-id="xiaoma">读取小码</button>
    <button type="button" data-learner-id="afei">读取阿飞</button>
    <button type="button" data-learner-id="nobody">试一个不存在的 ID</button>
  </div>
  <div class="be-api-result" data-api-result aria-live="polite">
    <strong>还没有发请求</strong>
    <p>如果 JavaScript 被禁用，直接在浏览器打开 API 地址也能查看 JSON。</p>
  </div>
</div>

</section>

<section id="modify-web-record" class="be-sample-learning-unit" data-learning-context="modify-web-record" data-context-type="modify" markdown="1">

## 加一条自己的学习记录

打开 `examples/web-api/app.py`，在 `SUMMARIES` 里增加一项。`learner_id` 只用小写字母、数字和连字符：

```python
"my-profile": LearningSummary(
    learner_id="my-profile",
    learner_name="你的名字",
    completed_lessons=2,
    planned_lessons=5,
    completed_hours=3.5,
    status="起步中",
),
```

Uvicorn 默认不会自动重载。停掉服务再启动，然后把浏览器请求里的 ID 换成 `my-profile`。如果想在开发时自动重载，可以显式增加 `--reload`，但不要把它当生产运行方式。

</section>

<section id="troubleshoot-web-request" class="be-sample-learning-unit" data-learning-context="troubleshoot-web-request" data-context-type="troubleshoot" markdown="1">

## 页面没有数据，先分清是哪一边停了

| 看到什么 | 意味着什么 | 先做什么 |
| --- | --- | --- |
| 浏览器提示无法连接 | 8780 端口没有服务 | 回到终端检查 Uvicorn |
| `404` | 服务在，但没有这条记录 | 检查 ID 拼写 |
| `422` | ID 没通过接口校验 | 改成规定格式 |
| 控制台出现 CORS | 页面来源没有被 API 允许 | 确认评审站点是 8768 |
| JSON 有值但卡片没变 | 前端取错字段或没有更新 DOM | 看浏览器开发者工具 |

我更建议按“网络 → 状态码 → JSON → 页面渲染”的顺序查。这样不会一看到空白页，就同时改前后端。

</section>

<section id="project-web-entry" class="be-sample-project-panel" data-learning-context="project-web-entry" data-context-type="project" markdown="1">

## 学习进度报告器有了 Web 入口

终端版和 Web 版可以共用同一套报告计算，区别只是把结果交给谁。后面加入数据库时，API 契约仍然可以保持不变。

| 原来 | 这次加上 | 暂时不做 |
| --- | --- | --- |
| 终端打印报告 | 浏览器读取 JSON | 登录和用户数据库 |
| Python 内部调用 | HTTP 接口 | 前端框架 |
| 运行一次看结果 | 成功与错误状态 | 公网部署 |

</section>

## 完成检查

- [ ] 能启动 API，并在浏览器看到健康检查。
- [ ] 能说清浏览器、HTTP、FastAPI 和 JSON 的顺序。
- [ ] 能分别解释 `200`、`404` 和服务未启动。
- [ ] 能增加一条本地记录，并从浏览器重新读到它。
- [ ] 知道接口契约为什么不该随意改字段。

下一页：[AI：第一次训练与验证](ai-reproducible-experiment.md)。

参考：[FastAPI 官方教程](https://fastapi.tiangolo.com/tutorial/) · [MDN Fetch API](https://developer.mozilla.org/docs/Web/API/Fetch_API)
