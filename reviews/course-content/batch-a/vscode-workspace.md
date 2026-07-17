# VS Code：从打开文件夹到验证保存结果

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-vscode-workspace" aria-hidden="true"></div>

<section id="overview-result" class="be-sample-hero" data-learning-context="overview-result" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">工具操作样板 · 工程基础</span>

## 这一课结束时，你会留下三份看得见的证据

不是“我好像打开过 VS Code”，而是：`learning-log.md` 已经保存、工作区搜索能找到修改、内置终端读到同一份内容。

<div class="be-sample-evidence-strip" role="list">
  <span role="listitem"><b>01</b> 保存后的文件</span>
  <span role="listitem"><b>02</b> 搜索命中位置</span>
  <span role="listitem"><b>03</b> 终端复核结果</span>
</div>

<div class="be-sample-actions" markdown="1">
[先认识界面](#concept-workspace){ .md-button .md-button--primary }
[下载练习目录](examples/learning-workspace/notes/learning-log.md){ .md-button }
</div>

</section>

## 先看完成后的工作区

<figure class="be-sample-figure" id="concept-workspace" data-learning-context="concept-workspace" data-context-type="concept">
  <img src="assets/vscode-workspace-annotated.webp" alt="VS Code 工作区实拍图：左侧文件树标为一，中间编辑区标为二，下方内置终端标为三，标签页未保存状态标为四。">
  <figcaption>VS Code macOS 实际界面，Stable 版，核查于 2026-07-16。编号只标出本课会用到的四个区域。</figcaption>
</figure>

<div class="be-sample-mental-grid" markdown="1">

<div markdown="1">
### ① 文件树

告诉你“现在打开的是哪个文件夹，文件位于哪里”。它对应磁盘上的真实目录结构。
</div>

<div markdown="1">
### ② 编辑区

显示并修改文件内容。屏幕上的变化只有保存后才会写回磁盘。
</div>

<div markdown="1">
### ③ 内置终端

它仍然是终端，只是放在编辑器窗口里。先确认当前位置，再执行命令。
</div>

<div markdown="1">
### ④ 标签与状态

圆点通常表示文件已经修改但尚未保存。它是本课最重要的反馈之一。
</div>

</div>

!!! abstract "一句话心智模型"
    **工作区是一个文件夹；文件树帮你定位，编辑区帮你修改，终端帮你从文件系统角度验证。**

<section id="reproduce-install" class="be-sample-learning-unit" data-learning-context="reproduce-install" data-context-type="reproduce" markdown="1">

## 第一次找到并打开 VS Code

本路线统一推荐 VS Code，是为了让按钮位置、截图和排错步骤保持一致。以后换 Cursor、Trae 或其他编辑器时，工作区、文件树、保存、搜索和终端这些概念仍然有效。

=== "Windows"

    1. 打开 [VS Code 官方 Windows 安装页](https://code.visualstudio.com/docs/setup/windows)。
    2. 下载面向当前用户的 **User Setup**，双击安装程序。
    3. 安装完成后按 Windows 键，输入 `Visual Studio Code`。
    4. 点击应用；看到左侧活动栏和中间欢迎页就算首次打开成功。

=== "macOS"

    1. 打开 [VS Code 官方 macOS 安装页](https://code.visualstudio.com/docs/setup/mac)。
    2. 下载后打开压缩包或磁盘映像，把应用放入“应用程序”。
    3. 按 `Command + Space`，输入 `Visual Studio Code`。
    4. 打开应用；看到左侧活动栏和中间欢迎页就算首次打开成功。

=== "Linux 简要补充"

    按 [VS Code 官方 Linux 安装说明](https://code.visualstudio.com/docs/setup/linux)选择发行版对应的软件包。完成后从应用列表搜索 Visual Studio Code。

!!! warning "先不要安装扩展"
    当前只需要 VS Code 本体。扩展会改变按钮、提示和运行行为，新手阶段先建立最小闭环。

</section>

<section id="reproduce-open-folder" class="be-sample-learning-unit" data-learning-context="reproduce-open-folder" data-context-type="reproduce" markdown="1">

## 复现：打开整个学习工作区

先准备下面的目录；样板已经提供了一份可直接使用的[练习工作区](examples/learning-workspace/notes/learning-log.md)：

```text
learning-workspace/
├── notes/
│   └── learning-log.md
├── practice/
└── assets/
```

在 VS Code 选择 **File → Open Folder...**，选中 `learning-workspace`，不要选其中的 `notes`，也不要只双击 `learning-log.md`。

看到下面三项就说明打开正确：

- 左侧根目录名是 `learning-workspace`。
- 能同时看到 `notes`、`practice` 和 `assets`。
- 展开 `notes` 后能打开 `learning-log.md`。

!!! tip "出现“是否信任此文件夹”"
    只有目录是你自己创建或来源可靠时才选择信任。来源不明的目录不要直接运行命令。

</section>

<section id="example-save" class="be-sample-learning-unit" data-learning-context="example-save" data-context-type="example" markdown="1">

## 小例子：屏幕上改了，不等于磁盘已经变了

打开 `notes/learning-log.md`，在“本次结果”下面追加：

```markdown
- 已完成：用 VS Code 打开工作区并保存记录。
```

先不要保存，观察标签页是否出现圆点。然后按：

- Windows：`Ctrl + S`
- macOS：`Command + S`

圆点消失后关闭文件，再从文件树重新打开。新增内容仍然存在，才说明保存成功。

<div class="be-sample-check" role="status">
  <strong>可观察结果</strong>
  <span>未保存标记消失；重新打开后内容仍在。</span>
</div>

</section>

<section id="modify-search-terminal" class="be-sample-learning-unit" data-learning-context="modify-search-terminal" data-context-type="modify" markdown="1">

## 轮到你修改：让搜索和终端都找到它

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

你的证据应该形成同一条链：编辑区看到关键词 → 工作区搜索命中 → 终端读取到相同内容。

</section>

<section id="troubleshoot-editor" class="be-sample-learning-unit" data-learning-context="troubleshoot-editor" data-context-type="troubleshoot" markdown="1">

## 三个安全失败实验

| 现象 | 最可能原因 | 先检查什么 | 恢复证据 |
| --- | --- | --- | --- |
| 左侧只有一个文件 | 只打开了文件，没有打开工作区 | 窗口标题和根目录 | 文件树同时出现三个子目录 |
| 找不到 `notes` | 打开了错误层级 | 文件树最上方根目录名 | 根目录变为 `learning-workspace` |
| 终端读不到最新内容 | 文件还没保存，或终端位置不对 | 标签圆点、`pwd` / `Get-Location` | 圆点消失且终端输出包含新关键词 |

请选择其中一个失败，在不破坏文件的前提下复现并恢复。记录“看到什么—检查什么—怎么确认恢复”，比只写“修好了”更有价值。

</section>

<section id="project-workspace" class="be-sample-project-panel" data-learning-context="project-workspace" data-context-type="project" markdown="1">

## 这不是一次性的编辑器练习

`learning-workspace` 会继续承载 Python 文件、运行记录、失败截图说明和项目证据。本课给后续课程增加的是一项基础能力：**你知道代码实际保存在哪里，也知道怎样从编辑器和终端两侧确认它。**

| 上一状态 | 本课增量 | 保存证据 | 下一版本 |
| --- | --- | --- | --- |
| 已会在文件系统和终端中定位目录 | 用 VS Code 打开、修改、保存、搜索、验证 | `learning-log.md` 与终端输出 | 在工作区创建并运行第一个 Python 文件 |

</section>

??? info "新手补给：找不到菜单怎么办"
    先确认应用窗口处于最前方。macOS 菜单位于屏幕顶部，Windows 菜单位于应用窗口顶部。按 `Command/Ctrl + Shift + P` 可以打开命令面板，但第一遍仍建议沿菜单完成，以建立位置感。

??? note "深入理解：编辑器没有替你管理文件"
    VS Code 显示的文件树来自磁盘。重命名、移动和删除会改变真实文件；版本控制、备份和恢复要由后续 Git 课程承担。

??? success "求职训练：怎样证明你具备基本工具能力"
    不要只回答“用过 VS Code”。可以展示一个结构清楚的工作区，说明如何定位文件、保存、搜索、用终端复现命令，以及遇到路径不一致时怎样判断。

## 完成检查

- [ ] 能解释工作区、文件树、编辑区和终端的关系。
- [ ] 能打开完整目录，而不是只打开单个文件。
- [ ] 能识别未保存状态并验证保存结果。
- [ ] 搜索和终端都能找到自己添加的独特关键词。
- [ ] 完成一次失败复现，并留下恢复证据。

下一页：[Python：变量、基本类型与输入输出](python-variables.md)。

