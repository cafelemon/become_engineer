# 终端与 Shell

<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-03" aria-hidden="true"></div>

本课直接在上一课的学习工作区完成一个命令闭环：确认位置、查看目录、进入目录、读取记录，再把一次错误保留下来。

## 五步任务路线

<div class="be-task-route" role="list" aria-label="本课五步任务">
  <span role="listitem">1 打开终端</span><span role="listitem">2 确认位置</span><span role="listitem">3 查看内容</span><span role="listitem">4 进入并读取</span><span role="listitem">5 记录错误</span>
</div>

<section id="step-1" class="be-task-step" data-step-id="step-1" markdown="1">

### 第一步：打开终端并进入工作区

**任务：** 打开系统或编辑器内置终端，进入上一课创建的学习工作区。**成功证据：** 提示符回到可输入状态，没有报错。

??? tip "提示一"
    macOS/Linux 常用 `cd 路径`；PowerShell 也可用 `cd 路径`。
??? tip "提示二"
    路径带空格时用引号包住，或先从较短的父目录逐级进入。

</section>

<section id="step-2" class="be-task-step" data-step-id="step-2" markdown="1">

### 第二步：确认你现在在哪里

**任务：** 执行 `pwd`（PowerShell 可用 `Get-Location`）。**成功证据：** 输出与学习工作区位置一致。

??? tip "提示一"
    终端不会自动知道你想操作哪个目录，先确认当前位置。
??? tip "提示二"
    若输出不对，使用 `cd` 回到目标目录后再检查。

</section>

<section id="step-3" class="be-task-step" data-step-id="step-3" markdown="1">

### 第三步：列出工作区内容

**任务：** 执行 `ls`（PowerShell 可用 `dir`），找到 `notes`、`practice`、`assets`。**成功证据：** 输出与文件树一致。

??? tip "提示一"
    先只观察输出，不要急着修改或删除文件。
??? tip "提示二"
    看不到目录时，回到第二步检查当前位置。

</section>

<section id="step-4" class="be-task-step" data-step-id="step-4" markdown="1">

### 第四步：进入目录并读取记录

**任务：** 进入 `notes`，用 `cat learning-log.md`（PowerShell 可用 `Get-Content learning-log.md`）读取文件，然后用 `cd ..` 回到父目录。**成功证据：** 能解释 `.`、`..` 和当前目录的关系。

??? tip "提示一"
    `cd notes` 会从当前目录进入 notes；`cd ..` 返回上一级。
??? tip "提示二"
    文件名不一致时先 `ls`，不要猜扩展名。

</section>

<section id="step-5" class="be-task-step" data-step-id="step-5" markdown="1">

### 第五步：记录一次可复现错误

**任务：** 有意执行一个错误文件名，记录命令、报错和正确修复方式。**成功证据：** 能区分命令失败与终端损坏。

??? tip "提示一"
    不存在的文件是安全的失败实验，不会修改原文件。
??? tip "提示二"
    记录后使用真实文件名重新执行，确认恢复成功。

</section>

## 前置知识

- 已完成 [学习方法](01-learning-method.md)。
- 已完成 [文件系统](02-filesystem.md)。
- 能区分文件、目录、项目根目录、相对路径和绝对路径。

## 学习目标

学完本节后，你应该能打开终端，知道自己在哪个目录，进入指定目录，查看目录内容，读取一个文本文件，并理解命令执行成功或失败的大概信号。

本节只讲最小终端操作，不讲 Git、包管理、环境变量、Shell 脚本或 Docker。

## 核心概念

### 终端

终端是一个用文字和电脑交互的窗口。你在里面输入命令，电脑返回输出。

常见终端包括：

- macOS：Terminal、iTerm2、编辑器内置终端。
- Windows：PowerShell、Windows Terminal、编辑器内置终端。
- Linux：Terminal、Konsole、GNOME Terminal 等。

本课程不要求你一开始理解所有终端差异。先学会最基本的目录和文件操作即可。

### Shell

Shell 是读取命令并执行命令的程序。

可以先这样理解：

```text
终端 = 你输入文字的窗口
Shell = 解释这些文字命令的程序
```

不同系统的 Shell 命令不完全一样，所以本节会给出 macOS/Linux 与 Windows PowerShell 的对照。

### 当前目录

当前目录是终端现在所在的位置。

当你输入相对路径时，电脑会从当前目录开始找文件。学习终端时，最重要的习惯之一就是先确认当前目录。

### 命令、参数和输出

一条命令通常长这样：

```text
命令 参数
```

例如：

```text
cd docs
```

这里：

