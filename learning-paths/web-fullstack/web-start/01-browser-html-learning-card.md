<div class="be-tutor-mount" data-tutor-lesson="web-start-01" aria-hidden="true"></div>

<section id="overview-learning-card" class="be-page-hero be-lesson-hero" data-learning-context="overview-learning-card" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Web 起步 · 第一课 · 学习进度报告器 Web v0.1</span>

# 浏览器、HTML 与第一张学习卡片

## 先在浏览器里看到它

<div class="be-profile-preview" aria-label="学习进度卡片预览">
  <span>学习进度报告器 Web v0.1</span>
  <strong>小码的学习卡片</strong>
  <p>正在学习 Python 与 Web，希望把练习做成可以展示的作品。</p>
  <div>
    <span><b>7 节</b><small>已完成课程</small></span>
    <span><b>6.5 小时</b><small>本周投入</small></span>
    <span><b>按计划推进</b><small>当前状态</small></span>
  </div>
</div>

这一页还没有按钮，也没有连接服务器。它只做一件基础但重要的事：把内容写成浏览器能理解的 HTML 文档。下一课再来整理它的外观。

<div class="be-page-actions" markdown="1">
[先看浏览器读到了什么](#concept-browser-document){ .md-button .md-button--primary }
[直接打开示例文件](#reproduce-open-page){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Web 起步 · 1 / 4</strong></div>
  <div><span>开始条件</span><strong>完成 Python 起步，能使用 VS Code</strong></div>
  <div><span>完成后留下</span><strong>index.html、styles.css 与浏览器截图</strong></div>
</div>

## 开始前

- 小白可以从头学习；如果你已有基础，先不看正文，独立写出带标题、介绍和三项数据的页面。能解释 `main`、`article`、`h1`、`dl` 的作用并通过本课测试，就可以跳到第二课。
- 在 `learning-workspace` 里新建 `practice/web-start/learning-dashboard/`。
- 这节课只需要 VS Code 和现代浏览器，不需要安装 Node.js、前端框架或 Web 服务器。

<section id="concept-browser-document" data-learning-context="concept-browser-document" data-context-type="concept" markdown="1">

## 浏览器拿到的是一份文档

双击 `index.html` 时，操作系统把文件交给浏览器。浏览器从上往下读取标签，先建立文档结构，再把它画到屏幕上。

<div class="be-data-flow" role="img" aria-label="index.html 文件经过浏览器解析后形成文档结构，最后显示为页面">
  <div><strong>index.html</strong><span>文字与标签</span></div>
  <div><strong>浏览器解析</strong><span>认出标题、段落和数据</span></div>
  <div><strong>文档结构</strong><span>元素之间有层级</span></div>
  <div><strong>屏幕页面</strong><span>把结构显示出来</span></div>
</div>

HTML 负责描述内容是什么。`h1` 是本页主标题，`p` 是段落，`article` 是一份可以独立理解的内容。颜色、间距和布局主要交给 CSS；按钮点击后的变化则主要交给 JavaScript。

</section>

<section id="concept-document-shell" data-learning-context="concept-document-shell" data-context-type="concept" markdown="1">

## 一份完整页面先要有外壳

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>小码的学习进度</title>
  </head>
  <body>
    <main>页面真正显示的内容</main>
  </body>
</html>
```

- `<!doctype html>` 告诉浏览器按现代 HTML 规则解释页面。
- `lang="zh-CN"` 标明正文语言，朗读工具和搜索引擎会用到它。
- `charset="utf-8"` 让中文按 UTF-8 解码，避免出现乱码。
- `viewport` 让手机按设备宽度排版。少了它，手机可能先画一张很宽的桌面页面，再整体缩小。
- `title` 出现在浏览器标签页；页面里的大标题仍要写 `h1`。

`head` 放文档信息和资源链接，`body` 放用户在页面里看到的内容。两者不要混在一起。

</section>

<section id="example-semantic-card" data-learning-context="example-semantic-card" data-context-type="example" markdown="1">

## 用合适的标签写卡片

```html
<main>
  <article aria-labelledby="profile-title">
    <h1 id="profile-title">小码的学习卡片</h1>
    <p>正在学习 Python 与 Web。</p>

    <dl>
      <div>
        <dt>已完成课程</dt>
        <dd>7 节</dd>
      </div>
      <div>
        <dt>当前状态</dt>
        <dd>按计划推进</dd>
      </div>
    </dl>
  </article>
</main>
```

这里用 `dl` 表示一组“名称—值”：`dt` 是名称，`dd` 是对应值。全换成 `div` 也可能画出相似的页面，但结构会变得含糊。标签不是为了让代码显得高级，而是让浏览器、辅助技术和后来维护代码的人知道这段内容的意思。

`aria-labelledby="profile-title"` 把卡片名称指向现有标题。这里已有可见标题，所以不需要再写一份重复的隐藏名称。

</section>

<section id="reproduce-open-page" data-learning-context="reproduce-open-page" data-context-type="reproduce" markdown="1">

## 把示例放进自己的工作区

建立下面的目录：

```text
practice/
└── web-start/
    └── learning-dashboard/
        ├── index.html
        └── styles.css
```

把正式示例复制进去：

=== "Windows PowerShell"

    ```powershell
    Copy-Item .\site-src\examples\web-start\learning-dashboard-v01\* `
      .\practice\web-start\learning-dashboard\
    ```

=== "macOS / Linux"

    ```bash
    cp site-src/examples/web-start/learning-dashboard-v01/* \
      practice/web-start/learning-dashboard/
    ```

在 VS Code 文件树里右键 `index.html`，选择“在 Finder 中显示”或“在文件资源管理器中显示”，再双击它。浏览器地址通常以 `file://` 开头，这表示它读取的是本地文件。

你应该看到第一屏中的学习卡片。随后查看页面源代码：浏览器显示的是经过 CSS 排版的页面，源代码仍是刚才那份 HTML。

!!! note "这节课不用急着装 Live Server"
    双击 HTML 已经足够验证静态页面。后面学习请求和模块时，我们会使用明确的本地服务器，不把编辑器插件当成 Web 原理。

</section>

<section id="modify-own-card" data-learning-context="modify-own-card" data-context-type="modify" markdown="1">

## 换成你自己的内容

打开本地 `index.html`，完成四处修改：

1. 把“小码”换成你的昵称。
2. 改写一句学习目标，不照抄示例。
3. 修改完成课程和本周投入。
4. 自己增加第四项，例如“正在进行”或“下一个里程碑”。

保存后刷新浏览器。改标题时，页面里的 `h1` 和浏览器标签页里的 `title` 要分别修改；它们服务的位置不同。

再把 `styles.css` 暂时改名为 `styles.off`，刷新看看。内容仍在，外观会变回浏览器默认样式。这正好说明 HTML 结构和 CSS 表现是两层。看完把文件名改回来。

</section>

<section id="troubleshoot-local-page" data-learning-context="troubleshoot-local-page" data-context-type="troubleshoot" markdown="1">

## 页面不对时，从文件关系开始查

| 看到什么 | 常见原因 | 怎样恢复 |
| --- | --- | --- |
| 浏览器显示旧内容 | 文件没保存，或打开的是另一份 `index.html` | 在 VS Code 保存，再比较浏览器地址与文件路径 |
| 中文变成乱码 | 缺少 UTF-8 声明，或文件不是 UTF-8 | 保留 `<meta charset="utf-8">`，检查编辑器编码 |
| 页面有内容但没有卡片外观 | `styles.css` 文件名或 `link href` 不一致 | 确认两个文件在同一目录，名称完全相同 |
| 双击后看到目录或下载提示 | 打开的不是 `index.html` | 回到文件管理器，确认扩展名没有变成 `.txt` |
| 手机预览特别小 | 缺少 viewport 声明 | 恢复本课给出的 `meta viewport` |

先核对“浏览器打开的是哪份文件”，再查 HTML 和 CSS。路径错了时，改再多标签也不会影响当前页面。

</section>

<section id="project-dashboard-v01" data-learning-context="project-dashboard-v01" data-context-type="project" markdown="1">

## 报告器第一次进入浏览器

Python 版本已经能计算和打印学习报告。这节课先把同一类信息做成静态页面，还没有让两边自动连接。

| 原来 | Web v0.1 增加 | 下一版 |
| --- | --- | --- |
| 终端里的文字报告 | 一份能直接打开的 HTML 学习卡片 | 用 CSS 自己完成布局与窄屏适配 |
| Python 数据结构 | HTML 中手写的示例数据 | 用 JavaScript 管理页面状态 |
| 命令行运行结果 | 浏览器页面与源文件 | 从 FastAPI 自动读取 JSON |

把 `index.html`、`styles.css` 和一张浏览器截图保存在项目中。截图只用于说明结果，源文件才是可以继续演进的作品。

</section>

<section id="career-explain-html" data-learning-context="career-explain-html" data-context-type="career" markdown="1">

## 求职加练：别只说“我会 HTML”

用自己的页面回答下面三个问题：

1. 为什么主标题写成 `h1`，数据组写成 `dl`？
2. 如果删掉 `meta viewport`，手机上可能出现什么变化？
3. 如何证明页面内容与样式没有绑死在一起？

回答时直接指向代码和你刚才做过的改名实验。这样的证据比罗列标签名称更有说服力。兴趣画像可以跳过这段口头整理，项目本身仍建议保留。

</section>

## 完成检查

- [ ] 能从文件管理器打开自己的 `index.html`，并确认浏览器打开的是正确路径。
- [ ] 能说清 `head`、`body`、`title` 与 `h1` 各自放什么。
- [ ] 页面包含一个主标题、一段介绍和至少四项“名称—值”数据。
- [ ] 暂时移走 CSS 后，内容仍按合理顺序出现。
- [ ] 能从旧内容、乱码、样式丢失或错误文件中恢复。

## 来源与版本

- HTML 语义与元素：WHATWG HTML Living Standard、MDN HTML 元素参考，核查于 2026-07-18。
- 页面创建与基础结构：MDN Learn Web Development，核查于 2026-07-18。
- 示例目标：现代 Chrome、Edge、Firefox 与 Safari；本课不依赖实验性 API。

## 下一步

下一课将不再只使用现成样式。你会读懂并修改 CSS，把同一份 HTML 做成桌面与手机都能阅读的学习面板：[CSS 布局、视觉层级与手机适配](02-css-layout-responsive-dashboard.md)。

参考：[HTML Living Standard](https://html.spec.whatwg.org/multipage/) · [MDN HTML 元素参考](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements) · [MDN：创建网页内容](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Creating_the_content)
