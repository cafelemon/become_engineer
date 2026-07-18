<div class="be-tutor-mount" data-tutor-lesson="cs-core-22" aria-hidden="true"></div>

<section id="overview-priority-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-priority-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">算法核心 · 第 2 课 · 可追踪优先队列与最短路实验</span>

# 稳定优先队列、同优先级顺序与下溢

## 优先级相同，先来的仍然先处理

```text
稳定优先队列
push：review@2, test@1, lint@1, deploy@3
heap_array：test@1, review@2, lint@1, deploy@3
peek：test@1
pop_order：test@1, lint@1, review@2, deploy@3
equal_priority_fifo=yes
```

`test` 和 `lint` 的优先级都是 1，队列没有按名字挑选，而是保留了到达顺序。做法很小：每个任务入队时带上一个不断递增的序号，比较键从 `priority` 变成 `(priority, sequence)`。

[看懂比较键](#example-stable-key){ .md-button .md-button--primary }
[运行短轨迹](#reproduce-priority-trace){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>算法核心 · 2 / 6</strong></span><span>前置<strong>二叉最小堆与上浮下沉</strong></span><span>完成后留下<strong>稳定队列、下溢契约与双语言报告</strong></span></div>

</section>

## 开始前

- 能解释最小堆为什么只保证根最小，不保证内部数组升序。
- 知道一次 `push` 或 `pop` 最多沿完全二叉树的一条路径移动。
- 本课沿用上一课的自研可追踪堆；标准库只作接口对照。

<section id="concept-interface-representation" data-learning-context="concept-interface-representation" data-context-type="concept" markdown="1">

## 优先队列管“下一项”，堆负责把它找出来

优先队列是一组接口：加入任务、查看下一项、取走下一项。它没有承诺“内部容器从左到右已经排好”。

上面的 `heap_array` 是 `test@1, review@2, lint@1, deploy@3`，并不按完整弹出顺序排列；但根始终是下一项。连续调用 `pop`，才会得到稳定的优先级顺序。

</section>

<section id="example-heap-vs-pop" data-learning-context="example-heap-vs-pop" data-context-type="example" markdown="1">

## 先看根，再看完整排空

```text
内部堆：test@1, review@2, lint@1, deploy@3
peek：  test@1            # 只读，不减少 size
pop：   test@1            # 与刚才的 peek 相同
余下：  lint@1, review@2, deploy@3
```

判断实现是否正确时，不要拿内部数组去和升序结果比较。更可靠的检查是：每次 `peek` 与紧接着的 `pop` 返回同一条目，而且 `peek` 前后大小不变。

</section>

<section id="concept-stable-key" data-learning-context="concept-stable-key" data-context-type="concept" markdown="1">

## 只比较优先级，还不够稳定

如果两项优先级相同，单凭 `priority` 无法决定谁先出队。不同实现可能保留原顺序，也可能因为交换路径而改变顺序；这不是可以依赖的契约。

每次入队分配唯一且递增的 `sequence`：

```text
先比较 priority
priority 相等，再比较 sequence
label 只保存任务内容，不参与先后判断
```

数值较小的优先级先出队；相同优先级中，序号较小的任务先出队。

</section>

<section id="example-stable-key" data-learning-context="example-stable-key" data-context-type="example" markdown="1">

## 四次入队，四个不会歧义的键

<div class="be-priority-key" aria-label="四个任务的优先级与稳定序号">
  <div><strong>review</strong><code>(2, 0)</code><span>第 1 个到达</span></div>
  <div data-tie="true"><strong>test</strong><code>(1, 1)</code><span>优先级 1，先到</span></div>
  <div data-tie="true"><strong>lint</strong><code>(1, 2)</code><span>优先级 1，后到</span></div>
  <div><strong>deploy</strong><code>(3, 3)</code><span>第 4 个到达</span></div>
</div>

先按第一列比较，因此 `test`、`lint` 排在 `review` 前；两项第一列相同，再看第二列，因此 `(1,1)` 先于 `(1,2)`。即使把标签都改成 `same`，顺序也不会含糊。

</section>

<section id="concept-peek-pop" data-learning-context="concept-peek-pop" data-context-type="concept" markdown="1">

## `peek` 读根，`pop` 删除根后继续下沉

`peek` 先检查队列是否为空，然后返回根条目，不修改数组和序号。`pop` 取走根，用末尾条目补到根，再按完整比较键选择较小孩子并下沉。

课程中的 `comparisons` 把“两个完整条目的先后判断”记作一次。不要把 `priority` 相等后查看 `sequence` 再算一次，否则 Python 与 C++ 很难保持同一份教学计数。

</section>

<section id="reproduce-priority-trace" data-learning-context="reproduce-priority-trace" data-context-type="reproduce" markdown="1">

## 把序号和弹出顺序打印出来

```bash
.venv/bin/python site-src/examples/algorithm-core/stable_priority_queue_trace.py
```

运行后留意两行：`test` 的键是 `(1,1)`，`lint` 的键是 `(1,2)`；最终 `tie_sequences=1, 2`。内部数组仍不是完整排序结果，这正好再次说明接口与表示的区别。

</section>

<section id="reproduce-bilingual-priority" data-learning-context="reproduce-bilingual-priority" data-context-type="reproduce" markdown="1">

## 运行 Python 和 C++ 阶段作品

```bash
cd exercises/cs-core/traceable-priority-shortest-path-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_priority_shortest_path_lab queue
```

```bash
cd exercises/cs-core/traceable-priority-shortest-path-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_priority_shortest_path_lab queue
```

再分别运行 `heap` 和 `dijkstra`。三个模式的 Python/C++ 标准输出都应逐字一致，说明本课没有破坏上一版最小堆，也没有改动下一版最短路依赖的接口。

</section>

<section id="modify-duplicate-labels" data-learning-context="modify-duplicate-labels" data-context-type="modify" markdown="1">

## 把两个标签都改成 `same`

加入 `same@1`、`same@1`，记录各自的序号，再连续弹出。两个标签相同并不代表它们是同一个条目：第一次入队的序号更小，必须先出队。

接着故意把比较键改成 `(priority, label)`。你会看到原本的到达顺序被标签字典序替代。恢复 `(priority, sequence)` 后，标签重新只负责携带内容。

</section>

<section id="modify-drain-input" data-learning-context="modify-drain-input" data-context-type="modify" markdown="1">

## 写一个稳定排空函数

完成 `drain_by_priority(tasks)`：按输入顺序逐项 `push`，再反复 `pop` 到空。请覆盖这些数据：

- 空输入。
- 负优先级。
- 重复标签。
- 全部任务优先级相同。
- 多种优先级混合。

函数应保留原输入，并通过队列操作产生结果，不能用一次全量 `sort` 偷换实现。换一组任务再做一次，先写出预期顺序，再运行测试。

</section>

<section id="troubleshoot-priority" data-learning-context="troubleshoot-priority" data-context-type="troubleshoot" markdown="1">

## 顺序漂了、空队列坏了，先查这里

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 同优先级任务顺序变化 | 没有保存递增序号 | 比较 `(priority, sequence)` |
| 改个标签就改变弹出顺序 | `label` 进入比较键 | 标签只作负载 |
| 把合法堆判成错误 | 要求内部数组全局排序 | 用连续 `pop` 检查接口 |
| C++ 先弹出较大优先级数值 | 沿用 `priority_queue` 默认最大项 | 提供最小方向比较器或自研最小堆 |
| 空 `peek/pop` 后状态变化 | 检查发生得太晚 | 修改数组以前拒绝下溢 |
| 双语言计数不同 | 拆开统计键的字段比较 | 一次条目顺序判断记一次 |

Python 空队列抛 `IndexError`，C++ 抛 `std::out_of_range`。异常类型可以不同，失败前检查和状态不变的契约必须相同。

</section>

<section id="project-priority-v02" data-learning-context="project-priority-v02" data-context-type="project" markdown="1">

## 可追踪优先队列与最短路实验 v0.2

上一版只处理整数最小堆；这一版加入 `PriorityEntry(priority, sequence, label)`、稳定 `push/peek/pop`、比较与交换计数，以及空队列保护。项目已经能回答“谁下一项”和“同优先级谁先来”两个问题。

[查看阶段作品](../../exercises/cs-core/traceable-priority-shortest-path-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-priority-cost" data-learning-context="deepen-priority-cost" data-context-type="deepen" markdown="1">

## 稳定序号没有改变堆的复杂度

给条目增加序号只让比较键多一个常量大小字段。`peek` 仍是 `Theta(1)`，`push` 与 `pop` 仍沿树高运行，为 `Theta(log n)`；稳定排空 n 项为 `Theta(n log n)`。

若只是一次性把全部输入排序，排序也能得到顺序。但优先队列的价值在于任务可以持续加入，同时随时以对数代价取下一项。

</section>

<section id="deepen-language-boundary" data-learning-context="deepen-language-boundary" data-context-type="deepen" markdown="1">

## 两个标准库的默认方向不同

Python 3.11 的 `heapq` 把最小项放在下标 0，常见做法是压入 `(priority, sequence, task)`。`sequence` 唯一时，任务对象本身不会进入比较。

C++ `std::priority_queue` 默认把最大项放在 `top()`；要获得较小优先级数值先出的行为，需要显式比较器。无论调用哪个库，都要先把“谁应该先出队”写成独立契约。

</section>

<section id="career-priority-evidence" data-learning-context="career-priority-evidence" data-context-type="career" markdown="1">

## 解释稳定优先队列时，别只说“底层是堆”

我更建议从一个平局开始：`test@1` 与 `lint@1` 谁先？然后给出 `(priority, sequence)`，说明标签为什么不能参与比较，再走一遍 `peek`、`pop` 和空队列。

最后补上接口与表示、复杂度以及 Python/C++ 默认方向差异。这样听的人能判断你是否真正理解了稳定性，而不是只记住一个容器名字。

</section>

## 完成检查

- [ ] 能说明优先队列接口与内部堆数组的区别。
- [ ] 能用 `(priority, sequence)` 保持同优先级 FIFO。
- [ ] 标签和重复标签不会改变先后判断。
- [ ] `peek` 只读，空 `peek/pop` 安全失败且状态不变。
- [ ] `drain_by_priority` 使用队列、保留输入并覆盖边界数据。
- [ ] 能比较 Python `heapq` 与 C++ `priority_queue` 的默认方向。
- [ ] Python 类型检查、C++ CTest 和三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [Python `heapq`](https://docs.python.org/3.11/library/heapq.html) | 三元组平局处理、最小堆接口 | Python 3.11，2026-07-17 核查 |
| [C++ `priority_queue`](https://eel.is/c++draft/priority.queue) | 容器适配器接口与比较方向 | 2026-07-17 核查 |
| [MIT 6.006 Binary Heaps](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/40d4851e550507ca14dc778b9b2266cc_MIT6_006S20_lec8.pdf) | 优先队列抽象与堆操作复杂度 | 2026-07-17 核查 |

本课不讨论任意删除、优先级原地更新、并发队列或懒惰删除；下一课会用“允许重复入队、弹出时丢弃过期项”的方式服务 Dijkstra。

## 下一步

进入[带权图松弛、Dijkstra 与过期条目](23-weighted-relaxation-dijkstra-stale-entries.md)，把稳定最小队列接到真实的最短路更新过程。
