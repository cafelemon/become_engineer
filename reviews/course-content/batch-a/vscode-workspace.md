# VS Code：打开第一个学习文件夹

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-vscode-workspace" aria-hidden="true"></div>

<section id="overview-result" class="be-sample-hero" data-learning-context="overview-result" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">工具操作样板 · 工程基础</span>

## 学完以后，屏幕上应该留下这三样东西

`learning-log.md` 已经保存，工作区搜索能找到你刚写的内容，内置终端也能读到同一份文件。只要这三件事都对上，第一次使用编辑器就算成功了。

<div class="be-sample-evidence-strip" role="list">
  <span role="listitem"><b>01</b> 保存后的文件</span>
  <span role="listitem"><b>02</b> 搜索命中位置</span>
  <span role="listitem"><b>03</b> 终端复核结果</span>
</div>

<div class="be-sample-actions" markdown="1">
[先认识界面](#concept-workspace){ .md-button .md-button--primary }
[打开练习记录](examples/learning-workspace/notes/learning-log.md){ .md-button }
</div>

</section>

## 先把四个区域认清

<figure class="be-sample-figure" id="concept-workspace" data-learning-context="concept-workspace" data-context-type="concept">
  <div class="be-vscode-shot">
    <img src="../assets/vscode-workspace.jpeg" alt="VS Code 工作区实拍图：左侧显示完整文件树，中间打开学习记录，下方终端读取到保存后的同一文件。">
    <span class="be-vscode-shot__callout" data-callout="explorer">1 文件树</span>
    <span class="be-vscode-shot__callout" data-callout="editor">2 编辑区</span>
    <span class="be-vscode-shot__callout" data-callout="terminal">3 内置终端</span>
    <span class="be-vscode-shot__callout" data-callout="saved">4 已保存标签</span>
  </div>
  <figcaption>VS Code macOS 实际界面，Stable 版，核查于 2026-07-17。编号只标出本课会用到的四个区域。</figcaption>
</figure>

<div class="be-sample-mental-grid" markdown="1">

<div markdown="1">
### ① 文件树

这里显示当前打开的文件夹和里面的文件。它不是一张示意图，而是电脑上真实的目录结构。
</div>

<div markdown="1">
### ② 编辑区

文件内容在这里打开和修改。记住：屏幕上改了，不代表磁盘里的文件已经跟着变了。
</div>

<div markdown="1">
### ③ 内置终端

它就是前一课学过的终端，只是搬进了 VS Code。运行命令前，还是要先看自己在哪个目录。
</div>

<div markdown="1">
### ④ 标签与状态

标签上的圆点通常表示“改过了，还没保存”。刚开始用编辑器时，我建议多看一眼这个圆点。
</div>

</div>

!!! abstract "先记住这句话"
    **工作区就是一个文件夹。文件树用来找文件，编辑区用来改文件，终端用来确认电脑实际读到的内容。**

<section id="reproduce-install" class="be-sample-learning-unit" data-learning-context="reproduce-install" data-context-type="reproduce" markdown="1">

## 先把 VS Code 打开

这条路线先统一使用 VS Code，这样你看到的按钮和截图不会总变。以后换成 Cursor、Trae 或其他编辑器也没关系，工作区、保存、搜索和终端这些基本概念是相通的。

=== "Windows"

    1. 打开 [VS Code 官方 Windows 安装页](https://code.visualstudio.com/docs/setup/windows)。
    2. 下载面向当前用户的 **User Setup**，双击安装程序。
    3. 安装完成后按 Windows 键，输入 `Visual Studio Code`。
    4. 点击应用。看到左侧的一排图标和中间的欢迎页，就说明打开成功了。

=== "macOS"

    1. 打开 [VS Code 官方 macOS 安装页](https://code.visualstudio.com/docs/setup/mac)。
    2. 下载后打开压缩包或磁盘映像，把应用放入“应用程序”。
    3. 按 `Command + Space`，输入 `Visual Studio Code`。
    4. 打开应用。看到左侧的一排图标和中间的欢迎页，就说明打开成功了。

=== "Linux 简要补充"

    按 [VS Code 官方 Linux 安装说明](https://code.visualstudio.com/docs/setup/linux)选择发行版对应的软件包。完成后从应用列表搜索 Visual Studio Code。

!!! warning "先不要安装扩展"
    现在只需要 VS Code 本体。扩展装多了，按钮和提示反而容易变乱；等我们先把打开、保存和运行走通，再按需要安装。

</section>

<section id="reproduce-open-folder" class="be-sample-learning-unit" data-learning-context="reproduce-open-folder" data-context-type="reproduce" markdown="1">

## 打开整个 `learning-workspace`

先看一下练习目录的样子。样板里已经准备好了[学习记录](examples/learning-workspace/notes/learning-log.md)：

```text
learning-workspace/
├── notes/
│   └── learning-log.md
├── practice/
└── assets/
```

在 VS Code 选择 **File → Open Folder...**，选中 `learning-workspace`，不要选其中的 `notes`，也不要只双击 `learning-log.md`。

打开后看左侧文件树，下面三项都对就行：

- 左侧根目录名是 `learning-workspace`。
- 能同时看到 `notes`、`practice` 和 `assets`。
- 展开 `notes` 后能打开 `learning-log.md`。

!!! tip "出现“是否信任此文件夹”"
    自己创建的目录可以信任。别人发来的陌生项目先别急着点，至少要确认来源，再决定是否运行里面的命令。

</section>

<section id="example-save" class="be-sample-learning-unit" data-learning-context="example-save" data-context-type="example" markdown="1">

## 改一行，保存，再重新打开

打开 `notes/learning-log.md`，在“本次结果”下面追加：

```markdown
- 已完成：用 VS Code 打开工作区并保存记录。
```

先不要保存，观察标签页是否出现圆点。然后按：

- Windows：`Ctrl + S`
- macOS：`Command + S`

圆点消失后，把文件关掉，再从左侧文件树打开一次。刚才那行还在，说明内容确实写进了文件。

<div class="be-sample-check" role="status">
  <strong>你应该看到</strong>
  <span>未保存标记消失；重新打开后内容仍在。</span>
</div>

</section>

<section id="modify-search-terminal" class="be-sample-learning-unit" data-learning-context="modify-search-terminal" data-context-type="modify" markdown="1">

## 换成你的内容，再从两个地方找到它

1. 把上面的句子改成你自己的结果，并加入一个独特关键词，例如 `FIRST-SAVE`。
2. 打开左侧搜索，搜索这个关键词，确认结果来自 `notes/learning-log.md`。
3. 打开 **Terminal → New Terminal**。
4. 先确认当前位置，再读取文件。

=== "macOS / Linux"

    ```bash
    pwd
    ls
    cat notes/learning-log.md
    ```

=== "Windows PowerShell"

    ```powershell
    Get-Location
    Get-ChildItem
    Get-Content notes/learning-log.md
    ```

最后对一下三个地方：编辑区里有这个关键词，搜索能命中它，终端输出里也能看到它。三个地方一致，说明你操作的是同一份文件。

</section>

<section id="troubleshoot-editor" class="be-sample-learning-unit" data-learning-context="troubleshoot-editor" data-context-type="troubleshoot" markdown="1">

## 故意走错三次

| 看到的现象 | 常见原因 | 先看哪里 | 修好后是什么样 |
| --- | --- | --- | --- |
| 左侧只有一个文件 | 只打开了文件，没有打开工作区 | 窗口标题和根目录 | 文件树同时出现三个子目录 |
| 找不到 `notes` | 打开了错误层级 | 文件树最上方根目录名 | 根目录变为 `learning-workspace` |
| 终端读不到最新内容 | 文件还没保存，或终端位置不对 | 标签圆点、`pwd` / `Get-Location` | 圆点消失且终端输出包含新关键词 |

挑一个试试看，不要删除原文件。记下当时看到了什么、检查了哪里、最后怎样确认已经恢复。以后再遇到类似问题，你就有自己的排错记录了。

</section>

<section id="project-workspace" class="be-sample-project-panel" data-learning-context="project-workspace" data-context-type="project" markdown="1">

## 这个文件夹后面还会继续用

后面的 Python 文件、运行结果和排错记录都会继续放在 `learning-workspace` 里。这节课做的事情看起来很基础，却很重要：**你开始知道代码到底存在哪里，也能从编辑器和终端两边把它找出来。**

| 原来会什么 | 这节课加了什么 | 留下什么 | 接下来做什么 |
| --- | --- | --- | --- |
| 已会在文件系统和终端中定位目录 | 用 VS Code 打开、修改、保存、搜索、验证 | `learning-log.md` 与终端输出 | 在工作区创建并运行第一个 Python 文件 |

</section>

??? info "新手补给：找不到菜单怎么办"
    先确认应用窗口处于最前方。macOS 菜单位于屏幕顶部，Windows 菜单位于应用窗口顶部。按 `Command/Ctrl + Shift + P` 可以打开命令面板，但第一遍仍建议沿菜单完成，以建立位置感。

??? note "深入理解：编辑器没有替你管理文件"
    VS Code 显示的文件树来自磁盘。重命名、移动和删除会改变真实文件；版本控制、备份和恢复要由后续 Git 课程承担。

??? success "面试时怎么讲这项能力"
    只说“用过 VS Code”没什么信息。更好的讲法是展示一个结构清楚的工作区，再说清自己怎样找文件、保存、搜索、运行命令，以及路径对不上时先检查什么。

## 完成检查

- [ ] 能解释工作区、文件树、编辑区和终端的关系。
- [ ] 能打开完整目录，而不是只打开单个文件。
- [ ] 能识别未保存状态并验证保存结果。
- [ ] 搜索和终端都能找到自己添加的独特关键词。
- [ ] 故意走错一次，并记下自己怎样恢复。

下一页：[Python：变量、基本类型与输入输出](python-variables.md)。
