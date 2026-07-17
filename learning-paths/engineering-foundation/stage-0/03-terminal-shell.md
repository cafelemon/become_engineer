<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-03" aria-hidden="true"></div>

<section id="overview-terminal-result" class="be-page-hero be-lesson-hero" data-learning-context="overview-terminal-result" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">工程基础入门 · 第三课</span>

# 终端与 Shell

## 不点文件夹，也能找到上一课的记录

下面不是电影里的“黑客界面”，只是用文字查看刚才建好的学习工作区：

=== "macOS / Linux"

    ```console
    $ pwd
    /Users/小码/Documents/learning-workspace
    $ ls
    assets  notes  practice
    $ cat notes/learning-log.md
    # 学习记录：学习方法
    ```

=== "Windows PowerShell"

    ```powershell
    PS> Get-Location
    Path
    ----
    C:\Users\小码\Documents\learning-workspace
    PS> Get-ChildItem -Name
    assets
    notes
    practice
    PS> Get-Content notes\learning-log.md -TotalCount 1
    # 学习记录：学习方法
    ```

今天只学会完成这段只读检查：确认位置、看见三个目录、读出学习记录第一行。暂时不碰删除、移动和批量修改命令。

<div class="be-page-actions" markdown="1">
[先认识终端](#concept-terminal-shell){ .md-button .md-button--primary }
[返回文件系统](02-filesystem.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>工程基础入门 · 3 / 10</strong></div>
  <div><span>带上什么</span><strong>learning-workspace</strong></div>
  <div><span>完成后留下</span><strong>一段命令、输出与排错记录</strong></div>
</div>

<section id="concept-terminal-shell" data-learning-context="concept-terminal-shell" data-context-type="concept" markdown="1">

## 终端是窗口，Shell 负责理解命令

<div class="be-terminal-model" role="img" aria-label="你在终端窗口输入文字，Shell 读取和解释命令，操作系统与文件系统完成操作，再把结果返回终端。">
  <div><span>你看到并输入</span><strong>终端窗口</strong></div>
  <b aria-hidden="true">→</b>
  <div><span>解释命令</span><strong>Shell</strong><small>PowerShell / zsh / bash</small></div>
  <b aria-hidden="true">→</b>
  <div><span>真正执行</span><strong>操作系统与文件系统</strong></div>
  <b aria-hidden="true">→</b>
  <div><span>回到屏幕</span><strong>输出或错误</strong></div>
</div>

- **终端**是显示提示符、接收键盘输入、展示结果的窗口。
- **Shell**是运行在窗口里的程序，它读取命令并决定怎样执行。
- **提示符**例如 `%`、`$` 或 `PS>`，表示 Shell 已经准备好接收下一条命令。

Windows Terminal 可以同时承载 PowerShell、命令提示符和 WSL；macOS 自带 Terminal，默认登录 Shell 通常是 zsh。现在不需要修改默认 Shell，只要先认清自己正在用哪一种。

!!! warning "示例里的 `$` 和 `PS>` 不要复制"
    它们表示提示符，不是命令的一部分。正文让你输入 `pwd` 时，只输入三个字母再按回车。

</section>

<section id="reproduce-open-terminal" data-learning-context="reproduce-open-terminal" data-context-type="reproduce" markdown="1">

## 先把终端找到并打开

=== "Windows 11"

    1. 按 Windows 键，输入 `Terminal`。
    2. 如果能找到“终端”，打开后看标签名称，选择 **PowerShell**。
    3. 如果搜索不到 Windows Terminal，改搜 `PowerShell`，直接打开它；本课不要求先安装新软件。
    4. 看到 `PS C:\Users\你的用户名>` 一类提示符和闪烁光标，就可以输入命令。

=== "macOS"

    1. 按 `Command + Space` 打开聚焦搜索。
    2. 输入 `Terminal` 或“终端”，按 Return。
    3. 也可以在 Finder 打开“应用程序 → 实用工具 → 终端”。
    4. 看到以 `%` 或 `$` 结尾的提示符，就可以输入命令。

=== "Linux 简要补充"

    从应用列表搜索 Terminal；很多桌面环境也支持 `Ctrl + Alt + T`。发行版不同，应用名称和默认 Shell 可能不同。

先输入一条不会修改文件的命令：

=== "macOS / Linux"

    ```bash
    pwd
    ```

=== "Windows PowerShell"

    ```powershell
    Get-Location
    ```

按 Enter 或 Return 后，终端显示一条路径并再次出现提示符，说明命令已经执行完。这个路径就是终端当前所在的位置。

</section>

<section id="example-command-anatomy" data-learning-context="example-command-anatomy" data-context-type="example" markdown="1">

## 一条命令里有什么

看下面这条 PowerShell 命令：

```powershell
Get-Content notes\learning-log.md -TotalCount 1
```

| 部分 | 含义 |
| --- | --- |
| `Get-Content` | 命令名：读取文件内容 |
| `notes\learning-log.md` | 参数：要读取哪个文件 |
| `-TotalCount 1` | 选项：只读取第一行 |

macOS／Linux 的对应写法是：

```bash
head -n 1 notes/learning-log.md
```

空格用来分开命令、参数和选项，所以路径里本身有空格时，要用引号包住：

```powershell
Set-Location "$HOME\Documents\my learning workspace"
```

```bash
cd "$HOME/Documents/my learning workspace"
```

这里先别背所有命令。每次只问三件事：要做什么、目标是什么、终端返回了什么。

</section>

<section id="reproduce-enter-workspace" data-learning-context="reproduce-enter-workspace" data-context-type="reproduce" markdown="1">

## 进入学习工作区

刚打开终端时，它通常位于你的用户主目录，而不是自动回到上一课。先查看当前位置和里面有什么：

=== "macOS / Linux"

    ```bash
    pwd
    ls
    ```

=== "Windows PowerShell"

    ```powershell
    Get-Location
    Get-ChildItem -Name
    ```

如果 `learning-workspace` 放在“文档／文稿”里，可以按实际位置输入：

=== "macOS / Linux"

    ```bash
    cd "$HOME/Documents/learning-workspace"
    pwd
    ls
    ```

=== "Windows PowerShell"

    ```powershell
    Set-Location "$HOME\Documents\learning-workspace"
    Get-Location
    Get-ChildItem -Name
    ```

`$HOME` 表示当前用户的主目录。若你的“文档”被移动到 OneDrive 或其他位置，不要照抄示例路径：回到文件管理器确认真实位置，再替换整条路径。

进入成功后，列表里应该同时出现：

```text
assets
notes
practice
```

如果没看到，不要立刻新建一遍。先看位置输出，确认自己是否进错了同名目录。

</section>

<section id="modify-read-record" data-learning-context="modify-read-record" data-context-type="modify" markdown="1">

## 从两个位置读取同一份记录

先留在项目根目录，直接读取文件第一行：

=== "macOS / Linux"

    ```bash
    head -n 1 notes/learning-log.md
    ```

=== "Windows PowerShell"

    ```powershell
    Get-Content notes\learning-log.md -TotalCount 1
    ```

然后进入 `notes`，用更短的相对路径再读一次：

=== "macOS / Linux"

    ```bash
    cd notes
    pwd
    head -n 1 learning-log.md
    cd ..
    pwd
    ```

=== "Windows PowerShell"

    ```powershell
    Set-Location notes
    Get-Location
    Get-Content learning-log.md -TotalCount 1
    Set-Location ..
    Get-Location
    ```

两次读取应显示同一行。变化的只是当前位置和相对路径，文件并没有复制一份。

把下面内容补进 `notes/learning-log.md`：

```markdown
## 终端检查

- 项目根目录：
- 列出的三个目录：
- 读取到的第一行：
```

其中的路径和输出要换成你电脑上实际看到的内容。

</section>

<section id="troubleshoot-terminal-errors" data-learning-context="troubleshoot-terminal-errors" data-context-type="troubleshoot" markdown="1">

## 看到报错，先别关窗口

故意读取一个不存在的文件：

=== "macOS / Linux"

    ```bash
    cat notes/not-exist.md
    ```

=== "Windows PowerShell"

    ```powershell
    Get-Content notes\not-exist.md
    ```

终端会提示没有这个文件。提示符再次出现，说明 Shell 还在正常工作；失败的是这条命令，不是整个终端。

| 现象 | 常见原因 | 怎样回来 |
| --- | --- | --- |
| 提示“找不到命令” | 把 `$`、`PS>` 或中文标点一起复制了 | 只重新输入命令本身 |
| 提示路径不存在 | 当前位置、目录名或文件名不对 | 先查位置，再列出当前目录 |
| 输入后出现 `>` 等待更多内容 | 引号只写了一边，Shell 认为命令没结束 | 按 `Ctrl + C` 取消，再补成一对引号 |
| 列表里没有三个目录 | 进入了错误的 `learning-workspace` | 对照绝对路径，返回父目录重新进入 |
| 屏幕没有输出 | 目录可能为空，或命令成功但本来就不输出 | 看提示符是否返回，再检查命令目的 |

把这次失败也写进学习记录：输入了什么、看到了哪句错误、最后怎样恢复。错误原文比“终端坏了”更有用。

</section>

<section id="deepen-command-status" data-learning-context="deepen-command-status" data-context-type="deepen" markdown="1">

## 没有输出，不等于没有执行

有些命令成功后只把提示符还给你，不会额外说“成功”。Shell 还会保存上一条命令的状态：

- macOS／Linux 的退出状态通常以 `0` 表示成功，非 `0` 表示失败；可以用 `echo $?` 查看上一条命令的数值。
- PowerShell 的 `$?` 表示上一条操作是否成功，结果是 `True` 或 `False`；调用外部程序时还可能用到 `$LASTEXITCODE`。

这一课不用背状态码。先养成习惯：同时看**输出、错误和提示符是否返回**，不要只看屏幕有没有新文字。

</section>

<section id="project-workspace-v03" data-learning-context="project-workspace-v03" data-context-type="project" markdown="1">

## 工程学习工作台 v0.3

前两课把文件保存并整理好；现在你能从命令行重新找到它：

| 原来有什么 | 这节课增加什么 | 保存什么 | 下一课怎样继续 |
| --- | --- | --- | --- |
| 目录树与路径判断 | 终端定位、列出目录、读取文件和一次错误恢复 | 实际命令、关键输出、错误原文 | 用 VS Code 同时查看文件树、编辑区和内置终端 |

这一段命令记录以后会成为排错材料。项目出现“文件明明在却找不到”时，先给出当前目录和实际列表，比一句“运行不了”更容易定位。

</section>

## 完成检查

- [ ] 能指出终端窗口、Shell 和提示符分别是什么。
- [ ] 能在自己的系统中找到并打开终端或 PowerShell。
- [ ] 能查看当前位置，并进入真实的 `learning-workspace`。
- [ ] 能列出 `assets`、`notes` 和 `practice`。
- [ ] 能从两个位置读取同一份 `learning-log.md`。
- [ ] 能复现一次安全的“文件不存在”错误，并恢复到正确命令。
- [ ] 学习记录保存了实际路径、输出和错误原文。

## 来源与版本

- 适用环境：Windows 11 的 Windows Terminal 或 PowerShell；当前受支持 macOS 的 Terminal（默认登录 Shell 通常为 zsh）；常见 Linux 桌面终端。
- Windows Terminal：[Microsoft Learn：Install and get started setting up Windows Terminal](https://learn.microsoft.com/en-us/windows/terminal/install)。
- PowerShell 命令：[Get-ChildItem](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem)；[Get-Content](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-content)。
- macOS Terminal：[Apple Support：Open or quit Terminal on Mac](https://support.apple.com/guide/terminal/open-or-quit-terminal-apd5265185d-f365-44cb-8b09-71a064a42125/mac)。
- 验证方式：在两个真实当前位置运行只读命令，对照文件管理器中的目录树和文件第一行。
- 核查日期：2026-07-17。

## 下一步

进入[VS Code 编辑器](04-editor.md)。下一课会把同一个工作区完整打开，在文件树中修改记录，再用内置终端复核磁盘里的内容。

<div class="be-next-panel" markdown="1">

<span class="be-panel-label">完成本课后</span>

**保留 `learning-workspace` 和终端检查记录，下一课会在 VS Code 里继续使用。**

[进入下一课：VS Code 编辑器](04-editor.md){ .md-button .md-button--primary }

</div>
