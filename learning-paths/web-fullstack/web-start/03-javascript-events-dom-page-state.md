<div class="be-tutor-mount" data-tutor-lesson="web-start-03" aria-hidden="true"></div>

<section id="overview-interactive-dashboard" class="be-page-hero be-lesson-hero" data-learning-context="overview-interactive-dashboard" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Web 起步 · 第三课 · 学习进度报告器 Web v0.3</span>

# JavaScript 事件、DOM 与页面状态

## 点一下，页面知道该换谁的数据

<div class="be-state-preview" aria-label="点击不同按钮后学习面板会进入加载、成功、空数据或错误状态">
  <div><strong>点击“小码”</strong><span>加载中</span></div>
  <div><strong>读取本地记录</strong><span>成功</span></div>
  <div><strong>点击“不存在”</strong><span>空数据</span></div>
  <div><strong>点击“模拟错误”</strong><span>错误</span></div>
</div>

前两课的页面只能显示写死在 HTML 里的内容。这一课加入一份 `app.js`：按钮发出事件，程序更新状态，再把状态显示回原来的 HTML 结构。

<div class="be-page-actions" markdown="1">
[先看点击后发生了什么](#concept-event-state-render){ .md-button .md-button--primary }
[直接运行 v0.3](#reproduce-dashboard-v03){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Web 起步 · 3 / 4</strong></div>
  <div><span>开始条件</span><strong>能读懂 v0.2 的 HTML 与 CSS</strong></div>
  <div><span>完成后留下</span><strong>app.js、四种状态截图与自动测试</strong></div>
</div>

## 开始前

- 第一次接触 JavaScript，可以把它先理解为“浏览器里运行的程序”。这节课不要求 Node.js、框架或异步网络知识。
- 已有基础者先做跳过检查：不用 `onclick`，实现按钮切换、统一 `render()`、四种状态、`aria-pressed` 和 `role="status"`，并让禁用 JavaScript 时初始卡片仍可读。全部做到即可进入 HTTP 与 API。
- 继续使用同一个 `practice/web-start/learning-dashboard/`，不要另起一份无法继承前两课成果的 Demo。

<section id="concept-dom-tree" data-learning-context="concept-dom-tree" data-context-type="concept" markdown="1">

## JavaScript 操作的不是 HTML 文件本身

浏览器读完 HTML 后，会在内存中建立 DOM，也就是可以被程序查询和修改的文档对象树。

<div class="be-data-flow" role="img" aria-label="HTML 文件被浏览器解析成 DOM，JavaScript 修改 DOM 后浏览器重新显示页面">
  <div><strong>index.html</strong><span>磁盘上的源文件</span></div>
  <div><strong>浏览器解析</strong><span>建立元素对象</span></div>
  <div><strong>DOM</strong><span>当前页面结构</span></div>
  <div><strong>屏幕更新</strong><span>重新显示变化</span></div>
</div>

```javascript
const title = document.querySelector("#profile-title");
title.textContent = "阿飞的学习面板";
```

`querySelector()` 返回第一个匹配 CSS 选择器的元素，找不到时返回 `null`。`textContent` 修改元素里的文字，不会把文字当成新的 HTML 标签解释。

刷新页面后，浏览器会重新读取源文件，刚才只存在于内存 DOM 中的修改会消失。第四课才会从服务端读取数据；本课也不会把状态写进浏览器存储。

</section>

<section id="concept-event-state-render" data-learning-context="concept-event-state-render" data-context-type="concept" markdown="1">

## 一次点击走过三段路

<div class="be-data-flow be-data-flow--three" role="img" aria-label="按钮点击产生事件，事件更新页面状态，render 函数把状态写入 DOM">
  <div><strong>事件</strong><span>用户点击“小码”</span></div>
  <div><strong>状态</strong><span>loading → success</span></div>
  <div><strong>render()</strong><span>把状态写入 DOM</span></div>
</div>

```javascript
button.addEventListener("click", () => {
  render({ kind: "loading", message: "正在读取小码……" });
  const view = getView("xiaoma");
  render(view);
});
```

`addEventListener()` 把一个函数登记为点击事件的监听器。按钮被点击时，浏览器再调用这个函数。

这里没有让按钮分别去改标题、小时和状态。按钮只负责选择数据，`getView()` 产出页面状态，`render()` 统一更新 DOM。以后数据来自 API 时，页面渲染部分仍能复用。

</section>

<section id="example-four-page-states" data-learning-context="example-four-page-states" data-context-type="example" markdown="1">

## 页面不能只有“成功”一种样子

```javascript
function getView(profileId) {
  if (profileId === "broken") {
    return { kind: "error", message: "模拟读取失败，请稍后重试。" };
  }

  const record = PROFILES[profileId];
  if (!record) {
    return { kind: "empty", message: "没有找到这位学习者。" };
  }

  return { kind: "success", message: `已显示${record.name}。`, record };
}
```

本课固定四种状态：

| 状态 | 页面告诉用户什么 | 是否显示旧数据 |
| --- | --- | --- |
| `loading` | 正在处理这次选择 | 暂时隐藏，避免误认为旧数据是新结果 |
| `success` | 数据读取成功 | 显示当前记录 |
| `empty` | 操作成功，但没有这条记录 | 不显示旧记录 |
| `error` | 这次处理失败 | 不显示旧记录，并给出恢复方向 |

“空数据”不等于“程序出错”。下一课接 API 后，它们会对应不同的 HTTP 与应用情况。

</section>

<section id="example-render-text-safely" data-learning-context="example-render-text-safely" data-context-type="example" markdown="1">

## 把文字放进页面，不要顺手拼 HTML

```javascript
function render(view, refs) {
  refs.status.dataset.kind = view.kind;
  refs.status.textContent = view.message;
  refs.content.hidden = view.kind !== "success";

  if (view.kind === "success") {
    refs.title.textContent = `${view.record.name}的学习面板`;
    refs.hours.textContent = `${view.record.hours} 小时`;
  }
}
```

本课显示的名字和说明都按普通文字处理，所以使用 `textContent`。如果把外部文字直接拼进 `innerHTML`，其中的标签可能被浏览器解释成页面结构。下一课的数据即使来自自己的 API，也继续把显示文字当文字，而不是默认信任它能变成 HTML。

`hidden` 控制当前记录区域是否显示。状态提示始终存在于 HTML 中，并使用 `role="status"`；内容更新时，辅助技术可以在合适的时机读出变化，不需要把键盘焦点强行抢走。

</section>

<section id="reproduce-dashboard-v03" data-learning-context="reproduce-dashboard-v03" data-context-type="reproduce" markdown="1">

## 复制三份文件，再直接打开

=== "Windows PowerShell"

    ```powershell
    Copy-Item .\site-src\examples\web-start\learning-dashboard-v03\* `
      .\practice\web-start\learning-dashboard\ -Force
    ```

=== "macOS / Linux"

    ```bash
    cp site-src/examples/web-start/learning-dashboard-v03/* \
      practice/web-start/learning-dashboard/
    ```

目录里现在有：

```text
learning-dashboard/
├── index.html
├── styles.css
└── app.js
```

双击 `index.html`，依次点击“小码”“阿飞”“不存在”“模拟错误”。状态提示应先显示正在读取，再进入成功、空数据或错误；成功状态会替换标题和四项指标。

关闭浏览器 JavaScript 后重新打开页面，初始小码记录仍应可读，并出现“交互功能需要 JavaScript”的说明。静态内容是降级路径，不是第二套应用。

在仓库根目录运行测试：

```bash
node scripts/test_web_start_html_v2.mjs
```

</section>

<section id="modify-add-profile" data-learning-context="modify-add-profile" data-context-type="modify" markdown="1">

## 加入你的记录和按钮

在 `PROFILES` 中增加自己的记录，再在 HTML 控制区增加一个匹配的按钮：

```javascript
"my-profile": {
  name: "你的昵称",
  description: "正在把学习记录做成可交互页面。",
  completedLessons: 9,
  hours: 8,
  status: "继续推进",
  nextMilestone: "连接本地 API"
}
```

按钮的 `data-profile-id` 必须是同一个 `my-profile`。先故意写成 `my-proflie`，观察它进入空数据，再改正。你会看到 DOM 选择器没坏，真正出错的是“按钮传入的 ID 与数据键不一致”。

最后新增一个字段，例如“本周完成”，并从记录对象一直接到 HTML 和 `render()`。只改对象而页面没变化，说明渲染契约还没有接上这个字段。

</section>

<section id="troubleshoot-javascript-page" data-learning-context="troubleshoot-javascript-page" data-context-type="troubleshoot" markdown="1">

## 点了没反应，先看控制台第一条错误

| 看到什么 | 常见原因 | 怎样恢复 |
| --- | --- | --- |
| 所有按钮都没反应 | `app.js` 路径错、文件未保存或脚本语法错误 | 打开开发者工具 Console，看第一条红色错误与文件行号 |
| 报 `Cannot read ... of null` | 选择器拼错，`querySelector()` 没找到元素 | 对照 HTML 中的 id、class 或 data 属性 |
| 总是进入空数据 | 按钮 ID 与 `PROFILES` 键不一致 | 在事件里临时输出 profileId，逐字比较 |
| 页面换了数据，按钮状态没变 | 忘记同步 `aria-pressed` | 每次选择时统一更新所有按钮 |
| 新名字被当成标签 | 使用了 `innerHTML` | 改用 `textContent` 显示普通文字 |

不要一看到空白就重写全部 JavaScript。先确认脚本有没有加载，再看第一条错误，然后检查事件是否触发、状态是否正确、最后才看 DOM 更新。

</section>

<section id="project-dashboard-v03" data-learning-context="project-dashboard-v03" data-context-type="project" markdown="1">

## 学习面板开始响应操作

| v0.2 | Web v0.3 增加 | 下一版 |
| --- | --- | --- |
| 一份静态学习记录 | 多条本地记录与选择按钮 | 用 HTTP 获取 JSON |
| CSS 负责桌面与手机布局 | 事件、状态和统一 render | 接入 FastAPI 契约 |
| 页面只有一种成功外观 | 加载、成功、空数据、错误 | 处理真实 200、404、422 和断线 |

项目现在已有三个清楚边界：HTML 负责结构，CSS 负责表现，JavaScript 负责状态和变化。下一课只替换数据获取方式，不推翻这三层。

</section>

<section id="deepen-dom-state-boundary" data-learning-context="deepen-dom-state-boundary" data-context-type="deepen" markdown="1">

## 再往里看：DOM 不应该是唯一数据源

如果程序每次都从页面文字里反推“当前完成了几节”，显示格式一改，逻辑也会跟着坏。本课让 `PROFILES` 和 `view.kind` 保存程序状态，DOM 只是状态的显示结果。

大型前端框架也会处理“状态怎样映射到界面”，只是提供了更系统的组件和更新方式。现在先用几十行原生 JavaScript 看懂这条关系，后面学框架时才知道它替你解决了什么。

</section>

<section id="career-explain-ui-state" data-learning-context="career-explain-ui-state" data-context-type="career" markdown="1">

## 求职加练：解释一次状态设计

不要只演示按钮能点。用代码回答：为什么空数据和错误要分开？为什么按钮不直接修改每个 DOM 字段？为什么显示名字使用 `textContent`？

再保留一份测试输出，证明已知记录、未知记录和模拟错误都得到确定状态。这样的讲法能把“小页面”说成一次有设计、有失败路径、有验证的工程增量。

</section>

## 完成检查

- [ ] 能说清 HTML 文件、DOM 和屏幕页面的关系。
- [ ] 能沿着“事件 → 状态 → render → DOM”解释一次点击。
- [ ] 页面能稳定展示加载、成功、空数据和错误四种状态。
- [ ] 自己增加一条记录、一个按钮和一个新字段。
- [ ] 能从脚本未加载、空选择器或错误 ID 中恢复。
- [ ] 禁用 JavaScript 后初始内容仍可阅读。
- [ ] 测试通过，手机宽度没有横向滚动。

## 来源与版本

- DOM 查询、事件监听与文字更新：MDN Web API 文档，核查于 2026-07-18。
- 动态状态提示：WAI-ARIA `status` role 与 MDN live regions，核查于 2026-07-18。
- JavaScript 语言目标：现代 Chrome、Edge、Firefox 与 Safari；示例使用普通脚本，不依赖打包器、框架或实验性 API。

## 下一步

下一课会把 `PROFILES` 中的本地对象替换为 FastAPI 返回的 JSON，让加载、成功、空数据和错误状态第一次对应真实 HTTP 请求：继续学习 [HTTP、JSON 与本地 API](04-http-json-local-api.md)。

参考：[MDN EventTarget](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget) · [MDN querySelector](https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector) · [MDN textContent](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent) · [MDN status role](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/status_role)
