<div class="be-tutor-mount" data-tutor-lesson="cs-core-01" aria-hidden="true"></div>

<section id="overview-data" class="be-page-hero be-lesson-hero" data-learning-context="overview-data" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">CS 起步 · 第一课 · 不要求 C++</span>

# 序列接口、数组表示与安全边界

## 一组数字，两种找法

今天只研究 <code>[2, 5, 3, 4]</code> 这四个数。

已经知道位置 2 时，程序可以直接取到 3；只知道“帮我找出 3”时，它要从前往后比较，第三次才找到。前者使用位置，后者寻找位置。这个差别会一路连接到数据结构、算法和程序性能。

这里先不背复杂度符号，也不实现底层数组。我们从 Python 已经会读的代码出发，把“数据怎样组织、程序做了几次动作、哪里会越界”想清楚。

<div class="be-page-actions" markdown="1">
[先看数据怎样进入程序](#concept-representation){ .md-button .md-button--primary }
[直接操作扫描图](#reproduce-scan){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>CS 起步 · 1 / 4</strong></div>
  <div><span>前置</span><strong>Python 起步；不要求 C++</strong></div>
  <div><span>完成后留下</span><strong>访问、扫描、边界与比较次数记录</strong></div>
</div>

## 开始前

- 能读懂 Python 列表、<code>for</code> 循环、<code>if</code> 和函数返回值。
- 已完成学习进度报告器 v1.0，见过多条课程记录的汇总。
- 这一课只讨论语言公开提供的序列行为，不把方格图冒充真实内存布局。
- C++ 连续容器、裸数组和跨语言边界会在系统方向出现，不是进入 CS 的前置。

<section id="concept-representation" data-learning-context="concept-representation" data-context-type="concept" markdown="1">

## 程序怎样记住四天的学习时间

“四天分别学习了 2、5、3、4 小时”是现实中的信息。要让程序保存并处理它，可以写成：

~~~python
hours = [2, 5, 3, 4]
~~~

<div class="be-representation-ladder" role="img" aria-label="现实中的四天学习时长，变成程序中的四个整数，再按顺序组织为 Python 列表，由此可以按下标访问或逐项扫描。">
  <span>现实信息<br><b>四天时长</b></span>
  <i aria-hidden="true">→</i>
  <span>程序中的值<br><b>2、5、3、4</b></span>
  <i aria-hidden="true">→</i>
  <span>一种表示<br><b>[2, 5, 3, 4]</b></span>
  <i aria-hidden="true">→</i>
  <span>允许的操作<br><b>访问、扫描</b></span>
</div>

数据是我们想表达的信息，表示是程序组织这些信息的方式。同一组时长也可以写进 JSON、元组或数据库表。表示不同，读取、修改和查找的方法会跟着变化。

先记住一句话：数据怎样组织，会影响程序能做哪些操作，以及完成这些操作需要多少工作。

</section>

<section id="concept-interface" data-learning-context="concept-interface" data-context-type="concept" markdown="1">

## 先说能做什么，再问底层怎样存

这一课把以下能力叫作“序列接口”：

- 取得元素数量。
- 按位置读取一个值。
- 从前往后逐项遍历。
- 判断某个值是否出现。
- 复制一份后再修改。

接口说的是“能做什么”。具体实现才回答“值怎样存、空间怎样增长、插入时要移动什么”。

Python <code>list</code> 提供可变序列能力，但不能直接描述成 C 或 C++ 的同类型原始数组。方格图只帮助我们看顺序与下标；Python 对象、引用和扩容等实现细节暂时由语言隐藏。

这个区分很重要。后面比较动态数组、链表和哈希时，我们会先固定需要的操作，再比较不同表示怎样实现以及成本有何差异。

</section>

<section id="concept-index" data-learning-context="concept-index" data-context-type="concept" markdown="1">

## 下标从 0 开始

<div class="be-array-row" aria-label="列表值和下标对照">
  <div><span>下标 0</span><strong>2</strong></div>
  <div><span>下标 1</span><strong>5</strong></div>
  <div><span>下标 2</span><strong>3</strong></div>
  <div><span>下标 3</span><strong>4</strong></div>
</div>

~~~python
hours = [2, 5, 3, 4]
print(hours[2])
~~~

输出是 3。列表有 4 个元素，有效非负下标却是 0、1、2、3，因此通用边界条件是：

~~~python
0 <= index < len(hours)
~~~

日常说“第三个”，代码写“下标 2”。读代码时尽量说清“第几个”还是“下标几”，很多差一错误就会少一半。

Python 还支持负下标，<code>hours[-1]</code> 表示最后一项。它是合法语言语义，不是越界。本课讲边界时会同时区分非负范围和 Python 自带的负下标约定。

</section>

<section id="example-access" data-learning-context="example-access" data-context-type="example" markdown="1">

## 已知位置，直接取值

先预测，再运行：

~~~python
hours = [2, 5, 3, 4]

print(hours[0])
print(hours[2])
print(hours[-1])
print(len(hours))
~~~

依次输出 2、3、4、4。

这里已经把位置告诉程序，所以只发生一次指定位置的读取。<code>len(hours)</code> 是元素数量，不是最后一个有效下标。

如果把 <code>hours[2]</code> 改成 <code>hours[4]</code>，会发生什么？先写出所有非负有效下标，再运行确认。

</section>

<section id="troubleshoot-boundary" data-learning-context="troubleshoot-boundary" data-context-type="troubleshoot" markdown="1">

## 长度是 4，为什么不能访问下标 4

访问 <code>hours[4]</code> 会触发：

~~~text
IndexError: list index out of range
~~~

遇到它时，先记录两个数：

| 要检查的事实 | 当前值 |
| --- | ---: |
| <code>index</code> | 4 |
| <code>len(hours)</code> | 4 |
| 是否满足 <code>0 <= index < len(hours)</code> | 否 |

别只把数字减一碰碰运气。你原本可能是想取最后一项，也可能真的少放了一条数据。先确认代码意图，再改下标或数据。

边界不只发生在访问时：

- 空列表没有下标 0。
- 扫描到末尾仍没找到时，需要返回明确的“未找到”。
- 切片的边界规则与单项索引不同，暂时不要混在一起。
- Python 负下标合法，但跨语言接口可能主动采用更窄的非负约定；那是接口选择，不是说 Python 错了。

</section>

<section id="reproduce-scan" data-learning-context="reproduce-scan" data-context-type="reproduce" markdown="1">

## 不知道位置，就一个个找

下面要找的是 3。每点一次“下一次比较”，程序看一个位置，直到找到目标。开始前先猜：要比较几次？

<div class="be-scan-demo" data-scan-demo data-values="2,5,3,4" data-target="3">
  <div class="be-scan-demo__header">
    <span>目标值 <strong data-scan-target>3</strong></span>
    <span>比较次数 <strong data-scan-count>0</strong></span>
  </div>
  <div class="be-scan-demo__cells" data-scan-cells aria-live="polite"></div>
  <p class="be-scan-demo__message" data-scan-message>还没开始。先猜一猜要比较几次。</p>
  <div class="be-scan-demo__controls">
    <button type="button" data-scan-prev>上一次</button>
    <button type="button" data-scan-next>下一次比较</button>
    <button type="button" data-scan-reset>重置</button>
  </div>
</div>

禁用 JavaScript 时，完整轨迹仍然可以直接读：

| 比较次数 | 下标 | 当前值 | 与目标 3 的关系 | 结果 |
| ---: | ---: | ---: | --- | --- |
| 1 | 0 | 2 | 不相等 | 继续 |
| 2 | 1 | 5 | 不相等 | 继续 |
| 3 | 2 | 3 | 相等 | 找到并停止 |

完整 Python 例子：

~~~python
--8<-- "examples/cs-start/data_representation.py"
~~~

~~~bash
python site-src/examples/cs-start/data_representation.py
~~~

它还查找不存在的 9，并安全复现一次 <code>IndexError</code>。对不存在的目标，扫描必须看完四个值才能确认“没有”。

</section>

<section id="concept-cost" data-learning-context="concept-cost" data-context-type="concept" markdown="1">

## 先数动作，再谈复杂度

对同一组数据：

| 问题 | 程序已经知道什么 | 重复动作 |
| --- | --- | --- |
| 读取下标 2 | 已知位置 | 一次指定位置读取 |
| 查找值 3 | 只知道目标值 | 比较 2、5、3，共 3 次 |
| 查找值 9 | 目标不存在 | 比较全部 4 项 |

现在不急着背 <code>O(1)</code> 和 <code>O(n)</code>。我更建议先回答：

1. 输入有多少项？
2. 程序在重复什么动作？
3. 最好什么时候停？
4. 最坏要做多少次？

下一课会让数据规模变大，观察比较次数怎样增长，再把规律写成复杂度。

第一次匹配的契约也在这里出现。数据中如果有两个 3，程序在第一个相等处停止；调用者能稳定得到第一个位置，比较次数也有明确含义。

</section>

<section id="modify-data" data-learning-context="modify-data" data-context-type="modify" markdown="1">

## 换一组数，再做一次

把数据和目标都换掉：

~~~python
hours = [1, 4, 4, 7, 2]
target = 7
~~~

运行前写下：

1. 第一个与最后一个值。
2. 目标第一次出现的下标。
3. 找到目标需要比较几次。
4. 目标换成 9 时，最坏比较几次。
5. 访问 <code>hours[len(hours)]</code> 会发生什么。

然后修改例子并运行核对。示例验证脚本会确认查找 7 得到下标 3、比较 4 次；查找 9 返回未找到、比较 5 次。

再做一个复制练习：

~~~python
copied = hours.copy()
copied[0] = 8

print(hours)
print(copied)
~~~

原列表与副本应不同。只检查新值还不够，也要确认原输入没有被偷偷修改。

</section>

<section id="project-records" data-learning-context="project-records" data-context-type="project" markdown="1">

## 把报告器当成一组数据来看

学习进度报告器 v1.0 已经保存多条课程记录。现在暂时不改项目代码，只重新观察它：

| 今天学到的 | 报告器中的对应问题 |
| --- | --- |
| 顺序表示 | 多条课程记录按什么顺序进入报告 |
| 下标访问 | 已知位置时怎样读取某条记录 |
| 逐项扫描 | 汇总全部时长、查找一门课程 |
| 边界 | 空记录、错误位置、目标不存在 |
| 操作成本 | 记录变多后，汇总和查找要做多少次 |

打开报告器的 <code>analysis.py</code>，找到遍历 <code>records</code> 的循环。每处理一条记录，就记一次“扫描动作”。记录从 3 条增加到 30 条时，这个循环会做多少次？

这次产出不是新功能，而是一张“项目数据与操作清单”：数据是什么表示、有哪些操作、每个操作最坏会检查多少项。它会成为后面选择数据结构的依据。

</section>

<section id="deepen-abstraction" data-learning-context="deepen-abstraction" data-context-type="deepen" markdown="1">

## 图很有用，但别把图当成实现

四个方格让下标一眼可见，但没有证明 Python 整数本身连续排在内存中。抽象会隐藏实现细节，让我们先可靠使用接口；需要比较内存、扩容和插入成本时，再打开相应实现。

同样，“数组访问很快”也需要前提：已经知道合法位置，并使用支持按位置访问的表示。若位置未知，程序仍要先查找；若输入不合法，先做边界检查。

表达结论时带上前提，比背一句“数组查询快”更准确。

</section>

<section id="career-complexity" data-learning-context="career-complexity" data-context-type="career" markdown="1">

## 被问到“这个查找有多快”时

不要只报一个符号。先讲过程：

- 输入是一组 n 个值。
- 查找只知道目标，不知道位置。
- 从头比较，找到第一个相等就停止。
- 最好第一次就找到；最坏要看完 n 项。
- 因此比较次数会随数据量一起增长。

如果题目改成“读取已知下标”，过程与结论都会改变。面试表达的价值不在记住字母，而在能说明输入、动作、停止条件和最坏情况。

</section>

## 完成检查

- [ ] 我能区分现实信息、程序中的值和数据表示。
- [ ] 我能说明接口讲“能做什么”，实现讲“怎样存和完成操作”。
- [ ] 我没有把 Python <code>list</code> 方格图当成真实内存布局。
- [ ] 我能解释列表长度、非负有效下标和 Python 负下标。
- [ ] 我复现并恢复了一次 <code>IndexError</code>。
- [ ] 我操作了扫描轨迹，也能在无 JavaScript 表格中读出相同过程。
- [ ] 我运行了固定 Python 例子。
- [ ] 我换了一组数据，先预测，再核对下标和比较次数。
- [ ] 我用返回值和原输入同时检查了一次复制修改。
- [ ] 我能从报告器中指出一次下标访问和一次逐项扫描。
- [ ] 我能用输入、重复动作和最坏次数描述查找成本。

## 来源与版本

- 适用版本：Python 3.11 及以上；示例只使用标准库。
- 核查日期：2026-07-17。
- 事实来源：[Python 序列类型](https://docs.python.org/3.11/library/stdtypes.html#sequence-types-list-tuple-range)用于索引、负索引、长度与可变序列语义；[Python 数据结构教程](https://docs.python.org/3.11/tutorial/datastructures.html)用于列表操作与遍历；[MIT 6.006 数据结构与动态数组](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-2-data-structures-and-dynamic-arrays/)用于接口、表示与操作成本的课程边界。
- 代码验证：仓库脚本检查固定访问、首次匹配、目标不存在、IndexError 和替换数据；扫描播放器提供前进、后退、重置和完整静态轨迹。

## 下一步

进入[操作计数、增长率与渐近复杂度](02-operation-count-growth-asymptotic-complexity.md)，把今天的 1、3、4 次动作扩展到更大的输入，再理解 <code>O(1)</code>、<code>O(n)</code> 和增长趋势。

[进入下一课](02-operation-count-growth-asymptotic-complexity.md){ .md-button .md-button--primary }


