<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-02" aria-hidden="true"></div>

<section id="overview-workspace-tree" class="be-page-hero be-lesson-hero" data-learning-context="overview-workspace-tree" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">工程基础入门 · 第二课</span>

# 文件系统

## 把上一课的文件放到找得到的位置

上一课留下的 `learning-log.md` 不能一直孤零零地躺在桌面或下载目录里。今天把它整理成下面这棵目录树：

<div class="be-fs-tree" role="img" aria-label="学习工作区目录树：根目录 learning-workspace 下有 notes、practice 和 assets 三个目录，learning-log.md 位于 notes 中。">
  <div class="be-fs-tree__root"><span>项目根目录</span><strong>📁 learning-workspace</strong></div>
  <div class="be-fs-tree__branches" aria-hidden="true">
    <div><strong>📂 notes</strong><span>└─ 📄 learning-log.md</span></div>
    <div><strong>📁 practice</strong><span>后面放代码</span></div>
    <div><strong>📁 assets</strong><span>后面放图片</span></div>
  </div>
</div>

完成后，你应该能从项目根目录写出这条路径：

```text
notes/learning-log.md
```

<div class="be-page-actions" markdown="1">
[先看懂这棵树](#concept-file-directory){ .md-button .md-button--primary }
[返回上一课](01-learning-method.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>工程基础入门 · 2 / 10</strong></div>
  <div><span>带上什么</span><strong>learning-log.md</strong></div>
  <div><span>完成后留下</span><strong>一棵可解释的目录树</strong></div>
</div>

<section id="concept-file-directory" data-learning-context="concept-file-directory" data-context-type="concept" markdown="1">

## 文件装内容，目录管位置

先把三个容易混在一起的词分开：

| 名称 | 例子 | 它负责什么 |
| --- | --- | --- |
| 文件 | `learning-log.md` | 保存文字、代码、图片或数据 |
| 目录（文件夹） | `notes/` | 收纳文件，也可以继续收纳子目录 |
| 项目根目录 | `learning-workspace/` | 这一组学习文件共同归属的最外层目录 |

在目录树里，缩进表示“装在里面”：

```text
learning-workspace/       ← 最外层，项目根目录
└── notes/                ← learning-workspace 里的目录
    └── learning-log.md   ← notes 里的文件
```

`notes` 不一定永远是目录，`learning-log.md` 也不是因为有点号就自动成为文件。真正的区别由文件系统记录；目录树里的图标、缩进和实际打开行为比名字更可靠。

</section>

<section id="example-name-extension" data-learning-context="example-name-extension" data-context-type="example" markdown="1">

## `.md` 是扩展名，不是文件内容

文件名常写成“名字＋扩展名”：

```text
learning-log .md
└── 名字     └── 扩展名
```

扩展名给人和软件一个类型提示：

| 扩展名 | 常见内容 |
| --- | --- |
| `.md` | Markdown 文档 |
| `.txt` | 普通文本 |
| `.py` | Python 源代码 |
| `.json` | JSON 数据 |
| `.png` | PNG 图片 |

它只是提示，不会自动转换内容。把 `photo.png` 改名成 `photo.txt`，图片数据并不会因此变成文字。

!!! tip "先让系统显示扩展名"
    Windows 11 在文件资源管理器选择“查看 → 显示 → 文件扩展名”。macOS 在 Finder 选择“Finder → 设置 → 高级 → 显示所有文件扩展名”。这样更容易发现 `learning-log.md.txt` 这类问题。

</section>

<section id="concept-path-start" data-learning-context="concept-path-start" data-context-type="concept" markdown="1">

## 路径一定有起点

路径是从某个起点走到目标的一串名字。相对路径之所以“相对”，就是因为它省略了固定起点。

<div class="be-path-equation" role="img" aria-label="从项目根目录 learning-workspace 出发，沿相对路径 notes/learning-log.md，到达学习记录文件。">
  <div><span>当前所在位置</span><strong>learning-workspace/</strong></div>
  <b aria-hidden="true">＋</b>
  <div><span>相对路径</span><strong>notes/learning-log.md</strong></div>
  <b aria-hidden="true">＝</b>
  <div><span>找到的目标</span><strong>📄 学习记录</strong></div>
</div>

如果当前位置改成 `notes/`，同一个文件的相对路径会缩短成：

```text
learning-log.md
```

绝对路径则从系统的固定起点写起，例如：

=== "Windows"

    ```text
    C:\Users\你的用户名\Documents\learning-workspace\notes\learning-log.md
    ```

=== "macOS / Linux"

    ```text
    /Users/你的用户名/Documents/learning-workspace/notes/learning-log.md
    ```

公开提问、文档和截图里，我更建议使用从项目根目录出发的相对路径。它容易复用，也不会把你的用户名和私人目录带出去。

</section>

<section id="reproduce-build-workspace" data-learning-context="reproduce-build-workspace" data-context-type="reproduce" markdown="1">

## 亲手建出这棵目录树

这一课不要求会终端，使用系统文件管理器就可以。

=== "Windows 11"

    1. 按 `Windows + E` 打开文件资源管理器。
    2. 进入“文档”或你准备长期保存学习文件的位置。
    3. 选择“新建 → 文件夹”，命名为 `learning-workspace`。
    4. 打开它，依次新建 `notes`、`practice`、`assets` 三个文件夹。
    5. 把上一课的 `learning-log.md` 拖进 `notes`。

=== "macOS"

    1. 点击 Dock 中的 Finder（笑脸图标）。
    2. 进入“文稿”或你准备长期保存学习文件的位置。
    3. 选择“文件 → 新建文件夹”，也可以按 `Shift + Command + N`，命名为 `learning-workspace`。
    4. 打开它，依次新建 `notes`、`practice`、`assets` 三个文件夹。
    5. 把上一课的 `learning-log.md` 拖进 `notes`。

完成后逐层点开，确认下面四项都是真的：

- 最外层名字是 `learning-workspace`。
- 三个子目录处在同一层。
- `learning-log.md` 只在 `notes` 里面。
- 双击这个文件仍能看到上一课写的内容。

</section>

<section id="modify-read-paths" data-learning-context="modify-read-paths" data-context-type="modify" markdown="1">

## 换一个文件，再读一次路径

在 `practice` 目录中新建一个普通文本文件，名字由你决定，例如：

```text
path-check.txt
```

然后完成三次判断：

1. 从 `learning-workspace/` 出发，它的相对路径是什么？
2. 从 `practice/` 出发，它的相对路径又是什么？
3. 如果写成 `notes/path-check.txt`，系统应该去哪里找？那里真的有这个文件吗？

参考答案先别急着展开：

??? question "对照路径"
    从项目根目录出发是 `practice/path-check.txt`；从 `practice/` 出发是 `path-check.txt`。`notes/path-check.txt` 会指向 `notes` 里的同名文件，但我们并没有把它放在那里，所以目标不存在。

把三次判断补进 `notes/learning-log.md`。这次不要只写答案，也写清每条路径的起点。

</section>

<section id="troubleshoot-path-missing" data-learning-context="troubleshoot-path-missing" data-context-type="troubleshoot" markdown="1">

## 路径找不到，按层级往下查

假设你想打开：

```text
notes/learning-log.md
```

却发现文件不存在。先不要到处搜索，按下面顺序检查：

1. **起点对吗？** 当前打开的是 `learning-workspace/`，还是它的父目录或 `notes/`？
2. **每一级都存在吗？** 先找 `notes`，再进入它找文件。
3. **名字完全一致吗？** 检查大小写、连字符和空格。
4. **扩展名完整吗？** 留意 `learning-log.md.txt` 或隐藏扩展名。
5. **移动的是真文件吗？** 重新打开，确认内容仍在。

| 现象 | 常见原因 | 回到正确状态 |
| --- | --- | --- |
| 看见三个目录，但看不到 `learning-log.md` | 文件还留在原位置 | 回原位置找到文件，再移动到 `notes` |
| 文件显示成 `learning-log.md.txt` | 系统曾隐藏扩展名 | 显示扩展名后谨慎改回正确文件名 |
| `notes/learning-log.md` 找不到 | 当前起点不是项目根目录 | 先确认当前打开的最外层目录 |
| 双击后内容为空 | 移动了另一个同名文件 | 用上一课的内容或备份恢复，再删除重复文件 |

排路径问题时，一次只核对一级。随意拖动多个文件，通常只会让位置更难判断。

</section>

<section id="project-workspace-v02" data-learning-context="project-workspace-v02" data-context-type="project" markdown="1">

## 工程学习工作台 v0.2

上一课只有一份学习记录；现在它有了稳定的家：

| 原来有什么 | 这节课增加什么 | 保存什么 | 下一课怎样继续 |
| --- | --- | --- | --- |
| `learning-log.md` | 项目根目录与三个用途明确的子目录 | 完整目录树、两条路径判断 | 在终端里进入目录并读取文件 |

请保留整个 `learning-workspace`，不要只交一张截图。后续代码、运行结果、图片和 Git 记录都会进入这同一个工作区。

</section>

## 完成检查

- [ ] 能用自己的话区分文件、目录和项目根目录。
- [ ] 已显示文件扩展名，并确认文件不是 `learning-log.md.txt`。
- [ ] `learning-workspace` 下有 `notes`、`practice` 和 `assets`。
- [ ] `notes/learning-log.md` 能重新打开，内容没有丢失。
- [ ] 能说明同一个相对路径为什么依赖当前位置。
- [ ] 已创建自选文件，并从两个起点写出它的路径。

## 来源与版本

- 适用环境：Windows 11 文件资源管理器；当前受支持 macOS 的 Finder。Linux 可使用桌面环境自带文件管理器完成同等操作。
- Windows 界面依据：[Microsoft Support：File Explorer in Windows](https://support.microsoft.com/en-US/Windows/Experience/FileExplorer/file-explorer-in-windows)。
- macOS 界面依据：[Apple Support：Organize files in folders on Mac](https://support.apple.com/guide/mac-help/mh26885/mac)；[Show or hide filename extensions on Mac](https://support.apple.com/guide/mac-help/mchlp2304/mac)。
- 验证方式：逐层打开目录、显示扩展名，并重新打开两个练习文件核对内容。
- 核查日期：2026-07-17。

## 下一步

进入[终端与 Shell](03-terminal-shell.md)。下一节不再只靠鼠标点目录，而是用命令确认当前位置、列出文件，并读取刚才保存的学习记录。

<div class="be-next-panel" markdown="1">

<span class="be-panel-label">完成本课后</span>

**保留整个 `learning-workspace`，下一课会从终端重新找到它。**

[进入下一课：终端与 Shell](03-terminal-shell.md){ .md-button .md-button--primary }

</div>
