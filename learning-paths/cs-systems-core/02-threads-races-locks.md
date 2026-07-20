<div class="be-tutor-mount" data-tutor-lesson="cs-systems-02" aria-hidden="true"></div>

<section id="overview-race-result" data-learning-context="overview-race-result" data-context-type="overview" markdown="1">

<div class="be-page-hero" markdown="1">
<span class="be-page-eyebrow">CS 系统基础 · 第二课 · 系统运行观察器 v0.2</span>

# 线程、竞态条件与锁

## 两个线程都加了一次，计数为什么只有 1

```text
without lock: expected=2 actual=1
with lock: expected=2000 actual=2000
```

第一行不是靠运气等一个偶发错误。实验让两个线程先读到同一个旧值，再分别写回，于是其中一次更新被覆盖。第二行把“读取—计算—写回”放进同一把锁，结果才与预期一致。

[复现丢失更新](#reproduce-concurrency-lab){ .md-button }
[看清三步操作](#concept-read-modify-write){ .md-button .md-button--secondary }
</div>

<div class="be-page-summary" markdown="1">
  <div><span>课程位置</span><strong>CS 系统基础 · 2 / 6</strong></div>
  <div><span>项目版本</span><strong>系统运行观察器 v0.2</strong></div>
  <div><span>主要结果</span><strong>共享状态、竞态、临界区、Lock</strong></div>
</div>

## 这节适合谁

- **小白**：先把两个线程想成两个人同时改一张纸；按顺序看读、等、写三步。
- **已有基础**：直接做跳过检查——能稳定复现 lost update；锁住完整读改写；不会把 GIL 当作业务同步保证；测试能覆盖空任务。都做到，可以等待下一课。
- **兴趣学习**：把线程数和更新次数换成自己的数据，观察锁保护前后的区别。
- **求职准备**：额外画出一次交错顺序，解释竞态、临界区、互斥和锁粒度。

四类画像共用系统运行观察器 v0.2。求职路线增加故障图和追问，但不会另复制一套线程课程。

前置是[程序、进程与退出状态](01-program-process-exit-status.md)。本课只讲共享状态与互斥，不把线程等同于并行，也不做真实性能结论。

</section>

<section id="concept-read-modify-write" data-learning-context="concept-read-modify-write" data-context-type="concept" markdown="1">

## `counter += 1` 里面不只一步

先忽略 Python 语法，把一次增加拆开：

```text
线程 A：读到 0 ───────────── 写回 1
线程 B：       读到 0 ────── 写回 1

两次工作完成，最后仍是 1
```

问题不在“加法算错”，而在结果取决于两个线程的交错顺序。只要多个执行单元共享可变状态，而且至少一个会写，就必须明确谁可以在什么时候修改。

发生读改写的代码区域叫临界区。互斥锁保证同一时刻只有一个线程进入这段区域；它保护的是不变量，不是某一行看起来像不像原子操作。

</section>

<section id="example-forced-interleaving" data-learning-context="example-forced-interleaving" data-context-type="example" markdown="1">

## 用 Barrier 固定交错，不靠“多跑几次看看”

失败实验先让两个线程都完成读取，再允许它们写回：

```python
snapshot = counter["value"]
both_have_read.wait()
counter["value"] = snapshot + 1
```

`Barrier(2)` 要等两个线程都到达。于是两份 `snapshot` 必然都是 `0`，两个线程最后都写 `1`。这个安排让测试每次都能解释同一个失败，不依赖调度器刚好在某一行切换。

Barrier 只用来搭建教学实验，它不是这个计数器的修复方案。

</section>

<section id="example-lock-critical-section" data-learning-context="example-lock-critical-section" data-context-type="example" markdown="1">

## 锁要包住完整的不变量

修复后的代码是：

```python
with lock:
    counter["value"] += 1
```

`with lock` 进入时获取锁，离开时释放。即使临界区抛出异常，上下文管理也会执行释放路径。

不要把读取放在锁外、只锁最后的写入：

```python
snapshot = counter["value"]  # 仍可能同时读到旧值
with lock:
    counter["value"] = snapshot + 1
```

这段代码看起来“用了锁”，但没有保护读取与写回之间的关系，lost update 仍然存在。

</section>

<section id="reproduce-concurrency-lab" data-learning-context="reproduce-concurrency-lab" data-context-type="reproduce" markdown="1">

## 先看错一次，再看锁修好它

完整示例在 `site-src/examples/cs-systems/runtime-observer-v02/`。

```bash
cd site-src/examples/cs-systems/runtime-observer-v02
python concurrency_lab.py
python -m unittest -v test_concurrency_lab.py
```

你应该看到两行固定输出和 3 项测试通过：

- Barrier 固定交错后，期望 2，实际 1。
- 2 个线程各加 1000 次，锁保护后得到 2000。
- 0 个线程时结果是 0，空工作量没有被当成错误。

这里没有用运行时间比较“加锁快不快”。线程调度、机器负载和 Python 实现都会影响耗时；本课先证明正确性。

</section>

<section id="modify-counter-invariant" data-learning-context="modify-counter-invariant" data-context-type="modify" markdown="1">

## 给计数器再加一个不变量

把共享状态改成：

```python
{"completed": 0, "remaining": 2000}
```

每次更新同时执行 `completed += 1` 和 `remaining -= 1`，始终满足两者之和为 2000。

先故意只锁其中一项，写测试证明不变量可能被破坏；再用同一把锁保护两项更新和检查。不要给两个字段各配一把互不相关的锁，那会让调用者看到只完成一半的状态。

</section>

<section id="troubleshoot-thread-lock" data-learning-context="troubleshoot-thread-lock" data-context-type="troubleshoot" markdown="1">

## 并发问题难查，是因为一次成功不能证明安全

| 看到什么 | 先查哪里 | 怎样回来 |
| --- | --- | --- |
| 计数偶尔变少 | 是否存在共享读改写 | 把交错顺序画出来，再确定临界区 |
| 已经写了 Lock 仍丢更新 | 读取是否还在锁外 | 用同一把锁包住完整读改写 |
| 程序永远等着 | 是否在持锁时等待另一个也需要这把锁的线程 | 缩小等待关系，设置超时并记录锁顺序 |
| 主线程先打印了旧结果 | 是否忘记 `join()` | 等所有工作线程结束后再验收结果 |
| 多跑几次都正确 | 测试是否没有固定交错 | 用 Barrier 或事件构造确定性的错误顺序 |
| 以为有 GIL 就不用锁 | 业务不变量是否跨多个操作 | 按共享状态和不变量决定同步，不依赖解释器偶然行为 |
| 加锁后结果对但程序很慢 | 临界区是否包含无关 I/O 或长计算 | 先保证正确，再缩小锁内工作；用测量而不是猜测优化 |

</section>

<section id="project-runtime-observer-v02" data-learning-context="project-runtime-observer-v02" data-context-type="project" markdown="1">

## 系统运行观察器 v0.2

v0.1 观察独立子进程怎样结束，v0.2 增加同一进程内的共享状态实验：

| v0.1 | v0.2 新增 | 后续继续 |
| --- | --- | --- |
| PID、父子关系 | 两个线程共享计数 | 内存和文件资源 |
| stdout、stderr、退出码 | 确定性 lost update | 本机 TCP 与 HTTP |
| 超时与失败分类 | Lock 保护临界区 | 事务、隔离与权限 |

保存两行实验输出、3 项测试、一次交错顺序图和你新增的双字段不变量。它们可以证明你没有只会调用 `Thread`，而是能先复现错误，再说明锁保护了什么。

</section>

<section id="deepen-gil-and-parallelism" data-learning-context="deepen-gil-and-parallelism" data-context-type="deepen" markdown="1">

## GIL 没有替你设计共享状态

在常见 CPython 3.11 中，GIL 限制同一时刻执行 Python 字节码的线程数量，但线程仍会在多个操作之间切换，I/O 期间也会释放执行机会。它不能替代业务层的锁、队列或不可变数据设计。

线程适合许多 I/O 并发任务，不等于让纯 Python 计算自动用满多个 CPU 核。后续系统工程课程还会比较进程、线程、异步任务和工作队列；本课只把共享状态的正确性做清楚。

</section>

<section id="career-explain-race" data-learning-context="career-explain-race" data-context-type="career" markdown="1">

## 求职加练：别只说“加锁就好了”

一份更完整的回答应该包含：

1. 共享状态和不变量是什么。
2. 哪两次操作可以交错，怎样出现错误结果。
3. 临界区从哪里开始、在哪里结束。
4. 为什么同一把锁能保护它，锁太大又会有什么代价。
5. 测试怎样稳定复现旧错误并防止回归。

如果问题扩大到多个进程或多台机器，`threading.Lock` 就不再覆盖全部参与者。那时需要数据库事务、分布式协调或重新设计所有权；不要把本课结论无限外推。

</section>

## 完成检查

- [ ] 我能画出两个线程怎样把 2 次更新写成 1。
- [ ] 我能解释 Barrier 为什么只负责固定实验顺序。
- [ ] 我把锁放在完整读改写周围，而不只包最后一行。
- [ ] 我等待线程结束后再检查结果。
- [ ] 我新增了双字段不变量，并用测试固定旧错误和修复。
- [ ] 我不会把 GIL 说成自动保证线程安全或多核并行。

## 来源与版本

- 适用：Python 3.11+；示例用于线程共享状态入门，不代表其他语言或自由线程 Python 的完整内存模型。
- 本课在 Python 3.11.9 与 Node.js 24.14.1 驱动的仓库验证脚本中复现；核查日期：2026-07-20。
- Python 官方：[threading：Thread、join 与 Lock](https://docs.python.org/3.11/library/threading.html)。
- Python 官方：[Lock 作为上下文管理器](https://docs.python.org/3.11/library/threading.html#using-locks-conditions-and-semaphores-in-the-with-statement)。
- Python 官方：[queue：线程安全的任务交换](https://docs.python.org/3.11/library/queue.html)。
- 验证方式：3 项 unittest、固定命令输出、课程根验证脚本；不访问网络，不以耗时作为正确性依据。

## 下一步

进入[内存、文件与资源生命周期](03-memory-file-resource-lifecycle.md)。下一课会把视线从线程共享变量移到对象、文件句柄和确定性释放。
