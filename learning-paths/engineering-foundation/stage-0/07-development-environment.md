# 开发环境

<div class="be-tutor-mount" data-tutor-lesson="engineering-foundation-07" aria-hidden="true"></div>

本课不先安装一堆工具，而是为你的学习工作区完成一份环境检查：版本、命令位置、PATH、依赖边界和一次错误记录。

## 五步任务路线

<div class="be-task-route" role="list" aria-label="本课五步任务">
  <span role="listitem">1 记录版本</span><span role="listitem">2 定位命令</span><span role="listitem">3 理解 PATH</span><span role="listitem">4 区分依赖</span><span role="listitem">5 验证迁移</span>
</div>

<section id="step-1" class="be-task-step" data-step-id="step-1" markdown="1">

### 第一步：记录一个可运行版本

**任务：** 在终端执行 `python3 --version`（或系统可用的 `python --version`），把命令和输出写入学习记录。**成功证据：** 版本号与执行命令成对保留。

??? tip "提示一"
    “装过 Python”不等于终端能找到可执行命令。
??? tip "提示二"
    若命令失败，先完整记录报错，暂时不要盲目重复安装。

</section>

<section id="step-2" class="be-task-step" data-step-id="step-2" markdown="1">

### 第二步：找到命令来自哪里

**任务：** 使用 `which python3`（Windows 可用 `where python`）查询命令位置。**成功证据：** 能说明版本输出和可执行文件路径来自同一次检查。

??? tip "提示一"
    系统可能安装多个同名程序，路径能解释你实际运行的是哪一个。
??? tip "提示二"
    没有结果时，把命令、系统和完整输出记录下来。

</section>

<section id="step-3" class="be-task-step" data-step-id="step-3" markdown="1">

### 第三步：用 PATH 解释一次查找

**任务：** 查看 PATH 的概念说明，并用自己的话写一句“系统如何找到 python”。**成功证据：** 能区分 PATH 是查找顺序，不是 Python 本身。

??? tip "提示一"
    输入命令时，Shell 会按 PATH 中的目录依次查找。
??? tip "提示二"
    同名命令冲突时，第二步记录的位置比猜测更可靠。

</section>

<section id="step-4" class="be-task-step" data-step-id="step-4" markdown="1">

### 第四步：区分代码、运行时和依赖

**任务：** 为一个 Python 小程序分别标注项目代码、解释器和将来可能安装的第三方依赖。**成功证据：** 不把 `.py` 文件、Python 程序和第三方库混成一个概念。

??? tip "提示一"
    解释器负责执行代码；依赖是项目额外需要的库。
??? tip "提示二"
    虚拟环境用于隔离不同项目的依赖，不等于复制项目代码。

</section>

<section id="step-5" class="be-task-step" data-step-id="step-5" markdown="1">

### 第五步：记录一次环境问题并迁移

**任务：** 任选“找不到命令”或“版本不对”的场景，写下环境、命令、输出和下一步检查。**成功证据：** 别人能据此重现或继续排查。

??? tip "提示一"
    环境问题先收集事实：系统、终端、命令、完整输出。
??? tip "提示二"
    下一节 Docker 会继续使用“命令 + 输出 + 判断”的验证方式。

</section>

本节解决一个最常见的小白困惑：同样一段代码，为什么有的人能运行，有的人运行不了。

开发环境不是某个软件的名字，而是一组让程序能被编写、运行和验证的条件。你现在只需要理解最小概念：解释器、编译器、运行时、版本、环境变量、PATH、依赖和虚拟环境。

## 前置知识

开始前应完成：

- [学习方法](01-learning-method.md)
- [文件系统](02-filesystem.md)
- [终端与 Shell](03-terminal-shell.md)
- [编辑器](04-editor.md)
- [Markdown](05-markdown.md)
- [本地 Git 与 .gitignore](06-git.md)
- [GitHub 远程协作](06-github-remote.md)

你需要能打开终端，能执行简单命令，能把结果记录到 Markdown 文件里。

## 学习目标

完成本节后，你应该能做到：

