# 本地 Git 与 .gitignore

<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-06" aria-hidden="true"></div>

本课先确认 Git 已安装，再在一个临时学习目录完成第一次本地闭环：初始化、忽略不应提交的文件、查看状态、暂存、提交和查看历史；不直接改动当前公开仓库。

## 开始前：安装并验证 Git

先在终端运行：

```bash
git --version
```

出现 `git version ...` 表示终端已经能找到 Git。版本号会随时间更新，不需要和截图完全一致。

=== "Windows"

    1. 打开 [Git 官方 Windows 安装页](https://git-scm.com/install/windows)，下载维护中的安装程序。
    2. 双击安装程序。第一次学习可以保留默认选项；不理解的 Shell、换行符和凭据选项不要随意改成教程外的配置。
    3. 安装结束后关闭并重新打开 PowerShell，再运行 `git --version`。

=== "macOS"

    1. 先运行 `git --version`；部分 macOS 会提示安装 Xcode Command Line Tools。
    2. 如果没有 Git，可按 [Git 官方 macOS 安装页](https://git-scm.com/install/mac.html)使用 `xcode-select --install`；已经使用 Homebrew 的学习者也可选择 `brew install git`。
    3. 安装结束后重新打开终端，再运行 `git --version`。

=== "Linux 简要补充"

    使用发行版的软件包管理器安装 Git，然后运行 `git --version`。命令因发行版不同而不同，以 [Git 官方安装入口](https://git-scm.com/install/)为准。

如果安装失败，记录系统版本、下载来源、安装步骤和完整错误；不要为了继续课程复制来源不明的一键安装脚本。

## 五步任务路线

<div class="be-task-route" role="list" aria-label="本课五步任务">
  <span role="listitem">1 建立临时仓库</span><span role="listitem">2 配置忽略并看状态</span><span role="listitem">3 暂存变化</span><span role="listitem">4 配置身份并提交</span><span role="listitem">5 检查历史</span>
</div>

<section id="step-1" class="be-task-step" data-step-id="step-1" markdown="1">

### 第一步：在临时目录初始化仓库

**任务：** 新建一个只用于练习的目录，进入后执行 `git init`。**成功证据：** Git 提示已初始化仓库，目录里出现 `.git` 管理信息。

??? tip "提示一"
    不要用当前公开课程仓库练习随意提交。
??? tip "提示二"
    先用 `pwd` 或 `Get-Location` 确认自己进入的是临时目录。

</section>

<section id="step-2" class="be-task-step" data-step-id="step-2" markdown="1">

### 第二步：创建 .gitignore、记录并查看状态

**任务：** 创建 `README.md`、临时文件 `debug.log` 和 `.gitignore`，在 `.gitignore` 写入 `*.log` 后执行 `git status`。**成功证据：** Git 显示 README 和 `.gitignore`，但不把 `debug.log` 列为待提交文件。

??? tip "提示一"
    `.gitignore` 只描述哪些未跟踪文件不应进入版本库；它自己通常应该提交。
??? tip "提示二"
    已经被 Git 跟踪的文件不会因为后来加入 `.gitignore` 就自动停止跟踪。本练习先创建忽略规则，再暂存文件。

</section>

<section id="step-3" class="be-task-step" data-step-id="step-3" markdown="1">

### 第三步：把变化放入暂存区

**任务：** 执行 `git add README.md .gitignore`，再次执行 `git status`。**成功证据：** README 和 `.gitignore` 显示为待提交，`debug.log` 仍被忽略。

??? tip "提示一"
    `git add` 是选择下一次提交包含哪些变化，不是永久保存。
??? tip "提示二"
    先精确写文件名，理解后再使用更宽泛的路径。

</section>

<section id="step-4" class="be-task-step" data-step-id="step-4" markdown="1">

### 第四步：创建一次有意义的提交

**任务：** 先检查 `git config --global user.name` 和 `git config --global user.email`；没有结果时按下面示例换成自己的信息，再执行 `git commit -m "add learning note"`。**成功证据：** 命令成功并返回提交标识。

```bash
git config --global user.name "你的名字或 GitHub 用户名"
git config --global user.email "你用于提交的邮箱"
```

用户名和邮箱会写进提交作者信息，不会自动创建 GitHub 账号，也不会把本地仓库连接到 GitHub。公开仓库可使用 GitHub 提供的 noreply 邮箱保护真实邮箱。

??? tip "提示一"
    提交消息描述这次变化做了什么，而不是写“修改”。
??? tip "提示二"
    若提示没有暂存内容，回到第三步重新查看状态。

</section>

<section id="step-5" class="be-task-step" data-step-id="step-5" markdown="1">

### 第五步：查看历史并完成迁移

**任务：** 执行 `git log --oneline`，然后在 README 追加一行并说明下一次应如何重复流程。**成功证据：** 能区分工作区、暂存区、提交历史。

??? tip "提示一"
    历史中每一行对应一次提交，不等于当前未提交的修改。
??? tip "提示二"
    第二次变化先 `git status`，再决定是否暂存和提交。

</section>

## 前置知识

- 已完成 [学习方法](01-learning-method.md)。
- 已完成 [文件系统](02-filesystem.md)。
- 已完成 [终端与 Shell](03-terminal-shell.md)。
- 已完成 [编辑器](04-editor.md)。
- 已完成 [Markdown](05-markdown.md)。
- 能打开终端、进入目录、修改并保存一个 Markdown 文件。

## 学习目标

学完本节后，你应该能验证 Git 安装、理解仓库、工作区、忽略规则、暂存区、提交、状态和历史，并完成一次本地 Git 提交流程。

本节只讲本地 Git 最小闭环。下一课专门处理 GitHub、远程地址、认证、push 和 clone；本节不讲分支策略、Pull Request、rebase、冲突处理或 GitHub Actions。

## 核心概念

### 仓库

Git 仓库是一个被 Git 管理历史的项目目录。

普通目录只是保存当前文件；Git 仓库还能记录文件每次重要变化。

初始化仓库的命令是：

```bash
git init
```

入门练习请使用一个临时学习目录，不要直接在当前公开仓库里随便提交。

### 工作区

工作区是你正在编辑的文件状态。

你修改了文件，但还没有告诉 Git 要保存这次变化时，这些变化就在工作区。

查看状态的命令是：

```bash
git status
```

### 暂存区

暂存区是准备进入下一次提交的变化清单。

把文件加入暂存区的命令是：

```bash
git add README.md
```

也可以添加当前目录下所有变化：

```bash
git add .
```

入门时建议先用具体文件名，减少误加无关文件。

### 提交

提交是一次带说明的历史记录。

提交命令是：

```bash
git commit -m "Add first learning note"
```

提交信息应该说明这次变化做了什么，而不是写“update”或“改了一下”。

### 历史

查看提交历史：

```bash
git log
```

如果输出太长，可以先按 `q` 退出。

### .gitignore

`.gitignore` 是仓库中的规则文件，用来声明缓存、日志、构建产物、密钥或本机配置等不应进入版本历史的路径。例如：

```gitignore
*.log
.venv/
.env
__pycache__/
```

忽略规则不是保密工具：文件一旦提交过，或内容已经被推送到远程，后来写进 `.gitignore` 不能抹掉历史。密钥和隐私文件从一开始就不要提交。

## 学习顺序

1. 新建一个临时学习目录。
2. 初始化 Git 仓库。
3. 创建或修改一个 Markdown 文件。
4. 查看状态。
5. 暂存文件。
6. 提交一次变化。
7. 查看提交历史。
8. 确认日志文件被忽略。

## 最小命令表

| 目标 | 命令 | 说明 |
| --- | --- | --- |
| 初始化仓库 | `git init` | 让当前目录变成 Git 仓库 |
| 查看状态 | `git status` | 查看哪些文件新增、修改或已暂存 |
| 暂存文件 | `git add README.md .gitignore` | 把指定文件放入下一次提交 |
| 提交变化 | `git commit -m "message"` | 保存一次历史记录 |
| 查看历史 | `git log` | 查看提交记录 |
| 验证忽略 | `git status --ignored` | 查看被忽略文件，避免误提交 |

## 示例：完成一次本地提交

创建一个临时学习目录，例如：

```text
git-practice/
```

进入目录后，按顺序执行：

```bash
git init
```

创建一个 `README.md`，写入：

```markdown
# Git Practice

这是我的 Git 入门练习。
```

再创建 `.gitignore` 并写入 `*.log`，同时创建不会提交的 `debug.log`。

查看状态：

```bash
git status
```

暂存文件：

```bash
git add README.md .gitignore
```

再次查看状态：

```bash
git status
```

提交：

```bash
git commit -m "Add Git practice README"
```

查看历史：

```bash
git log
```

如果 `git commit` 提示你配置用户名和邮箱，回到第四步完成本机身份配置后重试。

## 实践练习

### 练习 1：初始化临时仓库

新建一个临时学习目录，并在里面执行：

```bash
git init
```

需要产出：

```text
我的临时目录是：

`git init` 后我看到了什么输出：
```

### 练习 2：查看状态

创建 `README.md`、`.gitignore` 和 `debug.log`，在忽略规则写入 `*.log` 后执行：

```bash
git status
```

需要产出：

```text
Git 显示了哪些文件变化：

这些变化现在是否已经提交：
```

### 练习 3：暂存文件

执行：

```bash
git add README.md .gitignore
git status
```

需要产出：

```text
暂存前文件处于什么状态：

暂存后文件处于什么状态：
```

### 练习 4：提交变化

执行：

```bash
git commit -m "Add first learning note"
```

需要产出：

```text
我的提交信息是：

提交是否成功：

如果失败，错误信息是：
```

### 练习 5：查看历史和忽略结果

执行：

```bash
git log
git status --ignored
```

需要产出：

```text
我看到的最近一次提交信息是：

当前被忽略的文件是：

我的判断依据是：
```

## 常见错误与排查

| 错误 | 表现 | 怎么排查 |
| --- | --- | --- |
| 不在正确目录执行 Git | `git status` 显示不是仓库，或状态和预期不符 | 先运行 `pwd`，确认当前位置 |
| 忘记 `git add` | `git commit` 提示没有要提交的内容 | 先 `git status`，再 `git add 文件名` |
| 提交信息太模糊 | 历史里只看到 `update` | 用动词说明这次变化，比如 `Add learning note` |
| 把无关文件一起提交 | 提交里混入缓存、数据库或私人文件 | 用具体文件名 `git add README.md`，不要一开始就依赖 `git add .` |
| 不会退出 `git log` | 终端停在历史页面 | 按 `q` 退出 |
| 第一次提交失败 | Git 要求配置用户名和邮箱 | 按第四步配置自己的 `user.name` 和 `user.email` 后重试 |
| `.gitignore` 没生效 | 文件仍出现在已暂存或已跟踪列表 | 先确认规则和相对路径；已跟踪文件需单独从索引处理，不要直接删除真实文件 |

## 完成标准

完成本节需要同时满足：

- 能解释仓库、工作区、暂存区和提交的区别。
- 能在临时目录中运行 `git init`。
- 能用 `git status` 判断文件是否被修改或暂存。
- 能用 `git add` 暂存一个指定文件。
- 能尝试执行一次 `git commit`，并记录成功结果或失败原因。
- 能用 `git log` 查看提交历史。
- 能用 `.gitignore` 排除一个日志文件，并解释为什么密钥不能只依靠忽略规则保护。

## 下一步

进入 [GitHub 远程协作](06-github-remote.md)。下一节会把本地提交连接到 GitHub，实际执行 remote、push 和 clone。
