# C：变量、内存与第一次编译

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-c-memory" aria-hidden="true"></div>

<section id="overview-device-event" class="be-sample-hero" data-learning-context="overview-device-event" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">设备方向起步 · 设备事件记录器 v0.1</span>

## 先打印一条设备事件

```text
设备事件记录器 v0.1
pin=13, level=1, sequence=1
event address=0x...
```

这还没有连接真实开发板。我们先在电脑上把一条“13 号引脚变成高电平”的事件表示清楚，再去谈 GPIO 和中断。

<div class="be-sample-actions" markdown="1">
[看看数据放在哪里](#concept-c-memory){ .md-button .md-button--primary }
[直接编译](#reproduce-c-program){ .md-button }
</div>

</section>

<section id="concept-c-memory" class="be-sample-learning-unit" data-learning-context="concept-c-memory" data-context-type="concept" markdown="1">

## 变量既有值，也占位置

```c
uint8_t pin = 13U;
uint8_t level = 1U;
uint32_t sequence = 1U;
```

<div class="be-memory-strip" role="img" aria-label="三个 C 变量分别有名称、类型、当前值和内存位置">
  <div><strong>pin</strong><code>uint8_t · 13</code><span>一个无符号 8 位整数</span></div>
  <div><strong>level</strong><code>uint8_t · 1</code><span>这里约定 1 表示高电平</span></div>
  <div><strong>sequence</strong><code>uint32_t · 1</code><span>事件序号需要更大范围</span></div>
</div>

C 让你更直接地面对数据大小和内存位置。地址每次运行都可能不同，所以这里观察它存在即可，不把某个十六进制数背下来。

</section>

<section id="example-device-struct" class="be-sample-learning-unit" data-learning-context="example-device-struct" data-context-type="example" markdown="1">

## 把相关字段放在一起

```c
typedef struct {
    uint8_t pin;
    uint8_t level;
    uint32_t sequence;
} DeviceEvent;

const DeviceEvent event = {13U, 1U, 1U};
```

`struct` 把同一件事的多个字段组合起来。这里的字段按顺序表示引脚编号、电平和事件序号。`13U` 后面的 `U` 表示无符号整数常量。

打印固定宽度整数时，使用 `<inttypes.h>` 提供的宏：

```c
printf("pin=%" PRIu8 ", sequence=%" PRIu32 "\n",
       event.pin, event.sequence);
```

这样不会假设 `uint32_t` 在每个平台上都恰好对应同一种基础类型。

</section>

<section id="reproduce-c-program" class="be-sample-learning-unit" data-learning-context="reproduce-c-program" data-context-type="reproduce" markdown="1">

## 在电脑上编译 C17 样例

macOS 或装有 Clang 的环境：

```bash
mkdir -p /tmp/be-c-memory
clang -std=c17 -Wall -Wextra -Wpedantic -Wconversion -Wshadow \
  reviews/course-content/batch-b/examples/c-memory/device_event.c \
  -o /tmp/be-c-memory/device_event
/tmp/be-c-memory/device_event
```

Linux 可以把 `clang` 换成 `gcc`。Windows 建议先在 VS Code 中安装并使用 LLVM/Clang；本页先学习标准 C，不在第一节同时加入交叉编译器和芯片 SDK。

你看到的地址与示例不同是正常的。真正需要对照的是 `pin`、`level` 和 `sequence`。

</section>

<section id="modify-device-event" class="be-sample-learning-unit" data-learning-context="modify-device-event" data-context-type="modify" markdown="1">

## 换一条事件再编译

把引脚改为 `7U`，电平改为 `0U`，序号改为 `2U`。重新编译前先写下自己预计的输出。

然后增加一个时间字段：

```c
uint32_t tick_ms;
```

初始化时为它填入 `250U`，再把它打印出来。这里的毫秒只是模拟数据，还不是开发板上的真实定时器。

</section>

<section id="troubleshoot-c-format" class="be-sample-learning-unit" data-learning-context="troubleshoot-c-format" data-context-type="troubleshoot" markdown="1">

## 警告不是背景噪声

如果格式化字符串和参数类型对不上，编译器通常会给出警告。这里先别急着运行：先核对占位符、参数顺序和字段类型。

观察地址时要显式转换成 `void *`：

```c
printf("event address=%p\n", (const void *)&event);
```

本页只用 `&event` 取得地址并观察，不做地址加减，也不通过指针修改内存。那些内容要等数组、指针和生命周期有了更稳的基础再展开。

</section>

<section id="project-device-v01" class="be-sample-project-panel" data-learning-context="project-device-v01" data-context-type="project" markdown="1">

## 设备事件记录器 v0.1

现在它能表示并打印一条事件。GPIO 样板会保留同一组字段，把事件来源从手写常量换成“模拟边沿触发”，并让主循环只消费一次。

```text
v0.1：手工创建 DeviceEvent → 打印
v0.2：GPIO 边沿 → 中断函数记录 → 主循环取走 → 打印
```

这样安排是为了先学会表示数据，再处理事件怎样到达程序。两件事一起讲，反而很难看出问题发生在哪一层。

</section>

??? info "再深入一点：为什么先用固定宽度整数"
    设备寄存器、协议字段和文件格式往往关心明确位宽。`uint8_t` 和 `uint32_t` 表达得更清楚，但是否存在这些类型仍取决于实现；正式平台课会继续核对芯片和编译器文档。

## 完成检查

- [ ] 能编译并运行 C17 样例。
- [ ] 能解释变量的名称、类型、值和地址不是一回事。
- [ ] 能读懂 `DeviceEvent` 三个字段。
- [ ] 能用正确的格式宏打印固定宽度整数。
- [ ] 能增加 `tick_ms`，重新编译并得到预计输出。

下一页：[BFS：无权图中的最少步数](bfs-shortest-path.md)。