- 解释解释器和编译器分别在做什么。
- 解释版本不一致为什么会导致程序运行失败。
- 知道 PATH 是系统寻找命令的位置清单。
- 区分程序本身、项目代码和项目依赖。
- 理解虚拟环境为什么能减少不同项目之间的依赖冲突。
- 遇到“找不到命令”或“版本不对”时，能先记录检查结果。

## 学习顺序

按下面顺序学习：

1. 先理解“代码不会自己运行”。
2. 再区分解释器、编译器和运行时。
3. 接着检查版本和命令位置。
4. 然后理解环境变量和 PATH。
5. 最后理解依赖与虚拟环境。

本节不要求你安装任何新工具，也不要求你解决所有环境问题。目标是先会看、会问、会记录。

## 代码不会自己运行

你写在文件里的内容只是文本。电脑要真正执行它，需要某种程序来处理。

例如：

```text
Python 代码 -> Python 解释器 -> 执行结果
C++ 代码 -> 编译器 -> 可执行程序 -> 执行结果
JavaScript 代码 -> 浏览器或 Node.js 运行时 -> 执行结果
```

所以，当你看到“代码不能运行”时，不要只盯着代码文件，还要检查：

- 运行它的工具是否存在。
- 工具版本是否符合要求。
- 当前目录是否正确。
- 项目依赖是否准备好。
- 命令是否写错。

## 解释器、编译器和运行时

### 解释器

解释器通常是一边读取代码，一边执行代码的程序。

Python 常见执行方式：

```bash
python script.py
```

或：

```bash
python3 script.py
```

这里的 `python` 或 `python3` 就是命令名，它背后对应 Python 解释器。

### 编译器

编译器会先把源代码转换成另一种更适合机器运行的形式。

C++ 常见流程是：

```text
main.cpp -> 编译器 -> 可执行程序 -> 运行可执行程序
```

你现在不需要掌握 C++ 编译命令，只要先知道：C++ 通常不会像 Python 那样直接运行源文件。

### 运行时

运行时是程序执行时依赖的环境。

例如：

- 浏览器可以作为前端 JavaScript 的运行时。
- Node.js 可以作为服务端 JavaScript 的运行时。
- Java 程序依赖 JVM 运行。

初学时可以这样记：解释器、编译器和运行时都是“让代码变成实际行为”的工具，只是方式不同。

## 版本

同一个工具可能有多个版本。版本不同，支持的语法、功能和依赖也可能不同。

例如：

```text
Python 3.8
Python 3.11
Python 3.12
```

如果教程要求 Python 3.11，而你本机实际运行的是 Python 2 或 Python 3.8，就可能出现看不懂的新语法、依赖安装失败或运行结果不同。

检查版本的常见命令：

```bash
python --version
python3 --version
git --version
```

不同电脑上命令结果可能不同。记录真实输出，比猜测更重要。

## 命令位置

终端输入命令后，系统会去一组目录里寻找对应程序。

macOS 或 Linux 可以尝试：

```bash
which python3
which git
```

Windows PowerShell 可以尝试：

```powershell
where.exe python
where.exe git
```

如果系统找不到命令，常见表现是：

```text
command not found
```

或：

```text
'python' is not recognized as an internal or external command
```

这不一定表示软件没有安装，也可能表示系统不知道去哪里找它。

## 环境变量和 PATH

环境变量是一组给程序读取的配置。

PATH 是最常见的环境变量之一。它保存了一串目录，系统会按这些目录去找命令。

可以把 PATH 想成：

```text
当我输入 python3 时，请从这些地方依次找有没有叫 python3 的程序。
```

macOS 或 Linux 查看 PATH：

```bash
echo $PATH
```

Windows PowerShell 查看 PATH：

```powershell
$env:Path
```

本节只要求你知道 PATH 的作用，不要求你手动修改 PATH。随意修改 PATH 可能导致原本能用的命令失效。

## 依赖

依赖是项目运行时需要的外部代码或工具。

例如，一个 Python 项目可能需要：

```text
Python解释器
项目自己的 .py 文件
第三方库
配置文件
数据文件
```

如果缺少第三方库，代码本身没有写错，也可能运行失败。

常见错误可能长这样：

```text
ModuleNotFoundError: No module named 'requests'
```

这表示当前 Python 环境里找不到叫 `requests` 的依赖。

## 虚拟环境

