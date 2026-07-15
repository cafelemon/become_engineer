# Docker最小认知

<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-08" aria-hidden="true"></div>

本课用“读懂并安全验证一条容器命令”建立 Docker 最小认知：不强制安装，不执行生产部署，也不暴露任何密钥。

## 五步任务路线

<div class="be-task-route" role="list" aria-label="本课五步任务">
  <span role="listitem">1 检查可用性</span><span role="listitem">2 区分镜像容器</span><span role="listitem">3 读端口</span><span role="listitem">4 判断挂载</span><span role="listitem">5 安全迁移</span>
</div>

<section id="step-1" class="be-task-step" data-step-id="step-1" markdown="1">

### 第一步：检查 Docker 是否可用

**任务：** 执行 `docker --version`；没有安装也如实记录命令和输出。**成功证据：** 知道“未安装”是检查结果，不是学习失败。

??? tip "提示一"
    本课大部分练习可通过阅读命令完成，不要求立刻安装 Docker。
??? tip "提示二"
    命令找不到时，记录完整报错和当前环境，先不要复制不明安装脚本。

</section>

<section id="step-2" class="be-task-step" data-step-id="step-2" markdown="1">

### 第二步：用一句话区分镜像和容器

**任务：** 将镜像写成“可复用模板”，将容器写成“由模板启动的运行实例”。**成功证据：** 能判断 `docker run` 使用镜像并创建/启动容器。

??? tip "提示一"
    镜像不等于正在运行的程序；容器才有运行状态。
??? tip "提示二"
    同一个镜像可以启动多个彼此独立的容器。

</section>

<section id="step-3" class="be-task-step" data-step-id="step-3" markdown="1">

### 第三步：读懂一次端口映射

**任务：** 解释 `-p 8080:80` 中哪个是本机端口、哪个是容器端口。**成功证据：** 能说明浏览器访问本机 `8080` 后如何到达容器服务。

??? tip "提示一"
    冒号左侧是宿主机对外暴露的端口，右侧是容器内服务端口。
??? tip "提示二"
    端口被占用时，换左侧端口；不要随意改变服务实际监听的右侧端口。

</section>

<section id="step-4" class="be-task-step" data-step-id="step-4" markdown="1">

### 第四步：判断挂载与环境变量风险

**任务：** 看一条带 `-v` 和 `-e` 的命令，指出本机目录会暴露给容器、密钥不能写进公开命令。**成功证据：** 能说出挂载和环境变量各自传递什么。

??? tip "提示一"
    `-v` 将本机路径交给容器访问，路径写错可能写入意外位置。
??? tip "提示二"
    `-e` 可传配置，但令牌和密码不应出现在截图、提交或公开文档。

</section>

<section id="step-5" class="be-task-step" data-step-id="step-5" markdown="1">

### 第五步：完成安全学习记录

**任务：** 记录你检查到的 Docker 状态，并写下下一步只验证一个命令或概念。**成功证据：** 记录不含真实密钥、不把“镜像”和“容器”混淆。

??? tip "提示一"
    还未安装时，可记录“未安装，已理解 docker --version 的用途”。
??? tip "提示二"
    以后启动容器时先检查端口、挂载路径和环境变量来源。

</section>

本节先建立 Docker 的最小认知：它不是必须一开始就精通的工具，但后面做 Web、AI、LLM 和部署时会经常遇到。

工程基础入门只要求你知道 Docker 解决什么问题，能读懂最常见的几个词：镜像、容器、端口、挂载和环境变量。复杂的 Dockerfile、docker compose 和生产部署放到后续项目中学习。

## 前置知识

开始前应完成：

- [学习方法](01-learning-method.md)
- [文件系统](02-filesystem.md)
- [终端与 Shell](03-terminal-shell.md)
- [编辑器](04-editor.md)
- [Markdown](05-markdown.md)
- [Git](06-git.md)
- [开发环境](07-development-environment.md)

你需要能打开终端，能执行命令并记录输出。没有安装 Docker 也可以完成本节的大部分练习。

## 学习目标

完成本节后，你应该能做到：

- 解释 Docker 主要解决“环境一致性”问题。
- 区分镜像和容器。
- 解释端口映射为什么常见于 Web 服务。
- 解释挂载为什么会把本机目录交给容器使用。
- 知道环境变量可以给容器传配置，但不应该随意公开密钥。
- 认识 `docker --version`、`docker run`、`docker ps`、`docker logs` 和 `docker stop` 的用途。

## 学习顺序

按下面顺序学习：

1. 先理解为什么会需要 Docker。
2. 再区分镜像和容器。
3. 接着理解端口、挂载和环境变量。
4. 然后认识几个观察命令。
5. 最后完成一份 Docker 最小认知记录。

本节不要求写 Dockerfile，不要求配置 docker compose，也不要求部署真实项目。

## 为什么需要 Docker

很多项目不是只有代码，还依赖运行环境。

例如，一个后端项目可能需要：

```text
Python版本
第三方依赖
数据库
系统库
环境变量
启动命令
```

如果每个人都在自己的电脑上手动安装，就容易出现：

```text
我这里能跑，你那里不能跑。
```

Docker 的核心价值之一是把运行环境打包和隔离起来，让项目更容易在不同机器上以相似方式运行。

工程基础入门可以先这样理解：

```text
Docker = 用容器提供更一致的运行环境
```

## 镜像和容器

镜像和容器是 Docker 最重要的两个概念。

### 镜像

镜像可以理解为“可复制的运行环境模板”。

例如：

```text
某个 Python Web 项目的镜像
某个 PostgreSQL 数据库的镜像
某个 Redis 服务的镜像
```

