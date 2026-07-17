# GPIO、中断与设备事件

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-gpio-interrupts" aria-hidden="true"></div>

<section id="overview-gpio-event" class="be-sample-hero" data-learning-context="overview-gpio-event" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">设备系统样板 · 设备事件记录器 v0.2</span>

## 按键变化以后，程序怎样知道

```text
按钮按下
GPIO 低 → 高
中断函数记录 pin=13, edge=rising, sequence=1
主循环取走并处理事件
```

这一页先用浏览器轨迹和可测试的 C 程序把流程讲清楚。它不是某块开发板的真实电气实验，也不会假装测出了真实中断延迟。

<div class="be-sample-actions" markdown="1">
[跟着事件走一遍](#concept-gpio-edge){ .md-button .md-button--primary }
[运行 C 仿真](#reproduce-gpio-sim){ .md-button }
</div>

</section>

<section id="concept-gpio-edge" class="be-sample-learning-unit" data-learning-context="concept-gpio-edge" data-context-type="concept" markdown="1">

## 电平、边沿和中断是三件事

<div class="be-gpio-flow" role="img" aria-label="按钮引起 GPIO 电平变化，边沿触发中断，中断记录事件，主循环处理事件">
  <div><strong>按钮</strong><span>外部输入发生变化</span></div>
  <div><strong>GPIO 边沿</strong><span>低到高或高到低</span></div>
  <div><strong>中断函数</strong><span>快速记下必要信息</span></div>
  <div><strong>主循环</strong><span>完成打印和业务处理</span></div>
</div>

- **电平**是引脚当前被程序解释为低或高。
- **边沿**是电平变化的瞬间，例如低到高叫上升沿。
- **中断**让处理器在事件发生时转去执行一小段处理代码，然后回来继续原来的工作。

具体电压、上拉／下拉、引脚复用和中断控制器都由真实平台决定，本页不替厂商手册作决定。

</section>

<section id="example-gpio-trace" class="be-sample-learning-unit" data-learning-context="example-gpio-trace" data-context-type="example" markdown="1">

## 一次事件怎样穿过程序

<div class="be-trace-demo" data-trace-demo="gpio" aria-label="GPIO 边沿、中断函数和主循环单步演示"></div>

??? info "没有 JavaScript 时的完整轨迹"
    | 时刻 | GPIO | 程序里发生什么 |
    | --- | --- | --- |
    | 0 | 低 | 暂无事件，主循环继续 |
    | 1 | 低→高 | 产生上升沿，中断请求挂起 |
    | 2 | 高 | 中断函数记录 pin、edge、sequence |
    | 3 | 高 | 主循环取走事件并清除待处理标记 |
    | 4 | 高 | 再次检查时没有重复事件 |

中断函数里只记录必要信息。格式化输出、文件写入和耗时业务更适合留给主循环。

</section>

<section id="reproduce-gpio-sim" class="be-sample-learning-unit" data-learning-context="reproduce-gpio-sim" data-context-type="reproduce" markdown="1">

## 用 C 程序复现这条链路

```bash
mkdir -p /tmp/be-gpio
clang -std=c17 -Wall -Wextra -Wpedantic -Wconversion -Wshadow \
  reviews/course-content/batch-b/examples/gpio/device_event.c \
  reviews/course-content/batch-b/examples/gpio/device_event_test.c \
  -I reviews/course-content/batch-b/examples/gpio \
  -o /tmp/be-gpio/device_event_test
/tmp/be-gpio/device_event_test
```

程序会依次检查：没有事件、上升沿事件、事件只能取走一次、下降沿事件和递增序号。`gpio_edge_isr()` 是被测试代码主动调用的普通函数，用来模拟中断到达；它不是操作系统线程，也不代表某颗 MCU 的真实 ISR 注册方式。

</section>

<section id="modify-gpio-pin" class="be-sample-learning-unit" data-learning-context="modify-gpio-pin" data-context-type="modify" markdown="1">

## 换一个引脚，再加一种处理

把测试中的引脚从 `13U` 改为 `7U`，确认断言也跟着修改。然后在主循环取到下降沿时增加一条打印：

```c
if (event.edge == EDGE_FALLING) {
    puts("button released");
}
```

不要把打印塞进 `gpio_edge_isr()`。我们希望中断函数保持短小，主循环负责较慢、较复杂的工作。

</section>

<section id="troubleshoot-gpio-events" class="be-sample-learning-unit" data-learning-context="troubleshoot-gpio-events" data-context-type="troubleshoot" markdown="1">

## 仿真里正常，真机上仍可能出错

机械按键可能在一次按下时快速抖动多次，真实 ISR 与主循环还可能并发访问同一份状态。这个单线程仿真故意不假装解决它们。

| 现象 | 仿真里先看 | 真机还要继续查 |
| --- | --- | --- |
| 没有事件 | 是否调用模拟 ISR | 引脚复用、输入模式、中断使能 |
| 事件重复 | 待处理标记是否清除 | 按键抖动、边沿配置 |
| 字段偶尔不一致 | 事件写入顺序 | `volatile`、原子性、临界区和平台内存模型 |
| 中断后系统变慢 | ISR 是否做了耗时工作 | 优先级、屏蔽时间、实时调度 |

`volatile` 不是通用并发修复。具体平台需要结合寄存器语义、原子操作和临界区设计。

</section>

<section id="project-device-v02" class="be-sample-project-panel" data-learning-context="project-device-v02" data-context-type="project" markdown="1">

## 设备事件记录器 v0.2

C 起步样板里的事件由常量直接创建。现在事件有了一条来源链：

```text
模拟边沿 → gpio_edge_isr() → pending_event → main_loop_take_event()
```

下一阶段可以继续增加环形缓冲区、去抖、定时器时间戳和 RTOS 队列。但在正式选定 MCU 和 RTOS 以前，本样板只保留这条平台无关的教学接口。

</section>

<section id="deepen-hardware-boundary" class="be-sample-learning-unit" data-learning-context="deepen-hardware-boundary" data-context-type="deepen" markdown="1">

## 仿真能证明什么，真机还要证明什么

<div class="be-hardware-line">
  <div class="be-hardware-line__sim"><strong>这一页能检查</strong><p>事件字段、边沿分类、一次消费、序号递增、主循环与中断函数的职责分开。</p></div>
  <div class="be-hardware-line__real"><strong>真实设备必须再检查</strong><p>电气连接、上拉下拉、引脚复用、中断控制器、抖动、并发、延迟、功耗和异常恢复。</p></div>
</div>

真实硬件毕业时还需要原理图或接线说明、构建日志、串口或调试器输出、时序测量、故障复现和回归结果。浏览器动画不能替代这些材料。

</section>

## 完成检查

- [ ] 能区分电平、边沿和中断。
- [ ] 能按顺序讲出事件怎样到达主循环。
- [ ] 能编译并通过假 HAL 测试。
- [ ] 能新增一个引脚或下降沿处理。
- [ ] 能明确指出本页没有证明哪些真机问题。

返回[批次 B 评审说明](README.md)。
