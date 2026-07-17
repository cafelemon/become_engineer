# 课程内容架构样板 · 批次 A

<div class="be-sample-hero be-sample-hero--index" markdown="1">

<span class="be-sample-kicker">独立评审环境 · 不进入正式课程</span>

## 四节还在试讲的课

你可以把这里当成一个小型试听区。四个样板都从看得见的结果开始，概念讲到够用就停，紧接着运行、修改和排错。做完以后，刚学的东西还会留在同一个项目里，下一课接着用。

<div class="be-sample-actions" markdown="1">
[从 VS Code 样板开始](vscode-workspace.md){ .md-button .md-button--primary }
[直接看 Python 样板](python-variables.md){ .md-button }
</div>

</div>

## 阅读时帮我们留意四件事

<div class="be-sample-card-grid" markdown="1">

<article class="be-sample-card" markdown="1">
### 能不能很快进入状态

只看第一屏，能不能知道这节课要做什么、从哪里开始。
</article>

<article class="be-sample-card" markdown="1">
### 讲解能不能跟着做

图和小例子看得懂吗？页面里的命令、代码和输出能不能在自己的电脑上跑出来？
</article>

<article class="be-sample-card" markdown="1">
### 前后课程能不能接起来

学完一课后，能不能看出项目多了什么，以及下一课会接着解决什么问题。
</article>

<article class="be-sample-card" markdown="1">
### 深浅是否合适

新手说明够不够细，深入和求职部分有没有真正增加内容，而不是换种说法再讲一遍。
</article>

</div>

## 四个样板

| 样板 | 要验证的课型 | 核心产出 | 状态 |
| --- | --- | --- | --- |
| [VS Code：打开工作区并验证保存](vscode-workspace.md) | 工具操作 | 保存文件，并从搜索和终端再次找到它 | 已验收 |
| [Python：变量、类型与输入输出](python-variables.md) | 编程起步 | 个人学习档案 `v0.1` | 已验收 |
| [CS：数据如何在程序中表示](cs-data-representation.md) | CS 概念 | 下标访问与线性扫描轨迹 | 已验收 |
| [学习进度报告器](study-progress-reporter.md) | 项目整合 | `v0.1 → v1.0` 的成长过程与项目讲法 | 已验收 |

## 评审顺序

1. 每页先只看第一屏，看看自己是否知道接下来该做什么。
2. 跟着跑一个小例子，再把它改成自己的内容。
3. 故意试错一次，看看页面能不能帮你找到原因。
4. 打开小码同学，试试当前推荐的问题是否有用。
5. 分别用电脑和手机看看代码、图解和项目版本线。
6. 最后记下哪些地方想保留，哪些地方读着别扭，以及原因。

!!! info "评审边界"
    这四页只用于试听和评审，不会出现在正式课程导航和搜索里。目前的内容规范与课程生产 Skill 也还没有跟着改变。

## 本地运行

```bash
.venv/bin/mkdocs serve -f mkdocs.samples.yml -a 127.0.0.1:8766
```

严格构建：

```bash
.venv/bin/mkdocs build --strict -f mkdocs.samples.yml
```
