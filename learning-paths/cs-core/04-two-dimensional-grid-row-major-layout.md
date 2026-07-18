<div class="be-tutor-mount" data-tutor-lesson="cs-core-04" aria-hidden="true"></div>

<section id="overview-grid-coordinate" class="be-page-hero be-lesson-hero" data-learning-context="overview-grid-coordinate" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">CS 起步 · 第四课 · 从行列找到位置</span>

# 二维网格、行优先布局与坐标边界

## 点一下第 2 行第 3 列

下面是两门课程三天的学习小时。点任意一格，页面会同时告诉你行列坐标和它在一维列表中的位置。

<div class="be-page-actions" markdown="1">
[先试试坐标换算](#example-grid-explorer){ .md-button .md-button--primary }
[运行完整 Python 例子](#reproduce-grid-code){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>CS 起步 · 4 / 4</strong></div>
  <div><span>前置</span><strong>列表下标、扫描成本和边界检查</strong></div>
  <div><span>完成后留下</span><strong>坐标换算程序、学习数据矩阵视图和边界测试</strong></div>
</div>

## 开始前

- 能运行 Python 文件，并读懂列表、函数、循环和异常。
- 知道一维列表从下标 0 开始。
- 本课先把二维数据想清楚，不要求 C++、指针或连续内存知识。
- 准备一张纸，画出 2 行 3 列的小格子会很有帮助。

<section id="concept-grid-shape" data-learning-context="concept-grid-shape" data-context-type="concept" markdown="1">

## 数据没变，形状可以改变意思

先看这六个学习小时：

~~~python
hours = [2, 5, 3, 4, 1, 2]
~~~

只有这行代码时，我们知道它有六个值，却不知道它代表 <code>2 × 3</code>、<code>3 × 2</code>，还是一条长度为 6 的记录。**形状也是数据解释的一部分。**

把它解释成 2 行 3 列，可以写成：

|  | 周一 | 周二 | 周三 |
| --- | ---: | ---: | ---: |
| Python | 2 | 5 | 3 |
| CS | 4 | 1 | 2 |

这里约定行表示课程、列表示星期。坐标 <code>(1, 2)</code> 指第 1 行第 2 列，也就是 CS 的周三数据 2。坐标仍然从 0 开始，所以它是人眼看到的第 2 行第 3 列。

同样六个值若解释为 3 行 2 列，<code>(1, 1)</code> 会变成第 4 个值 4。值没有移动，坐标的含义变了。

</section>

<section id="concept-row-major" data-learning-context="concept-row-major" data-context-type="concept" markdown="1">

## 一行放完，再放下一行

行优先布局先依次放完第 0 行，再放第 1 行。若每行有 <code>columns</code> 个值，走到第 <code>row</code> 行之前，已经越过了 <code>row * columns</code> 个值；再向右走 <code>column</code> 格即可。

~~~text
flat_index = row * columns + column
~~~

对 2 行 3 列的网格：

~~~text
(0, 0) -> 0 * 3 + 0 = 0
(0, 2) -> 0 * 3 + 2 = 2
(1, 0) -> 1 * 3 + 0 = 3
(1, 2) -> 1 * 3 + 2 = 5
~~~

<div class="be-grid-formula" role="img" aria-label="二维坐标先跨过完整的行，再向右移动到目标列，得到一维下标。">
  <span><b>row × columns</b><small>前面完整的行</small></span>
  <i>+</i>
  <span><b>column</b><small>本行向右移动</small></span>
  <i>=</i>
  <span><b>flat index</b><small>一维列表的位置</small></span>
</div>

行优先是我们选定的一种约定，并不是二维数据天生只有这一种存法。只要写入和读取双方使用同一套布局，坐标才能落到正确的位置。

</section>

<section id="example-grid-explorer" data-learning-context="example-grid-explorer" data-context-type="example" markdown="1">

## 点一格，核对一次换算

先点 <strong>CS · 周三</strong>，再点 <strong>Python · 周二</strong>。每次都先自己算，再看页面给出的结果。

<div class="be-grid-demo" data-grid-demo data-rows="2" data-columns="3" data-values="2,5,3,4,1,2" data-row-labels="Python,CS" data-column-labels="周一,周二,周三">
  <div class="be-grid-demo__status" aria-live="polite">
    <span>坐标 <strong data-grid-coordinate>（还没选择）</strong></span>
    <span>一维下标 <strong data-grid-index>—</strong></span>
    <span>值 <strong data-grid-value>—</strong></span>
  </div>
  <div class="be-grid-demo__board" data-grid-board aria-label="学习小时二维网格"></div>
  <p class="be-grid-demo__message" data-grid-message>先选一格。行列坐标从 0 开始。</p>
  <button type="button" data-grid-reset>重置</button>
</div>

<noscript>

| 选择 | 坐标 | 一维下标 | 值 |
| --- | --- | ---: | ---: |
| Python · 周一 | <code>(0, 0)</code> | 0 | 2 |
| Python · 周二 | <code>(0, 1)</code> | 1 | 5 |
| Python · 周三 | <code>(0, 2)</code> | 2 | 3 |
| CS · 周一 | <code>(1, 0)</code> | 3 | 4 |
| CS · 周二 | <code>(1, 1)</code> | 4 | 1 |
| CS · 周三 | <code>(1, 2)</code> | 5 | 2 |

</noscript>

按钮只是帮助你观察。真正需要记住的是：形状先确定每行多长，坐标通过公式落到一维位置，访问前还必须检查边界。

</section>

<section id="concept-grid-boundary" data-learning-context="concept-grid-boundary" data-context-type="concept" markdown="1">

## 先检查形状，再检查坐标

一个可靠的二维访问需要回答两个问题。

第一，数据长度和形状是否一致：

~~~text
rows * columns == len(values)
~~~

第二，坐标是否落在网格内：

~~~text
0 <= row < rows
0 <= column < columns
~~~

检查顺序很重要。若声称是 <code>2 × 3</code>，实际只收到 5 个值，即使坐标 <code>(0, 0)</code> 看起来合法，整个网格仍然没有满足约定。先拒绝坏形状，后面的每次访问才有可信基础。

空网格 <code>rows=0, columns=0, values=[]</code> 可以是合法形状，但它没有任何可访问坐标。合法容器不等于任意访问都合法。

</section>

<section id="reproduce-grid-code" data-learning-context="reproduce-grid-code" data-context-type="reproduce" markdown="1">

## 把坐标和检查写进代码

完整例子把返回结果写成 <code>GridCell</code>，避免只返回一个值后丢掉它来自哪里：

~~~python
--8<-- "examples/cs-start/grid_coordinates.py"
~~~

~~~bash
python site-src/examples/cs-start/grid_coordinates.py
~~~

你应该看到：

~~~text
shape=2x3
coordinate=(1, 2), flat_index=5, value=2
row=1, total=7, visits=3
same_values_as_3x2: coordinate=(2, 1), flat_index=5, value=2
~~~

<code>sum_grid_row()</code> 还会记录访问次数。扫描一整行时，每列恰好访问一次，所以 3 列对应 3 次访问。这把上一课的“操作计数”带进了二维数据。

</section>

<section id="troubleshoot-grid-alias" data-learning-context="troubleshoot-grid-alias" data-context-type="troubleshoot" markdown="1">

## 为什么改一格，三行一起变了

故意运行一次：

~~~python
grid = [[0] * 2] * 3
grid[0][0] = 9
print(grid)
~~~

结果是：

~~~text
[[9, 0], [9, 0], [9, 0]]
~~~

外层的 <code>* 3</code> 没有创建三份独立的行，而是把同一个行列表的引用放了三次。三行其实指向同一个对象。

需要独立行时，用列表推导：

~~~python
grid = [[0] * 2 for _ in range(3)]
grid[0][0] = 9
print(grid)  # [[9, 0], [0, 0], [0, 0]]
~~~

本课正式例子继续使用扁平列表，因为形状和坐标换算更容易检查。嵌套列表并非错误，只是它表达的是“行组成的列表”，各行甚至可以长度不同。

</section>

<section id="modify-grid-shape" data-learning-context="modify-grid-shape" data-context-type="modify" markdown="1">

## 把 2 × 3 改成 3 × 2

保留 <code>[2, 5, 3, 4, 1, 2]</code>，把形状改为 3 行 2 列。运行前先画出来，再回答：

1. 坐标 <code>(1, 1)</code> 对应哪个值？
2. 最后一个值的坐标是什么？
3. 扫描第 2 行会访问几次、总和是多少？
4. 原来合法的 <code>(1, 2)</code> 为什么现在越界？

然后把数据换成你自己的六个非负整数，再做一次。保存手算结果和程序输出；若两者不同，先检查列数是否仍然是 2，而不是立刻改公式。

</section>

<section id="project-study-grid" data-learning-context="project-study-grid" data-context-type="project" markdown="1">

## 给学习进度报告器加一张矩阵视图

学习进度报告器已经有多条记录。现在可以增加一份**单独的诊断视图**，用行表示课程，用列表示 <code>计划小时</code>、<code>完成小时</code> 和 <code>剩余小时</code>：

|  | 计划 | 完成 | 剩余 |
| --- | ---: | ---: | ---: |
| Python | 10 | 6 | 4 |
| CS | 8 | 3 | 5 |

先把二维值展平成：

~~~python
metrics = [10, 6, 4, 8, 3, 5]
rows = 2
columns = 3
~~~

为项目补三类测试：

- 两门课程三项指标能通过坐标准确读取。
- 形状和数据长度不一致时立即失败。
- 计算矩阵视图后，原始学习记录保持不变。

这次不要改动 v1.0 主报告文字。新视图先作为独立诊断函数和测试存在，等以后真正需要表格输出或 Web API 时再接入公开接口。这样既能连续演进项目，也不会为了练习破坏已经稳定的契约。

</section>

<section id="deepen-grid-representation" data-learning-context="deepen-grid-representation" data-context-type="deepen" markdown="1">

## 扁平列表和嵌套列表各有用途

扁平列表加形状有几个优点：长度契约明确、坐标换算统一、遍历顺序容易控制。嵌套列表更接近人眼看到的行，但可能出现长短不一的“锯齿行”，也可能因重复引用共享同一行。

后续系统方向还会讨论真实内存布局、连续存储、步长、C++ 视图和乘法溢出；图像与数值计算则会遇到通道、批次和更多维度。那些内容都建立在今天的三个问题上：

- 形状是什么？
- 坐标怎样映射到存储位置？
- 哪些坐标允许访问？

共同 CS 起步先用 Python 把这三个问题说清楚，不急着把语言底层细节一起塞进来。

</section>

<section id="career-grid-contract" data-learning-context="career-grid-contract" data-context-type="career" markdown="1">

## 看到二维数据，先问清约定

表格、棋盘、图像像素、座位图和神经网络张量都会出现多维坐标。面试或设计讨论中，不要一上来只写公式，先说清：

- 行列分别代表什么，是否从 0 开始。
- 数据是行优先、列优先，还是由库决定。
- 是否允许空网格和长短不一的行。
- 形状不匹配、坐标越界时怎样失败。
- 要访问一个位置，还是扫描一行、一个区域或全部数据。

一个短而完整的回答可以是：“我会把形状作为接口契约，先验证 <code>rows * columns</code> 与数据长度，再检查行列边界，最后按约定布局计算位置；同时用首格、末格、空网格、坏形状和越界坐标补齐测试。”

</section>

## 完成检查

- [ ] 我能解释同一组值为什么在 <code>2 × 3</code> 和 <code>3 × 2</code> 中含义不同。
- [ ] 我能从行优先布局推导 <code>row * columns + column</code>，而不是只背公式。
- [ ] 我点过网格中的首格、末格和中间格，并核对坐标、下标和值。
- [ ] 我能分别检查形状、行边界和列边界。
- [ ] 我运行了完整 Python 例子，并核对行扫描次数。
- [ ] 我复现并解释了 Python 重复行引用问题。
- [ ] 我把同一组值改成 <code>3 × 2</code>，先手算再运行。
- [ ] 我为学习进度报告器设计了独立矩阵视图和三类测试，没有改坏主报告。
- [ ] 我知道 Python 嵌套列表不等同于底层连续二维数组。
- [ ] 我能用形状、布局、边界和操作范围说明一份二维数据接口。

## 来源与版本

- 适用版本：Python 3.11 及以上；示例只使用标准库。
- 核查日期：2026-07-17。
- 事实来源：[Python FAQ：怎样创建多维列表](https://docs.python.org/3.11/faq/programming.html#how-do-i-create-a-multidimensional-list)用于重复行引用与独立行创建；[Python 列表类型](https://docs.python.org/3.11/library/stdtypes.html#lists)用于列表、下标和可变序列语义；[Python 表达式参考](https://docs.python.org/3.11/reference/expressions.html#subscriptions)用于订阅与越界行为。
- 代码验证：仓库脚本检查两种形状、首尾坐标、负坐标、行列越界、坏形状、空网格、行扫描次数、输入不变和重复行引用；不联网、不安装第三方包。

## 下一步

四节 CS 起步到这里收口。下一课进入[动态数组容量、扩容成本与摊还分析](05-dynamic-array-capacity-amortized-cost.md)，开始共同算法与数据结构基础；如果你准备先走应用工程，也可以回到课程地图进入 Python 核心与工程化。

[进入下一课](05-dynamic-array-capacity-amortized-cost.md){ .md-button .md-button--primary }
[查看完整课程地图](../curriculum-map.md){ .md-button }
