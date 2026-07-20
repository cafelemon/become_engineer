<div class="be-tutor-mount" data-tutor-lesson="cs-systems-01" aria-hidden="true"></div>

<section id="overview-process-result" data-learning-context="overview-process-result" data-context-type="overview" markdown="1">

<div class="be-page-hero" markdown="1">
<span class="be-page-eyebrow">CS 系统基础 · 第一课 · 系统运行观察器 v0.1</span>

# 程序、进程与退出状态

## 同一段代码启动三次，结果并不只在屏幕上

```text
success: exit=0 child_different=True parent_matches=True
failure: exit=7 stderr=simulated worker failure
timeout: timed_out=True
```

第一行正常结束，第二行明确失败，第三行在期限内没有结束。调用者不能只看“有没有打印内容”，还要同时读标准输出、标准错误、退出状态和超时。

[运行观察器](#reproduce-runtime-observer){ .md-button }
[先看程序和进程的区别](#concept-program-process){ .md-button .md-button--secondary }
</div>

<div class="be-page-summary" markdown="1">
  <div><span>课程位置</span><strong>CS 系统基础 · 1 / 6</strong></div>
  <div><span>项目版本</span><strong>系统运行观察器 v0.1</strong></div>
  <div><span>主要结果</span><strong>子进程、输出流、退出码、超时</strong></div>
</div>

## 这节适合谁

- **小白**：按顺序做。你只需要会运行 Python 文件，不必提前懂操作系统术语。
- **已有基础**：直接做跳过检查——不用 `shell=True` 启动子进程；能区分 stdout、stderr、非零退出和超时；测试能证明父子 PID 关系。都做到，可以进入下一课。
- **兴趣学习**：把 worker 改成自己常用的小脚本，观察它怎样结束。
- **求职准备**：额外保存一次非零退出和一次超时复盘，练习解释“进程挂了”和“进程还没结束”的区别。

四类画像共用同一份系统运行观察器。小白获得可重复的第一次观察，已有基础者用失败分支检查理解，求职画像再补故障表达。

前置是 [CS 起步](../cs-core/README.md) 和 Python 的异常、测试基础。本课不要求 C/C++，也不会从系统调用手册开始背概念。

</section>

<section id="concept-program-process" data-learning-context="concept-program-process" data-context-type="concept" markdown="1">

## 程序是文件，进程是一次正在运行的实例

`worker.py` 放在磁盘上时是一份程序。Python 解释器加载它、操作系统分配进程标识和资源后，才有一个正在运行的进程。

```text
observer.py（程序文件）
       │ Python 进程，PID 41000
       │ subprocess.run([...])
       ▼
worker.py（程序文件）
       └─ 新的 Python 进程，PID 41001，父 PID 41000
```

同一份 `worker.py` 可以同时启动多次，每次都有自己的 PID、退出状态和运行时间。PID 只是当前系统用来识别进程的编号，会变化，也可能在以后被复用；不要把它当成永久业务 ID。

</section>

<section id="example-streams-and-exit" data-learning-context="example-streams-and-exit" data-context-type="example" markdown="1">

## stdout 说结果，stderr 说问题，退出码给调用者判断

观察器没有拼一条 Shell 字符串，而是把命令和参数逐项传给 `subprocess.run()`：

```python
completed = subprocess.run(
    [sys.executable, str(WORKER), "--mode", mode],
    capture_output=True,
    text=True,
    timeout=timeout,
    check=False,
)
```

- `stdout` 适合机器要继续处理的正常结果。
- `stderr` 适合诊断信息；失败时不要把它悄悄丢掉。
- `returncode == 0` 通常表示成功，非零值表示程序按自己的约定报告失败。
- `timeout` 到期表示调用者不再愿意等，不等同于 worker 主动返回某个失败码。

`check=False` 让观察器自己记录非零退出；如果换成 `check=True`，非零退出会变成 `CalledProcessError`。两种方式都可以，关键是调用者必须明确处理。

</section>

<section id="reproduce-runtime-observer" data-learning-context="reproduce-runtime-observer" data-context-type="reproduce" markdown="1">

## 跑三条不同的结束路径

完整示例在 `site-src/examples/cs-systems/runtime-observer-v01/`，只使用 Python 3.11 标准库。

```bash
cd site-src/examples/cs-systems/runtime-observer-v01
python observer.py
python -m unittest -v test_observer.py
```

你应该看到开头的三行固定结果，以及 3 项测试通过。PID 本身没有写进固定输出，测试检查的是关系：子进程 PID 与父进程不同，worker 报告的父 PID 与 observer 一致。

打开 `worker.py`，你会看到三种模式：

1. `success` 打印 JSON，返回 `0`。
2. `fail` 把诊断写到 stderr，返回 `7`。
3. `sleep` 睡眠两秒；观察器只等 0.05 秒，因此进入超时分支。

</section>

<section id="modify-worker-mode" data-learning-context="modify-worker-mode" data-context-type="modify" markdown="1">

## 加一种结束方式

给 worker 增加 `--mode invalid-input`：

- stderr 写 `invalid input`。
- 返回码使用 `2`。
- `observer.py` 展示它，但不要把失败改成成功。
- 增加测试，证明 stderr 和退出码都被保留。

再把超时时间从 `0.05` 改成 `3` 秒，先写下你认为 `sleep` 会出现什么结果，再运行验证。这里要观察的是“调用者等待多久”怎样改变结果分类，而不是比较机器性能。

</section>

<section id="troubleshoot-subprocess" data-learning-context="troubleshoot-subprocess" data-context-type="troubleshoot" markdown="1">

## 子进程不对时，先看它有没有启动

| 看到什么 | 先查哪里 | 怎样回来 |
| --- | --- | --- |
| `FileNotFoundError` | 命令或 worker 路径 | 使用 `sys.executable` 和由 `__file__` 计算出的绝对路径 |
| 退出码非零但没有异常 | `check=False` 与 stderr | 读取 `returncode` 和 stderr，不要只看 stdout |
| `CalledProcessError` | 是否使用 `check=True` | 从异常读取退出码、stdout 和 stderr |
| 一直卡住 | 是否设置 timeout，输出是否可能塞满管道 | 优先使用 `subprocess.run()` 或 `communicate()`，给外部程序明确期限 |
| Windows 能跑，Shell 命令换平台就失败 | 是否依赖 Bash 字符串 | 传参数列表，不为这节课开启 `shell=True` |
| 测试偶尔只差 PID | 是否把动态 PID 写进固定快照 | 检查父子关系，不断言某个具体数字 |

</section>

<section id="project-runtime-observer-v01" data-learning-context="project-runtime-observer-v01" data-context-type="project" markdown="1">

## 系统运行观察器 v0.1

这版项目已经能保存四类事实：启动了谁、正常输出了什么、失败诊断是什么、最后怎样结束。

| 现在已经能证明 | 还不能证明 |
| --- | --- |
| 父进程启动了独立子进程 | 两个进程如何共享或隔离内存 |
| 成功与非零退出没有混在一起 | 多个执行单元同时修改数据是否安全 |
| stderr 没有被 stdout 掩盖 | 网络连接和数据库事务怎样工作 |
| 超时有单独状态 | 生产系统的重启、监控与容量 |

保存 `observer.py` 的输出和 3 项测试结果。下一课会让一个进程里的两个线程同时修改计数，观察为什么“都执行了”仍可能少一次更新。

</section>

<section id="deepen-process-boundary" data-learning-context="deepen-process-boundary" data-context-type="deepen" markdown="1">

## 为什么这节不直接教 fork

POSIX 系统可以用 `fork`、`exec` 和 `wait` 解释进程创建，Windows 的进程创建接口并不是同一套模型。Python 的 `subprocess` 提供了更适合跨平台入门的共同边界：传参数、收输出、等结束、读退出码。

系统工程方向后面会回到平台接口、信号、进程组和文件描述符。本课先把调用者真正需要处理的结果做完整，避免把“记住一个 Unix 调用序列”误当成已经会管理进程。

</section>

<section id="career-process-failure" data-learning-context="career-process-failure" data-context-type="career" markdown="1">

## 求职加练：进程失败和超时有什么不同

试着不用“程序挂了”概括所有问题：

- 没启动成功时，调用者连子进程都没有得到。
- 非零退出表示进程已经结束，并主动给出失败状态。
- 超时表示期限到了；调用者需要结束并回收子进程，不能假定它已经自己退出。
- stdout 有内容也不代表成功，最终还要看退出状态和业务协议。

可以按“现象 → 状态 → 诊断信息 → 清理 → 测试”来讲本课项目。不要声称做了进程监控平台；你完成的是一个小而完整的子进程边界。

</section>

## 完成检查

- [ ] 我能用自己的话区分程序文件和进程实例。
- [ ] 我能解释 PID 为什么不能当永久业务标识。
- [ ] 我能分别处理 stdout、stderr、非零退出和超时。
- [ ] 我用参数列表启动 worker，没有为了方便开启 `shell=True`。
- [ ] 我新增了一种失败方式，并用测试固定退出码和诊断。
- [ ] 我知道这节课还没有覆盖共享内存、信号和生产监控。

## 来源与版本

- 适用：Python 3.11+，Windows、macOS 与常见 Linux 环境。
- 本课在 Python 3.11.9 与 Node.js 24.14.1 驱动的仓库验证脚本中复现；核查日期：2026-07-20。
- Python 官方：[subprocess：创建进程、收集输出、退出码与超时](https://docs.python.org/3.11/library/subprocess.html)。
- Python 官方：[os.getpid() 与 os.getppid()](https://docs.python.org/3.11/library/os.html#os.getpid)。
- POSIX 参考：[_Exit 与进程结束状态](https://pubs.opengroup.org/onlinepubs/9799919799/functions/_exit.html)。
- 验证方式：3 项 unittest、固定命令输出、课程根验证脚本；不访问网络，不安装第三方包。

## 下一步

进入[线程、竞态条件与锁](02-threads-races-locks.md)。下一课仍使用 Python 标准库，但关注点从“一个子进程怎样结束”变成“同一进程里的两个线程怎样共享数据”。
