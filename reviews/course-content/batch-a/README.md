# 课程内容架构样板 · 批次 A

<div class="be-sample-hero be-sample-hero--index" markdown="1">

<span class="be-sample-kicker">独立评审环境 · 不进入正式课程</span>

## 先理解，再一起动手

这一批不是给现有课程换皮，而是在正式迁移前验证一种新的学习节奏：先看见结果并建立心智模型，再通过小例子、复现、主动修改和受控失败获得证据，最后把本课增量放回连续项目。

<div class="be-sample-actions" markdown="1">
[从 VS Code 样板开始](vscode-workspace.md){ .md-button .md-button--primary }
[直接看 Python 样板](python-variables.md){ .md-button }
</div>

</div>

## 本轮要评审什么

<div class="be-sample-card-grid" markdown="1">

<article class="be-sample-card" markdown="1">
### 第一感官

第一屏能否在两分钟内回答：这节课为什么学、最终会得到什么、从哪里开始。
</article>

<article class="be-sample-card" markdown="1">
### 理解与复现

图解和微型例子是否真的降低理解成本；命令、代码和预期输出能否在本地复现。
</article>

<article class="be-sample-card" markdown="1">
### 项目连续性

学习者是否能看见“上一版本—本课增量—保存证据—下一版本”，而不是每课重新开始。
</article>

<article class="be-sample-card" markdown="1">
### 分层深度

新手补给、深入理解和求职训练是否各自清楚，又没有把正文复制成三份。
</article>

</div>

## 四个样板

| 样板 | 要验证的课型 | 核心产出 | 状态 |
| --- | --- | --- | --- |
| [VS Code：打开工作区并验证保存](vscode-workspace.md) | 工具操作 | 一份保存、搜索和终端一致性证据 | 待评审 |
| [Python：变量、类型与输入输出](python-variables.md) | 编程起步 | 个人学习档案 `v0.1` | 待评审 |
| [CS：数据如何在程序中表示](cs-data-representation.md) | CS 概念 | 下标访问与线性扫描轨迹 | 待评审 |
| [学习进度报告器](study-progress-reporter.md) | 项目整合 | `v0.1 → v1.0` 版本线与求职证据 | 待评审 |

## 评审顺序

1. 先看每页第一屏，不向下滚动，判断方向是否清楚。
2. 完成一个微型例子和一次主动修改。
3. 故意触发一个失败，检查页面能否帮助恢复。
4. 打开小码同学，观察推荐问题是否随阅读位置变化。
5. 分别在桌面和手机查看项目版本线、代码和图解。
6. 回到本页记录：保留、修改、删除，以及原因。

!!! info "评审边界"
    这四页使用独立样板配置和语义上下文助教。它们不会进入正式导航、正式搜索或 55 节课程计数，也不代表内容规范和课程生产 Skill 已经更新。

## 本地运行

```bash
.venv/bin/mkdocs serve -f mkdocs.samples.yml -a 127.0.0.1:8766
```

严格构建：

```bash
.venv/bin/mkdocs build --strict -f mkdocs.samples.yml
```

