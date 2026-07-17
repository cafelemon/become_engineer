<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-07" aria-hidden="true"></div>

<section id="overview-environment-fingerprint" class="be-page-hero be-lesson-hero" data-learning-context="overview-environment-fingerprint" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">工程基础入门 · 第八课</span>

# 开发环境

## 同一份代码能不能运行，先看它实际用了哪一个 Python

<div class="be-git-result" role="group" aria-label="系统 Python 与项目虚拟环境 Python 的检查结果" markdown="1">

```text
系统 Python
  版本：Python 3.11 或更高版本
  位置：电脑上实际被命令找到的解释器

项目 Python
  位置：learning-workspace/.venv/...
  是否处于独立环境：True
```

</div>

代码没有变，执行它的解释器、版本和依赖却可能不同。这节课不靠“我应该装过”来判断环境，而是在 `learning-workspace` 里建立一个项目自己的 Python 环境，并留下别人看得懂的检查记录。

<div class="be-page-actions" markdown="1">
[先看懂代码与环境的关系](#concept-code-runtime-dependencies){ .md-button .md-button--primary }
[检查上一课的远程仓库](06-github-remote.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>工程基础入门 · 8 / 10</strong></div>
  <div><span>继续使用</span><strong>learning-workspace 与 GitHub 远程仓库</strong></div>
  <div><span>完成后留下</span><strong>.venv 与 environment-check.md</strong></div>
</div>

## 开始前

- 已完成[GitHub 远程协作](06-github-remote.md)，本地 `learning-workspace` 能正常提交和推送。
- 能在 VS Code 中打开工作区和内置终端。
- 本课以 Python 3.11 及以上为课程基线，只使用标准库；Windows、macOS 和 Linux 均有对应命令。
- 如果还没有 Python，本课会从官方下载入口开始；不要复制来历不明的安装脚本。

!!! note "先不安装第三方包"
    这节课只创建空的项目虚拟环境并检查 `pip` 属于哪一个 Python。真正安装课程依赖会在需要依赖的项目里进行，这样更容易知道变化来自哪里。

<section id="concept-code-runtime-dependencies" data-learning-context="concept-code-runtime-dependencies" data-context-type="concept" markdown="1">

## 代码、解释器和依赖不是同一件东西

<div class="be-environment-flow" role="img" aria-label="源代码由 Python 解释器读取，解释器再结合项目依赖产生运行结果。">
  <div><span>你写的文本</span><strong>项目代码</strong><small>例如 main.py</small></div>
  <b aria-hidden="true">交给 →</b>
  <div><span>真正执行代码的程序</span><strong>Python 解释器</strong><small>有版本，也有具体位置</small></div>
  <b aria-hidden="true">读取 →</b>
  <div><span>项目额外需要的代码</span><strong>第三方依赖</strong><small>安装在某个 Python 环境中</small></div>
  <aside><span>运行结果还会受什么影响</span><strong>操作系统、当前目录、环境变量、配置和输入数据</strong></aside>
</div>

先把三个词分开：

- **项目代码**是仓库里的 `.py`、配置和数据文件，可以由 Git 传到另一台电脑。
- **Python 解释器**是读取并执行 Python 代码的程序。它不在仓库里，必须在电脑上安装。
- **第三方依赖**是项目额外使用的软件包。它们也不应该直接复制进 Git，而应根据依赖声明重新安装。

所以，上一课的 `clone` 只能带回仓库内容，不能替你复制本机 Python 和 `.venv`。这正是开发环境需要单独记录和重建的原因。

</section>

<section id="example-path-chooses-command" data-learning-context="example-path-chooses-command" data-context-type="example" markdown="1">

## 输入一个命令，Shell 会去哪里找

假设 PATH 的查找顺序是：

```text
1. /usr/local/bin
2. /usr/bin
3. /bin
```

当你输入 `python3`，Shell 会从第一项开始寻找同名可执行程序，找到后就停止。两个目录里即使都有 Python，排在前面的那个通常会先被执行。

这也解释了一个常见现象：安装已经完成，但旧终端仍然找不到新命令。安装程序更新了 PATH，新打开的终端能读到新配置，原来的终端却还保留旧值。

PATH 是“去哪些目录找命令”的顺序，不是 Python 本身，也不是项目依赖。初学阶段先学会查看结果，不要为了试错随意覆盖整条 PATH。

</section>

<section id="reproduce-find-python" data-learning-context="reproduce-find-python" data-context-type="reproduce" markdown="1">

## 找到并确认电脑上的 Python

先在 `learning-workspace` 的 VS Code 终端执行与你系统对应的一组命令。

=== "Windows PowerShell"

    ```powershell
    python --version
    Get-Command python | Select-Object -ExpandProperty Source
    git --version
    ```

    新安装的 Windows 环境优先使用 Python 官方 Install Manager。打开 [Python 下载页](https://www.python.org/downloads/)，安装管理器和一个稳定的 Python 3 运行时，再关闭并重新打开终端。管理多个版本时可以用 `py list` 查看现有运行时。

=== "macOS"

    ```bash
    python3 --version
    command -v python3
    git --version
    ```

    如果 `python3` 不可用，从 [Python 下载页](https://www.python.org/downloads/) 选择 macOS 安装包，完成后重新打开终端。课程不要求修改系统自带目录，也不建议用 `sudo pip` 往系统 Python 里安装课程依赖。

=== "Linux"

    ```bash
    python3 --version
    command -v python3
    git --version
    ```

    Linux 发行版通常通过自己的包管理器提供 Python。先查看发行版官方文档并安装 Python 3、`venv` 和 `pip` 支持；不要直接照搬其他发行版的命令。

应该至少得到三条事实：

1. 哪个命令能启动 Python。
2. 它的版本是否为 3.11 或更高。
3. 这个命令实际指向哪个可执行文件。

绝对路径可能含用户名或公司目录。它适合本地排错，写入公开仓库前请把私人部分改成 `<HOME>`，不要把整条 PATH、令牌或密钥贴进课程记录。

</section>

<section id="concept-project-environment" data-learning-context="concept-project-environment" data-context-type="concept" markdown="1">

## 为什么每个项目都要有自己的 `.venv`

全局 Python 像一间公用工具室。所有项目都往里面装包，今天升级项目 B 的依赖，明天就可能让项目 A 失效。

虚拟环境会在项目旁边建立一套独立的 Python 入口和包目录：

```text
电脑上的 Python 3.13
├── 用来创建 learning-workspace/.venv
└── 用来创建 another-project/.venv

两个 .venv 可以安装不同版本的第三方包
```

`.venv` 可以删除并重建，因此上一课已经把它写进 `.gitignore`。仓库保存的是代码和依赖声明，不是某一台电脑生成的虚拟环境目录。

</section>

<section id="reproduce-create-venv" data-learning-context="reproduce-create-venv" data-context-type="reproduce" markdown="1">

## 创建项目自己的 Python 环境

确认终端当前位于 `learning-workspace` 根目录。下面的做法**不依赖激活脚本**，直接调用 `.venv` 里的 Python，新手更容易判断到底运行了哪一个解释器。

=== "Windows PowerShell"

    ```powershell
    python -m venv .venv
    .\.venv\Scripts\python.exe --version
    .\.venv\Scripts\python.exe -c "import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)"
    .\.venv\Scripts\python.exe -m pip --version
    ```

=== "macOS / Linux"

    ```bash
    python3 -m venv .venv
    ./.venv/bin/python --version
    ./.venv/bin/python -c "import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)"
    ./.venv/bin/python -m pip --version
    ```

你应该看到：

- Python 版本仍然满足 3.11 及以上。
- `sys.executable` 的路径位于 `learning-workspace/.venv` 中。
- `sys.prefix != sys.base_prefix` 输出 `True`，说明当前解释器属于虚拟环境。
- `pip --version` 显示的路径同样位于 `.venv`。

这里使用 `python -m pip`，意思是“让眼前这个 Python 运行它自己的 pip 模块”。它比单独输入 `pip` 更容易避免把包装到另一个 Python 环境里。

</section>

<section id="example-activation-is-convenience" data-learning-context="example-activation-is-convenience" data-context-type="example" markdown="1">

## 激活只是让命令变短

激活虚拟环境后，Shell 会把 `.venv` 的可执行目录临时放到 PATH 前面，于是可以直接输入 `python`。关闭终端或执行 `deactivate` 后，这个临时变化就会消失。

=== "Windows PowerShell"

    ```powershell
    .\.venv\Scripts\Activate.ps1
    python -c "import sys; print(sys.executable)"
    deactivate
    ```

=== "macOS / Linux"

    ```bash
    source .venv/bin/activate
    python -c "import sys; print(sys.executable)"
    deactivate
    ```

如果 Windows 因执行策略阻止 `Activate.ps1`，这不妨碍使用虚拟环境。继续写完整路径 `.\.venv\Scripts\python.exe` 即可，不必为了这一课修改全局安全策略。

</section>

<section id="modify-write-environment-note" data-learning-context="modify-write-environment-note" data-context-type="modify" markdown="1">

## 写成你自己的环境记录

新建 `notes/environment-check.md`，把占位内容换成你刚才看到的真实结果：

````markdown
# 开发环境检查

- 操作系统：Windows / macOS / Linux
- 使用的终端：PowerShell / zsh / bash / 其他
- Python 命令：python / python3
- Python 版本：
- Python 位置：公开记录时将私人目录替换为 `<HOME>`
- Git 版本：
- 项目虚拟环境：已创建 / 尚未创建
- `.venv` 中的 Python 版本：
- `sys.prefix != sys.base_prefix`：
- `.venv` 是否被 Git 忽略：

## 我遇到的问题

- 执行的命令：
- 完整报错：
- 我已经确认的事实：
- 下一项检查：
````

然后验证 `.venv` 没有进入 Git：

```bash
git status --short --ignored
```

预期能看到 `!! .venv/`，而 `notes/environment-check.md` 是新的可提交文件。不要照抄示例版本号；版本不同不一定是错误，关键是它满足项目要求并且记录与实际命令一致。

</section>

<section id="troubleshoot-environment" data-learning-context="troubleshoot-environment" data-context-type="troubleshoot" markdown="1">

## 环境问题先查这五件事

| 你看到的现象 | 先检查什么 | 怎样继续 |
| --- | --- | --- |
| `python` 或 `python3` 找不到 | 安装是否完成、终端是否重开、命令拼写 | 回到官方安装说明；Windows 再检查 `py list`，macOS/Linux 检查 `command -v python3` |
| 版本低于 3.11 | 命令位置和机器上已有的版本 | 安装受支持的 Python，再用位置命令确认没有继续命中旧版本 |
| `No module named venv` | Python 是否由精简的 Linux 系统包提供 | 按发行版官方说明安装对应的 venv 组件，再重新创建 `.venv` |
| `pip` 指向全局目录 | 是否直接输入了裸 `pip` | 改用 `.venv` 中的 Python 执行 `-m pip --version` |
| 激活脚本被 PowerShell 阻止 | 完整错误和当前执行策略 | 不改策略也可以工作：直接调用 `.venv\Scripts\python.exe` |
| `.venv` 出现在待提交文件中 | `.gitignore` 是否有 `.venv/`，环境是否建在仓库根目录 | 补回忽略规则；提交前再次运行 `git status --short --ignored` |

不要只写“环境坏了”。一条能继续排查的记录至少应包含：操作系统、终端、当前目录、完整命令、完整输出和你已经确认的命令位置。

</section>

<section id="deepen-path-and-interpreter" data-learning-context="deepen-path-and-interpreter" data-context-type="deepen" markdown="1">

## PATH 选命令，`sys.executable` 告诉你最终选中了谁

`command -v` 或 `Get-Command` 观察 Shell 的命令查找结果；`sys.executable` 则由已经运行起来的 Python 报告自己的可执行文件位置。两者放在一起，能回答两个不同问题：

```text
Shell 准备运行谁？        command -v / Get-Command
Python 实际是谁？         sys.executable
它是否处于虚拟环境？      sys.prefix != sys.base_prefix
pip 属于这个 Python 吗？  python -m pip --version
```

解释器版本只是环境的一部分。以后项目还会增加 `pyproject.toml`、锁定依赖、系统库和服务配置；这节课先把最容易混淆的 Python 入口固定下来。

</section>

<section id="project-workspace-v08" data-learning-context="project-workspace-v08" data-context-type="project" markdown="1">

## 工程学习工作台 v0.8

| 上一版已经有 | 这节课增加 | 本地保留但不提交 | 下一版准备做什么 |
| --- | --- | --- | --- |
| 本地提交、GitHub 远程和独立 clone | 一份经过脱敏的环境检查记录 | `.venv/` 与私人绝对路径 | 读懂 Docker 如何描述另一层可复现环境 |

完成检查后提交这份公开安全的记录：

```bash
git add notes/environment-check.md
git diff --cached
git commit -m "record development environment"
git push
```

再确认工作区状态：

```bash
git status --short --ignored
```

应该没有未提交的普通文件，并能看到 `.venv/` 仍处于忽略状态。此时项目不是“把我的 Python 上传了”，而是留下了版本要求、检查方法和可重建的本地环境边界。

</section>

## 完成检查

- [ ] 我能区分项目代码、Python 解释器和第三方依赖。
- [ ] 我确认了可用的 Python 命令、版本和实际位置。
- [ ] 我在 `learning-workspace/.venv` 创建了项目虚拟环境。
- [ ] 我用 `.venv` 中的 Python 验证了版本、解释器位置和 `pip` 归属。
- [ ] 我没有把 `.venv`、完整 PATH、令牌或私人绝对路径提交到 Git。
- [ ] 我提交并推送了经过脱敏的 `notes/environment-check.md`。
- [ ] 遇到错误时，我能留下系统、终端、目录、命令和完整输出。

## 来源与版本

- 适用版本：Python 3.11–3.14、Git 2.28 及以上；Windows 11 PowerShell、当前受支持的 macOS 与常见 Linux 发行版。
- 核查日期：2026-07-17。
- 官方资料：[Python 下载](https://www.python.org/downloads/)、[Windows 使用 Python](https://docs.python.org/3/using/windows.html)、[`venv` 文档](https://docs.python.org/3/library/venv.html)、[`sys` 文档](https://docs.python.org/3/library/sys.html)、[PyPA 虚拟环境指南](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)。
- 验证方式：仓库测试在临时目录创建真实 `.venv`，分别调用基础解释器和虚拟环境解释器，检查 `sys.executable`、`sys.prefix`、`sys.base_prefix` 与 `pip`，全程不联网、不安装第三方包。
- 平台说明：Windows Python Install Manager 和命令行为易变化界面，本课按 Python 3.14 官方文档核查；安装时以当前官方页面为准。

## 下一步

进入 [Docker 最小认知](08-docker-basics.md)。你已经知道代码、解释器、依赖和本地虚拟环境各自负责什么；下一节会继续追问，怎样用镜像和容器描述更完整、更一致的运行环境。