虚拟环境是给某个项目单独准备的一套依赖空间。

它解决的问题是：

```text
项目 A 需要某个库的旧版本
项目 B 需要同一个库的新版本
如果都装在全局环境里，就容易互相影响
```

使用虚拟环境后，可以让不同项目尽量互不干扰。

本节只建立认知，不要求你马上创建虚拟环境。真正的 Python 虚拟环境操作会在 Python 起步学习。

## 示例：记录一次环境检查

你可以在学习记录里写成这样：

````markdown
# 开发环境检查

## Python

命令：

```bash
python3 --version
```

结果：

```text
Python 3.x.x
```

## Git

命令：

```bash
git --version
```

结果：

```text
git version x.x.x
```

## 我的判断

- 我能运行 `python3` 吗：
- 我能运行 `git` 吗：
- 我看到的版本是：
- 我还不确定的问题是：
````

重点不是你的版本一定要和别人一样，而是你能说清楚自己的环境是什么。

## 实践练习

### 练习 1：记录 Python 版本

在终端中尝试：

```bash
python --version
python3 --version
```

需要产出：

```text
`python --version` 的结果是：

`python3 --version` 的结果是：

我的电脑应该优先使用哪个命令：

判断依据是：
```

如果其中一个命令失败，也要记录失败信息。

### 练习 2：记录命令位置

macOS 或 Linux 尝试：

```bash
which python3
which git
```

Windows PowerShell 尝试：

```powershell
where.exe python
where.exe git
```

需要产出：

```text
Python命令位置：

Git命令位置：

我能不能根据这个结果判断系统找到了哪个程序：
```

### 练习 3：解释 PATH

不用修改 PATH，只记录它。

macOS 或 Linux：

```bash
echo $PATH
```

Windows PowerShell：

```powershell
$env:Path
```

需要产出：

```text
PATH看起来像一串什么：

PATH的作用是：

我是否修改了PATH：
```

第三项应写“没有”。本节不要求修改 PATH。

### 练习 4：区分项目组成

看下面这个项目结构：

```text
demo-project/
├── README.md
├── main.py
├── requirements.txt
└── data/
    └── sample.json
```

回答：

```text
项目代码文件是：

说明文档是：

可能记录依赖的文件是：

数据文件是：

运行这个项目可能还需要本机有什么工具：
```

### 练习 5：记录一个环境错误

从你本机或教程中找一个环境相关错误，写成：

```text
我执行的命令：

完整错误信息：

我判断它属于：
- 命令找不到
- 版本不对
- 当前目录不对
- 缺少依赖
- 其他

我的判断依据：
```

不要急着修，先学会把错误描述完整。

## 常见错误与排查

| 错误 | 表现 | 怎么排查 |
| --- | --- | --- |
| 把代码文件当成可直接运行的东西 | 双击文件后没反应或打开编辑器 | 先确认它需要解释器、编译器还是运行时 |
| 混用 `python` 和 `python3` | 同一段代码在不同命令下结果不同 | 分别运行版本检查并记录输出 |
| 只说“环境坏了” | 无法判断问题发生在哪一步 | 记录命令、目录、版本和完整错误 |
| 盲目修改 PATH | 原本能用的命令也失效 | 本节只查看 PATH，不修改 PATH |
| 把依赖装到全局环境 | 后续项目互相影响 | 先理解虚拟环境，后续在 Python 起步练习 |
| 忽略当前目录 | 命令找不到文件或配置 | 先运行 `pwd` 或观察编辑器打开的项目根目录 |

## 完成标准

完成本节需要同时满足：

- 能用自己的话解释解释器、编译器和运行时的区别。
- 能记录 Python 和 Git 的版本检查结果。
- 能记录至少一个命令的位置，或记录找不到命令的错误。
- 能解释 PATH 是系统寻找命令的位置清单。
- 能区分项目代码、依赖、配置和数据。
- 能解释虚拟环境要解决的依赖隔离问题。
- 能用“命令、结果、判断依据”的格式记录一个环境问题。

## 下一步

进入 [Docker最小认知](08-docker-basics.md)。下一节会学习 Docker 解决什么问题，以及镜像、容器、端口、挂载和环境变量的基本含义。
