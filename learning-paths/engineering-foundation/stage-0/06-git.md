<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-06" aria-hidden="true"></div>

<section id="overview-local-history" class="be-page-hero be-lesson-hero" data-learning-context="overview-local-history" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">工程基础入门 · 第六课</span>

# 本地 Git 与 .gitignore

## 文件还在原处，但现在能看见它怎样一步步变成今天的样子

<div class="be-git-result" role="group" aria-label="完成本课后的本地 Git 检查结果" markdown="1">

```console
$ git log -2 --format="%h %s"
<提交标识> document Git setup
<提交标识> record learning workspace

$ git status --short --ignored
!! debug.log
```

</div>

前两行是已经保存进本地历史的版本，最后一行是明确不让 Git 收录的调试日志。整个过程都在你的电脑上完成，还没有连接 GitHub。

<div class="be-page-actions" markdown="1">
[先看懂一次提交保存了什么](#concept-three-places){ .md-button .md-button--primary }
[返回 Markdown](05-markdown.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>工程基础入门 · 6 / 10</strong></div>
  <div><span>继续使用</span><strong>learning-workspace</strong></div>
  <div><span>完成后留下</span><strong>两次本地提交和一份 .gitignore</strong></div>
</div>

## 开始前

- 已经完成[终端与 Shell](03-terminal-shell.md)、[VS Code 编辑器](04-editor.md)和[Markdown](05-markdown.md)。
- `learning-workspace` 中至少有 `notes/learning-log.md` 和 `practice/README.md`。
- 本课使用 Git 2.28 或更新版本；示例已在 Git 2.50.1 验证。
- 本课只建立本地历史。GitHub、`remote`、认证、`push` 和 `clone` 留到下一课。

<section id="concept-three-places" data-learning-context="concept-three-places" data-context-type="concept" markdown="1">

## 一次提交保存的不是整个硬盘

Git 不会自动把目录里的一切都塞进历史。你先修改文件，再从这些变化中挑出这次要保存的部分，最后给它写一条说明。

<div class="be-git-flow" role="img" aria-label="Git 本地流程：工作区经 git add 进入暂存区，再经 git commit 写入本地历史；未跟踪且匹配 gitignore 的文件保持在历史之外。">
  <div><span>你正在编辑</span><strong>工作区</strong><small>notes/learning-log.md</small></div>
  <b aria-hidden="true">git add →</b>
  <div><span>这次准备保存</span><strong>暂存区</strong><small>被选中的文件内容</small></div>
  <b aria-hidden="true">git commit →</b>
  <div><span>已经保存</span><strong>本地历史</strong><small>提交标识 + 说明</small></div>
  <aside><span>.gitignore</span><strong>debug.log 留在工作区，不进入历史</strong></aside>
</div>

先记住三个判断：

- **工作区**回答“磁盘上的文件现在是什么样”。
- **暂存区**回答“下一次提交准备收哪些内容”。
- **提交历史**回答“以前正式保存过哪些版本”。

`git add` 只把当时的文件内容放进暂存区，不等于提交；`git commit` 只保存已经暂存的内容，不会替你把所有未保存、未暂存的修改一起带走。

</section>

<section id="example-read-status" data-learning-context="example-read-status" data-context-type="example" markdown="1">

## 先读懂一小段状态

假设目录中刚创建了三个文件：

```text
learning-workspace/
├── .gitignore
├── debug.log
└── notes/
    └── learning-log.md
```

`.gitignore` 中只有一条规则：

```gitignore
*.log
```

运行：

```bash
git status --short --ignored
```

可能看到：

```text
?? .gitignore
?? notes/
!! debug.log
```

- `??` 表示 Git 看见了新文件，但还没有开始跟踪。
- `!!` 表示文件匹配了忽略规则。
- 没有输出不一定是坏事，也可能表示工作区已经干净。

这里先别急着背符号。每次执行 `git add` 或 `git commit` 前后都看一次状态，很快就能把命令和变化对应起来。

</section>

<section id="reproduce-install-git" data-learning-context="reproduce-install-git" data-context-type="reproduce" markdown="1">

## 先确认终端能找到 Git

打开一个**新终端**，运行：

```bash
git --version
```

看到 `git version ...`，说明终端已经能找到 Git。版本号不必和课程一致；若低于 2.28，先更新，或者在后面的初始化命令中使用兼容写法。

=== "Windows"

    1. 打开 [Git 官方 Windows 下载页](https://git-scm.com/download/win)。
    2. 运行 Git for Windows 安装程序。第一次安装保留默认选项即可，不要照着来源不明的教程随意更改 Shell、换行符和凭据设置。
    3. 安装结束后关闭旧 PowerShell，在 VS Code 中新建终端，再运行 `git --version`。

=== "macOS"

    1. 先在“终端”中运行 `git --version`；系统可能提示安装 Xcode Command Line Tools。
    2. 没有出现系统提示时，可使用 [Git 官方 macOS 下载页](https://git-scm.com/download/mac)。已经在使用 Homebrew 的学习者也可以运行 `brew install git`。
    3. 安装结束后重开终端，再检查版本。

=== "Linux 简要补充"

    使用发行版的软件包管理器安装 Git。例如 Debian/Ubuntu 常用 `sudo apt install git`，Fedora 常用 `sudo dnf install git`。其他发行版查看 [Git 官方安装说明](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)。

如果仍提示找不到 `git`，先确认安装确实完成，再重开终端。不要通过关闭安全软件或运行陌生的一键脚本来绕过安装问题。

</section>

<section id="reproduce-initialize-workspace" data-learning-context="reproduce-initialize-workspace" data-context-type="reproduce" markdown="1">

## 把学习工作区变成本地仓库

在 VS Code 中重新打开完整的 `learning-workspace`，然后打开内置终端。先核对当前位置和文件：

=== "macOS / Linux"

    ```bash
    pwd
    ls
    ```

=== "Windows PowerShell"

    ```powershell
    Get-Location
    Get-ChildItem
    ```

你应该看到 `notes`、`practice` 和 `assets`，当前位置的最后一段应该是 `learning-workspace`。

### 先确认它没有被上层仓库管理

运行：

```bash
git rev-parse --show-toplevel
```

- 出现 `not a git repository`：符合本课预期，可以继续初始化。
- 输出正好是当前 `learning-workspace`：它已经是仓库，不要再次初始化，先运行 `git status` 看现状。
- 输出的是更上层目录：先停下来。当前文件已经受另一个仓库管理，建议把 `learning-workspace` 移到“文档”等独立位置后再继续。

确认无误后运行：

```bash
git init -b main
git branch --show-current
git status
```

第二条命令应输出 `main`。如果旧版本不支持 `-b`，改用：

```bash
git init
git branch -M main
```

`git init` 会在根目录创建隐藏的 `.git` 管理目录。不要手工修改其中的文件，也不要把它当作普通练习目录删除。它只建立本地仓库，不会创建 GitHub 仓库；此时运行 `git remote -v` 通常没有输出。

</section>

<section id="concept-ignore-generated-files" data-learning-context="concept-ignore-generated-files" data-context-type="concept" markdown="1">

## `.gitignore` 是入口规则，不是保密工具

在工作区根目录创建 `.gitignore`：

```gitignore
# 调试和运行日志
*.log

# Python 后续课程会生成的本地环境与缓存
.venv/
__pycache__/

# 本机配置与常见系统文件
.env
.DS_Store
Thumbs.db
```

再在根目录创建 `debug.log`，写入一句普通测试文字。**不要拿真实密码、token 或私人数据测试忽略规则。**

检查是哪条规则生效：

```bash
git check-ignore -v debug.log
git status --short --ignored
```

第一条命令应指出 `.gitignore` 中的 `*.log`，第二条命令应把 `debug.log` 标为 `!!`。

`.gitignore` 只影响尚未跟踪的文件。文件一旦进入提交历史，后来添加规则不会抹掉历史；密钥即使很快删除，也可能已经被复制或推送。因此正确顺序是：**先写忽略规则，再检查状态，最后暂存。**

!!! note "为什么 `.gitignore` 自己要提交"
    它描述了这个项目共同产生、共同不应提交的文件。把规则提交后，下一课克隆仓库的人也会得到同样的约束。

</section>

<section id="reproduce-first-commit" data-learning-context="reproduce-first-commit" data-context-type="reproduce" markdown="1">

## 保存工程学习工作台的第一个版本

每个提交都要有作者姓名和邮箱。为了不改动电脑上其他仓库，本课先把身份只配置在当前仓库：

```bash
git config --local user.name "你的提交署名"
git config --local user.email "你愿意写入提交历史的邮箱"
git config --local --list --show-origin
```

不要直接照抄占位文字。邮箱会写入提交元数据；如果以后公开到 GitHub，可在 GitHub 账号设置中查看并使用 noreply 邮箱。

现在只暂存这次真正需要的文件：

```bash
git add .gitignore notes/learning-log.md practice/README.md
git status
git diff --cached
```

逐行检查：

- `.gitignore`、学习记录和练习说明位于 `Changes to be committed`。
- `debug.log` 没有进入暂存内容。
- `git diff --cached` 展示的正是你准备保存的文字。

确认后提交：

```bash
git commit -m "record learning workspace"
git log -1 --format="%h %s"
```

提交成功后会出现一段短标识和 `record learning workspace`。这个标识由 Git 计算，每个人都可能不同，不需要和课程截图一致。

</section>

<section id="modify-second-commit" data-learning-context="modify-second-commit" data-context-type="modify" markdown="1">

## 自己做第二次变化

在 `notes/learning-log.md` 的 Git 记录部分补上真实信息：

```markdown
## Git 本地记录

- Git 版本：替换为自己的 `git --version` 输出
- 当前分支：main
- 忽略检查：debug.log 匹配 `*.log`
- 第一次提交：替换为自己的提交标识和说明
```

先不要暂存，运行：

```bash
git status --short
git diff -- notes/learning-log.md
```

这里看到的是工作区中的新变化。确认文字准确后再运行：

```bash
git add notes/learning-log.md
git diff --cached
git commit -m "document Git setup"
git log -2 --format="%h %s"
git status --short --ignored
```

最终应该有两次提交，`debug.log` 仍显示为忽略状态。把版本号、提交标识和排错记录换成自己的内容；不要为了和示例一致而伪造输出。

</section>

<section id="troubleshoot-local-git" data-learning-context="troubleshoot-local-git" data-context-type="troubleshoot" markdown="1">

## 先看状态，再决定下一条命令

| 你看到什么 | 常见原因 | 怎么回来 |
| --- | --- | --- |
| `not a git repository` | 当前目录不在仓库中 | 查看当前位置和文件列表，回到 `learning-workspace` |
| `Author identity unknown` | 当前仓库没有作者信息 | 配置本课的 `user.name`、`user.email` 后重试提交 |
| `nothing to commit` | 没有新变化，或变化还没暂存 | 运行 `git status`；有修改时再用具体路径 `git add` |
| `debug.log` 仍是 `??` | `.gitignore` 没保存、规则没匹配 | 运行 `git check-ignore -v debug.log`，核对文件名和规则位置 |
| `debug.log` 出现在已暂存内容中 | 文件在写规则前已经被暂存 | 运行 `git rm --cached debug.log`；它会移出暂存/索引但保留本地文件 |
| 暂存了不该提交的普通文件 | `git add` 选多了 | 已有第一次提交后可用 `git restore --staged 文件路径`，再检查状态 |
| `git log` 占满终端 | Git 打开了分页器 | 按 `q` 返回终端 |
| 状态里出现完全陌生的项目文件 | 打开了错误目录或处于上层仓库 | 运行 `git rev-parse --show-toplevel`，不要继续提交 |

不要用 `git add .`、`git commit -a` 或批量删除来“试试能不能恢复”。新手阶段先写具体路径，每次提交前固定看 `git status` 和 `git diff --cached`，误收文件的概率会低很多。

</section>

<section id="deepen-staging-snapshot" data-learning-context="deepen-staging-snapshot" data-context-type="deepen" markdown="1">

## `git add` 记录的是当时那一版

如果先运行 `git add notes/learning-log.md`，随后又继续编辑同一个文件，`git status` 可能同时显示它“已暂存”和“尚未暂存”。这不是 Git 重复了文件，而是暂存区保留着上一次 `git add` 时的内容，工作区又出现了更新版本。

可以分别查看：

```bash
# 工作区相对暂存区又改了什么
git diff

# 暂存区相对上次提交准备保存什么
git diff --cached
```

想把最新修改也放进同一次提交，就再次运行 `git add`；想留到下一次提交，就保持不动。暂存区的价值正在这里：一次提交可以只讲清一件事。

</section>

<section id="project-workspace-v06" data-learning-context="project-workspace-v06" data-context-type="project" markdown="1">

## 工程学习工作台 v0.6

现在工作台第一次拥有了可检查的本地历史：

| 上一版已经有 | 这节课加了什么 | 新增或变化的内容 | 下一版 |
| --- | --- | --- | --- |
| 结构清楚的目录、Markdown 学习记录和练习说明 | 本地仓库、共同忽略规则、两次有说明的提交 | `.gitignore`、`.git/`、`notes/learning-log.md`、Git 历史 | 创建 GitHub 空仓库，配置 origin，push 后再 clone 验证 |

`.git/` 由 Git 自动维护，不需要截图内部文件。请保存下面这些可以复核的结果：

```bash
git --version
git status --short --ignored
git log -2 --format="%h %s"
git check-ignore -v debug.log
```

这套结果能说明：工具已安装、日志确实被忽略、历史中有两次提交，而且当前检查发生在你自己的仓库中。

</section>

## 完成检查

- [ ] `git --version` 能在新终端中返回版本号。
- [ ] `git rev-parse --show-toplevel` 指向自己的 `learning-workspace`。
- [ ] 能解释工作区、暂存区和本地历史各自保存什么。
- [ ] `.gitignore` 已提交，`debug.log` 没有进入历史。
- [ ] `git log -2` 能看到两次由自己完成的提交。
- [ ] 提交前实际检查过 `git status` 和 `git diff --cached`。
- [ ] 能说明为什么 `git init` 不会自动连接 GitHub。

## 来源与版本

- 适用版本：Git 2.28 及以上；命令在 Git 2.50.1（Apple Git-155）复核。
- 安装：[Pro Git：Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)。
- 作者身份与配置层级：[Pro Git：First-Time Git Setup](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup)。
- 文件状态、暂存与提交：[Pro Git：Recording Changes to the Repository](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository)。
- 忽略规则：[gitignore 官方参考](https://git-scm.com/docs/gitignore)与[`git check-ignore` 官方参考](https://git-scm.com/docs/git-check-ignore)。
- 核查日期：2026-07-17。
- 验证方式：课程测试在隔离临时目录中初始化仓库、生成两次提交，并检查分支、暂存内容、忽略匹配与提交历史。

## 下一步

进入[GitHub 远程协作](06-github-remote.md)。下一节继续使用这个仓库，创建空远程仓库、检查 `origin`、完成第一次 `push`，再从另一个目录 `clone` 回来验证。

**保留整个 `learning-workspace` 和两次本地提交；下一课不会重新创建仓库。**
