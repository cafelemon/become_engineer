<div class="be-tutor-mount" data-tutor-lesson="web-core-03" aria-hidden="true"></div>

<section id="overview-one-request-one-record" data-learning-context="overview-one-request-one-record" data-context-type="overview" markdown="1">

<div class="be-page-hero" markdown="1">
<span class="be-page-eyebrow">Web 核心 · 第三课 · 学习进度报告器 Web v0.7</span>

# REST 资源、CRUD、分页与幂等

## 同一个请求发两次，只新增一条记录

页面点了一次，网络却可能重试。第一次请求已经写入数据库，响应又恰好在路上断掉；如果浏览器再发一次，累计小时数不该凭空多一份。

v0.7 用资源 URL 整理查询、创建、替换和删除，再给创建请求带一个 `Idempotency-Key`。下面是同一份请求连续发送两次的真实结果：

```text
第一次：201 Created  → session_id 5 → replayed false
第二次：200 OK       → session_id 5 → replayed true
数据库：只增加一行
```

[运行 v0.7](#reproduce-dashboard-v07){ .md-button }
[先看资源怎么命名](#concept-resource-urls){ .md-button .md-button--secondary }
</div>

<div class="be-page-summary" markdown="1">
  <div><span>课程位置</span><strong>Web 核心 · 3 / 4</strong></div>
  <div><span>项目版本</span><strong>学习进度报告器 Web v0.7</strong></div>
  <div><span>主要结果</span><strong>CRUD、游标分页、重复写入保护</strong></div>
</div>

## 这节适合谁

- **小白**：按顺序做。先把 URL 当作“要操作的东西”，再看 GET、POST、PUT、DELETE 分别做什么。
- **已有基础**：先做跳过检查——能给学习者与学习时段设计资源 URL；能解释 `201`、`204`、`404`、`409`；能证明分页不重复；能让同一创建请求重放后不多写。全部做到，可以直接进入表单课。
- **兴趣学习**：完成主线和自己的学习时段修改，不额外做接口评审题。
- **求职准备**：再保存 OpenAPI 差异、重复写入测试和一次设计取舍说明。四类画像共用同一份 v0.7 项目。

前置是 [关系模型、SQLite 与持久化边界](02-relational-model-sqlite-persistence.md)。这节沿用两张表和事务，不重复讲数据库入门。

!!! note "先说清楚范围"
    这是本机、单用户练习 API。它能证明资源设计、校验、分页和幂等行为；不能证明身份认证、并发扩容或生产安全。那些内容会在 Web 工程化继续补齐。

</section>

<section id="concept-resource-urls" data-learning-context="concept-resource-urls" data-context-type="concept" markdown="1">

## URL 先说“操作谁”

下面四个地址已经足够覆盖本课：

| 方法与 URL | 读法 | 成功结果 |
| --- | --- | --- |
| `GET /api/learners/xiaoma/study-sessions` | 读取小码的学习时段集合 | `200` 与一页记录 |
| `POST /api/learners/xiaoma/study-sessions` | 在这个集合中新建一条 | 首次 `201` |
| `GET /api/study-sessions/5` | 读取编号为 5 的单条资源 | `200` 或 `404` |
| `PUT /api/study-sessions/5` | 用完整的新内容替换编号 5 | `200` 或 `404` |
| `DELETE /api/study-sessions/5` | 删除编号 5 | 首次 `204` |

URL 使用名词 `learners` 和 `study-sessions`。动作交给 HTTP 方法表达，因此不用再写 `/create-session`、`/delete-session` 这类重复动词。

这不表示“用了四个方法就是完整 REST”。接口仍要考虑表示格式、缓存、认证、并发更新和错误模型。本课先把最容易验证的一层做好。

```text
浏览器
  │  方法 + 资源 URL + JSON/请求头
  ▼
FastAPI 路由
  │  路径、查询参数、请求体校验
  ▼
LearningDatabase
  │  参数化 SQL + 事务
  ▼
SQLite
```

</section>

<section id="example-methods-and-status" data-learning-context="example-methods-and-status" data-context-type="example" markdown="1">

## 方法相同，重复后的含义也不同

先看一个小表：

| 方法 | 重复一次通常想得到什么 | 本课怎样验证 |
| --- | --- | --- |
| `GET` | 仍然只读取，不增加记录 | 记录数不变 |
| `PUT` | 资源最终保持同一份内容 | 连续替换两次，响应内容相同 |
| `DELETE` | 资源最终都不存在 | 第一次 `204`，第二次可以 `404`，最终状态相同 |
| `POST` | 默认可能再创建一条 | 加应用定义的幂等键，重复请求返回原记录 |

HTTP 中的“幂等”关心的是多次相同请求对服务器产生的预期效果，与只执行一次相同。它不要求每次响应状态码逐字一致。

本课的 `POST` 不是天然幂等。我们额外约定：

1. 客户端为一次“我要保存这条学习时段”的意图生成一个键。
2. 服务端把键与新记录一起保存，并由 `UNIQUE` 约束阻止重复键。
3. 同一个键、同一份内容再次到达时，返回原记录。
4. 同一个键却换了小时数或备注时，返回 `409 Conflict`，不猜客户端想要哪一份。

`Idempotency-Key` 在这里是项目自己的请求头约定，不要把它说成所有 HTTP 服务自动具备的能力。

</section>

<section id="concept-cursor-pagination" data-learning-context="concept-cursor-pagination" data-context-type="concept" markdown="1">

## 一页只读两条

小码现在有三条学习时段：

```text
id 1 ── 2.0 小时
id 2 ── 2.5 小时
id 3 ── 3.0 小时
```

第一页请求：

```text
GET /api/learners/xiaoma/study-sessions?limit=2&after_id=0
```

返回 `1、2`，并告诉页面 `next_after_id = 2`。下一页从 `id > 2` 继续，因此得到 `3`。

数据库实际读取 `limit + 1` 条。多出来的那条不交给页面，只用来判断后面还有没有数据：

```sql
SELECT id, learner_id, hours, note, created_at
FROM study_sessions
WHERE learner_id = ? AND id > ?
ORDER BY id ASC
LIMIT ?;
```

参数依次是 `learner_id`、`after_id`、`limit + 1`。索引 `(learner_id, id)` 正好对应过滤和排序方向。

与“第几页”相比，游标不会因为前面一条记录被删除就整体向前挪。但这个小例子也不是数据库快照：翻页过程中新增的记录可能出现在后续页，复杂排序还需要更完整的游标。

</section>

<section id="reproduce-dashboard-v07" data-learning-context="reproduce-dashboard-v07" data-context-type="reproduce" markdown="1">

## 跑起来，连续发两次

完整示例在 `site-src/examples/web-core/learning-dashboard-v07/`。使用 Python 3.11+、Node.js 24 与 TypeScript 7.0.2。

```bash
cd site-src/examples/web-core/learning-dashboard-v07
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-test.txt
npm install
npm test
python -m unittest -v test_app.py
uvicorn app:app --reload --port 8780
```

打开 `http://127.0.0.1:8780/`。你应该看到第一页两条学习时段，点击“下一页”后出现第三条。

再点击“连续发送两次”。页面会生成一个新键并发送两次完全相同的 `POST`。正常结果类似：

```text
第一次 201，第二次 200；两次都是记录 #5。
```

也可以在另一个终端直接观察分页：

```bash
curl -s "http://127.0.0.1:8780/api/learners/xiaoma/study-sessions?limit=2&after_id=0" \
  | python -m json.tool
```

创建一条记录并保留响应头：

```bash
curl -i -X POST "http://127.0.0.1:8780/api/learners/xiaoma/study-sessions" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: my-rest-practice-001" \
  -d '{"hours": 1.25, "note": "复盘 REST 资源"}'
```

第一次应为 `201 Created`，响应头含有新资源的 `Location`。原样再运行一次，应为 `200 OK`，`replayed` 变成 `true`，`session_id` 不变。

!!! tip "Windows PowerShell"
    如果单引号和续行符让命令难读，可以直接打开 `http://127.0.0.1:8780/docs`，在 Swagger UI 中填写相同路径、请求头与 JSON。重点是比较两次响应和数据库记录数，不是背 Shell 写法。

</section>

<section id="example-update-delete-conflict" data-learning-context="example-update-delete-conflict" data-context-type="example" markdown="1">

## 再试更新、删除和冲突

把下面的 `5` 换成你刚创建的 `session_id`。

完整替换：

```bash
curl -i -X PUT "http://127.0.0.1:8780/api/study-sessions/5" \
  -H "Content-Type: application/json" \
  -d '{"hours": 1.5, "note": "补上分页测试"}'
```

连续执行两次，资源都保持 `1.5` 小时，不会累加成 `3.0`。

删除：

```bash
curl -i -X DELETE "http://127.0.0.1:8780/api/study-sessions/5"
```

第一次是 `204 No Content`，没有响应正文；第二次是 `404`。两次之后数据库里的最终状态相同：编号 5 不存在。

最后故意制造一个冲突：先用键 `my-rest-practice-002` 保存 `1.0` 小时，再用同一个键发送 `2.0` 小时。服务应返回 `409`，原记录不能被第二份内容偷偷改掉。

</section>

<section id="modify-own-rest-resource" data-learning-context="modify-own-rest-resource" data-context-type="modify" markdown="1">

## 换成自己的记录

不要只保留固定的“REST 与幂等练习”。做一组自己的数据：

1. 新建 `0.75` 小时，备注写今天实际完成的内容。
2. 原样重复请求，先预测记录总数和累计小时数。
3. 用 `PUT` 把它改成 `1.0` 小时，并再次执行相同 `PUT`。
4. 读取第一页和下一页，确认每条 ID 只出现一次。
5. 删除这条记录，再分别检查单条 GET 与学习汇总。

然后改一个接口行为。可以把默认 `limit` 从 `2` 改成 `3`，也可以给列表增加 `max_id` 静态上界。改之前写下预期请求和响应，改完补一条后端测试。

</section>

<section id="troubleshoot-rest-api" data-learning-context="troubleshoot-rest-api" data-context-type="troubleshoot" markdown="1">

## 结果不对时，从状态码往回查

| 看到什么 | 先查哪里 | 怎样回来 |
| --- | --- | --- |
| `422` | 路径、`limit`、JSON 与请求头格式 | `limit` 保持 1–50；键至少 8 个允许字符；小时数大于 0 且不超过 24 |
| `404` | 学习者 ID 或学习时段 ID | 先用列表接口确认资源是否存在，不要直接改数据库 |
| 重复 POST 新增了两条 | 两次请求头 | 确认两次真的使用同一个 `Idempotency-Key` |
| `409` | 相同键对应的请求体 | 原意图重试必须保持内容相同；新意图请生成新键 |
| 下一页重复或漏项 | `after_id` 与排序 | 用上一页最后一条 ID 继续，并保持 `ORDER BY id ASC` |
| 删除后记录又回来 | 初始化种子逻辑 | 演示数据只能在空数据库首次创建时写入，不能每次请求都补种子 |
| 页面说成功但列表没变 | Network 与刷新请求 | 检查 POST 状态、返回的 ID，以及写入后是否重新读取第一页 |
| `503` | 数据库路径与应用日志 | 先确认数据库可打开；不要把服务不可用伪装成空列表 |

这节开发时真的遇到过“删除后种子数据被自动补回来”。测试先暴露问题，再把初始化改成只给空数据库写入演示数据。把这样的故障留下来，比只保存绿色截图更有用。

</section>

<section id="project-dashboard-v07" data-learning-context="project-dashboard-v07" data-context-type="project" markdown="1">

## 学习进度报告器 Web v0.7

| v0.6 已经有 | v0.7 新增 | 下一节继续 |
| --- | --- | --- |
| 两张关系表与事务 | 集合资源和单条资源 URL | 表单字段与用户输入 |
| 汇总读取与追加时段 | GET、POST、PUT、DELETE | 提交中、成功、失败状态 |
| SQLite 持久化 | 游标分页与组合索引 | 乐观更新与服务端错误回填 |
| 参数化 SQL | 幂等键、`201/200/204/409` 测试 | 前后端状态同步 |

保存这些材料：OpenAPI 路径、两页 JSON、一次 `201 → 200` 重放、一次 `409`、重复 PUT、重复 DELETE 的最终状态，以及 16 项后端测试。项目仍是本机练习，不虚构登录用户、并发规模或线上流量。

</section>

<section id="deepen-pagination-idempotency" data-learning-context="deepen-pagination-idempotency" data-context-type="deepen" markdown="1">

## 这套实现还缺什么

- `id` 游标适合当前按递增 ID 展示的记录。按时间、分数或多个字段排序时，游标也要包含完整排序键。
- `UNIQUE(idempotency_key)` 能防重复键，但高并发下还要测试事务竞争、锁等待和重试。
- 演示把幂等键长期放在业务表。正式系统通常还会定义过期时间、请求摘要、响应缓存和清理策略。
- `PUT` 直接覆盖整条可修改内容，尚未处理两个用户同时编辑。后续可以用版本号、ETag 与条件请求防止丢失更新。
- 当前任何人只要知道 URL 就能操作记录。认证与授权不是“之后加个登录按钮”，而是每个资源操作都要经过身份和权限判断。

</section>

<section id="career-explain-rest-failure" data-learning-context="career-explain-rest-failure" data-context-type="career" markdown="1">

## 求职加练：从一次重复写入讲接口可靠性

试着回答：

1. 为什么学习时段列表放在学习者下面，单条更新却使用独立资源 URL？
2. 为什么 `DELETE` 第二次返回 `404`，仍不违背幂等语义？
3. 只给 `POST` 加一个随机请求头还不够，数据库里为什么也要有唯一约束？
4. 为什么第一页请求多取一条，而不是先执行一次 `COUNT(*)`？
5. 这套本机 API 距离生产系统还缺哪些身份、并发和运维能力？

我更建议按真实故障来讲：响应丢失可能触发重试 → 普通 POST 会重复累计 → 客户端标识一次意图 → 数据库唯一约束守住写入 → 相同请求返回原资源 → 不同内容用 `409` 拒绝。每一步都有接口测试支撑。

</section>

## 完成检查

- [ ] 我能从资源 URL 说清集合与单条记录的关系。
- [ ] 我能独立完成创建、读取、替换和删除，并读懂主要状态码。
- [ ] 我能翻完两页记录，不重复也不漏掉已存在的数据。
- [ ] 我用同一个幂等键重放创建请求，数据库只增加一条。
- [ ] 我让同一个键携带不同内容，确认服务返回 `409`。
- [ ] 我能解释幂等关心最终效果，不要求每次响应完全相同。
- [ ] 我保留了自动测试和一次真实故障修复记录。

## 来源与版本

- 适用：Python 3.11+、SQLite 3、FastAPI 0.139.2、Node.js 24 LTS、TypeScript 7.0.2。
- 本课在 Python 3.11.9、SQLite 3.45.1、Node.js 24.14.1 上复现；核查日期：2026-07-18。
- [RFC 9110：HTTP 方法与幂等语义](https://www.rfc-editor.org/rfc/rfc9110.html#name-idempotent-methods)
- [FastAPI：Query 参数校验](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/)
- [FastAPI：Header 参数](https://fastapi.tiangolo.com/tutorial/header-params/)
- [FastAPI：响应状态码](https://fastapi.tiangolo.com/tutorial/response-status-code/)
- [SQLite：CREATE INDEX 与 UNIQUE 索引](https://www.sqlite.org/lang_createindex.html)

## 下一步

下一课 [《表单校验、提交与前后端状态同步》](04-form-validation-submission-state-sync.md) 会让学习者真正填写小时数和备注，并处理输入中、提交中、成功、服务端拒绝、网络中断与恢复。v0.7 的资源接口继续保留，页面不会绕过后端直接改 DOM。