- `cd` 是命令。
- `docs` 是参数，表示要进入的目录。

命令执行后，终端可能会显示一段输出，也可能什么都不显示。没有输出不一定代表失败。

### 退出状态

命令执行完后，Shell 会记录一个退出状态。

通常：

- `0` 表示成功。
- 非 `0` 表示失败或异常。

入门时不需要记住所有状态码，只要知道“命令可能成功，也可能失败”，并能把失败时看到的错误信息记录下来。

## 学习顺序

1. 打开终端。
2. 查看当前目录。
3. 进入一个目录。
4. 查看目录内容。
5. 读取一个文本文件。
6. 观察成功输出和错误输出。

## 最小命令对照

| 目标 | macOS / Linux | Windows PowerShell | 说明 |
| --- | --- | --- | --- |
| 查看当前目录 | `pwd` | `pwd` | 显示终端现在所在位置 |
| 查看目录内容 | `ls` | `dir` 或 `ls` | 显示当前目录下有什么 |
| 进入目录 | `cd docs` | `cd docs` | 进入 `docs` 目录 |
| 回到上一级 | `cd ..` | `cd ..` | 回到当前目录的父目录 |
| 读取文本文件 | `cat README.md` | `type README.md` | 显示文件内容 |
| 清屏 | `clear` | `cls` | 清理屏幕显示，不删除文件 |

如果某个命令在你的系统上不可用，先记录错误信息，不要急着安装东西。

## 示例：从项目根目录查看 README

假设你的项目结构是：

```text
become_engineer/
├── README.md
└── docs/
    └── 00_overview.md
```

如果终端当前目录是项目根目录，可以这样做：

macOS / Linux：

```bash
pwd
ls
cat README.md
```

Windows PowerShell：

```powershell
pwd
dir
type README.md
```

你应该能看到：

- `pwd` 显示当前位置。
- `ls` 或 `dir` 显示 `README.md` 和 `docs/`。
- `cat` 或 `type` 显示 `README.md` 的文本内容。

## 示例：进入 docs 目录再回来

macOS / Linux：

```bash
cd docs
pwd
ls
cd ..
pwd
```

Windows PowerShell：

```powershell
cd docs
pwd
dir
cd ..
pwd
```

观察重点：

- 第一次 `pwd` 应该显示你已经进入 `docs`。
- `cd ..` 后，第二次 `pwd` 应该显示你回到了项目根目录。

## 实践练习

### 练习 1：确认当前位置

打开终端，输入查看当前目录的命令。

需要产出：

```text
我当前所在目录是：

我判断它是不是项目根目录的依据是：
```

### 练习 2：查看目录内容

在项目根目录下查看目录内容，并写下你看到了哪些文件或目录。

需要产出：

```text
我看到的文件：
-

我看到的目录：
-
```

### 练习 3：进入目录再回来

选择一个你能看到的目录，进入它，再回到上一级目录。

需要产出：

```text
我进入的目录是：

进入后 `pwd` 显示：

回到上一级后 `pwd` 显示：
```

### 练习 4：读取一个文本文件

读取一个 `.md` 或 `.txt` 文件，并记录你看到的第一行内容。

需要产出：

```text
我读取的文件是：

第一行内容是：
```

### 练习 5：记录一次错误

故意读取一个不存在的文件，例如：

macOS / Linux：

```bash
cat not-exist.md
```

Windows PowerShell：

```powershell
type not-exist.md
```

需要产出：

```text
我输入的命令是：

终端返回的错误信息是：

我判断失败原因是：
```

## 常见错误与排查

| 错误 | 表现 | 怎么排查 |
| --- | --- | --- |
| 不确认当前目录就运行命令 | 找不到文件或进入错误目录 | 先运行 `pwd` |
| 把文件当目录进入 | `cd README.md` 失败 | 回到文件系统，确认文件和目录区别 |
| 相对路径从错误位置出发 | 明明文件存在却找不到 | 先说明当前位置，再解释路径 |
| 混用不同系统命令 | Windows 中 `cat` 不可用，或 macOS 中 `dir` 行为不同 | 查本节命令对照表 |
| 看到错误就关掉终端 | 下次无法复盘 | 把命令和错误信息复制到学习记录 |

## 完成标准

完成本节需要同时满足：

- 能打开终端并查看当前目录。
- 能进入一个目录，再返回上一级目录。
- 能查看当前目录下的文件和目录。
- 能读取一个文本文件。
- 能记录一条失败命令和对应错误信息。

## 下一步

进入 [编辑器](04-editor.md)。下一节会学习如何用编辑器打开整个项目、搜索文件、修改文件，并使用编辑器内置终端。
