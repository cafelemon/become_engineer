<div class="be-tutor-mount" data-tutor-lesson="cs-core-02" aria-hidden="true"></div>

<section id="overview-growth" class="be-page-hero be-lesson-hero" data-learning-context="overview-growth" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">CS 起步 · 第二课 · 从次数看到趋势</span>

# 操作计数、增长率与渐近复杂度

## 数据翻一倍，工作也只翻一倍吗

上一课用 4 个学习时长做了三次不同的事：读取已知位置只取 1 次；查找不存在的值要比较 4 次；如果让每一对数据互相比较，则要比较 6 次。

现在把数据增加到 8 项。前两种次数变成 1 和 8，两两比较却变成 28。输入只是翻了一倍，第三种工作的增长明显更快。

这一课先看次数怎样变化，再给规律命名。这样遇到 <code>O(1)</code>、<code>O(n)</code> 和 <code>O(n²)</code> 时，你知道符号背后到底在数什么。

<div class="be-page-actions" markdown="1">
[先确定要数的动作](#concept-count){ .md-button .md-button--primary }
[让输入连续翻倍](#reproduce-growth){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>CS 起步 · 2 / 4</strong></div>
  <div><span>前置</span><strong>数据表示、位置、扫描和边界</strong></div>
  <div><span>完成后留下</span><strong>增长表、相邻增长统计和项目成本清单</strong></div>
</div>

## 开始前

- 能读懂 Python 列表、循环、函数返回值和简单数据类。
- 已经能区分“读取已知位置”和“寻找未知位置”。
- 这一课分析的是操作次数随输入规模怎样增长，不比较 Python 与 C++ 谁更快。
- 所有正确性结论都来自固定输入和整数计数；真实耗时只放在后面辅助观察。

<section id="concept-count" data-learning-context="concept-count" data-context-type="concept" markdown="1">

## 先说清楚 n 和动作

复杂度分析经常写 <code>n</code>。它不是一个固定数字，而是“输入规模”的名字。这一课把它定义为列表中的元素数量：

~~~python
hours = [2, 5, 3, 4]
n = len(hours)  # n 是 4
~~~

接着选一种要数的动作：

| 程序在做什么 | 这一课数什么 |
| --- | --- |
| 读取已知下标 | 指定位置读取了几次 |
| 查找一个值 | 元素与目标比较了几次 |
| 检查所有不同元素对 | 两个元素互相比较了几次 |

这一步不能省。若一个人按“循环次数”数，另一个人按“CPU 指令”数，两张表就不能直接比较。

空列表也要说明。里面没有合法位置和元素对，因此本课三种操作都记 0 次。渐近分析关心输入变大后的趋势，实现仍要把小输入处理正确。

</section>

<section id="example-three-costs" data-learning-context="example-three-costs" data-context-type="example" markdown="1">

## 同一组数据，三种工作量

还是这四个值：

<div class="be-array-row" aria-label="四个学习时长">
  <div><span>下标 0</span><strong>2</strong></div>
  <div><span>下标 1</span><strong>5</strong></div>
  <div><span>下标 2</span><strong>3</strong></div>
  <div><span>下标 3</span><strong>4</strong></div>
</div>

### 已知位置：1 次

~~~python
value = hours[2]
~~~

只要位置合法，这次读取不会因为列表从 4 项变成 40 项就自动多读 39 次。

### 目标不存在：n 次

~~~python
for value in hours:
    if value == 9:
        break
~~~

要确认 9 不在列表里，四项都得比较。列表有 <code>n</code> 项时，最坏要比较 <code>n</code> 次。

### 每一对互相比较：n(n-1)/2 次

四项中不同的两两组合是：

~~~text
(2, 5) (2, 3) (2, 4)
       (5, 3) (5, 4)
              (3, 4)
~~~

一共 6 对。第一项和后面 3 项比较，第二项和后面 2 项比较，第三项和后面 1 项比较，所以是 <code>3 + 2 + 1</code>。

</section>

<section id="reproduce-growth" data-learning-context="reproduce-growth" data-context-type="reproduce" markdown="1">

## 让输入连续翻倍

点“下一组”，把 <code>n</code> 从 4 依次增加到 8、16、32。留意三种次数怎样变化，而不是只盯最后一个数字。

<div class="be-growth-demo" data-growth-demo data-sizes="4,8,16,32" markdown="0">
  <div class="be-growth-demo__header">
    <span>输入规模 <strong data-growth-size>4</strong></span>
    <span>相对上一组 <strong data-growth-change>起点</strong></span>
  </div>
  <div class="be-growth-demo__chart" aria-live="polite">
    <span class="be-growth-demo__row"><b>已知位置读取</b><i data-growth-bar="constant"></i><strong data-growth-value="constant">1</strong></span>
    <span class="be-growth-demo__row"><b>缺失目标扫描</b><i data-growth-bar="linear"></i><strong data-growth-value="linear">4</strong></span>
    <span class="be-growth-demo__row"><b>不同元素两两比较</b><i data-growth-bar="pairs"></i><strong data-growth-value="pairs">6</strong></span>
  </div>
  <p class="be-growth-demo__message" data-growth-message>先记住 1、4、6。下一组会把输入增加到 8 项。</p>
  <div class="be-growth-demo__controls">
    <button type="button" data-growth-prev>上一组</button>
    <button type="button" data-growth-next>下一组</button>
    <button type="button" data-growth-reset>重置</button>
  </div>
</div>

禁用 JavaScript 时，完整数据仍然可以直接读：

| 输入规模 <code>n</code> | 已知位置读取 | 缺失目标扫描 | 不同元素两两比较 |
| ---: | ---: | ---: | ---: |
| 4 | 1 | 4 | 6 |
| 8 | 1 | 8 | 28 |
| 16 | 1 | 16 | 120 |
| 32 | 1 | 32 | 496 |

完整 Python 例子：

~~~python
--8<-- "examples/cs-start/operation_growth.py"
~~~

~~~bash
python site-src/examples/cs-start/operation_growth.py
~~~

输出中的数字由函数计算，不是手填表格。课程测试还会检查空输入、查找开头与缺失目标，以及换一组学习时长后的结果。

</section>

<section id="concept-asymptotic" data-learning-context="concept-asymptotic" data-context-type="concept" markdown="1">

## 从次数提取增长规律

增长表里有三个不同的函数：

~~~text
读取：      T(n) = 1
扫描：      T(n) = n
两两比较：  T(n) = n(n-1)/2
~~~

当 <code>n</code> 变得很大时，我们先看增长最快的部分：

- <code>1</code> 不随输入增长，写作 <code>Θ(1)</code>。
- <code>n</code> 与输入一起增长，写作 <code>Θ(n)</code>。
- <code>n(n-1)/2 = n²/2 - n/2</code>，其中 <code>n²</code> 最终占主导，写作 <code>Θ(n²)</code>。

这里的 <code>Θ</code> 可以先读成“增长速度同一量级”。它忽略固定倍数和较低阶项，不是说精确次数消失了。要检查代码对不对，我们仍然断言 6、28、120、496；要比较输入变大后的趋势，才使用渐近符号。

</section>

<section id="example-bounds" data-learning-context="example-bounds" data-context-type="example" markdown="1">

## O、Ω 和 Θ 各自说什么

- <code>O(g(n))</code> 给出渐近上界：增长最终不会超过某个常数倍的 <code>g(n)</code>。
- <code>Ω(g(n))</code> 给出渐近下界：增长最终至少达到某个常数倍的 <code>g(n)</code>。
- <code>Θ(g(n))</code> 同时给出上下界，说明增长同阶。

缺失目标的线性扫描精确比较 <code>n</code> 次，因此写 <code>Θ(n)</code> 最清楚。写 <code>O(n)</code> 也给出了正确上界，只是信息更少。

最好、最坏和平均情况是另一层说明。查找目标若在第一项，只比较 1 次；若在最后一项或不存在，最坏要比较 <code>n</code> 次。说“线性查找是 O(n)”时，通常需要补上自己讨论的是哪种输入情形。

</section>

<section id="troubleshoot-timing" data-learning-context="troubleshoot-timing" data-context-type="troubleshoot" markdown="1">

## 计时变快，不等于复杂度变了

同一段代码连续运行两次，耗时可能不同。后台任务、解释器状态、缓存、处理器和测量顺序都会带来波动。

~~~python
from timeit import repeat

times = repeat("sum(range(1000))", number=1000, repeat=5)
print(times)
~~~

<code>timeit</code> 适合观察小段代码，但这节课不写“必须小于 1 毫秒”之类的测试。机器换了，断言就可能失效；返回结果和精确操作次数却应保持一致。

看到下面几种说法时，先停一下：

| 说法 | 问题在哪里 |
| --- | --- |
| “这次只用了 0.1 秒，所以是 O(1)” | 单次耗时不能推出增长率 |
| “有两层循环，所以一定是 O(n²)” | 内层可能固定次数，也可能提前停止 |
| “O(n) 就是精确执行 n 次” | O 描述上界，不是精确等式 |
| “小数据更快，所以算法更好” | 常数、实现与增长趋势混在了一起 |

排查复杂度结论时，回到三个问题：<code>n</code> 是什么、重复动作是什么、最坏要重复几次。

</section>

<section id="modify-adjacent" data-learning-context="modify-adjacent" data-context-type="modify" markdown="1">

## 数一数相邻增长

把输入换成：

~~~python
hours = [1, 4, 4, 7, 2]
~~~

从第二项开始，每个值只和前一项比较一次：

| 相邻一对 | 是否增长 |
| --- | --- |
| 1 → 4 | 是 |
| 4 → 4 | 否 |
| 4 → 7 | 是 |
| 7 → 2 | 否 |

运行前先写下增长次数和比较次数，再实现：

~~~python
def count_adjacent_increases(values: list[int]) -> tuple[int, int]:
    ...
~~~

长度为 <code>n</code> 的序列有 <code>n-1</code> 对相邻位置；空列表和单元素列表比较 0 次。你的函数应返回 <code>(2, 4)</code>，并保持原列表不变。

然后再试三组数据：完全递增、完全下降、包含重复值。不要只看增长数，也要核对比较次数。

</section>

<section id="project-report-operations" data-learning-context="project-report-operations" data-context-type="project" markdown="1">

## 给报告器补一张成本清单

学习进度报告器 v1.0 会读取多条课程记录、汇总时长并查找课程。现在给项目文档增加一张小表，不必改主报告输出：

| 项目操作 | 输入规模 | 重复动作 | 最坏次数 | 增长趋势 |
| --- | --- | --- | ---: | --- |
| 读取第一条记录 | 记录数 <code>n</code> | 已知位置读取 | 1 | <code>Θ(1)</code> |
| 汇总全部完成小时 | 记录数 <code>n</code> | 读取一条记录的小时数 | <code>n</code> | <code>Θ(n)</code> |
| 按课程名逐项查找 | 记录数 <code>n</code> | 名称相等比较 | <code>n</code> | <code>Θ(n)</code> |

打开项目的 <code>analysis.py</code>，逐行找到与这三项对应的代码。若你的版本没有“读取第一条”操作，就不要为了填表虚构它；只记录真实存在的操作。

再为“按课程名查找”加入一个比较计数返回值或测试辅助函数。用目标在开头、末尾和不存在三种情况证明表格，而不是只在说明里写一个符号。

这张清单以后会继续变化：当课程查找改用映射或索引时，接口、额外空间和操作成本都要重新说明。

</section>

<section id="deepen-cost-model" data-learning-context="deepen-cost-model" data-context-type="deepen" markdown="1">

## 模型有用，也有边界

<code>Θ(n)</code> 的程序不一定在所有小输入上都比 <code>Θ(n²)</code> 快。实现常数、数据分布、语言运行时、内存访问和硬件都会影响真实耗时。渐近分析回答的是：输入继续变大时，工作量按什么趋势增长。

操作模型也要跟问题匹配。本课把一次列表元素比较当成一步；若比较的是超长字符串，一次“相等比较”内部还可能继续扫描字符。进入字符串、数据库或网络课程后，输入规模和基本操作都需要重新定义。

空间也有增长趋势。一个函数即使只扫描一次，如果同时复制了整个输入，就还使用了随 <code>n</code> 增长的额外空间。时间和空间需要分别说明。

</section>

<section id="career-explain-cost" data-learning-context="career-explain-cost" data-context-type="career" markdown="1">

## 被问到复杂度时，先讲过程

我更建议按这个顺序回答：

1. <code>n</code> 代表什么。
2. 代码重复做什么动作。
3. 什么时候提前停止。
4. 最好和最坏分别要做多少次。
5. 最后再给出渐近结论。

例如：“<code>n</code> 是课程记录数。查找从头比较课程名，首次匹配就停止。最好比较一次；目标在末尾或不存在时比较 <code>n</code> 次，所以最坏时间是 <code>Θ(n)</code>，额外空间是 <code>Θ(1)</code>。”

这比只说“线性”更有用，因为别人能听出你的输入、过程和前提是否一致。

</section>

## 完成检查

- [ ] 我能先定义输入规模和基本操作，再开始计数。
- [ ] 我能从 1、4、6 推导出 1、8、28，而不是背表格。
- [ ] 我操作了增长播放器，也能从静态表读出完整变化。
- [ ] 我运行了固定 Python 例子，并核对空输入和缺失目标。
- [ ] 我能解释 <code>Θ(1)</code>、<code>Θ(n)</code> 和 <code>Θ(n²)</code> 分别对应哪种增长。
- [ ] 我能区分精确次数、上界和同阶增长。
- [ ] 我没有用一次计时结果证明复杂度。
- [ ] 我完成了相邻增长函数，并换至少三组数据测试。
- [ ] 我为报告器写下真实操作的成本清单，没有虚构项目行为。
- [ ] 我能用输入、重复动作、停止条件和最坏次数解释一次查找。

## 来源与版本

- 适用版本：Python 3.11 及以上；示例只使用标准库。
- 核查日期：2026-07-17。
- 事实来源：[MIT 6.006 课程](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)用于算法、数据结构与性能分析的关系；[MIT 6.006 数据结构与动态数组](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-2-data-structures-and-dynamic-arrays/)用于操作模型与接口成本；[Python `timeit`](https://docs.python.org/3.11/library/timeit.html)用于重复计时及结果解释。
- 代码验证：仓库脚本检查三类增长公式、线性查找最好与最坏路径、空输入、相邻增长和替换数据；增长播放器提供前进、后退、重置和完整静态表。

## 下一步

进入[字符串、UTF-8 字节与码点边界](03-string-utf8-byte-code-point-boundaries.md)，看看“长度”为什么不能总理解成字符个数，并重新定义输入规模和扫描动作。

[进入下一课](03-string-utf8-byte-code-point-boundaries.md){ .md-button .md-button--primary }
