<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-05" aria-hidden="true"></div>

<section id="overview-markdown-result" class="be-page-hero be-lesson-hero" data-learning-context="overview-markdown-result" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">工程基础入门 · 第五课</span>

# Markdown

## 左边是纯文本，右边是给人读的文档

<div class="be-markdown-compare" role="group" aria-label="同一份 Markdown 源文本与渲染后阅读效果的对照">
  <div class="be-markdown-compare__source">
    <span>你编辑的源文本</span>
    <pre><code># 学习记录

## 本次结果

- 找到项目目录
- 保存并复核文件

&#96;&#96;&#96;text
assets  notes  practice
&#96;&#96;&#96;</code></pre>
  </div>
  <div class="be-markdown-compare__preview">
    <span>预览中的阅读效果</span>
    <div class="be-markdown-preview-card">
      <strong>学习记录</strong>
      <h3>本次结果</h3>
      <ul><li>找到项目目录</li><li>保存并复核文件</li></ul>
      <pre><code>assets  notes  practice</code></pre>
    </div>
  </div>
</div>

两边来自同一份 `.md` 文件。Markdown 没有把源文本变成另一份文档；预览器只是按照符号和结构，把它显示得更容易阅读。

<div class="be-page-actions" markdown="1">
[先看懂源文本和预览](#concept-source-preview){ .md-button .md-button--primary }
[返回 VS Code 编辑器](04-editor.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>工程基础入门 · 5 / 10</strong></div>
  <div><span>继续使用</span><strong>notes/learning-log.md</strong></div>
  <div><span>完成后留下</span><strong>一份可阅读、可复核的学习记录</strong></div>
</div>

<section id="concept-source-preview" data-learning-context="concept-source-preview" data-context-type="concept" markdown="1">

## 源文本负责保存，预览负责阅读

Markdown 是一种纯文本写法。文件仍然由普通字符组成，所以编辑器、终端和 Git 都能直接读取；支持 Markdown 的工具会把其中的结构渲染成标题、列表、链接和代码块。

```text
learning-log.md（磁盘中的纯文本）
        │
        ├── VS Code 编辑区：修改原始字符
        ├── 终端 cat / Get-Content：读取原始字符
        └── Markdown 预览：按照语法显示阅读效果
```

预览不是最终事实。修改是否真的保存，要看标签状态、重新打开结果或终端读取；链接是否正确，要实际点击；命令是否有效，要回到终端运行。

!!! tip "文件扩展名仍然重要"
    保存为 `learning-log.md`，VS Code 才会自动启用内置 Markdown 支持。若文件实际叫 `learning-log.md.txt`，先回到文件系统课修正扩展名。

</section>

<section id="example-markdown-building-blocks" data-learning-context="example-markdown-building-blocks" data-context-type="example" markdown="1">

## 先用五种写法整理一份记录

### 标题说明文档层级

```markdown
# 工程学习记录

## 本次目标

## 实际操作

## 结果与问题
```

`#` 后留一个空格。这里把一级标题留给整篇文档，主要部分使用二级标题；标题表达结构，不是用来把字变大。

### 列表把并列项和步骤分开

```markdown
## 实际操作

1. 打开学习工作区。
2. 修改并保存学习记录。
3. 从终端重新读取文件。

## 结果与问题

- 搜索能找到独特关键词。
- 曾经打开错一层目录，已经恢复。
```

有先后顺序的操作用有序列表；互相并列的结果用无序列表。标记后也要留空格，例如 `- 结果`，不要写成 `-结果`。

### 链接把相关文件连起来

```markdown
[练习目录说明](../practice/README.md)
```

方括号里是读者看见的文字，圆括号里是目标地址。这个链接从 `notes/learning-log.md` 出发，先回到上一层，再进入 `practice`。

### 代码块保留命令和输出

````markdown
```text
assets
notes
practice
```
````

前后各一行三个反引号。`text` 是语言标记，表示这段只是普通文字；若记录 Shell 命令，也可以写 `bash` 或 `powershell`。

### 表格只在需要对照时使用

```markdown
| 检查项 | 实际结果 | 下一步 |
| --- | --- | --- |
| 文件保存 | 重新打开仍能看到新内容 | 用 Git 保存版本 |
```

表格的第二行叫分隔行。它属于 GitHub Flavored Markdown（GFM）扩展，不在 CommonMark 基础语法中；GitHub、VS Code 和本站能显示，但其他渲染器不一定支持。

</section>

<section id="reproduce-structure-learning-log" data-learning-context="reproduce-structure-learning-log" data-context-type="reproduce" markdown="1">

## 把现有记录整理成下面的结构

在 VS Code 打开 `notes/learning-log.md`。先复制一份备份为 `notes/learning-log-before-markdown.txt`，然后把原文件整理成下面的完整版本。已有的真实路径、命令和错误记录不要丢，替换到对应位置。

````markdown
# 工程学习记录

## 当前目标

完成工程基础入门，并保留每次操作和排错记录。

## 已完成

- 建立 `learning-workspace` 目录。
- 从终端定位并读取学习记录。
- 用 VS Code 修改、保存和搜索文件。

## 终端检查

```text
项目根目录：换成你的真实路径
目录内容：assets  notes  practice
```

## 编辑器检查

1. 打开完整工作区。
2. 保存带有独特关键词的修改。
3. 从搜索和内置终端复核同一份文件。

## 相关文件

[练习目录说明](../practice/README.md)

## 当前状态

| 检查项 | 实际结果 | 下一步 |
| --- | --- | --- |
| 文件和目录 | 能从三种入口找到 | 用 Git 保存第一个版本 |
````

接着在 `practice` 中新建 `README.md`：

```markdown
# 练习目录

这里保存后续课程的可运行代码和练习结果。
```

现在 `learning-log.md` 中的相对链接有了真实目标。保存两个文件，再从文件树重新打开，确认内容都还在。

</section>

<section id="reproduce-preview-side-by-side" data-learning-context="reproduce-preview-side-by-side" data-context-type="reproduce" markdown="1">

## 在 VS Code 里一边写，一边看

保持 `learning-log.md` 处于编辑状态：

1. 打开命令面板：Windows / Linux 按 `Ctrl + Shift + P`，macOS 按 `Command + Shift + P`。
2. 输入 `Markdown: Open Preview to the Side` 并执行。
3. 左边保留源文本，右边显示预览。
4. 点击每个标题、列表和链接，确认结构与目标正确。

也可以使用快捷键：

- 当前标签切换预览：Windows / Linux `Ctrl + Shift + V`；macOS `Command + Shift + V`。
- 打开侧边预览：Windows / Linux `Ctrl + K` 后按 `V`；macOS `Command + K` 后按 `V`。

预览会随编辑更新，但这里仍建议先保存，再用终端读取一次：

=== "macOS / Linux"

    ```bash
    head -n 12 notes/learning-log.md
    ```

=== "Windows PowerShell"

    ```powershell
    Get-Content notes\learning-log.md -TotalCount 12
    ```

预览、编辑区和终端都指向同一份文件，才完成这次整理。

</section>

<section id="modify-personal-learning-log" data-learning-context="modify-personal-learning-log" data-context-type="modify" markdown="1">

## 把模板改成你的真实记录

模板只是起点。至少完成下面四处修改：

1. 把“当前目标”换成自己正在完成的目标。
2. 把终端路径和目录列表换成真实输出。
3. 在“已完成”里加入一条只有你做过的操作。
4. 把表格的“实际结果”改成能被文件、输出或操作证明的描述。

然后点击 `[练习目录说明](../practice/README.md)`。如果预览能打开刚创建的文件，再返回学习记录，说明相对路径正确。

最后请一个不了解前几课的人只读预览，或者隔几分钟后自己重读一次，回答三个问题：现在做到哪里、遇到过什么、下一步是什么。答案都能从页面中找到，文档才真的清楚。

</section>

<section id="troubleshoot-markdown-rendering" data-learning-context="troubleshoot-markdown-rendering" data-context-type="troubleshoot" markdown="1">

## 预览不对，先看源文本

| 预览中的现象 | 常见原因 | 怎样修 |
| --- | --- | --- |
| `#标题` 仍是普通文字 | `#` 后没有空格 | 改成 `# 标题` |
| `-结果` 没变成列表 | 列表标记后没有空格 | 改成 `- 结果` |
| 后面整页都变成代码 | 围栏代码块没有闭合 | 找到开头三个反引号，补上结尾三个 |
| 链接点击后找不到文件 | 路径起点或目标文件不对 | 从当前 `.md` 所在目录逐级走一遍 |
| 表格仍显示竖线文字 | 缺少分隔行，或当前渲染器不支持 GFM 表格 | 补上 `| --- |`；必要时改用列表 |
| 预览和终端内容不同 | 文件尚未保存，或读了同名文件 | 看标签圆点，再核对完整路径 |

故意删掉代码块最后三个反引号，观察后续内容怎样被吞进代码块；然后补回并保存。这个错误很常见，亲眼见过一次，以后更容易从页面突然“全变灰”定位到围栏未闭合。

</section>

<section id="deepen-markdown-portability" data-learning-context="deepen-markdown-portability" data-context-type="deepen" markdown="1">

## 不同平台为什么可能显示不同

“Markdown”不是所有平台完全相同的一套功能。CommonMark 规定了标题、段落、列表、链接和围栏代码块等共同基础；GitHub Flavored Markdown 在此之上增加表格、任务列表、删除线和自动链接等扩展。

为了让项目文档更容易迁移：

- 主要结构优先使用 CommonMark 基础语法。
- 表格适合短小对照；内容很长时改用标题和列表。
- 不依赖复杂 HTML、脚本或只在某个插件里生效的写法。
- 发布前在目标平台实际预览，不把 VS Code 预览当成所有平台的最终效果。

</section>

<section id="project-workspace-v05" data-learning-context="project-workspace-v05" data-context-type="project" markdown="1">

## 工程学习工作台 v0.5

工作区里的记录不再只是零散文字，它开始承担项目说明和复盘入口：

| 原来会什么 | 这节课增加什么 | 发生变化的文件 | 下一课怎样继续 |
| --- | --- | --- | --- |
| 用编辑器保存、搜索和复核文件 | 用标题、列表、链接、代码块和表格组织真实记录 | `notes/learning-log.md`、`practice/README.md` | 安装 Git，建立 `.gitignore`，保存第一个本地版本 |

保留 `learning-log-before-markdown.txt` 作为整理前对照。下一课 Git 初始化前，会先判断哪些文件应该进入版本库，哪些临时文件应该忽略。

</section>

??? success "求职时怎样展示"
    文档能力不是“会背 Markdown 语法”。更有价值的是：项目入口清楚、命令和错误可复现、相对链接能打开、别人能从记录理解你做了什么以及怎样验证。

## 完成检查

- [ ] 能解释 Markdown 源文本和预览的区别。
- [ ] `learning-log.md` 有一个主标题和清楚的二级标题结构。
- [ ] 能根据内容选择有序列表或无序列表。
- [ ] 相对链接能从学习记录打开 `practice/README.md`。
- [ ] 代码块完整保留一段真实命令或输出。
- [ ] 能说明表格属于 GFM 扩展，并在不支持时改用列表。
- [ ] 已故意制造并修复一次未闭合代码块。
- [ ] 预览、编辑区和终端读取的是同一份保存文件。

## 来源与版本

- 适用格式：CommonMark 0.31.2 基础语法；GitHub Flavored Markdown 的表格扩展。
- 基础语法：[CommonMark Spec](https://spec.commonmark.org/0.31.2/)。
- 表格扩展：[GitHub Flavored Markdown Spec：Tables](https://github.github.com/gfm/#tables-extension-)。
- VS Code 编辑与预览：[Markdown and Visual Studio Code](https://code.visualstudio.com/docs/languages/markdown)。
- 验证方式：在 VS Code Stable 中使用侧边预览，并从终端读取保存后的源文本；相对链接实际点击打开目标文件。
- 核查日期：2026-07-17。

## 下一步

进入 [本地 Git 与 .gitignore](06-git.md)。下一节会先安装并验证 Git，再把当前工作区的文档变成可以查看历史、撤回和继续演进的本地版本库。

<div class="be-next-panel" markdown="1">

<span class="be-panel-label">完成本课后</span>

**保留整理前后的两份记录和 `practice/README.md`，下一课会判断它们怎样进入版本历史。**

[进入下一课：本地 Git 与 .gitignore](06-git.md){ .md-button .md-button--primary }

</div>
