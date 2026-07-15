# Git

<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-06" aria-hidden="true"></div>

本课在一个临时学习目录完成第一次本地 Git 闭环：初始化、查看状态、暂存、提交、查看历史；不直接改动当前公开仓库。

## 五步任务路线

<div class="be-task-route" role="list" aria-label="本课五步任务">
  <span role="listitem">1 建立临时仓库</span><span role="listitem">2 查看状态</span><span role="listitem">3 暂存变化</span><span role="listitem">4 创建提交</span><span role="listitem">5 检查历史</span>
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

### 第二步：创建记录并查看状态

**任务：** 在临时仓库创建 `README.md`，写下一句练习说明，执行 `git status`。**成功证据：** 能看到未跟踪文件状态。

??? tip "提示一"
    工作区是你正在编辑的文件状态，`git status` 不会修改文件。
??? tip "提示二"
    看不到文件时，先确认文件已经保存且当前目录正确。

</section>

<section id="step-3" class="be-task-step" data-step-id="step-3" markdown="1">

### 第三步：把变化放入暂存区

**任务：** 执行 `git add README.md`，再次执行 `git status`。**成功证据：** 文件显示为待提交，而不是未跟踪。

??? tip "提示一"
    `git add` 是选择下一次提交包含哪些变化，不是永久保存。
??? tip "提示二"
    先精确写文件名，理解后再使用更宽泛的路径。

</section>

<section id="step-4" class="be-task-step" data-step-id="step-4" markdown="1">

### 第四步：创建一次有意义的提交

**任务：** 执行 `git commit -m "add learning note"`。**成功证据：** 命令成功并返回提交标识；若要求配置身份，按报错完成本机配置后重试。

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

学完本节后，你应该能理解仓库、工作区、暂存区、提交、状态、历史和远程仓库的最小概念，并完成一次本地 Git 提交流程。

本节只讲本地 Git 最小闭环和远程仓库认知。不讲分支策略、Pull Request、rebase、冲突处理或 GitHub Actions。

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

### 远程仓库

远程仓库是放在 GitHub 等平台上的仓库副本。

查看当前仓库配置的远程地址：

```bash
git remote -v
```

本节只要求知道远程仓库是什么，不要求执行 push 或配置 GitHub 权限。

## 学习顺序

1. 新建一个临时学习目录。
2. 初始化 Git 仓库。
3. 创建或修改一个 Markdown 文件。
4. 查看状态。
5. 暂存文件。
6. 提交一次变化。
7. 查看提交历史。
8. 查看远程仓库配置。

## 最小命令表

| 目标 | 命令 | 说明 |
| --- | --- | --- |
| 初始化仓库 | `git init` | 让当前目录变成 Git 仓库 |
| 查看状态 | `git status` | 查看哪些文件新增、修改或已暂存 |
| 暂存文件 | `git add README.md` | 把指定文件放入下一次提交 |
| 提交变化 | `git commit -m "message"` | 保存一次历史记录 |
| 查看历史 | `git log` | 查看提交记录 |
| 查看远程 | `git remote -v` | 查看远程仓库地址 |

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

查看状态：

```bash
git status
```

暂存文件：

```bash
git add README.md
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

如果 `git commit` 提示你配置用户名和邮箱，先记录提示内容。用户名和邮箱配置属于后续工程环境内容，这里只要求你知道提交失败在哪里。

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

创建一个 `README.md`，写入一行学习记录，然后执行：

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
git add README.md
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

### 练习 5：查看历史和远程

执行：

```bash
git log
git remote -v
```

需要产出：

```text
我看到的最近一次提交信息是：

当前是否配置了远程仓库：

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
| 第一次提交失败 | Git 要求配置用户名和邮箱 | 记录错误信息，后续在开发环境处理 |

## 完成标准

完成本节需要同时满足：

- 能解释仓库、工作区、暂存区和提交的区别。
- 能在临时目录中运行 `git init`。
- 能用 `git status` 判断文件是否被修改或暂存。
- 能用 `git add` 暂存一个指定文件。
- 能尝试执行一次 `git commit`，并记录成功结果或失败原因。
- 能用 `git log` 查看提交历史。
- 能用 `git remote -v` 判断当前是否配置远程仓库。

## 下一步

进入 [开发环境](07-development-environment.md)。下一节会学习解释器、编译器、环境变量和依赖的基本概念。
