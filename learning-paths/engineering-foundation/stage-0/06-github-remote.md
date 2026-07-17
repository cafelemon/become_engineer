<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-10" aria-hidden="true"></div>

<section id="overview-remote-roundtrip" class="be-page-hero be-lesson-hero" data-learning-context="overview-remote-roundtrip" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">工程基础入门 · 第七课</span>

# GitHub 远程协作：remote、push 与 clone

## 同一次提交，在原目录和新克隆目录里应该有同一个标识

<div class="be-git-result" role="group" aria-label="原仓库与克隆仓库的提交标识一致" markdown="1">

```console
$ git -C learning-workspace rev-parse --short HEAD
<同一提交标识>

$ git -C learning-workspace-clone rev-parse --short HEAD
<同一提交标识>
```

</div>

中间的 GitHub 不是“另一个文件夹”，而是远程仓库。原目录把已经提交的历史推上去，新目录再把同一份文件和历史克隆回来，三个位置才真正连成闭环。

<div class="be-page-actions" markdown="1">
[先看懂本地与远程的关系](#concept-local-remote-clone){ .md-button .md-button--primary }
[检查上一课的本地仓库](06-git.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>工程基础入门 · 7 / 10</strong></div>
  <div><span>继续使用</span><strong>learning-workspace 的两次本地提交</strong></div>
  <div><span>完成后留下</span><strong>origin、GitHub 仓库和独立 clone</strong></div>
</div>

## 开始前

- 已完成[本地 Git 与 .gitignore](06-git.md)，`git log -2` 能看到两次提交。
- 当前分支是 `main`，`git status --short --ignored` 除了预期的忽略文件外没有待提交变化。
- 拥有可以登录的 GitHub 账号，并能完成自己的双因素认证。
- 本课使用 Git 2.28 及以上和 GitHub.com；界面文字于 2026-07-17 核查。

!!! warning "先决定仓库是否适合公开"
    学习记录可能含真实姓名、电脑路径、邮箱、截图或私人计划。第一次练习更建议创建 **Private** 仓库。只有逐个检查当前文件和历史提交，确认没有隐私、密钥或受限内容后，再考虑公开。

<section id="concept-local-remote-clone" data-learning-context="concept-local-remote-clone" data-context-type="concept" markdown="1">

## `origin` 只是这条远程地址的本地简称

<div class="be-git-flow be-remote-flow" role="img" aria-label="原本地仓库通过 push 把提交发送到 GitHub 远程仓库，再通过 clone 建立第二个本地仓库。">
  <div><span>原来的电脑目录</span><strong>本地仓库</strong><small>learning-workspace</small></div>
  <b aria-hidden="true">push →</b>
  <div><span>网络上的仓库</span><strong>GitHub</strong><small>OWNER/REPOSITORY</small></div>
  <b aria-hidden="true">clone →</b>
  <div><span>新建的电脑目录</span><strong>克隆仓库</strong><small>learning-workspace-clone</small></div>
  <aside><span>origin</span><strong>本地保存的远程名称，指向一个 HTTPS 或 SSH URL</strong></aside>
</div>

- `git remote add origin URL`：在**当前本地仓库**中记录一条远程名称和地址。
- `git push`：把已经提交的历史发送到远程，不读取编辑器里尚未保存或提交的文字。
- `git clone URL`：从远程新建本地目录，复制文件和历史，并自动把来源记为 `origin`。

`origin` 不是 GitHub 账号，也不是固定服务器。它只是一个常用简称；真正决定目标的是后面的 URL，真正决定能否访问的是仓库权限与认证。

</section>

<section id="example-read-remote-url" data-learning-context="example-read-remote-url" data-context-type="example" markdown="1">

## 把一行远程地址拆开看

课程中的占位地址是：

```text
https://github.com/OWNER/REPOSITORY.git
```

| 部分 | 表示什么 | 需要替换吗 |
| --- | --- | --- |
| `https://github.com` | GitHub.com 的 HTTPS 主机 | 不替换 |
| `OWNER` | 你的 GitHub 用户名或组织名 | 必须替换 |
| `REPOSITORY` | 你刚创建的仓库名 | 必须替换 |
| `.git` | Git URL 常见结尾 | 从页面复制即可 |

例如账号是 `xiaoma-study`、仓库叫 `learning-workspace`，地址才会类似：

```text
https://github.com/xiaoma-study/learning-workspace.git
```

这只是结构示例，不代表真实账号。最稳妥的方式不是手敲，而是在自己的 GitHub 仓库页面复制 **HTTPS** URL，再用 `git remote -v` 复核。

</section>

<section id="reproduce-review-before-push" data-learning-context="reproduce-review-before-push" data-context-type="reproduce" markdown="1">

## 推送前再检查一次本地历史

在 `learning-workspace` 根目录运行：

```bash
git rev-parse --show-toplevel
git branch --show-current
git status --short --ignored
git log -2 --format="%h %s"
git remote -v
```

继续之前应该满足：

- 仓库根目录就是自己的 `learning-workspace`。
- 当前分支是 `main`。
- 除了 `!! debug.log` 等预期忽略项，没有 `??`、`M` 或待提交内容。
- 历史中能看到上一课的两次提交。
- `git remote -v` 没有输出；若已经有输出，先核对来源，不要重复添加。

还要在 VS Code 文件树和最近两次提交中检查一次隐私。`.gitignore` 只能阻止尚未跟踪的文件，不能让已经提交的密码或 token 从历史里消失。发现敏感内容时先停止本课、立即轮换凭据，再评估历史清理；不要把“删掉当前文件”误认为风险已经解除。

</section>

<section id="reproduce-create-empty-repo" data-learning-context="reproduce-create-empty-repo" data-context-type="reproduce" markdown="1">

## 在 GitHub 创建一个空仓库

1. 登录 GitHub，打开 [Create a new repository](https://github.com/new)。也可以使用右上角 **＋ → New repository**。
2. 在 **Owner** 选择自己的账号。
3. **Repository name** 填 `learning-workspace`；名称已被占用时可加自己的简短后缀。
4. 第一次练习建议选择 **Private**。
5. **不要**勾选添加 README、`.gitignore` 或 License。上一课已经有本地历史，远程先保持空白最容易连接。
6. 点击 **Create repository**。创建后应看到 **Quick setup** 和 HTTPS 地址。

!!! note "为什么不要在网页上先加 README"
    GitHub 会为网页初始化内容创建远程提交，这样本地和远程会各自拥有不同的起点。本课故意使用空远程，让第一次 `push` 只处理一条清楚的历史线；以后再学习 `fetch`、`pull` 和合并。

仓库公开或私有只改变访问范围，不改变 Git 命令。不要为了方便验收把含私人学习记录的仓库改成 Public。

</section>

<section id="reproduce-add-origin" data-learning-context="reproduce-add-origin" data-context-type="reproduce" markdown="1">

## 把复制的地址记为 `origin`

回到 `learning-workspace` 的 VS Code 内置终端。把下面的占位地址换成自己刚复制的 HTTPS URL：

```bash
git remote add origin https://github.com/OWNER/REPOSITORY.git
git remote -v
git remote get-url origin
```

`git remote -v` 会分别显示 fetch 和 push 地址，它们在本课中应该相同；`git remote get-url origin` 应只输出你复制的那条 URL。

在执行 push 前，逐段核对：

- 域名是 `github.com`。
- OWNER 是自己当前登录的账号或有权限的组织。
- 仓库名与刚创建的空仓库一致。
- URL 中没有 token、密码或多余空格。

若出现 `remote origin already exists`，不要连续重试。先运行 `git remote -v`；地址正确就直接沿用，地址错误才运行：

```bash
git remote set-url origin https://github.com/OWNER/REPOSITORY.git
git remote -v
```

</section>

<section id="reproduce-first-push" data-learning-context="reproduce-first-push" data-context-type="reproduce" markdown="1">

## 第一次 push 会建立跟踪关系

再次确认分支名和远程地址：

```bash
git branch --show-current
git remote -v
```

确认是 `main` 和自己的 GitHub URL 后运行：

```bash
git push -u origin main
```

这条命令可以拆成四部分：

- `git push`：发送本地已提交历史。
- `-u`：把本地 `main` 的上游设置为 `origin/main`。
- `origin`：目标远程的本地简称。
- `main`：要推送的本地分支。

系统可能打开浏览器或 Git Credential Manager。核对授权页面域名后，按自己的方式完成登录和双因素认证。GitHub 不再接受账号登录密码作为命令行 Git 的密码；不要把 token 写进 URL、Shell 历史、课程文件、截图或聊天记录。

成功后刷新 GitHub 仓库页面，应该看到 `.gitignore`、`notes`、`practice` 和上一课的两次提交。然后运行：

```bash
git status -sb
```

输出首行应包含类似 `main...origin/main`，且不提示本地领先或落后。

</section>

<section id="modify-second-push" data-learning-context="modify-second-push" data-context-type="modify" markdown="1">

## 再做一次自己的变化

在 `notes/learning-log.md` 的 Git 部分补上：

```markdown
## GitHub 远程验证

- 远程名称：origin
- 远程仓库：只写 OWNER/REPOSITORY，不记录 token
- 首次 push：成功，或记录真实错误与恢复过程
- clone 检查：等待完成
```

保存后按熟悉的顺序运行：

```bash
git status
git diff -- notes/learning-log.md
git add notes/learning-log.md
git diff --cached
git commit -m "document remote verification"
git push
```

第一次 push 已建立上游，所以这次通常不必再写 `origin main`。刷新 GitHub 页面，本地 `git log -1 --format="%h %s"` 与网页最新提交的短标识和说明应该一致。

如果网页没变化，先判断是否真的产生新提交，再检查当前分支和 `origin`。反复运行 `git push` 不会替你保存未提交的文件。

</section>

<section id="reproduce-clone-verify" data-learning-context="reproduce-clone-verify" data-context-type="reproduce" markdown="1">

## 从另一个目录 clone 回来

先回到 `learning-workspace` 的父目录。macOS/Linux 可用 `cd ..`，PowerShell 可用 `Set-Location ..`。确认当前位置后运行：

```bash
git clone https://github.com/OWNER/REPOSITORY.git learning-workspace-clone
```

把 URL 替换为自己的地址。克隆成功后，在父目录执行这些跨平台命令：

```bash
git -C learning-workspace rev-parse HEAD
git -C learning-workspace-clone rev-parse HEAD
git -C learning-workspace-clone log -1 --format="%h %s"
git -C learning-workspace-clone remote -v
```

前两条完整提交标识应该逐字相同；克隆目录的最新提交应为 `document remote verification`，并且已经自动存在 `origin`。

打开 `learning-workspace-clone/notes/learning-log.md`，确认刚推送的 GitHub 远程记录也在。这个检查比“网页看起来有文件”更强：文件、提交历史和远程关系都来自同一次 clone。

验证后先不要同时编辑两个目录。保留克隆目录作为本课结果，或在确认原仓库安全后从文件管理器删除它；不要删除原来的 `learning-workspace`。

</section>

<section id="troubleshoot-remote-sync" data-learning-context="troubleshoot-remote-sync" data-context-type="troubleshoot" markdown="1">

## 错误通常落在四个位置

| 你看到什么 | 先检查哪里 | 怎么处理 |
| --- | --- | --- |
| `not a git repository` | 当前终端目录 | 回到原 `learning-workspace`，核对仓库根目录 |
| `remote origin already exists` | `git remote -v` 的现有 URL | 正确就沿用，错误才用 `git remote set-url origin URL` |
| `src refspec main does not match any` | 当前分支和本地提交 | 运行 `git branch --show-current` 与 `git log -1`；没有提交不能推送历史 |
| `Repository not found` | OWNER、仓库名、可见性与登录账号 | 从自己的仓库页面重新复制 URL，确认当前账号有权限 |
| `Authentication failed` | URL 是 HTTPS 还是 SSH、系统用了哪种凭据 | 按对应认证方式处理；不要输入账号登录密码或把 token 拼进 URL |
| `non-fast-forward` | 远程是否已经有本地没有的提交 | 停止 push，更不要 `--force`；保留错误，后续学习 fetch/pull 后再合并 |
| push 成功但网页没更新 | 提交、分支和 origin 是否一致 | 比较本地最新提交、当前分支、远程 URL 和网页正在查看的分支 |
| clone 提示目标目录已存在且非空 | 目标目录名冲突 | 换一个新目录名，不要覆盖原工作区 |

排错顺序固定为：**目录 → 本地提交 → 远程 URL → 分支 → 认证**。把完整错误中的 token、邮箱、私人仓库名遮住后再求助，不要只发一句“push 不行”。

</section>

<section id="deepen-upstream-tracking" data-learning-context="deepen-upstream-tracking" data-context-type="deepen" markdown="1">

## `origin/main` 是本地保存的远程状态记录

第一次 `git push -u origin main` 后，本地 `main` 会记录上游是 `origin/main`。以后直接运行 `git push` 时，Git 才知道默认把哪个本地分支发到哪个远程分支。

```bash
git branch -vv
git status -sb
```

`origin/main` 并不是每次都实时读取 GitHub。它是本地的远程跟踪引用，会在 `fetch`、`pull`、`push` 等网络操作后更新。下一阶段学习多人协作时，你会用它判断本地领先、落后或分叉；本课只要求建立并检查跟踪关系。

</section>

<section id="project-workspace-v07" data-learning-context="project-workspace-v07" data-context-type="project" markdown="1">

## 工程学习工作台 v0.7

| 上一版已经有 | 这节课加了什么 | 可以复核的结果 | 下一版 |
| --- | --- | --- | --- |
| 本地仓库、`.gitignore` 和两次提交 | GitHub 空远程、origin、两次 push、独立 clone | 远程 URL、跟踪关系、网页提交、两个目录的相同 HEAD | 记录解释器、编译器、PATH 与第三方依赖，建立可复现开发环境 |

请在不暴露隐私的前提下保留：

```bash
git remote -v
git branch -vv
git log -3 --format="%h %s"
git -C ../learning-workspace-clone rev-parse --short HEAD
```

公开截图要遮住私人仓库名、邮箱和任何凭据信息。最有价值的结果不是一张 GitHub 首页，而是你能解释本地提交如何经 `origin` 到达远程，又怎样被另一个目录完整克隆回来。

</section>

## 完成检查

- [ ] 推送前检查过当前目录、分支、状态、提交历史和隐私内容。
- [ ] GitHub 仓库由已有本地历史接入，没有在网页上额外初始化 README。
- [ ] `git remote -v` 指向自己的正确仓库，URL 中没有凭据。
- [ ] 第一次 `git push -u origin main` 成功并建立上游。
- [ ] 自己完成第三次提交并用普通 `git push` 同步。
- [ ] 独立 clone 中的最新完整提交标识与原仓库一致。
- [ ] 能解释 `origin`、`origin/main`、push 和 clone 分别是什么。
- [ ] 遇到认证或 non-fast-forward 错误时知道停止，而不是输入密码或强制覆盖。

## 来源与版本

- 适用版本：Git 2.28 及以上、GitHub.com 当前网页；核查日期 2026-07-17。
- 创建空仓库并接入已有本地代码：[Adding locally hosted code to GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)。
- 远程名称、URL 与修改方式：[Managing remote repositories](https://docs.github.com/en/get-started/git-basics/managing-remote-repositories)。
- HTTPS／SSH 与远程地址：[About remote repositories](https://docs.github.com/en/get-started/git-basics/about-remote-repositories)。
- 命令行认证：[About authentication to GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github)。
- 克隆行为：[Cloning a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)。
- 验证方式：自动测试使用本机裸仓库模拟远程，不访问 GitHub、不读取账号或凭据；真实 GitHub 页面、认证和可见性由学习者按完成检查人工复核。

## 下一步

进入[开发环境](07-development-environment.md)。下一节会把“我的电脑能运行”拆成可复核的解释器／编译器、PATH、依赖和版本记录，让克隆出来的项目更接近可复现。

**保留原工作区、GitHub 仓库和一次独立 clone 的检查结果；不要把凭据保存进任何课程文件。**
