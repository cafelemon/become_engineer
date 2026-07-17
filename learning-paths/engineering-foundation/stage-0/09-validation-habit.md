<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-09" aria-hidden="true"></div>

<section id="overview-stage-result" class="be-page-hero be-lesson-hero" data-learning-context="overview-stage-result" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">工程基础入门 · 第十课</span>

# 验证习惯

## “我做过”还不够，要能说明现在是什么状态

<div class="be-tool-result" role="group" aria-label="工程基础阶段检查结果" markdown="1">

```text
[通过] 当前目录就是 learning-workspace
[通过] Git 历史至少有 3 次提交
[通过] .venv 仍被 Git 忽略
[已复现] 错误文件名会失败；改回正确路径后恢复
[未检查] Docker Engine（可选，不阻断进入 Python）

结论：必需项通过；一次失败已经恢复；可选项如实保留。
```

</div>

前九课留下了目录、记录、提交、远程仓库、开发环境和 Docker 认知。这节课不再增加一个新工具，而是把它们检查一遍：看到什么就写什么，没有运行的项目就标“未检查”。

<div class="be-page-actions" markdown="1">
[先看一份判断怎样成立](#concept-claim-evidence-judgment){ .md-button .md-button--primary }
[检查上一课的 Docker 记录](08-docker-basics.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>工程基础入门 · 10 / 10</strong></div>
  <div><span>继续使用</span><strong>learning-workspace 的文件、Git 与环境</strong></div>
  <div><span>完成后留下</span><strong>stage-0-acceptance.md 与工作台 v1.0</strong></div>
</div>

## 开始前

- 已按顺序完成前九课，并保留同一个 `learning-workspace`。
- 工作区至少有 `notes/learning-log.md`、`practice/README.md`、`.gitignore` 和本地 Git 历史。
- 已完成 GitHub 远程配置和项目 `.venv`；如果中途没有完成，请如实记为待补，不要补写不存在的结果。
- Docker 安装和 Engine 运行仍是可选项；本阶段要求能解释和检查，不要求所有电脑都运行容器。

!!! note "公开前先脱敏"
    验收记录可以提交，但完整用户目录、公司路径、内部仓库地址、账号、令牌、环境变量和 Docker 配置不应进入公开页面或 Git。

<section id="concept-claim-evidence-judgment" data-learning-context="concept-claim-evidence-judgment" data-context-type="concept" markdown="1">

## 一次检查怎样变成可靠判断

<div class="be-validation-cycle" role="list" aria-label="验证记录从主张到下一步的五个组成部分">
  <article role="listitem"><b>1</b><span>主张</span><small>我想确认什么</small></article>
  <article role="listitem"><b>2</b><span>环境与操作</span><small>在哪里，执行了什么</small></article>
  <article role="listitem"><b>3</b><span>实际结果</span><small>原样保留关键输出</small></article>
  <article role="listitem"><b>4</b><span>判断</span><small>结果为什么支持结论</small></article>
  <article role="listitem"><b>5</b><span>下一步</span><small>失败或未检查时继续做什么</small></article>
</div>

例如，“Git 应该没问题”不是一条可靠判断。可以把它改成：

```text
主张：当前目录是 Git 仓库，并且能读取最近一次提交。
环境：learning-workspace 根目录，Git 2.x。
操作：git rev-parse --show-toplevel；git log -1 --oneline。
结果：第一条显示工作区根目录，第二条显示最近一次提交。
判断：通过，因为目录与提交历史都能由 Git 自己读取。
下一步：提交阶段验收后再检查一次状态和最新提交。
```

结果和判断要分开。结果是命令真正输出了什么；判断是这段输出为什么足以支持主张。把两者混在一起，很容易只留下“应该可以”。

</section>

<section id="example-three-statuses" data-learning-context="example-three-statuses" data-context-type="example" markdown="1">

## 通过、失败、未检查不是一回事

<div class="be-validation-status" role="list" aria-label="验证的三种状态">
  <article role="listitem" data-state="success"><strong>通过</strong><span>已经执行，结果符合事先写下的判断条件。</span></article>
  <article role="listitem" data-state="failure"><strong>失败</strong><span>已经执行，结果不符合条件；保留错误并写恢复动作。</span></article>
  <article role="listitem" data-state="unverified"><strong>未检查</strong><span>还没有运行或没有足够依据；不能写成通过。</span></article>
</div>

“失败”说明检查给出了有用信息，不等于整个项目没有价值；“未检查”也不是失败，只是当前没有足够依据。真正需要避免的是把未检查写成完成，或者看到失败后删掉错误记录。

工程基础阶段还要区分**必需项**和**可选项**：项目目录、文件、Git 和 Python 环境属于进入下一阶段的必需项；Docker Engine 是否已经安装属于可选项。可选项未检查，不会阻断 Python 起步。

</section>

<section id="reproduce-stage-check" data-learning-context="reproduce-stage-check" data-context-type="reproduce" markdown="1">

## 给工作台做一次阶段检查

先在 `learning-workspace` 根目录新建 `notes/stage-0-acceptance.md`，写下日期、系统和终端。然后运行与你系统对应的命令。

=== "Windows PowerShell"

    ```powershell
    Get-Location
    Test-Path .\notes\learning-log.md
    Test-Path .\practice\README.md
    git rev-parse --show-toplevel
    git status --short --ignored
    git log --oneline -3
    git remote get-url origin
    .\.venv\Scripts\python.exe -c "import sys; print(sys.version); print(sys.prefix != sys.base_prefix)"
    docker version
    ```

=== "macOS / Linux"

    ```bash
    pwd
    test -f notes/learning-log.md && echo "learning log: found"
    test -f practice/README.md && echo "practice readme: found"
    git rev-parse --show-toplevel
    git status --short --ignored
    git log --oneline -3
    git remote get-url origin
    ./.venv/bin/python -c "import sys; print(sys.version); print(sys.prefix != sys.base_prefix)"
    docker version
    ```

逐项判断：

| 检查项 | 通过时应该看到什么 | 要求 |
| --- | --- | --- |
| 项目根目录 | 当前路径与 `git rev-parse --show-toplevel` 指向同一个工作区 | 必需 |
| 关键文件 | 学习记录与练习说明都存在 | 必需 |
| Git 历史 | 能看到至少 3 次有说明的提交 | 必需 |
| Git 忽略 | `.venv/` 显示为忽略项，没有进入提交 | 必需 |
| 远程关系 | `origin` 已配置；公开记录时不暴露私人地址或凭据 | 必需 |
| Python 环境 | 项目 Python 能运行，prefix 对比为 `True` | 必需 |
| Docker Engine | Client 与 Server 都能显示；没有安装则如实记录 | 可选 |

`git status --short --ignored` 可能显示新建的验收文件，这是正常变化，不要为了追求“空输出”先删除它。记录当前状态，等文件完成并提交后再检查工作区是否收口。

如果 `docker version` 找不到命令或只有 Client、没有 Server，把实际状态写下即可。上一课要求的是能区分和检查这些层，不是强制安装。

</section>

<section id="example-minimal-failure" data-learning-context="example-minimal-failure" data-context-type="example" markdown="1">

## 故意写错一次文件名，再恢复

这个练习不会删除或覆盖任何文件，只是读取一个不存在的路径。

=== "Windows PowerShell"

    ```powershell
    Get-Content .\notes\does-not-exist.md
    Get-Content .\notes\learning-log.md -TotalCount 3
    ```

=== "macOS / Linux"

    ```bash
    head -n 3 notes/does-not-exist.md
    head -n 3 notes/learning-log.md
    ```

第一条应该报告找不到文件，第二条应该重新读到真实学习记录。把这段过程写成：

```text
主张：错误文件名会被明确拒绝，改回正确路径后可以恢复。
错误命令：
完整错误：
我确认的原因：notes 目录中没有这个文件。
恢复命令：
恢复结果：
```

最小复现不是故意把真实项目弄坏。它只保留触发问题所需的最少条件，并且知道怎样回到正常状态。

</section>

<section id="modify-write-acceptance" data-learning-context="modify-write-acceptance" data-context-type="modify" markdown="1">

## 写成你自己的阶段验收

把真实检查结果整理进 `notes/stage-0-acceptance.md`：

````markdown
# 工程基础阶段验收

- 核查日期：
- 操作系统与终端：
- 工作区：learning-workspace（不写私人绝对路径）

| 主张 | 必需/可选 | 状态 | 关键结果 | 判断与下一步 |
| --- | --- | --- | --- | --- |
| 当前目录是项目根目录 | 必需 | 通过/失败/未检查 |  |  |
| 学习记录与练习说明存在 | 必需 |  |  |  |
| Git 历史至少有 3 次提交 | 必需 |  |  |  |
| .venv 被 Git 忽略 | 必需 |  |  |  |
| origin 已配置 | 必需 |  |  |  |
| 项目 Python 属于 .venv | 必需 |  |  |  |
| 能解释 CLI、Engine、镜像和容器 | 必需 |  |  |  |
| Docker Engine 可以运行 | 可选 |  |  |  |

## 一次失败与恢复

- 错误命令：
- 完整错误：
- 原因判断：
- 恢复动作：
- 恢复结果：

## 进入 Python 前

- 已经具备的能力：
- 仍需补上的必需项：
- 第一个 Python 文件准备放在哪里：
````

至少把一项最初的“失败”或“未检查”推进一步：补上缺失文件、重新进入正确目录、确认 `.venv`，或者明确写出可选 Docker 暂不安装的理由。修改后重新运行对应命令，用新结果更新状态。

</section>

<section id="troubleshoot-validation" data-learning-context="troubleshoot-validation" data-context-type="troubleshoot" markdown="1">

## 阶段检查卡住时，先别把所有问题混在一起

| 现象 | 先判断什么 | 怎样继续 |
| --- | --- | --- |
| 项目根目录和当前目录不同 | 是否打开了父目录、clone 副本或 `notes/` | 回到真正要验收的 `learning-workspace` 再运行命令 |
| 关键文件找不到 | 路径起点、拼写和文件是否保存 | 用文件树和目录命令逐层确认，不重建同名空文件冒充原记录 |
| Git 提交少于 3 次 | 是否一直没有提交，或打开了另一个仓库 | 先看完整 `git log` 和仓库根目录，再决定需要补哪次有意义的提交 |
| `.venv` 出现在普通待提交文件中 | `.gitignore` 是否包含 `.venv/`，文件是否已被跟踪 | 回到 Git 课的忽略检查；不要直接批量提交 |
| `origin` 不存在 | 本地仓库是否完成远程课 | 按远程课配置自己的 GitHub 仓库，再独立 clone 验证 |
| 项目 Python prefix 对比为 `False` | 调用的是全局 Python，不是 `.venv` 中的解释器 | 使用平台对应的 `.venv` 完整路径重新检查 |
| Docker Server 无法连接 | CLI 和 Engine 的状态不同 | 记为 Docker 可选项未通过或未完成，不影响必需项结论 |
| 验收记录含私人信息 | 复制了完整路径、远程 URL 或环境输出 | 保留判断所需片段，其余替换为 `<HOME>`、`<REPOSITORY>` 等占位符 |

一张表里可能同时有通过、失败和未检查。按检查项逐个处理，比写一句“环境有问题”更容易继续。

</section>

<section id="deepen-manual-to-automated" data-learning-context="deepen-manual-to-automated" data-context-type="deepen" markdown="1">

## 手工检查以后会怎样长成自动化测试

现在的检查由你运行命令、读输出并写判断。以后进入编程和项目课程，同样的结构会逐渐变成自动化：

```text
手工主张        → 测试名称
手工操作        → 测试代码或脚本
预期结果        → 断言
实际输出        → 测试报告和日志
修复后再检查    → 回归测试
多人重复执行    → CI
```

自动化不会替你决定应该验证什么。一个脚本即使每次都显示绿色，也可能只检查了不重要的事情。因此本课先练主张、结果和判断，后面的测试框架再把重复动作交给程序。

</section>

<section id="career-handoff-story" data-learning-context="career-handoff-story" data-context-type="career" markdown="1">

## 求职时，这个小工作台能说明什么

它还不是商业项目，也不需要包装成“完整开发平台”。更诚实的说法是：

> 我从零建立了一个可交接的学习工作区。文件、Markdown、Git、本地与远程仓库、Python 虚拟环境和 Docker 基础检查都沿同一目录演进；阶段结束时，我用通过、失败、未检查三种状态整理结果，并保留了一次可重复的错误与恢复记录。

如果被继续追问，可以打开提交历史、`.gitignore`、环境记录和阶段验收，说明一次具体问题是怎样定位的。能够拿出文件和命令解释，比背一句“我有工程意识”更有说服力。

</section>

<section id="project-workspace-v10" data-learning-context="project-workspace-v10" data-context-type="project" markdown="1">

## 工程学习工作台 v1.0

| 版本 | 工作台新学会了什么 |
| --- | --- |
| v0.1–v0.3 | 记录目标，建立目录，并从终端读写同一份学习记录 |
| v0.4–v0.5 | 用 VS Code 操作工作区，用 Markdown 整理成可读文档 |
| v0.6–v0.7 | 建立本地版本历史，安全连接 GitHub，并用 clone 复核 |
| v0.8–v0.9 | 固定项目 Python 环境，读懂 Docker 的对象和配置 |
| v1.0 | 汇总必需项、可选项、失败恢复和进入 Python 的准备状态 |

确认验收文件已经脱敏，再完成这次阶段提交：

```bash
git add notes/stage-0-acceptance.md
git diff --cached
git commit -m "complete engineering foundation"
git push
git status --short --ignored
git log -1 --oneline
```

最后两条应该显示：没有意外的普通修改，`.venv/` 仍处于忽略状态，最新提交就是阶段收口。若 push 暂时失败，本地提交仍然存在；把远程失败单独记录和修复，不要重做整个工作区。

从下一课开始，`learning-workspace` 不再继续堆放所有编程文件。Python 起步会建立自己的练习目录和“学习进度报告器”，但本课形成的目录、版本、环境和验证习惯会继续使用。

</section>

## 完成检查

- [ ] 我能把一次检查写成主张、环境与操作、实际结果、判断和下一步。
- [ ] 我能区分通过、失败和未检查，不把可选 Docker 状态当成 Python 的阻断项。
- [ ] 我检查了项目根目录、关键文件、Git 历史、忽略规则、远程关系和项目 Python。
- [ ] 我安全复现了一次错误文件名，并用正确路径恢复。
- [ ] 我至少推进了一项原来的失败或未检查状态。
- [ ] `stage-0-acceptance.md` 已脱敏，并保存了真实命令和关键结果。
- [ ] 我完成阶段提交，再检查了工作区状态和最新提交。
- [ ] 我知道进入 Python 起步后，哪些能力和记录方式仍会继续使用。

## 来源与版本

- 适用版本：Git 2.28 及以上、Python 3.11–3.14；Docker CLI／Engine 27–29 为可选检查项。Windows 11 PowerShell、当前受支持的 macOS 与常见 Linux 发行版均提供对应路径。
- 核查日期：2026-07-17。
- 官方资料：[Git 状态](https://git-scm.com/docs/git-status)、[Git 历史](https://git-scm.com/docs/git-log)、[仓库根目录解析](https://git-scm.com/docs/git-rev-parse)、[读取远程 URL](https://git-scm.com/docs/git-remote)、[Python `venv`](https://docs.python.org/3/library/venv.html)、[Docker Client／Server 版本](https://docs.docker.com/reference/cli/docker/version/)。
- 验证方式：仓库测试在临时目录创建真实 Git 工作区和 3 次提交，检查根目录、提交数量、`.venv` 忽略和干净状态；随后触发一次无破坏的缺失文件错误并恢复。测试不访问网络、不调用 Docker。
- 隐私说明：自动测试只使用临时路径和无效测试邮箱；学习者公开自己的记录前仍需检查私人路径、账号、远程地址、环境变量和凭据。

## 下一步

进入 [Python 起步](../../programming-languages/python-basics/README.md)。第一课会让“个人学习档案”先运行起来；工程基础形成的文件、终端、Git、环境和验证方法会直接用在这个新程序上。
