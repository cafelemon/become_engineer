<div class="be-tutor-mount" data-tutor-lesson="cs-systems-03" aria-hidden="true"></div>

<section id="overview-resource-result" data-learning-context="overview-resource-result" data-context-type="overview" markdown="1">

<div class="be-page-hero" markdown="1">
<span class="be-page-eyebrow">CS 系统基础 · 第三课 · 系统运行观察器 v0.3</span>

# 内存、文件与资源生命周期

## 变量删掉了，资源就一定释放了吗

```text
memory: retained=True released=True traced_drop=True
file: open_inside=True closed_outside=True
failure: closed_after_error=True
temporary: removed=True
```

第一行说明删除一个变量名后，别名仍能让对象活着；最后一个强引用消失后，弱引用才观察到对象结束。后面三行证明文件和临时目录在正常、异常路径都按明确边界清理。

[运行资源实验](#reproduce-resource-lab){ .md-button }
[先看生命周期](#concept-reference-lifecycle){ .md-button .md-button--secondary }
</div>

<div class="be-page-summary" markdown="1">
  <div><span>课程位置</span><strong>CS 系统基础 · 3 / 6</strong></div>
  <div><span>项目版本</span><strong>系统运行观察器 v0.3</strong></div>
  <div><span>主要结果</span><strong>引用、分配追踪、文件关闭、异常清理</strong></div>
</div>

## 这节适合谁

- **小白**：把对象想成仓库里的箱子，变量名只是指向箱子的标签；先跟着引用图走一遍。
- **已有基础**：直接做跳过检查——能区分变量、对象和资源；能解释 `with` 为什么覆盖异常路径；不会把 `tracemalloc` 当作 RSS。都做到，可以进入下一课。
- **兴趣学习**：把载荷大小和临时文件内容换成自己的数据，观察结论是否保持。
- **求职准备**：保存一张所有权图和一次异常清理测试，练习解释文件描述符泄漏怎样发生。

四类画像共用系统运行观察器 v0.3。求职路线增加资源责任和故障追问，不另外复制一套内存课程。

前置是[线程、竞态条件与锁](02-threads-races-locks.md)。本课使用 Python 对象和文件建立共同认识，不替代 C/C++ 的地址、指针和 RAII 深化。

</section>

<section id="concept-reference-lifecycle" data-learning-context="concept-reference-lifecycle" data-context-type="concept" markdown="1">

## 生命周期看的是对象和资源，不只是变量名

```text
payload ─┐
         ├──> Payload 对象 ───> 1 MB bytearray
alias ───┘

删除 payload：对象仍被 alias 保留
删除 alias：最后一个强引用消失，弱引用不负责保活
```

变量名、Python 对象和对象管理的外部资源是三层不同的东西。删除一个名字，只是去掉一条引用；文件对象即使仍在内存中，也可能已经关闭了操作系统文件句柄。

最稳妥的做法不是猜垃圾回收何时运行，而是让资源所有者拥有明确的进入和退出边界。文件、锁、数据库连接和 socket 都适合用上下文管理器表达这种责任。

</section>

<section id="example-memory-trace" data-learning-context="example-memory-trace" data-context-type="example" markdown="1">

## 弱引用看存活，tracemalloc 看 Python 分配

示例创建一个装有 `bytearray` 的 `Payload`，再保留一个别名：

```python
payload = Payload(bytearray(size))
observer = weakref.ref(payload)
alias = payload
del payload
```

此时 `observer()` 仍能取回对象，因为 `alias` 是强引用。删除 `alias` 并执行一次 `gc.collect()` 后，弱引用返回 `None`；同时 `tracemalloc` 的当前追踪值应低于持有大对象时的值。

这里测到的是 Python 分配器追踪的内存块，不等于操作系统 RSS 一定立刻下降。解释结果时只使用“对象是否存活”和“追踪值是否回落”，不把字节数写成跨机器固定答案。

</section>

<section id="example-file-context" data-learning-context="example-file-context" data-context-type="example" markdown="1">

## with 把关闭责任放在一个清楚的出口

```python
with path.open("w+", encoding="utf-8") as handle:
    handle.write("runtime observer\n")
    handle.seek(0)
    content = handle.read()
```

进入 `with` 后文件处于打开状态；离开代码块时，无论是正常结束还是抛出异常，`__exit__` 都负责关闭文件。关闭后再读取会得到 `ValueError`，这比悄悄继续使用失效资源更容易定位。

Python 文件对象包装了更底层的系统句柄。对象、句柄和磁盘文件不是同一个东西：关闭句柄不会删除磁盘文件，删除目录也不等于仍打开的句柄在所有平台都能继续使用。

</section>

<section id="reproduce-resource-lab" data-learning-context="reproduce-resource-lab" data-context-type="reproduce" markdown="1">

## 跑完四条释放路径

完整示例在 `site-src/examples/cs-systems/runtime-observer-v03/`，只使用 Python 3.11 标准库。

```bash
cd site-src/examples/cs-systems/runtime-observer-v03
python resource_lifecycle.py
python -m unittest -v test_resource_lifecycle.py
```

你应该看到页面开头的四行固定结果和 4 项测试通过。测试不比较某个固定内存字节数，也不读取平台专用的文件描述符计数，因此 Windows、macOS 和常见 Linux 可以验证同一组生命周期关系。

</section>

<section id="modify-resource-owner" data-learning-context="modify-resource-owner" data-context-type="modify" markdown="1">

## 给资源再加一层所有者

新增 `TraceWriter` 上下文管理器，让它在进入时打开文件、退出时写入一行 `closed by TraceWriter` 后关闭。先完成正常路径测试，再让代码块主动抛出 `RuntimeError`，确认文件仍然关闭。

然后把 `Payload` 大小改成 2 MB。运行前先预测：弱引用结论会不会变化，`tracemalloc` 的具体数字能不能继续当固定输出。正确修改不应把动态字节数写进快照。

</section>

<section id="troubleshoot-resource-lifecycle" data-learning-context="troubleshoot-resource-lifecycle" data-context-type="troubleshoot" markdown="1">

## 资源问题先找最后一个所有者

| 看到什么 | 先查哪里 | 怎样回来 |
| --- | --- | --- |
| `ValueError: I/O operation on closed file` | 是否在 `with` 外继续使用句柄 | 在作用域内完成读写，或返回数据而不是返回已关闭句柄 |
| 文件偶尔没有完整写入 | 是否依赖进程结束时隐式关闭 | 用 `with`，需要持久化时明确 flush、fsync 与错误处理边界 |
| 打开很多文件后报资源不足 | 哪条异常路径没有 close | 用上下文管理器，并用测试走过异常分支 |
| 删除变量后弱引用仍存活 | 是否还有容器、闭包或别名引用对象 | 画引用图，逐条找强引用，不用 `del` 当万能释放命令 |
| tracemalloc 降了但系统监控没降 | 是否把 Python 分配追踪当作 RSS | 分开记录对象存活、Python 分配器和操作系统进程指标 |
| Windows 删除临时文件失败 | 文件是否仍打开 | 先离开文件上下文，再删除文件或临时目录 |

</section>

<section id="project-runtime-observer-v03" data-learning-context="project-runtime-observer-v03" data-context-type="project" markdown="1">

## 系统运行观察器 v0.3

| v0.2 已有 | v0.3 新增 | 下一版继续 |
| --- | --- | --- |
| 线程共享状态与竞态 | 强／弱引用生命周期 | 本机端口与 TCP 连接 |
| Lock 保护不变量 | Python 分配追踪趋势 | HTTP 请求与响应 |
| 确定性错误交错 | 文件和临时目录清理 | 连接超时与关闭 |

保存四行输出、4 项测试和一张“变量名—对象—系统资源”图。现在观察器不只知道工作怎样结束，还能证明资源由谁持有、何时释放、异常时是否清理。

</section>

<section id="deepen-memory-boundary" data-learning-context="deepen-memory-boundary" data-context-type="deepen" markdown="1">

## Python 实验不能替代所有语言的内存模型

CPython 3.11 常用引用计数配合循环垃圾回收，但 Python 语言并不承诺所有实现都在最后一个引用消失的瞬间完成回收。`gc.collect()` 在这里用于让实验边界清楚，不是业务代码应该频繁调用的性能方案。

C++ 课程会继续用对象生命周期、引用、指针和 RAII 讨论确定性析构；系统工程还会进入虚拟内存、页、映射和性能。不要把本课的弱引用实验外推成这些机制的完整解释。

</section>

<section id="career-resource-ownership" data-learning-context="career-resource-ownership" data-context-type="career" markdown="1">

## 求职加练：怎样解释一次资源泄漏排查

从一个原创故障开始：批处理程序每轮打开日志文件，成功时会关闭，但解析失败时直接返回。回答时依次说明资源是什么、谁拥有它、哪条路径跳过释放、系统最终看到什么、怎样用上下文管理器和异常测试修复。

把本课 4 项测试作为证据：引用不是释放命令，正常路径和异常路径都要验证，动态内存数字不能冒充跨平台结论。这道追问来自文件描述符与系统可靠性能力信号，只使用能力方向，不复述外部题目。

</section>

## 完成检查

- [ ] 我能区分变量名、对象和对象管理的系统资源。
- [ ] 我能解释为什么删除一个变量不一定结束对象生命周期。
- [ ] 我用弱引用观察存活，用 tracemalloc 观察 Python 分配趋势。
- [ ] 我证明文件在正常和异常路径都会关闭。
- [ ] 我主动增加了资源所有者，并补了失败测试。
- [ ] 我不会把 tracemalloc 结果说成操作系统 RSS 一定同步变化。

## 来源与版本

- 适用：Python 3.11+，Windows、macOS 与常见 Linux；不依赖平台专用文件描述符接口。
- 本课在 Python 3.11.9 与 Node.js 24.14.1 驱动的仓库验证脚本中复现；核查日期：2026-07-20。
- Python 官方：[tracemalloc：追踪 Python 分配的内存块](https://docs.python.org/3.11/library/tracemalloc.html)。
- Python 官方：[weakref：不负责保活的弱引用](https://docs.python.org/3.11/library/weakref.html)。
- Python 官方：[open 与文件对象](https://docs.python.org/3.11/library/functions.html#open)。
- 验证方式：4 项 unittest、固定命令输出、课程根验证脚本；临时文件只写系统临时目录。

## 下一步

进入[从端口到 HTTP 的本机网络链路](04-local-network-port-http.md)。下一课会把文件句柄的打开与关闭经验迁移到 socket，观察服务端监听、客户端连接、HTTP 消息和超时。
