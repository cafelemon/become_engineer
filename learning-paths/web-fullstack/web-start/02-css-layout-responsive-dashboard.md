<div class="be-tutor-mount" data-tutor-lesson="web-start-02" aria-hidden="true"></div>

<section id="overview-readable-dashboard" class="be-page-hero be-lesson-hero" data-learning-context="overview-readable-dashboard" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Web 起步 · 第二课 · 学习进度报告器 Web v0.2</span>

# CSS 布局、视觉层级与手机适配

## 同一份内容，换个宽度也要好读

<div class="be-responsive-compare" aria-label="学习面板在桌面和手机宽度下的布局对比">
  <div class="be-responsive-compare__desktop">
    <span>桌面 · 三列</span>
    <strong>小码的学习面板</strong>
    <div><i>7 节</i><i>6.5 小时</i><i>按计划推进</i></div>
  </div>
  <div class="be-responsive-compare__mobile">
    <span>手机 · 单列</span>
    <strong>小码的学习面板</strong>
    <div><i>7 节</i><i>6.5 小时</i><i>按计划推进</i></div>
  </div>
</div>

HTML 没有变成两份。CSS 根据可用宽度调整间距和排列，让标题、说明和数据始终有清楚的先后关系。

<div class="be-page-actions" markdown="1">
[先读懂一条 CSS 规则](#concept-css-rule){ .md-button .md-button--primary }
[直接复现 v0.2](#reproduce-dashboard-v02){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Web 起步 · 2 / 4</strong></div>
  <div><span>开始条件</span><strong>完成第一张 HTML 学习卡片</strong></div>
  <div><span>完成后留下</span><strong>桌面截图、390px 截图与 styles.css</strong></div>
</div>

## 开始前

- 如果你第一次写 CSS，从“一条规则怎样找到一个元素”开始。
- 如果你已有基础，先不看正文：让 v0.1 在宽屏显示三列，在 390px 显示单列，并解释 `box-sizing`、Grid 和媒体查询各解决什么问题。能通过本课测试，可以进入 JavaScript。
- 继续使用上一课的 `practice/web-start/learning-dashboard/`，不要另起一个无关页面。

<section id="concept-css-rule" data-learning-context="concept-css-rule" data-context-type="concept" markdown="1">

## CSS 先找到元素，再改变表现

```css
.study-card {
  padding: 2rem;
  border-radius: 1.5rem;
  background: #ffffff;
}
```

<div class="be-style-rule" aria-label="CSS 规则由选择器、属性和值组成">
  <div><strong>.study-card</strong><span>选择器：找谁</span></div>
  <div><strong>padding</strong><span>属性：改什么</span></div>
  <div><strong>2rem</strong><span>值：改成怎样</span></div>
</div>

`.study-card` 会找到 `class="study-card"` 的元素。花括号里每一行都是一条声明，冒号左边是属性，右边是值。

类名可以重复使用，`id` 应该在页面中保持唯一。写样式时通常优先用类名：它既清楚，又不会把选择器权重抬得太高。

</section>

<section id="concept-box-model" data-learning-context="concept-box-model" data-context-type="concept" markdown="1">

## 卡片占多宽，要把四层算在一起

一个元素从里到外有内容、内边距、边框和外边距：

```text
外边距 margin
└─ 边框 border
   └─ 内边距 padding
      └─ 内容 content
```

浏览器默认的 `content-box` 会把 `width` 只算作内容宽度，内边距和边框还要额外加上。项目开头加入下面这条规则，会更容易判断最终尺寸：

```css
* {
  box-sizing: border-box;
}
```

现在 `width: 100%` 已经包含内边距和边框。它不会自动解决所有溢出，但能避开新手最常遇到的一类“明明 100%，为什么还超出去”。

</section>

<section id="example-grid-hierarchy" data-learning-context="example-grid-hierarchy" data-context-type="example" markdown="1">

## 让三项数据排成真正的网格

先给 `dl` 一个更明确的类名：

```html
<dl class="metrics">
  <div>
    <dt>已完成课程</dt>
    <dd>7 节</dd>
  </div>
  <!-- 另外两项保持相同结构 -->
</dl>
```

再把它设成三列：

```css
.metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}
```

- `display: grid` 让这个容器按网格安排直接子元素。
- `repeat(3, ...)` 建立三列。
- `1fr` 表示分享可用空间；`minmax(0, 1fr)` 允许列在内容很长时继续收缩。
- `gap` 只负责网格项之间的距离，不需要给每个卡片单独补外边距。

视觉层级也不是“所有文字都放大”。主标题最醒目，指标值次之，标签和说明用较轻的颜色与字号。读者扫一眼就知道先看什么。

</section>

<section id="example-responsive-width" data-learning-context="example-responsive-width" data-context-type="example" markdown="1">

## 页面变窄时，别硬塞三列

先写适合宽屏的默认样式，再在窄屏覆盖必要部分：

```css
@media (max-width: 40rem) {
  body {
    padding: 0.75rem;
  }

  .metrics {
    grid-template-columns: 1fr;
  }
}
```

媒体查询不是在判断“这是不是某款手机”，而是在判断当前视口是否不超过 `40rem`。这样调整浏览器窗口、手机横竖屏或分屏窗口时，布局都能按可用空间变化。

字号和卡片内边距可以用 `clamp()` 在上下限之间平滑变化：

```css
h1 {
  font-size: clamp(2rem, 7vw, 3.25rem);
}
```

这里的字号不会小于 `2rem`，不会大于 `3.25rem`，中间部分随视口变化。

</section>

<section id="reproduce-dashboard-v02" data-learning-context="reproduce-dashboard-v02" data-context-type="reproduce" markdown="1">

## 把 v0.2 放进自己的项目

复制这一版示例：

=== "Windows PowerShell"

    ```powershell
    Copy-Item .\site-src\examples\web-start\learning-dashboard-v02\* `
      .\practice\web-start\learning-dashboard\ -Force
    ```

=== "macOS / Linux"

    ```bash
    cp site-src/examples/web-start/learning-dashboard-v02/* \
      practice/web-start/learning-dashboard/
    ```

保存后刷新浏览器。先看桌面宽度，再打开浏览器开发者工具的设备模式，把宽度改成 `390`。你应该看到：

- 桌面宽度下三项数据并排。
- 390px 下三项数据改成单列。
- 页面没有横向滚动条，长的“下一个里程碑”也能换行。
- 系统处于深色模式时，页面不会出现白底白字或刺眼的大白块。

开发者工具只是快速改变视口。最后仍建议在真实手机浏览器打开一次；桌面模拟不能证明触摸、浏览器工具栏和系统字体缩放都没有问题。

</section>

<section id="modify-personal-theme" data-learning-context="modify-personal-theme" data-context-type="modify" markdown="1">

## 做一版属于你的视觉层级

不要只换昵称，这次至少改四处 CSS：

1. 修改 `--accent`，选一个仍能看清文字的主色。
2. 调整卡片最大宽度，并观察太宽时阅读为什么变累。
3. 把窄屏断点从 `40rem` 改成 `32rem`，拖动窗口比较切换时机。
4. 给自己新增的第四项数据补样式，放入 `.metrics` 网格。

每改一处先预测，再刷新验证。保留一张桌面截图和一张 390px 截图，并写一句说明：你为什么选这个断点，而不是“大家都这么写”。

</section>

<section id="troubleshoot-css-layout" data-learning-context="troubleshoot-css-layout" data-context-type="troubleshoot" markdown="1">

## 样式不对时，先看哪条规则赢了

| 看到什么 | 常见原因 | 怎样恢复 |
| --- | --- | --- |
| 改了 CSS 完全没变化 | 文件没保存、链接路径错或浏览器打开旧副本 | 先确认 Network／Sources 中加载的是当前 `styles.css` |
| 规则被划掉 | 后面有同等或更高权重的规则覆盖它 | 在开发者工具 Styles 面板找到最终生效声明 |
| 手机仍是三列 | 媒体查询括号、单位或选择器写错 | 检查 `@media (max-width: 40rem)` 与 `.metrics` |
| 页面出现横向滚动 | 固定宽度、长单词或网格最小宽度撑开容器 | 查超宽元素，使用 `minmax(0, 1fr)` 和合理换行 |
| 深色模式对比很差 | 只改了背景，忘记文字和子卡片 | 在深色媒体查询中一起检查背景、正文和弱化文字 |

CSS 的“级联”会综合来源、重要性、选择器权重和出现顺序。起步阶段先保持选择器简单，并把同一组件的规则放在一起；不要用一串 `!important` 掩盖覆盖关系。

</section>

<section id="project-dashboard-v02" data-learning-context="project-dashboard-v02" data-context-type="project" markdown="1">

## 学习面板有了稳定布局

| v0.1 | Web v0.2 增加 | 下一版 |
| --- | --- | --- |
| HTML 语义结构 | 颜色变量、盒模型和视觉层级 | 用 JavaScript 切换数据 |
| 浏览器默认流与基础样式 | 桌面三列、手机单列 | 展示加载、成功和空状态 |
| 能直接打开 | 深浅色与窄屏检查 | 把数据从 HTML 中分离 |

把两张截图和 `styles.css` 一起提交到学习工作区。截图说明结果，CSS 记录实现；两者缺一时，别人都很难复现你的判断过程。

</section>

<section id="deepen-cascade-responsive" data-learning-context="deepen-cascade-responsive" data-context-type="deepen" markdown="1">

## 再往里看：响应式不是缩小版桌面

真正的响应式设计会根据空间重新安排优先级。三项指标在桌面并排便于比较，在窄屏改成单列便于阅读；这不是单纯把所有东西按比例缩小。

项目目前只用了一个断点，因为内容只有一张卡片。以后页面出现导航、图表或双栏编辑区，再由内容何时开始拥挤来增加断点。断点应该来自布局需要，不来自设备型号清单。

</section>

<section id="career-explain-responsive" data-learning-context="career-explain-responsive" data-context-type="career" markdown="1">

## 求职加练：用一次溢出说明你的判断

故意把 `.study-card` 改成 `width: 50rem`，在 390px 视口观察横向滚动；随后恢复为 `width: min(100%, 42rem)`。

用“现象—原因—修复—验证”讲清这次排错：固定宽度超过视口，改为流动宽度并保留上限，最后在桌面与 390px 各验证一次。求职画像保存这段复盘；兴趣画像做完恢复即可。

</section>

## 完成检查

- [ ] 能指出一条 CSS 规则中的选择器、属性和值。
- [ ] 能解释 `box-sizing: border-box` 改变了怎样的尺寸计算。
- [ ] 学习数据在宽屏三列、390px 单列，且没有横向滚动。
- [ ] 能用开发者工具找到一条被覆盖的规则，而不是盲目添加 `!important`。
- [ ] 保存自己的桌面与手机截图，并说明断点选择。
- [ ] 第一课的 HTML 语义结构仍然完整。

## 来源与版本

- CSS 盒模型、级联与属性：MDN CSS 指南，核查于 2026-07-18。
- Grid 与响应式设计：MDN Learn Web Development，核查于 2026-07-18。
- 媒体查询：CSS Media Queries Level 4 与 MDN，核查于 2026-07-18。
- 示例目标：现代 Chrome、Edge、Firefox 与 Safari；不依赖实验性 CSS。

## 下一步

下一课会保留这份布局，用 JavaScript 让页面切换学习者数据，并明确加载、成功、空数据和错误四种状态：[JavaScript 事件、DOM 与页面状态](03-javascript-events-dom-page-state.md)。

参考：[MDN CSS 盒模型](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Box_model) · [MDN CSS Grid](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Grids) · [MDN 响应式设计](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design) · [CSS Media Queries Level 4](https://www.w3.org/TR/mediaqueries-4/)
