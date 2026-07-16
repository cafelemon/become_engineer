# 稳定优先队列、同优先级顺序与下溢

<div class="be-tutor-mount" data-tutor-lesson="cs-core-22" aria-hidden="true"></div>

> **任务先行：** 用上一课的堆维护任务优先级，并加入单调递增序号，让同优先级任务跨语言稳定地先进先出。

## 任务路线

<div class="be-task-route" role="list" aria-label="本课六步任务"><span role="listitem">1 运行基线</span><span role="listitem">2 接口与表示</span><span role="listitem">3 稳定序号</span><span role="listitem">4 查看与出队</span><span role="listitem">5 平局与下溢</span><span role="listitem">6 排空迁移</span></div>

<section id="step-1" class="be-task-step" data-step-id="step-1" markdown="1">

## 第一步：运行最小堆与任务队列基线

依次运行 `heap` 和 `queue`。**当前任务：**确认优先级 1 的 `test`、`lint` 先于 2 和 3 弹出，同时 `test` 保持在 `lint` 前。**成功证据：**固定输出包含 `equal_priority_fifo=yes`。

</section>

<section id="step-2" class="be-task-step" data-step-id="step-2" markdown="1">

## 第二步：区分优先队列接口与堆表示

优先队列承诺能查看或移除“下一项”，不承诺遍历内部容器时全局有序。样例内部优先级是 `1,2,1,3`，仍是合法堆；连续弹出才得到 `1,1,2,3`。

**主动修改：**打印内部堆数组和完整弹出序列。**成功证据：**两者不同，但每次 `peek` 都与下一次 `pop` 一致。

</section>

<section id="step-3" class="be-task-step" data-step-id="step-3" markdown="1">

## 第三步：用稳定序号处理同优先级任务

每次入队创建 `(priority, sequence, label)`，比较只使用前两项；优先级越小越先，优先级相等时序号越小越先，标签不参与破除平局。

```mermaid
flowchart LR
    A["任务 + 优先级"] --> S["附加递增 sequence"]
    S --> H["按 priority, sequence 入堆"]
    H --> O["稳定弹出"]
```

**成功证据：**两个同名、同优先级任务仍按各自序号 0、1 弹出。

</section>

<section id="step-4" class="be-task-step" data-step-id="step-4" markdown="1">

## 第四步：实现查看、出队与完整排空

`peek` 只读取根；`pop` 删除根后沿用最小堆下沉。比较次数按“两个完整队列项的一次顺序判断”统计，不把元组内部字段比较拆开。

Python 3.11 `heapq` 是最小堆；C++ `std::priority_queue` 默认把最大元素放在 `top`，要得到最小行为必须显式提供比较器。本实验使用自研可追踪实现，不读取标准库内部计数。

</section>

<section id="step-5" class="be-task-step" data-step-id="step-5" markdown="1">

## 第五步：复现遗漏序号和空队列失败

临时只按 `(priority, label)` 比较。**预期失败：**同优先级任务按标签而非输入顺序排列。恢复序号后，再对空队列执行 `peek` 与 `pop`；Python 抛出 `IndexError`，C++ 抛出 `std::out_of_range`，状态保持为空。

</section>

<section id="step-6" class="be-task-step" data-step-id="step-6" markdown="1">

## 第六步：完成 `drain_by_priority` 迁移验收

接收任务序列的副本并稳定排空。**验收：**覆盖空输入、负优先级、重复标签、全部同优先级与混合优先级；结果按 `(priority, sequence)` 排列，原输入不变。不要直接调用全量排序替代队列操作。

</section>

## 固定输出

```text
稳定优先队列
push：review@2, test@1, lint@1, deploy@3
heap_array：test@1, review@2, lint@1, deploy@3
peek：test@1
pop_order：test@1, lint@1, review@2, deploy@3
equal_priority_fifo=yes
```

## 常见错误与排查

| 现象 | 原因 | 恢复 |
| --- | --- | --- |
| 同优先级顺序漂移 | 没有稳定序号 | 比较 `(priority, sequence)` |
| 标签改变结果 | 把标签放进比较键 | 标签只作为负载 |
| 认为内部数组应排序 | 混淆接口与表示 | 通过连续弹出观察顺序 |
| C++ 先弹出最大优先级数值 | 使用默认 `priority_queue` | 提供最小比较器或自研最小堆 |

## 来源与版本

| 来源 | 用途 | 核查日期 |
| --- | --- | --- |
| [Python 3.11 `heapq`](https://docs.python.org/3.11/library/heapq.html) | 稳定三元组与懒惰删除建议 | 2026-07-16 |
| [C++ `priority_queue`](https://eel.is/c++draft/priority.queue) | 容器适配器接口与比较器 | 2026-07-16 |
| [MIT 6.006 Binary Heaps](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/40d4851e550507ca14dc778b9b2266cc_MIT6_006S20_lec8.pdf) | 优先队列抽象与堆实现 | 2026-07-16 |

本地材料中“优先队列保证整个集合有序”的表述只作为误区候选；本课明确只承诺下一项，不发布 Top-K 或面试题。

## 下一步

下一课把稳定最小队列接入[带权图松弛与 Dijkstra](23-weighted-relaxation-dijkstra-stale-entries.md)。
