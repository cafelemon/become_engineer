<div class="be-tutor-mount" data-tutor-lesson="web-core-01" aria-hidden="true"></div>

<section id="overview-200-but-rejected" class="be-page-hero be-lesson-hero" data-learning-context="overview-200-but-rejected" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Web 核心 · 第一课 · 学习进度报告器 Web v0.5</span>

# TypeScript、OpenAPI 与运行时数据契约

## 接口明明返回 200，页面为什么拒绝显示？

```text
GET /api/demo-contract-drift
HTTP 200 OK

completed_hours: "七个半小时"
                   ↑ 页面需要 number

页面提示：字段或类型不符合 LearningSummary
```

`200` 只说明请求成功到达并得到响应，不保证正文就是页面期待的数据。v0.5 会在渲染前检查 JSON：正确记录照常显示，字段漂移则停在边界上，不把错误继续传进 DOM。

<div class="be-page-actions" markdown="1">
[先看三份契约怎样配合](#concept-three-contract-views){ .md-button .md-button--primary }
[运行 v0.5](#reproduce-dashboard-v05){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Web 核心 · 1 / 4</strong></div>
  <div><span>开始条件</span><strong>完成 Web 起步 v0.4</strong></div>
  <div><span>完成后留下</span><strong>严格 TypeScript、OpenAPI 契约与漂移测试</strong></div>
</div>

## 开始前

- 第一次使用 TypeScript，按本课的 Node.js 安装和命令逐行做。这里先不引入 React、Vue 或代码生成器。
- 已有基础者先做跳过检查：开启 `strict` 与 `noEmitOnError`，把 `response.json()` 当作 `unknown`，写类型守卫并证明 HTTP 200 的错误字段会被拒绝。全部做到，可以直接进入下一节数据库课程。
- 四类画像共用学习进度报告器。兴趣画像做到项目修改；求职画像再完成契约漂移复盘和接口评审。

<section id="concept-compile-time-runtime" data-learning-context="concept-compile-time-runtime" data-context-type="concept" markdown="1">

## TypeScript 能检查代码，不能替你检查网络

先看这行：

```typescript
const payload: LearningSummary = await response.json();
```

它看起来很安心，却把一件没有证明的事直接告诉了编译器：网络回来的 JSON 一定是 `LearningSummary`。TypeScript 的类型会在编译后消失，服务器仍然可以返回缺字段、错类型，甚至完全不是 JSON 的内容。

更诚实的写法是：

```typescript
const payload: unknown = await response.json();

if (!isLearningSummary(payload)) {
  return { kind: "contract-error", message: "字段或类型不符合约定。" };
}

// 从这里开始，payload 才是 LearningSummary
return { kind: "success", record: summaryToRecord(payload) };
```

`unknown` 的意思不是“这个值很神秘”，而是“使用前先证明”。这也是本课最重要的一条边界。

</section>

<section id="concept-three-contract-views" data-learning-context="concept-three-contract-views" data-context-type="concept" markdown="1">

## 同一份数据，有三个观察位置

<div class="be-data-flow" role="img" aria-label="Pydantic 在服务端校验响应，OpenAPI 描述公开接口，TypeScript 与运行时守卫在浏览器端检查数据">
  <div><strong>Pydantic</strong><span>服务端实际返回什么</span></div>
  <div><strong>OpenAPI</strong><span>接口公开承诺什么</span></div>
  <div><strong>TypeScript</strong><span>前端代码怎样使用</span></div>
  <div><strong>类型守卫</strong><span>这次 JSON 是否真的符合</span></div>
</div>

FastAPI 的 `response_model=LearningSummary` 会校验和过滤正常接口响应，并生成 OpenAPI schema。浏览器端的 `interface LearningSummary` 帮助编辑器和编译器检查代码。运行时守卫检查这一回真正收到的值。

三者不是互相替代：

| 位置 | 能发现什么 | 发现不了什么 |
| --- | --- | --- |
| Pydantic | 服务端返回模型不合法 | 浏览器是否拿到旧缓存、代理错误或其他服务响应 |
| OpenAPI | 公开字段、类型和错误描述 | 每次响应是否真的遵守文档 |
| TypeScript | 前端代码里的字段拼写和分支遗漏 | 网络 JSON 的真实形状 |
| 运行时守卫 | 当前 JSON 的字段和类型漂移 | 服务内部为什么产生错误 |

</section>

<section id="example-interface-page-state" data-learning-context="example-interface-page-state" data-context-type="example" markdown="1">

## 先把数据和页面状态写清楚

```typescript
interface LearningSummary {
  learner_id: string;
  learner_name: string;
  completed_lessons: number;
  completed_hours: number;
  status: "起步中" | "按计划推进" | "本周已完成";
  next_milestone: string;
}

type PageState =
  | { kind: "loading"; message: string }
  | { kind: "success"; message: string; record: LearningRecord }
  | { kind: "empty"; message: string }
  | { kind: "error"; message: string }
  | { kind: "contract-error"; message: string };
```

`kind` 是一枚判别字段。`render()` 先看它，再决定能否读取 `record`。如果你漏掉一种状态，编辑器会比用户更早提醒你。

本课继续把请求和渲染分开：

```text
api.ts        HTTP → PageState
render.ts     PageState → DOM
main.ts       按钮事件 → 调用两者
contracts.ts  数据与状态的共同语言
```

</section>

<section id="example-runtime-guard" data-learning-context="example-runtime-guard" data-context-type="example" markdown="1">

## 类型守卫怎样把 unknown 变成可用数据

```typescript
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isLearningSummary(value: unknown): value is LearningSummary {
  if (!isRecord(value)) return false;

  return (
    typeof value.learner_id === "string" &&
    typeof value.learner_name === "string" &&
    Number.isInteger(value.completed_lessons) &&
    typeof value.completed_hours === "number" &&
    Number.isFinite(value.completed_hours)
  );
}
```

真实示例还会检查其余字段和三个合法状态。这里先看判断方式：每个条件都回答一个具体问题，不使用 `as LearningSummary` 强行通过。

我更建议新手先手写这一个守卫。以后字段变多，可以评估 JSON Schema、OpenAPI 代码生成或校验库；但如果不知道生成物解决了什么，工具只会把错误藏得更深。

</section>

<section id="reproduce-dashboard-v05" data-learning-context="reproduce-dashboard-v05" data-context-type="reproduce" markdown="1">

## 编译 TypeScript，再启动原来的 FastAPI

本课使用 Node.js 24 LTS 与 TypeScript 7.0.2。先在终端确认：

```bash
node --version
npm --version
```

如果提示找不到命令，从 [Node.js 官方下载页](https://nodejs.org/en/download) 安装 LTS 版本，关闭并重新打开 VS Code 终端。Windows、macOS 都可以直接使用官方安装包；Linux 按发行版或官方说明安装。看到 `v24` 开头的 Node 版本即可继续。

把完整 v0.5 复制到新的练习目录：

=== "Windows PowerShell"

    ```powershell
    New-Item -ItemType Directory -Force .\practice\web-core\learning-dashboard | Out-Null
    Copy-Item .\site-src\examples\web-core\learning-dashboard-v05\* `
      .\practice\web-core\learning-dashboard\ -Recurse -Force
    ```

=== "macOS / Linux"

    ```bash
    mkdir -p practice/web-core/learning-dashboard
    cp -R site-src/examples/web-core/learning-dashboard-v05/. \
      practice/web-core/learning-dashboard/
    ```

删除复制过来的 `node_modules`（如果存在），再按锁文件安装和编译：

```bash
cd practice/web-core/learning-dashboard
npm ci
npm test
```

你应该看到 TypeScript 编译通过，并列出五种页面状态。然后回到仓库根目录，运行 API 测试：

=== "Windows PowerShell"

    ```powershell
    .\.venv\Scripts\python.exe -m pip install `
      -r .\practice\web-core\learning-dashboard\requirements-test.txt
    .\.venv\Scripts\python.exe -m unittest discover `
      -s .\practice\web-core\learning-dashboard -p test_app.py -v
    ```

=== "macOS / Linux"

    ```bash
    .venv/bin/python -m pip install \
      -r practice/web-core/learning-dashboard/requirements-test.txt
    .venv/bin/python -m unittest discover \
      -s practice/web-core/learning-dashboard -p test_app.py -v
    ```

启动服务：

```bash
.venv/bin/python -m uvicorn app:app \
  --app-dir practice/web-core/learning-dashboard \
  --host 127.0.0.1 --port 8780
```

Windows 把开头换成 `.\.venv\Scripts\python.exe`。打开 `http://127.0.0.1:8780/`，依次点击六个按钮。`200 + 错误字段` 应该显示契约错误，并隐藏旧的指标；正确数据仍能恢复页面。

</section>

<section id="modify-add-focus-topic" data-learning-context="modify-add-focus-topic" data-context-type="modify" markdown="1">

## 给学习记录增加 focus_topic

现在自己完成一次前后端同步。新增字段：

```text
focus_topic: "TypeScript 契约"
```

按这个顺序改：

1. 在 Python `LearningSummary` 和两条记录中增加 `focus_topic: str`。
2. 打开 `/openapi.json`，找到新字段和 `required`。
3. 在 TypeScript `LearningSummary` 与运行时守卫中增加检查。
4. 在 `LearningRecord`、`summaryToRecord()`、HTML 和 `render()` 中显示它。
5. 给 Python 与 Node 测试各增加一个断言，再运行 `npm test` 和 unittest。

故意漏掉守卫里的检查：编译器可能仍然通过，因为接口声明里有字段；把演示响应的 `focus_topic` 改成数字，页面也可能放行。补回运行时检查后再试一次，你就能看到静态类型与网络边界的区别。

</section>

<section id="troubleshoot-typescript-contract" data-learning-context="troubleshoot-typescript-contract" data-context-type="troubleshoot" markdown="1">

## 报错时先看它来自哪一层

| 看到什么 | 多半是哪一层 | 怎样继续 |
| --- | --- | --- |
| `Cannot find module` 或找不到 `tsc` | Node 依赖 | 回到含 `package-lock.json` 的目录运行 `npm ci` |
| `tsc` 报字段不存在 | TypeScript 静态检查 | 对照 interface、映射和 render，不要先写 `as any` |
| 改了 `.ts`，页面还是旧行为 | 编译产物 | 重新运行 `npm run build`，确认 `dist/` 更新时间 |
| API 是 200，页面显示契约错误 | 运行时数据 | 在 Network 看 JSON，再逐字段检查守卫 |
| `/openapi.json` 还是旧字段 | FastAPI 进程 | 保存 Python，停止并重新启动 Uvicorn |
| JSON 无法解析 | HTTP 正文 | 看响应正文与 Content-Type，不要把 HTML 错误页当 JSON |
| 页面加载不到模块 | 静态路径或 ES module | 从 FastAPI 地址打开，确认 `/dist/main.js` 返回 200 |

这里先别同时修改 Python 模型、TypeScript interface、守卫和 DOM。找出最早不一致的那一层，改完就重跑对应测试。

</section>

<section id="project-dashboard-v05" data-learning-context="project-dashboard-v05" data-context-type="project" markdown="1">

## 学习进度报告器 Web v0.5

| v0.4 已经有 | v0.5 新增 | 下一节继续 |
| --- | --- | --- |
| FastAPI + JSON + fetch | TypeScript 严格编译 | SQLite 持久化 |
| 200、404、422、503 与断线 | `unknown` + 类型守卫 | 关系模型与迁移 |
| Pydantic 响应模型 | OpenAPI、前端接口和漂移测试 | 重启后保留记录 |

保存这些材料：`npm test` 输出、8 项 API 测试、正确响应、契约漂移提示，以及一次新增字段的提交差异。它们能证明项目不只是“能显示”，还知道错误数据应该停在哪里。

</section>

<section id="deepen-generate-or-maintain" data-learning-context="deepen-generate-or-maintain" data-context-type="deepen" markdown="1">

## 字段多了，要不要从 OpenAPI 生成 TypeScript？

手工维护两份类型容易漂移，生成代码可以降低重复劳动。但生成不等于运行时安全：要看工具是否同时生成校验器、怎样处理版本变化，以及生成物由谁评审。

这个小项目先手写，因为字段少、学习目标清楚。团队接口变多后，可以这样判断：

- OpenAPI 是不是唯一权威来源？
- 生成步骤能否在 CI 中稳定复现？
- 破坏性变更会不会让构建失败？
- 运行时是否仍有不可信输入，需要额外校验？

不要为了少写十行代码，先引入一条没人理解的生成链。

</section>

<section id="career-review-contract-drift" data-learning-context="career-review-contract-drift" data-context-type="career" markdown="1">

## 求职加练：讲清一次契约漂移

用自己的 `focus_topic` 修改回答：服务端、OpenAPI、TypeScript interface、运行时守卫和 DOM 分别改了什么？如果只漏一处，会在编译、测试还是浏览器中暴露？

再把演示接口当作一次小故障：HTTP 是 200，为什么仍不能显示？你怎样证明没有把错误数据传给 `render()`？修复后补了哪条测试？

面试里谈“前后端类型一致”时，我更看重这种具体证据，而不是只说“我们用了 TypeScript，所以类型安全”。网络外部输入不会因为项目用了 TypeScript 自动可信。

</section>

## 完成检查

- [ ] 能解释 TypeScript 编译时类型为什么不能证明网络 JSON 正确。
- [ ] 能说明 Pydantic、OpenAPI、TypeScript interface 与运行时守卫各自负责什么。
- [ ] `npm test`、8 项 API 测试和严格 MkDocs 构建通过。
- [ ] 页面正确处理成功、404、422、503、断线、无效 JSON和契约漂移。
- [ ] 已把 `focus_topic` 从 Python 模型一直接到页面，并补上两端测试。
- [ ] 手机宽度下按钮、提示和指标不横向溢出；禁用 JavaScript 后仍能访问接口文档和示例 JSON。
- [ ] 求职画像能用代码与测试讲清一次契约漂移；兴趣画像不必做额外面试题。

## 来源与版本

- Node.js 24 LTS、TypeScript 7.0.2、FastAPI 0.139.2、Pydantic 2.13.4、Uvicorn 0.51.0；示例核查于 2026-07-18。
- TypeScript modules、narrowing、`strict` 与 `noEmitOnError`：[TypeScript 官方文档](https://www.typescriptlang.org/docs/handbook/2/modules.html)、[Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)、[strict](https://www.typescriptlang.org/tsconfig/strict.html)、[noEmitOnError](https://www.typescriptlang.org/tsconfig/noEmitOnError.html)。
- FastAPI 响应模型与 OpenAPI：[Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)、[First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)。
- `demo-contract-drift` 故意绕过响应模型，只存在于本地教学示例；正常 API 仍由 Pydantic 校验。自动测试不访问网络，不保存真实学习数据。

## 下一步

下一节会把内存字典换成 SQLite。先不急着写一大串 SQL：我们会先画清学习者、课程和学习记录之间的关系，再验证重启、重复写入和事务失败时会发生什么。

