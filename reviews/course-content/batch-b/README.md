# 课程内容架构样板 · 批次 B

<div class="be-sample-hero be-sample-hero--index" markdown="1">

<span class="be-sample-kicker">系统、算法与设备方向 · 独立评审环境</span>

## 五节课，三条连续作品线

这一批开始碰编译器、内存、图算法和硬件事件。页面不会先扔出一串任务，而是从一段输出、一张图或一个具体问题讲起。看明白以后，再在本地把代码跑起来。

<div class="be-sample-actions" markdown="1">
[从 C++ 起步开始](cpp-build.md){ .md-button .md-button--primary }
[直接看 GPIO 样板](gpio-interrupts.md){ .md-button }
</div>

</div>

## 这一批怎样连起来

<div class="be-sample-card-grid" markdown="1">

<article class="be-sample-card" markdown="1">
### 学习进度报告器

C++ 起步先得到一个可执行程序；RAII 再让它安全地写出审计文件。
</article>

<article class="be-sample-card" markdown="1">
### 设备事件记录器

C 起步先打印一条模拟按键事件；GPIO 样板再把电平、边沿和中断处理接进来。
</article>

<article class="be-sample-card" markdown="1">
### 可追踪图遍历实验

BFS 用同一张小图记录队列、距离和父节点，继续连接现有双语言 CS 实验。
</article>

<article class="be-sample-card" markdown="1">
### 仿真到哪里为止

设备样板只验证程序逻辑。引脚复用、电气特性、真实中断时序和并发问题，必须留到真机课程。
</article>

</div>

## 五个样板

| 样板 | 读完以后能做什么 | 连续作品 | 状态 |
| --- | --- | --- | --- |
| [C++：源码怎样变成程序](cpp-build.md) | 独立编译并运行一个 C++20 小程序 | 学习进度报告器 | 已验收 |
| [C：变量、内存与第一次编译](c-memory.md) | 编译并修改一条设备事件 | 设备事件记录器 v0.1 | 已验收 |
| [BFS：无权图中的最少步数](bfs-shortest-path.md) | 手工追踪队列并恢复一条最短路径 | 可追踪图遍历实验 | 已验收 |
| [对象生命周期与 RAII](cpp-raii.md) | 看懂作用域，并让文件自动关闭 | 学习进度报告器审计导出 | 已验收 |
| [GPIO、中断与设备事件](gpio-interrupts.md) | 追踪一次按键事件从边沿到主循环 | 设备事件记录器 v0.2 | 已验收 |

## 阅读时帮我们留意

1. 第一屏是否让你愿意继续读，而不是先被术语挡住。
2. 图、小例子和命令能不能把抽象概念接起来。
3. 编译或运行失败时，页面有没有告诉你该看哪里。
4. 项目前后两节是否真的在演进同一份成果。
5. GPIO 页面有没有把仿真与真机说清楚。
6. 小码的问题听起来是否像学习者会问的话。

!!! info "评审说明"
    这五页已通过用户评审并冻结，不进入正式课程导航和搜索，也不增加正式课程数量。后续改动只在跨方向统一评审后按新规范迁移。

## 本地运行

```bash
.venv/bin/mkdocs serve -f mkdocs.samples-b.yml -a 127.0.0.1:8767
```

严格构建：

```bash
.venv/bin/mkdocs build --strict -f mkdocs.samples-b.yml
```
