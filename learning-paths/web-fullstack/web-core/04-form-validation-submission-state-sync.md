<div class="be-tutor-mount" data-tutor-lesson="web-core-04" aria-hidden="true"></div>

<section id="overview-form-from-error-to-saved" data-learning-context="overview-form-from-error-to-saved" data-context-type="overview" markdown="1">

<div class="be-page-hero" markdown="1">
<span class="be-page-eyebrow">Web 核心 · 第四课 · 学习进度报告器 Web v0.8</span>

# 表单校验、提交与前后端状态同步

## 填错时留在原地，保存后再相信服务器

把小时数写成 `0.3`，页面会指向“学习小时”并告诉你要按 `0.25` 递增；改成 `1.25` 后，按钮进入提交中，成功时出现新记录，累计小时也从服务器重新读取。

```text
0.3 小时  →  页面拦下，没有请求
1.25 小时 →  正在保存，按钮暂时不可点
201        →  记录 #5 已保存
重新 GET   →  汇总 8.75 小时，列表出现记录 #5
```

如果网络在提交时断开，输入不会消失。原样重试继续使用同一个请求键，服务器即使已经写入，也不会再新增一条。

[运行 v0.8](#reproduce-dashboard-v08){ .md-button }
[先看谁负责校验](#concept-validation-layers){ .md-button .md-button--secondary }
</div>

<div class="be-page-summary" markdown="1">
  <div><span>课程位置</span><strong>Web 核心 · 4 / 4</strong></div>
  <div><span>项目版本</span><strong>学习进度报告器 Web v0.8</strong></div>
  <div><span>主要结果</span><strong>表单、错误回填、可重试提交、服务器同步</strong></div>
</div>

## 这节适合谁

- **小白**：按顺序做。先观察一个字段怎样从输入框走到数据库，不需要提前记住所有状态名。
- **已有基础**：先做跳过检查——能同时处理浏览器和服务端校验；提交期间能防重复点击；断线重试不重复写；写入后从服务器重读；旧响应不会盖掉新页面。全部做到，可以进入 Web 工程化。
- **兴趣学习**：完成主线，再把默认记录改成自己的内容。
- **求职准备**：额外保存状态图、错误响应、前后端约束对照和一次网络失败复盘。四类画像共用同一份 v0.8 项目。

前置是 [REST 资源、CRUD、分页与幂等](03-rest-resources-crud-pagination-idempotency.md)。v0.8 不改资源 URL，只把真实输入接到已经验证过的接口。

!!! note "这仍是本机练习"
    页面没有登录、权限、跨设备草稿或多人同时编辑。它能证明表单状态、错误处理和可重试提交，不能冒充生产前端。

</section>

<section id="concept-validation-layers" data-learning-context="concept-validation-layers" data-context-type="concept" markdown="1">

## 四道检查，各有一份责任

同一个小时数会经过四层：

```text
HTML 输入框
  min=0.25 · max=24 · step=0.25
          │
          ▼
TypeScript
  读取字符串 · 去空格 · 生成明确中文提示
          │
          ▼
FastAPI / Pydantic
  不信任浏览器 · 再验范围、步长和备注
          │
          ▼
SQLite CHECK
  最后守住已经进入写入路径的数据
```

浏览器检查得快，能少等一次网络；服务端检查是信任边界，因为请求可以绕过页面直接发送；数据库约束防止应用代码某条路径漏检。

不要因为规则重复就删掉后两层。前端代码在用户设备上运行，任何人都能改；服务端和数据库必须独立守住自己的数据。

</section>

<section id="example-html-and-typescript-validation" data-learning-context="example-html-and-typescript-validation" data-context-type="example" markdown="1">

## 输入框先做最便宜的检查

项目里的小时字段写着：

```html
<input
  name="hours"
  type="number"
  min="0.25"
  max="24"
  step="0.25"
  required>
```

代码提交前再调用：

```ts
if (!form.checkValidity()) {
  renderForm({
    kind: "invalid",
    message: "先改好标出的字段。",
    errors: nativeErrors()
  });
  form.reportValidity();
  return;
}
```

`checkValidity()` 只回答能不能继续，`reportValidity()` 让浏览器把问题显示出来。项目仍保留 `validateSessionDraft()`，因为备注只输入空格时，`required` 看见“有字符”，业务规则却应该把它当作空内容。

先预测三个输入：`0`、`0.3`、`1.25`。按照本课规则，只有 `1.25` 能进入提交。

</section>

<section id="concept-form-state-flow" data-learning-context="concept-form-state-flow" data-context-type="concept" markdown="1">

## 一次提交不只有成功和失败

页面至少会经过这些状态：

| 状态 | 页面应该做什么 | 还保留什么 |
| --- | --- | --- |
| `idle / editing` | 允许修改和提交 | 当前输入 |
| `invalid` | 指到具体字段，不发送请求 | 当前输入 |
| `submitting` | 按钮暂时不可点，显示正在保存 | 当前输入、请求键 |
| `field-error` | 把服务端问题放回对应字段 | 当前输入、请求键 |
| `network-error` | 说明结果未知，允许原样重试 | 当前输入、同一个请求键 |
| `saved` | 重新读取汇总和列表 | 服务端返回的记录 ID |
| `sync-error` | 禁止再次 POST，只允许重新 GET | 已保存的记录 ID |

这里最容易写错的是最后两行。POST 已经返回成功，后面的 GET 却失败时，不能把整次操作说成“保存失败”。记录已经在服务器里了，再生成新键提交一次反而会重复。

</section>

<section id="example-retry-same-intent" data-learning-context="example-retry-same-intent" data-context-type="example" markdown="1">

## 重试的是同一件事

v0.8 为“这次要保存的内容”保留一个请求键：

```ts
const key = intent.keyFor({
  hours: 1.25,
  note: "复盘表单状态"
});
```

- 内容没变，断线后重试得到同一个键。
- 小时数或备注变了，表示新的保存意图，换一个键。
- 收到保存成功响应后，这个意图结束，下次提交再换键。

网络错误只说明浏览器没有拿到完整响应，不证明服务器一定没写入。上一课的幂等接口在这里真正派上用场：原样重试，服务端要么第一次写入，要么找回刚才那条记录。

</section>

<section id="reproduce-dashboard-v08" data-learning-context="reproduce-dashboard-v08" data-context-type="reproduce" markdown="1">

## 跑起来，填错一次再保存

完整示例在 `site-src/examples/web-core/learning-dashboard-v08/`。使用 Python 3.11+、Node.js 24 与 TypeScript 7.0.2。

```bash
cd site-src/examples/web-core/learning-dashboard-v08
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-test.txt
npm install
npm test
python -m unittest -v test_app.py
uvicorn app:app --reload --port 8780
```

打开 `http://127.0.0.1:8780/`：

1. 把小时数改成 `0.3`，点击保存。页面应停在表单，并指出步长问题。
2. 改成 `1.25`，备注写“复盘表单状态”。提交时按钮不可重复点击。
3. 成功后，表单清空，累计小时和学习时段列表一起变化。
4. 查看浏览器 Network：一次 POST 后面跟着汇总 GET 和列表 GET。

服务端也会独立拒绝错误请求。下面的命令绕过页面直接发送 `0.3`：

```bash
curl -i -X POST "http://127.0.0.1:8780/api/learners/xiaoma/study-sessions" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: lesson-v08-invalid-hours" \
  -d '{"hours": 0.3, "note": "绕过页面"}'
```

应得到 `422`，`detail` 中的位置包含 `body → hours`。前端就是根据这段位置把错误放回“学习小时”下面。

!!! tip "试一次断线恢复"
    页面打开后先停止 Uvicorn，再点击保存。输入会保留，并提示原样重试仍使用同一个请求键。重新启动服务后，不改表单直接再点一次。这个练习不需要猜第一次有没有写入，因为重复写入保护会处理两种情况。

</section>

<section id="modify-form-rules" data-learning-context="modify-form-rules" data-context-type="modify" markdown="1">

## 改一条规则，别只改输入框

先完成最小修改：把默认小时和备注换成你今天真实学习的内容，预测累计小时，提交后核对服务器结果。

再把项目的小时步长从 `0.25` 改成 `0.5`。这不是只改一处：

1. `index.html` 的 `min` 与 `step`。
2. `src/form.ts` 的整数倍检查和提示。
3. `app.py` 中 Pydantic 的 `multiple_of`。
4. `schema.sql` 的 `CHECK`。
5. 前后端自动测试里的有效值和错误值。

改之前写下 `0.5`、`0.75`、`1.0` 各会在哪一层通过或失败。改完删除练习数据库，用全新 schema 启动，再运行前后端测试。

已有基础者可以再加一个 `category` 字段，但必须把 HTML、TypeScript 类型、Pydantic 模型、数据库列、迁移策略、接口测试和页面展示一起补齐。只让输入框多一项不算完成。

</section>

<section id="troubleshoot-form-submission" data-learning-context="troubleshoot-form-submission" data-context-type="troubleshoot" markdown="1">

## 表单不对时，先判断失败发生在哪一层

| 看到什么 | 先查哪里 | 怎样回来 |
| --- | --- | --- |
| 点击保存没有请求 | 输入框下方与 `checkValidity()` | 先修正必填、范围、步长和长度 |
| `422` 但页面没显示字段 | 响应 `detail[].loc` | 确认最后一段是 `hours` 或 `note`，再检查错误映射 |
| 连点产生多次请求 | 提交状态与按钮 `disabled` | 进入 `submitting` 时立即锁定，不等响应回来 |
| 断线后输入消失 | 失败分支是否调用 `reset()` | 只有保存并同步成功后才清空表单 |
| 断线重试新增两条 | 两次内容和请求键 | 同一内容必须复用同一个键；不要每次点击都无条件换键 |
| 保存成功但累计小时没变 | 成功后的 GET 与响应顺序 | 写入后重新读取汇总和列表，不只改 DOM |
| 旧学习者覆盖新页面 | 异步刷新顺序 | 用递增请求令牌，只渲染最后一次选择的结果 |
| 显示“保存失败”，数据库却有记录 | POST 与后续 GET 的状态是否混在一起 | 写入成功、同步失败要单独处理，只允许重新读取 |
| JavaScript 关闭后按钮无效 | `<noscript>` 与本地接口文档 | 保留课程命令和 `/docs`，不要把知识藏在交互里 |

</section>

<section id="project-dashboard-v08" data-learning-context="project-dashboard-v08" data-context-type="project" markdown="1">

## 学习进度报告器 Web v0.8

| v0.7 已经有 | v0.8 新增 | 后续工程化继续 |
| --- | --- | --- |
| REST 资源与状态码 | 真实小时数与备注表单 | 登录、会话与资源授权 |
| 游标分页与运行时守卫 | HTML、TypeScript、Pydantic、SQLite 四层校验 | 更完整的前后端测试 |
| 幂等键与冲突处理 | 同一内容断线重试复用请求键 | 数据迁移、并发更新与审计 |
| 写入、替换和删除接口 | 提交中、字段错误、网络错误和同步错误 | 部署、健康检查与可观测性 |

保存这些材料：一张表单成功截图、一份 `422` 响应、一次断线重试、一次“保存成功但同步失败”的状态说明、前后端测试结果，以及你修改规则后的差异。

Web 核心到这里形成了一个完整本机作品：页面能读写 SQLite 数据，有运行时契约、资源边界、分页、幂等、输入校验和失败恢复。下一阶段再进入身份、部署和运行可靠性，不把这些能力提前写进项目介绍。

</section>

<section id="deepen-client-server-state" data-learning-context="deepen-client-server-state" data-context-type="deepen" markdown="1">

## 为什么这版没有先把数字加上去

很多页面会做乐观更新：请求发出后先改界面，失败再回滚。它能让交互更快，但要处理临时 ID、回滚、重复提交和并发覆盖。

v0.8 选择更容易证明的路径：收到写入成功后，重新读取服务器状态。这个本机项目的网络延迟很低，先把正确性做清楚更划算。

项目还用 `LatestRequestGate` 给每次刷新一个递增编号。用户快速切换学习者时，旧请求即使更晚返回，也没有资格覆盖新页面。正式系统还可能使用 `AbortController` 取消旧请求，但“取消浏览器等待”并不等于服务器一定停止处理。

</section>

<section id="career-explain-form-recovery" data-learning-context="career-explain-form-recovery" data-context-type="career" markdown="1">

## 求职加练：讲清一次结果未知

试着回答：

1. 有 HTML 校验，服务端为什么还必须再校验？
2. 为什么网络错误时保留输入和请求键，而不是立刻清空？
3. POST 成功、刷新失败，页面应该显示什么？
4. 为什么按钮禁用只能减少重复点击，不能替代数据库唯一约束？
5. 为什么项目选择服务器重读，而没有做乐观更新？

可以按一次真实链路来讲：输入先在浏览器反馈 → 服务端守住信任边界 → 提交中锁住按钮 → 网络结果未知时保留同一个意图 → 幂等键避免重复写 → 成功后重新 GET → 刷新失败与写入失败分开。每个判断都能在代码或测试里找到对应位置。

</section>

## 完成检查

- [ ] 我能解释客户端校验改善体验，但不能替代服务端校验。
- [ ] 我让错误显示在对应字段旁边，并且键盘可以完成填写和提交。
- [ ] 我能区分编辑、提交中、字段错误、网络错误、成功和同步失败。
- [ ] 我在网络错误后原样重试，确认使用同一个请求键。
- [ ] 我确认保存成功后，累计小时和列表来自新的 GET 响应。
- [ ] 我修改过一条真实规则，并同步更新了前端、后端、数据库和测试。
- [ ] 我能说明这版仍缺少身份、授权、部署和并发更新。

## 来源与版本

- 适用：Python 3.11+、SQLite 3、FastAPI 0.139.2、Pydantic 2、Node.js 24 LTS、TypeScript 7.0.2、现代浏览器。
- 本课在 Python 3.11.9、SQLite 3.45.1、Node.js 24.14.1 上复现；核查日期：2026-07-18。
- [HTML Living Standard：表单与约束校验](https://html.spec.whatwg.org/multipage/forms.html)
- [HTML Living Standard：约束校验 API 与安全说明](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints)
- [FastAPI：处理错误与请求校验错误](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Pydantic：字段约束](https://docs.pydantic.dev/latest/concepts/fields/)
- [Pydantic：字段校验器](https://docs.pydantic.dev/latest/concepts/validators/)
- [SQLite：CHECK 约束](https://www.sqlite.org/lang_createtable.html#ckconst)
- 验证方式：`npm test`、17 项 FastAPI／SQLite 测试、课程根验证脚本及浏览器手工断线练习。

## 下一步

先回到 [Web 核心说明](README.md) 检查四个版本怎样连起来。随后进入 Web 工程化前置审计：补齐需要的网络、进程、数据库事务和安全基础，再建设认证、权限、测试与部署课程。还没有正文和验收的页面不会提前创建。
