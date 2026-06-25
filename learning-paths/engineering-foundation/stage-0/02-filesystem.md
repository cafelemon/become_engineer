# 02 文件系统

## 前置知识

- 已完成 [01 学习方法](01-learning-method.md)。
- 能写一份包含目标、操作、结果、问题和下一步的学习记录。

## 学习目标

学完本单元后，你应该能解释文件、目录、扩展名、项目根目录、相对路径和绝对路径，并能判断一个文件应该放在项目的哪个位置。

本单元不讲终端命令。你只需要先把“文件在哪里”这件事想清楚。

## 核心概念

### 文件

文件是电脑里保存内容的基本单位。比如：

```text
README.md
notes.txt
main.py
photo.png
```

文件名通常由两部分组成：

```text
名字.扩展名
```

例如 `README.md` 中：

- `README` 是名字。
- `.md` 是扩展名。

扩展名常用来提示文件类型：

| 扩展名 | 常见含义 |
| --- | --- |
| `.md` | Markdown 文档 |
| `.txt` | 普通文本 |
| `.py` | Python 代码 |
| `.json` | JSON 数据 |
| `.png` | 图片 |

扩展名不是绝对保证，但它是阅读项目时的重要线索。

### 目录

目录也常被叫做文件夹。它用来组织文件和其他目录。

一个项目可能长这样：

```text
become_engineer/
├── README.md
├── docs/
│   └── 00_overview.md
└── learning-paths/
    └── engineering-foundation/
```

这里：

- `become_engineer/` 是一个目录。
- `README.md` 是一个文件。
- `docs/` 是一个目录。
- `00_overview.md` 是 `docs/` 目录里的文件。

结尾带 `/` 的名字通常表示目录，比如 `docs/`。不带 `/` 且带扩展名的名字通常表示文件，比如 `README.md`。

### 项目根目录

项目根目录是一个项目最外层的目录。

在上面的例子中：

```text
become_engineer/
```

就是项目根目录。

很多说明文档会说“在项目根目录下创建文件”。意思是在项目最外层创建，而不是随便找一个子目录。

### 路径

路径用来描述文件或目录的位置。

例如：

```text
docs/00_overview.md
```

它表示：

```text
docs 目录里的 00_overview.md 文件
```

再看一个更深的例子：

```text
learning-paths/engineering-foundation/stage-0/02-filesystem.md
```

它表示：

```text
learning-paths 目录
  -> engineering-foundation 目录
    -> stage-0 目录
      -> 02-filesystem.md 文件
```

### 绝对路径

绝对路径从电脑里的固定起点开始描述位置。

macOS 或 Linux 上常见长这样：

```text
/Users/your-name/Desktop/become_engineer/README.md
```

Windows 上常见长这样：

```text
C:\Users\your-name\Desktop\become_engineer\README.md
```

绝对路径的特点是：不管你现在在哪个目录，它都能从系统固定起点找到目标。

公开文档中通常不写个人电脑上的绝对路径，因为它会暴露私人路径，也不适合别人复用。

### 相对路径

相对路径从“当前位置”开始描述位置。

如果当前位置是项目根目录 `become_engineer/`，那么：

```text
README.md
docs/00_overview.md
learning-paths/engineering-foundation/README.md
```

都是相对路径。

相对路径的特点是：它依赖当前位置。当前位置变了，同一个相对路径可能指向不同位置，或者找不到目标。

## 学习顺序

1. 先区分文件和目录。
2. 再看扩展名，判断文件大概是什么类型。
3. 找到项目根目录。
4. 用路径描述一个文件的位置。
5. 判断路径是绝对路径还是相对路径。

## 示例：读懂一个项目结构

看到这个结构：

```text
my-project/
├── README.md
├── notes/
│   └── day-1.md
└── data/
    └── sample.json
```

可以这样解释：

- 项目根目录是 `my-project/`。
- `README.md` 在项目根目录下。
- `day-1.md` 在 `notes/` 目录下。
- `sample.json` 在 `data/` 目录下。
- `notes/day-1.md` 是从项目根目录出发的相对路径。

## 实践练习

### 练习 1：标出文件和目录

看下面的结构，写出哪些是目录，哪些是文件。

```text
study-demo/
├── README.md
├── docs/
│   └── plan.md
├── notes/
│   └── stage-0.md
└── data/
    └── example.json
```

需要产出：

```text
目录：
- 

文件：
- 
```

### 练习 2：写出路径含义

解释下面三个路径分别表示什么。

```text
README.md
docs/plan.md
notes/stage-0.md
```

需要写成类似这样：

```text
docs/plan.md 表示 docs 目录里的 plan.md 文件。
```

### 练习 3：判断相对路径和绝对路径

判断下面哪些是相对路径，哪些是绝对路径。

```text
README.md
docs/00_overview.md
/Users/your-name/Desktop/become_engineer/README.md
C:\Users\your-name\Desktop\become_engineer\README.md
learning-paths/engineering-foundation/README.md
```

需要产出：

```text
相对路径：
- 

绝对路径：
- 
```

### 练习 4：设计一个学习目录

设计一个自己的学习目录结构，至少包含：

- 一个项目根目录。
- 一个 `README.md`。
- 一个放学习记录的目录。
- 一个放资料索引的目录。

示例格式：

```text
my-learning/
├── README.md
├── notes/
│   └── stage-0.md
└── resources/
    └── index.md
```

## 常见错误与排查

| 错误 | 表现 | 怎么排查 |
| --- | --- | --- |
| 分不清文件和目录 | 把 `docs/` 当成文件，或把 `README.md` 当成目录 | 看是否带 `/`，再看是否有扩展名 |
| 不知道项目根目录 | 文件随便放，后面找不到 | 找最外层项目目录，通常里面有 `README.md` |
| 把绝对路径写进公开文档 | 文档里出现自己的电脑用户名或桌面路径 | 改成从项目根目录出发的相对路径 |
| 相对路径依赖当前位置 | 同一个路径在不同位置解释不同 | 先说清“当前位置是哪里” |
| 只看文件名不看扩展名 | 不知道文件大概是什么类型 | 先看 `.md`、`.py`、`.json` 等后缀 |

## 完成标准

完成本单元需要同时满足：

- 能说清文件、目录和扩展名的区别。
- 能指出一个项目结构中的项目根目录。
- 能解释至少 3 个路径的含义。
- 能区分相对路径和绝对路径。
- 能设计一个简单学习目录结构，并说明每个目录的用途。

## 下一步

进入 [03 终端与 Shell](03-terminal-shell.md)。下一单元会开始用命令进入目录、查看文件和运行简单命令。
