<div class="be-tutor-mount" data-tutor-lesson="web-start-04" aria-hidden="true"></div>

<section id="overview-first-api-response" class="be-page-hero be-lesson-hero" data-learning-context="overview-first-api-response" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Web 起步 · 第四课 · 学习进度报告器 Web v0.4</span>

# HTTP、JSON 与本地 API

## 页面里的数据，第一次来自 Python

```http
GET /api/learning-summary/xiaoma

HTTP/1.1 200 OK
Content-Type: application/json

{
  "learner_name": "小码",
  "completed_lessons": 7,
  "completed_hours": 6.5,
  "status": "按计划推进"
}
```

上一课把学习记录写在 `app.js` 里。现在 Python 保存记录，FastAPI 把它变成 HTTP 响应，浏览器再用 `fetch()` 取回 JSON。页面的样子没推翻，数据来源换了。

<div class="be-page-actions" markdown="1">
[先看数据走了哪条路](#concept-browser-http-api-json){ .md-button .md-button--primary }
[启动 v0.4](#reproduce-dashboard-v04){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Web 起步 · 4 / 4</strong></div>
  <div><span>开始条件</span><strong>能解释事件、状态与 render()</strong></div>
  <div><span>完成后留下</span><strong>FastAPI、页面、接口测试与故障记录</strong></div>
</div>

## 开始前

- 第一次接触后端服务，按本课命令启动一个地址即可。这里先不加入数据库、登录、前端框架或公网部署。
- 已有基础者先做跳过检查：独立写出带响应模型的 `GET` 接口，让页面处理 `200`、`404`、`422`、`503` 和断线，并用测试证明接口契约。全部做到即可进入 Web 核心。
- 继续使用 `practice/web-start/learning-dashboard/`。这次会增加 Python 文件和依赖文件，不另建一个失去前三课样式与状态处理的 Demo。

<section id="concept-browser-http-api-json" data-learning-context="concept-browser-http-api-json" data-context-type="concept" markdown="1">

## 浏览器不会直接读取 Python 变量

<div class="be-data-flow" role="img" aria-label="浏览器发出 HTTP GET 请求，FastAPI 调用 Python 函数，再把学习记录序列化为 JSON 响应">
  <div><strong>浏览器</strong><span>发出 GET 请求</span></div>
  <div><strong>HTTP</strong><span>路径、状态码和正文</span></div>
  <div><strong>FastAPI</strong><span>调用 Python 函数</span></div>
  <div><strong>JSON</strong><span>把结果送回页面</span></div>
</div>

在同一台电脑上，这条路仍然存在：

```text
http://127.0.0.1:8780/api/learning-summary/xiaoma
```

- `127.0.0.1` 表示当前电脑。
- `8780` 是这次练习使用的端口。
- `/api/learning-summary/xiaoma` 是请求路径，其中 `xiaoma` 是学习者 ID。

HTTP 负责传递请求和响应，JSON 只是响应正文的一种文本格式。不要把“HTTP 接口”和“JSON 文件”当成同一件事。

</section>

<section id="concept-status-before-json" data-learning-context="concept-status-before-json" data-context-type="concept" markdown="1">

## 先看状态码，再决定怎样读正文

同一条接口可能返回不同结果：

| 状态码 | 这次请求发生了什么 | 页面进入什么状态 |
| --- | --- | --- |
| `200` | 找到记录，正文符合约定 | `success` |
| `404` | 接口存在，但没有这个 ID | `empty` |
| `422` | ID 没通过格式检查 | `error` |
| `503` | 服务暂时不能完成请求 | `error` |
| 没有响应 | 服务没启动、已停止或连接失败 | `error` |

`fetch()` 遇到 `404` 时通常仍会得到一个 `Response`，不会自动进入 `catch`。所以页面必须检查 `response.status` 或 `response.ok`，不能只等待 JSON。

```javascript
const response = await fetch("/api/learning-summary/xiaoma");

if (response.status === 404) {
  return { kind: "empty", message: "没有这位学习者。" };
}

if (!response.ok) {
  return { kind: "error", message: `API 返回 ${response.status}` };
}
```

</section>

<section id="example-response-contract" data-learning-context="example-response-contract" data-context-type="example" markdown="1">

## Python 先把响应约好

`LearningSummary` 列出浏览器可以收到的字段和类型：

```python
class LearningSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    learner_id: str
    learner_name: str
    description: str
    completed_lessons: int
    completed_hours: float
    status: Literal["起步中", "按计划推进", "本周已完成"]
    next_milestone: str
```

接口声明返回这个模型：

```python
@app.get("/api/learning-summary/{learner_id}", response_model=LearningSummary)
def learning_summary(learner_id: Annotated[str, ApiPath(pattern=r"^[a-z0-9-]{3,32}$")]) -> LearningSummary:
    summary = SUMMARIES.get(learner_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="没有找到这位学习者")
    return summary
```

这份模型是接口契约，不是数据库。它能检查返回数据、生成接口文档，也能限制响应只保留声明过的字段。当前记录仍在内存字典里，重启后会回到源代码中的内容。

</section>

<section id="example-fetch-and-render" data-learning-context="example-fetch-and-render" data-context-type="example" markdown="1">

## fetch 只负责取数据，render 继续负责页面

```javascript
async function fetchSummary(profileId, fetchImpl) {
  const response = await fetchImpl(
    `/api/learning-summary/${encodeURIComponent(profileId)}`,
    { headers: { Accept: "application/json" } }
  );

  if (response.status === 404) {
    return { kind: "empty", message: "API 正常响应，但没有找到这位学习者。" };
  }
  if (!response.ok) {
    return { kind: "error", message: `API 返回 ${response.status}` };
  }

  const summary = await response.json();
  return { kind: "success", record: summaryToRecord(summary) };
}
```

按钮点击后的主线没有变：

```text
click → loading → fetch → response → JSON → success / empty / error → render
```

`fetchSummary()` 不碰 DOM，`render()` 不发网络请求。测试时可以给 `fetchSummary()` 一份假的 `fetchImpl`，不需要真的占用端口；在浏览器里再用真实 `fetch` 做最后验证。

</section>

<section id="reproduce-dashboard-v04" data-learning-context="reproduce-dashboard-v04" data-context-type="reproduce" markdown="1">

## 启动一个服务，打开一个地址

先把 v0.4 复制到练习目录：

=== "Windows PowerShell"

    ```powershell
    Copy-Item .\site-src\examples\web-start\learning-dashboard-v04\* `
      .\practice\web-start\learning-dashboard\ -Force
    ```

=== "macOS / Linux"

    ```bash
    cp site-src/examples/web-start/learning-dashboard-v04/* \
      practice/web-start/learning-dashboard/
    ```

目录现在包含前端和 API：

```text
learning-dashboard/
├── index.html
├── styles.css
├── app.js
├── app.py
├── test_app.py
├── requirements.txt
└── requirements-test.txt
```

安装本课依赖：

=== "Windows PowerShell"

    ```powershell
    .\.venv\Scripts\python.exe -m pip install `
      -r .\practice\web-start\learning-dashboard\requirements-test.txt
    ```

=== "macOS / Linux"

    ```bash
    .venv/bin/python -m pip install \
      -r practice/web-start/learning-dashboard/requirements-test.txt
    ```

启动服务：

=== "Windows PowerShell"

    ```powershell
    .\.venv\Scripts\python.exe -m uvicorn app:app `
      --app-dir .\practice\web-start\learning-dashboard `
      --host 127.0.0.1 --port 8780
    ```

=== "macOS / Linux"

    ```bash
    .venv/bin/python -m uvicorn app:app \
      --app-dir practice/web-start/learning-dashboard \
      --host 127.0.0.1 --port 8780
    ```

看到 `Uvicorn running on http://127.0.0.1:8780` 后，依次打开：

1. `http://127.0.0.1:8780/api/health`：应该看到版本与 `ok`。
2. `http://127.0.0.1:8780/api/learning-summary/xiaoma`：应该看到 JSON。
3. `http://127.0.0.1:8780/`：打开学习面板并依次点击五个按钮。
4. `http://127.0.0.1:8780/docs`：查看 FastAPI 生成的接口文档。

另开一个终端运行测试：

=== "Windows PowerShell"

    ```powershell
    .\.venv\Scripts\python.exe -m unittest discover `
      -s .\practice\web-start\learning-dashboard -p test_app.py -v
    node .\scripts\test_web_start_html_v2.mjs
    ```

=== "macOS / Linux"

    ```bash
    .venv/bin/python -m unittest discover \
      -s practice/web-start/learning-dashboard -p test_app.py -v
    node scripts/test_web_start_html_v2.mjs
    ```

按 `Ctrl+C` 可以停止服务。关闭 JavaScript 后，HTML 里的初始记录和直接访问 API 的路径仍然可用。

</section>

<section id="modify-add-api-record" data-learning-context="modify-add-api-record" data-context-type="modify" markdown="1">

## 加一条自己的记录，再让页面读到它

在 `app.py` 的 `SUMMARIES` 中增加：

```python
"my-profile": LearningSummary(
    learner_id="my-profile",
    learner_name="你的昵称",
    description="正在完成 Web 起步的最后一课。",
    completed_lessons=10,
    completed_hours=8.0,
    status="按计划推进",
    next_milestone="进入 Web 核心",
),
```

再在 `index.html` 增加 `data-profile-id="my-profile"` 的按钮。先只改 Python，不加按钮：直接访问 API，确认服务端记录已经存在；然后再补按钮，确认浏览器能显示它。

接着把 `completed_lessons` 故意写成字符串，例如 `"10"`，观察 Pydantic 是否接受转换；再使用一个明显错误的值，例如 `"十节"`，看服务为什么无法按契约启动或返回。最后恢复为整数并重跑测试。

</section>

<section id="troubleshoot-local-api" data-learning-context="troubleshoot-local-api" data-context-type="troubleshoot" markdown="1">

## 页面没更新，按请求走过的顺序查

| 看到什么 | 常见原因 | 怎样恢复 |
| --- | --- | --- |
| `No module named uvicorn` | 依赖装到了别的 Python | 用本项目 `.venv` 的 Python 安装并启动 |
| `Address already in use` | 8780 已有进程占用 | 停掉旧服务，或前后统一改成另一个端口 |
| 浏览器显示无法连接 | Uvicorn 没启动或已经停止 | 回到服务终端看最后一行日志 |
| `404` | 服务正常，但 ID 不存在 | 核对按钮的 `data-profile-id` 与 `SUMMARIES` 键 |
| `422` | ID 不满足小写字母、数字和连字符规则 | 修改 ID，不要绕过接口校验 |
| `503` | 服务收到请求，但暂时不能完成 | 保留旧数据隐藏状态，给出重试方向 |
| JSON 正常，页面仍是旧数据 | 前端字段名或 `render()` 契约没接上 | 在 Network 看响应，再检查 `summaryToRecord()` |
| 从磁盘双击 HTML 后请求异常 | 页面不在 FastAPI 的同一来源下 | 从 `http://127.0.0.1:8780/` 打开页面 |

我更建议按“服务是否活着 → 请求路径 → 状态码 → JSON → 页面映射”检查。一次只确认一层，别同时改 Python、路径和 DOM。

</section>

<section id="project-dashboard-v04" data-learning-context="project-dashboard-v04" data-context-type="project" markdown="1">

## Web 起步第一次闭环

| v0.3 已经会做 | Web v0.4 增加 | Web 核心继续做 |
| --- | --- | --- |
| 本地对象切换四种页面状态 | FastAPI 返回学习报告 | 把前后端契约拆成可维护模块 |
| render 统一更新 DOM | fetch 把 HTTP 结果映射成状态 | 加入 TypeScript 与组件边界 |
| 模拟空数据和错误 | 测试 200、404、422、503 与断线 | 接数据库、认证和更完整测试 |

保存这些结果：完整代码、六项 API 测试输出、五种请求结果截图，以及一次“JSON 正常但页面没更新”的排错记录。它们共同说明你不只会写页面，还能沿着一次请求定位问题。

</section>

<section id="deepen-same-origin-cors-contract" data-learning-context="deepen-same-origin-cors-contract" data-context-type="deepen" markdown="1">

## 再往里看：为什么本课只启动一个来源

本课的页面与 API 都来自 `http://127.0.0.1:8780`，协议、主机和端口相同，属于同一来源。这样第一次连接前后端时，不需要先配置 CORS。

如果以后把页面放在 `http://127.0.0.1:3000`，API 仍在 `8780`，浏览器会把它们视为不同来源。后端需要明确允许哪些来源、方法和请求头。不要为了省事永久允许所有来源；登录和凭据加入后，来源策略会成为安全边界的一部分。

响应模型也不是只为“自动补全”。它把服务内部对象和公开响应分开，能过滤未声明字段。后面加入用户数据时，密码、内部备注和调试信息不能因为“对象里刚好有”就被一起返回。

</section>

<section id="career-explain-api-failure" data-learning-context="career-explain-api-failure" data-context-type="career" markdown="1">

## 求职加练：讲清一次完整请求

用项目代码回答四个问题：浏览器怎样找到接口？为什么 `404` 不等于断线？为什么页面不直接把 JSON 拼进 `innerHTML`？响应模型怎样保护公开契约？

再选一次真实故障，用“现象 → 先查哪一层 → 找到什么 → 怎样修复 → 用什么测试防止复发”讲完整。这里的重点不是背状态码，而是能沿着浏览器、HTTP、API、数据和 DOM 找到责任位置。

</section>

## 完成检查

- [ ] 能沿着“浏览器 → HTTP → FastAPI → JSON → 页面状态”解释一次请求。
- [ ] 能启动一个本地服务，并分别打开页面、健康检查、JSON 与接口文档。
- [ ] 页面能正确处理 `200`、`404`、`422`、`503` 和连接失败。
- [ ] 自己增加一条 API 记录和按钮，没有破坏前三课的响应式布局。
- [ ] 能根据服务日志、Network、状态码和 JSON 定位一次失败。
- [ ] 六项 API 测试与 Web 起步总测试通过。
- [ ] 知道同源为什么简单，也知道前后端拆开后 CORS 会在哪里出现。

## 来源与版本

- FastAPI `0.139.2`、Uvicorn `0.51.0`、HTTPX `0.28.1`、Pydantic `2.13.4`，Python `3.11+`；示例与测试核查于 2026-07-18。
- 响应模型、路径参数与 CORS：FastAPI 官方教程，核查于 2026-07-18。
- Fetch、`Response.ok` 与 JSON 读取：MDN Web API 文档，核查于 2026-07-18。
- 示例只监听 `127.0.0.1`，不包含账号、数据库、真实个人数据或公网部署；自动测试不访问网络。

## 下一步

继续进入 [TypeScript、OpenAPI 与运行时数据契约](../web-core/01-typescript-openapi-runtime-contract.md)。下一课会保留 v0.4 的页面和 API，在错误 JSON 进入 `render()` 前把它拦下来。

Web 起步四课已经把 HTML、CSS、页面状态和本地 API 连成一个可运行项目。先回到 [Web 起步说明](README.md) 检查四个版本；下一组 Web 核心会进入 TypeScript、组件边界、API 契约与数据库。

参考：[FastAPI Response Model](https://fastapi.tiangolo.com/tutorial/response-model/) · [FastAPI Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/) · [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/) · [MDN Using Fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
