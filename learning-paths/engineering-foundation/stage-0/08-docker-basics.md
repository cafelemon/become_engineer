<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-08" aria-hidden="true"></div>

<section id="overview-first-container" class="be-page-hero be-lesson-hero" data-learning-context="overview-first-container" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">工程基础入门 · 第九课</span>

# Docker最小认知

## 先分清一条命令背后发生了什么

<div class="be-tool-result" role="group" aria-label="Docker 第一次检查可能得到的结果" markdown="1">

```text
Docker CLI：已找到
Docker Engine：可以连接
第一次容器：Hello from Docker!
运行结束后：容器已自动删除（--rm）
```

</div>

这是安装并启动 Docker 后可能看到的结果。电脑上还没有 Docker 也没关系：这节课有一条不依赖安装的练习线，先把命令读懂；愿意安装时，再运行一个官方的最小容器验证。

<div class="be-page-actions" markdown="1">
[先看 Docker 里有哪些角色](#concept-cli-engine-image-container){ .md-button .md-button--primary }
[检查上一课的开发环境](07-development-environment.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>工程基础入门 · 9 / 10</strong></div>
  <div><span>安装要求</span><strong>默认不要求；真实运行为可选练习</strong></div>
  <div><span>完成后留下</span><strong>docker-check.md 与命令阅读记录</strong></div>
</div>

## 开始前

- 已完成[开发环境](07-development-environment.md)，能在 `learning-workspace` 中打开 VS Code 终端。
- 知道项目代码、解释器和依赖不是同一件东西。
- 默认练习只阅读和拆解命令，不下载镜像，也不要求管理员权限。
- 如果选择真实运行，需要联网下载小型镜像，并允许 Docker 在本机使用少量存储空间。

!!! note "先别急着复制命令"
    容器命令可以开放端口、读取本机目录和接收配置。先知道每个参数交出了什么，再决定是否运行。课程中的 `demo-web:1.0` 是讲解用的虚构镜像，不能直接执行。

<section id="concept-cli-engine-image-container" data-learning-context="concept-cli-engine-image-container" data-context-type="concept" markdown="1">

## 一条 `docker run` 命令经过了谁

<div class="be-docker-flow" role="img" aria-label="用户输入 Docker 命令，Docker CLI 把请求交给 Docker Engine，引擎根据镜像创建并运行容器。">
  <div><span>你在终端输入</span><strong>Docker CLI</strong><small>例如 docker run</small></div>
  <b aria-hidden="true">请求 →</b>
  <div><span>真正管理对象</span><strong>Docker Engine</strong><small>拉取镜像、创建容器、管理网络与存储</small></div>
  <b aria-hidden="true">使用 →</b>
  <div><span>模板与运行实例</span><strong>镜像 → 容器</strong><small>一个镜像可以创建多个容器</small></div>
  <aside><span>macOS 与 Windows 上通常由谁提供这些组件</span><strong>Docker Desktop；引擎运行在它管理的 Linux 虚拟机环境中</strong></aside>
</div>

先把四个词拆开：

- **Docker CLI** 是你在终端里调用的客户端，负责把请求交给引擎。
- **Docker Engine** 才是创建、运行和停止容器的后台服务。
- **镜像**是只读分层的运行包，包含启动程序需要的文件、库和配置基础。
- **容器**是由镜像创建的运行实例，有自己的状态，但仍会共享宿主机的部分资源。

镜像不是“一个正在运行的软件”，容器也不是“另一台完整电脑”。这里先记住它们的关系，虚拟机、命名空间和文件系统分层放到后面的系统课程再展开。

</section>

<section id="reproduce-check-docker" data-learning-context="reproduce-check-docker" data-context-type="reproduce" markdown="1">

## 检查 CLI，也检查 Engine

如果电脑上已经安装 Docker，请依次运行：

```bash
docker --version
docker version
```

两条命令回答的问题不同：

| 命令 | 能确认什么 | 不能单独确认什么 |
| --- | --- | --- |
| `docker --version` | 终端能找到 Docker CLI，并显示客户端版本 | Engine 是否已经启动、是否能够连接 |
| `docker version` | 正常时同时显示 `Client` 和 `Server` | 具体应用是否能在容器中正确运行 |

如果 `docker --version` 成功，`docker version` 却在 `Server` 部分报连接错误，通常不是“Docker 完全没装”，而是引擎尚未启动或当前用户不能连接它。

### 还没有 Docker

本课可以继续，不必为了看完概念立刻安装。准备安装时只从 [Docker 官方安装入口](https://docs.docker.com/get-started/get-docker/) 进入：

- Windows 与 macOS 通常安装 Docker Desktop，安装后打开应用，等引擎完成启动，再重新执行 `docker version`。
- Linux 可以按发行版官方说明安装 Docker Engine，也可以使用 Docker Desktop。不要把其他发行版的命令或不明安装脚本直接搬过来。
- 在公司电脑使用 Docker Desktop 前，先确认组织的软件许可与安全要求。

把实际结果写下来。命令不存在、只有 Client、Client 与 Server 都正常，都是清楚而有用的结论。

</section>

<section id="reproduce-run-hello" data-learning-context="reproduce-run-hello" data-context-type="reproduce" markdown="1">

## 可选：运行第一个最小容器

只有在 `docker version` 能正常显示 Client 和 Server，并且你愿意联网下载镜像时，才运行：

```bash
docker run --rm --name be-hello-check hello-world
```

第一次运行时，Engine 会发现本机没有 `hello-world` 镜像，于是先下载，再创建并启动容器。程序打印完问候语后退出，`--rm` 随即删除这个容器。

可以再检查一次：

```bash
docker ps -a --filter name=be-hello-check
docker image ls hello-world
```

第一条通常不再显示 `be-hello-check` 容器；第二条仍能看到下载到本机的镜像。**容器自动删除不等于镜像也被删除。**

如果提示容器名称已经存在，先用 `docker ps -a --filter name=be-hello-check` 看清它是什么。不要为了赶进度删除不属于这次练习的容器；可以换一个只属于你的练习名称。

### 不安装也能完成的练习

把下面四句话补完整，并和上一节的开发环境对照：

```text
Docker CLI 负责：
Docker Engine 负责：
镜像更像：
容器更像：
```

能准确解释这四项，就可以继续后面的命令阅读练习。真实运行只是增加一次亲手验证，不是理解概念的唯一方式。

</section>

<section id="example-read-docker-run" data-learning-context="example-read-docker-run" data-context-type="example" markdown="1">

## 从左到右读一条容器命令

下面是讲解用命令，镜像 `demo-web:1.0` 并不存在，不要直接运行：

```bash
docker run --rm --name be-preview \
  -p 127.0.0.1:8080:80 \
  --mount type=bind,src=/ABSOLUTE/PATH/learning-workspace/notes,dst=/workspace/notes,readonly \
  --env APP_MODE=study \
  demo-web:1.0
```

按顺序读：

| 片段 | 它告诉 Docker 什么 |
| --- | --- |
| `docker run` | 根据一个镜像创建并运行容器 |
| `--rm` | 程序退出后删除这个容器 |
| `--name be-preview` | 给容器一个容易识别的名字 |
| `-p 127.0.0.1:8080:80` | 只在本机回环地址开放 `8080`，转到容器的 `80` |
| `--mount ... readonly` | 把本机 `notes` 目录只读提供给容器中的 `/workspace/notes` |
| `--env APP_MODE=study` | 传入一项非敏感配置 |
| `demo-web:1.0` | 最后写要使用的镜像名和标签 |

不要把整行当成咒语。以后换镜像、换端口或换目录，仍然可以按这张表逐段检查。

</section>

<section id="concept-port-mount-config" data-learning-context="concept-port-mount-config" data-context-type="concept" markdown="1">

## 端口、挂载和配置都在跨越容器边界

### 端口：谁能访问这个服务

`-p 8080:80` 的左边是宿主机端口，右边是容器端口。没有写主机地址时，Docker 默认可能把端口发布到所有网络接口。学习和本机预览更稳妥的写法是：

```text
127.0.0.1:8080:80
└──只允许本机访问  └──容器服务端口
```

这不是完整的生产安全方案，但至少不会无意间把练习服务直接开放给同一网络中的其他设备。

### 挂载：容器能看到哪些本机文件

Bind mount 会把一个宿主机路径提供给容器。它默认可以写入，因此课程示例明确使用 `readonly`，并且只挂载项目中的 `notes`，不挂载整个用户目录。

先问三件事：

1. `src` 是不是我准备开放的真实目录？
2. 容器只需读取，还是确实需要写入？
3. 这个目录里有没有 `.env`、SSH 密钥、浏览器资料或其他私人文件？

### 环境变量：配置不等于秘密保险箱

`APP_MODE=study` 只是普通配置。真实令牌、密码和私钥可能通过命令历史、进程信息、截图或容器配置泄露，不要把它们写进公开命令、课程记录和 Git。密钥管理会在真实部署课程中单独处理。

</section>

<section id="modify-review-command" data-learning-context="modify-review-command" data-context-type="modify" markdown="1">

## 改一条命令，再解释你的选择

复制上一条讲解命令到 `practice/docker-command.txt`，只做三处修改：

1. 把本机端口从 `8080` 改为 `9090`，容器端口仍保留 `80`。
2. 把只读挂载目录从 `notes` 改为 `practice`。
3. 把 `APP_MODE=study` 改为 `APP_MODE=review`。

然后在命令下面写四行说明：

```text
浏览器应该访问：http://127.0.0.1:9090
容器内服务仍监听：80
容器能读取的本机目录：learning-workspace/practice
这条命令没有包含真实密钥：是 / 否
```

这仍然是命令阅读题，不要运行虚构镜像。重点是确认你能修改参数，而不是只会照抄原命令。

</section>

<section id="troubleshoot-docker" data-learning-context="troubleshoot-docker" data-context-type="troubleshoot" markdown="1">

## Docker 出错时先看哪一层

| 你看到的现象 | 它更接近哪一层 | 怎样继续 |
| --- | --- | --- |
| `docker: command not found` | CLI | 回到官方安装入口；安装后重开终端 |
| `docker --version` 成功，Server 连接失败 | Engine | 启动 Docker Desktop 或检查官方 Linux 服务说明和当前用户权限 |
| 拉取镜像超时 | 网络或镜像仓库 | 保存完整错误，检查网络；不要反复高频重试 |
| `Conflict. The container name ... is already in use` | 容器对象 | 用 `docker ps -a --filter name=...` 先查来源，换练习名或只处理自己的旧容器 |
| `port is already allocated` | 宿主机端口 | 换冒号左侧端口，例如 `9090:80` |
| bind source path does not exist | 宿主机路径 | 确认使用绝对路径、目录存在且只开放必要范围 |
| `permission denied` | 文件或 Engine 权限 | 不要直接用 `sudo` 反复尝试；先确认出错对象，再查平台官方说明 |

记录完整命令和完整错误，别只写“Docker 坏了”。CLI、Engine、镜像下载、容器启动、端口和挂载是不同层，先定位层次，处理会快很多。

</section>

<section id="deepen-container-boundary" data-learning-context="deepen-container-boundary" data-context-type="deepen" markdown="1">

## 容器带来一致性，但不是完整隔离承诺

镜像把应用需要的用户空间文件组织成可复制的分层包，容器再以受限制的进程形式运行它。与完整虚拟机相比，容器通常启动更快、包更小；它也会共享宿主系统内核，不等于一台拥有独立内核的新电脑。

在 macOS 和 Windows 上，Docker Desktop 会管理一个 Linux 虚拟机，让 Linux 容器能够运行。于是你在终端里看到的是 Docker CLI，背后还存在 Engine、虚拟机、网络和文件共享。遇到路径或性能问题时，这层关系很重要。

容器也不是天然安全沙箱。开放端口、挂载目录、运行来源不明的镜像或授予过高权限，都会扩大风险。本课只采用本机端口、最小只读目录和公开非敏感配置，后面的部署课还会继续加固。

</section>

<section id="project-workspace-v09" data-learning-context="project-workspace-v09" data-context-type="project" markdown="1">

## 工程学习工作台 v0.9

| 上一版已经有 | 这节课增加 | 不写进仓库 | 下一版准备做什么 |
| --- | --- | --- | --- |
| GitHub 远程、`.venv` 和开发环境记录 | Docker 状态、概念解释与命令阅读记录 | 镜像缓存、容器数据、私人路径和密钥 | 用一套检查习惯收束整个工程基础阶段 |

新建 `notes/docker-check.md`：

````markdown
# Docker 检查

- Docker CLI：未安装 / 已安装，版本为……
- Docker Engine：未检查 / 无法连接 / 可以连接
- hello-world：未运行 / 已运行，结果为……
- 镜像和容器的区别：
- 我检查端口时会看：
- 我检查挂载时会看：
- 环境变量中是否包含真实密钥：否
- 遇到的问题与完整错误：
````

完成 `practice/docker-command.txt` 后检查提交内容：

```bash
git add notes/docker-check.md practice/docker-command.txt
git diff --cached
git commit -m "record Docker basics"
git push
```

如果记录含用户名、公司地址、内部镜像仓库、令牌或私人绝对路径，先删掉或改成占位符再提交。Git 仓库保存学习记录，不保存 Docker 自己下载的镜像和容器数据。

</section>

## 完成检查

- [ ] 我能区分 Docker CLI、Engine、镜像和容器。
- [ ] 我知道 `docker --version` 不能单独证明 Engine 可用。
- [ ] 我能从左到右解释 `docker run` 示例中的每一个参数。
- [ ] 我能分清宿主机端口和容器端口，并优先把本机练习绑定到 `127.0.0.1`。
- [ ] 我只挂载必要目录，能说明 `readonly` 的作用。
- [ ] 我没有把真实密钥、私人路径或内部地址写进命令和提交。
- [ ] 没有安装 Docker 时，我也完成了概念解释和命令修改。
- [ ] 我提交并推送了 `docker-check.md` 与命令阅读记录。

## 来源与版本

- 适用版本：Docker CLI 与 Engine 27–29；Docker Desktop 当前受支持版本。不同版本的输出可能略有差异，以官方说明和本机完整结果为准。
- 核查日期：2026-07-17。
- 官方资料：[Docker 架构概览](https://docs.docker.com/get-started/docker-overview/)、[镜像基础](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/)、[`docker run` 参考](https://docs.docker.com/reference/cli/docker/container/run/)、[`docker version` 参考](https://docs.docker.com/reference/cli/docker/version/)、[端口发布](https://docs.docker.com/engine/network/port-publishing/)、[bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)、[获取 Docker](https://docs.docker.com/get-started/get-docker/)。
- 验证方式：仓库自动测试只解析固定命令，检查端口、只读挂载、非敏感配置和镜像字段，不调用 Docker、不联网。`hello-world` 属于学习者主动选择的本机练习。
- 安全说明：Docker 文档和产品界面会持续更新；真实部署的网络、密钥、镜像供应链和权限策略必须按当时官方文档与组织要求重新核查。

## 下一步

进入[验证习惯](09-validation-habit.md)。你已经用版本、路径、环境、Docker 对象和命令参数检查过多个工具；下一节会把这些零散动作整理成一套可以反复使用的验证方法。