镜像本身通常不表示正在运行，它更像一个可以启动的模板。

### 容器

容器是从镜像启动出来的运行实例。

可以这样类比：

```text
镜像 = 模板
容器 = 用模板启动出来的正在运行或曾经运行过的实例
```

同一个镜像可以启动多个容器。

## 端口

Web 服务通常需要通过端口被访问。

如果一个服务在容器内部监听 `8000` 端口，你的电脑浏览器不一定能直接访问它。通常需要把容器端口映射到本机端口。

常见写法类似：

```bash
docker run -p 8000:8000 some-image
```

可以先读成：

```text
把本机的8000端口连接到容器里的8000端口。
```

本节只要求读懂端口映射的含义，不要求你排查复杂网络问题。

## 挂载

挂载是把本机文件或目录交给容器使用。

常见写法类似：

```bash
docker run -v /local/path:/app/data some-image
```

可以先读成：

```text
把本机的 /local/path 提供给容器里的 /app/data 使用。
```

挂载很有用，但也要谨慎。不要随便把私人目录、密钥目录或整个用户目录挂载进不熟悉的容器。

## 环境变量

容器经常通过环境变量接收配置。

常见写法类似：

```bash
docker run -e APP_ENV=dev some-image
```

可以先读成：

```text
启动容器时传入一个叫 APP_ENV 的配置，值是 dev。
```

环境变量可以传配置，但不要把真实密钥、访问令牌或私人密码写进公开文档、截图或提交记录。

## 常见命令认知

本节只要求认识这些命令的用途。

### 查看 Docker 是否可用

```bash
docker --version
```

用途：查看本机是否能找到 Docker 命令，以及 Docker 版本。

### 启动一个容器

```bash
docker run hello-world
```

用途：从镜像启动容器。`hello-world` 常用于检查 Docker 基本功能。

如果本机没装 Docker，或 Docker 服务没启动，这条命令可能失败。失败也可以作为学习记录。

### 查看容器

```bash
docker ps
```

用途：查看正在运行的容器。

查看所有容器通常会看到：

```bash
docker ps -a
```

### 查看日志

```bash
docker logs container-name-or-id
```

用途：查看某个容器输出过什么信息。

### 停止容器

```bash
docker stop container-name-or-id
```

用途：停止正在运行的容器。

## 示例：读懂一条 Docker 命令

看这条命令：

```bash
docker run -p 8000:8000 -e APP_ENV=dev demo-web
```

可以拆成：

```text
docker run      启动一个容器
-p 8000:8000    做端口映射
-e APP_ENV=dev  传入环境变量
demo-web        使用的镜像名称
```

如果你能把命令拆开解释，就已经完成工程基础入门的 Docker 最小目标。

## 实践练习

### 练习 1：记录 Docker 是否可用

在终端中执行：

```bash
docker --version
```

需要产出：

```text
命令是否成功：

输出结果或错误信息：

我判断本机 Docker 当前是否可用：

判断依据：
```

如果命令失败，不要急着安装。先把失败信息记录完整。

### 练习 2：区分镜像和容器

用自己的话回答：

```text
镜像是什么：

容器是什么：

为什么同一个镜像可以启动多个容器：
```

要求不要只抄定义，要写出自己的理解。

### 练习 3：读懂端口映射

看命令：

```bash
docker run -p 8080:80 nginx
```

回答：

```text
本机端口是：

容器端口是：

浏览器可能访问哪个本机地址：

这条命令使用的镜像可能是：
```

### 练习 4：识别挂载风险

看命令：

```bash
docker run -v /Users/me:/data some-image
```

回答：

```text
这条命令把本机哪个目录交给了容器：

这可能有什么风险：

如果目录里有私人文件，应该怎么处理：
```

Windows 学习者可以把 `/Users/me` 理解为某个本机用户目录。

### 练习 5：读懂环境变量

看命令：

```bash
docker run -e APP_ENV=dev -e DEBUG=true demo-app
```

回答：

```text
传入了几个环境变量：

变量名分别是：

变量值分别是：

哪些内容不应该写进公开命令示例：
```

## 常见错误与排查

| 错误 | 表现 | 怎么排查 |
| --- | --- | --- |
| 把镜像当成容器 | 以为下载镜像就等于服务正在运行 | 记住镜像是模板，容器才是运行实例 |
| Docker 命令存在但服务没启动 | `docker --version` 成功，`docker run` 失败 | 记录完整错误，判断是命令问题还是 Docker 服务问题 |
| 端口理解反了 | 浏览器访问错误端口 | 拆开 `-p 本机端口:容器端口` |
| 随意挂载私人目录 | 容器能访问不该访问的文件 | 只挂载项目需要的最小目录 |
| 把密钥写进公开命令 | 文档或提交记录里出现真实 token | 使用占位符，不公开真实凭据 |
| 一开始就学复杂部署 | 概念混在一起，难以排查 | 工程基础入门只掌握镜像、容器、端口、挂载和环境变量 |

## 完成标准

完成本节需要同时满足：

- 能解释 Docker 主要解决环境一致性问题。
- 能区分镜像和容器。
- 能读懂 `docker --version`、`docker run`、`docker ps`、`docker logs` 和 `docker stop` 的用途。
- 能解释 `-p 本机端口:容器端口` 的基本含义。
- 能说明挂载会让容器访问本机文件，因此要谨慎选择目录。
- 能说明环境变量可以传配置，但真实密钥不能公开。
- 能记录一次 Docker 可用性检查的成功结果或失败信息。

## 下一步

进入 [验证习惯](09-validation-habit.md)。下一节会把前面学到的命令、文件、环境和 Docker 认知串起来，学习如何运行、观察输出、复现错误、记录命令和结果。
