# CS 起步：数据如何在程序中表示

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-cs-data-representation" aria-hidden="true"></div>

<section id="overview-data" class="be-sample-hero" data-learning-context="overview-data" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">CS 概念样板 · 不要求 C++</span>

## 一组数字，两种找法

今天只研究 `[2, 5, 3, 4]` 这四个数。知道位置时，程序可以直接取值；只知道要找什么时，它可能得一个个看过去。先把这两件事看明白，暂时不用背复杂度符号。

<div class="be-sample-actions" markdown="1">
[先看表示过程](#concept-representation){ .md-button .md-button--primary }
[直接操作扫描图](#example-scan){ .md-button }
</div>

</section>

<section id="concept-representation" class="be-sample-learning-unit" data-learning-context="concept-representation" data-context-type="concept" markdown="1">

## 程序怎样记住四天的学习时间

“四天分别学习了 2、5、3、4 小时”是一条现实信息。要让程序保存并处理它，我们可以写成：

```python
hours = [2, 5, 3, 4]
```

<div class="be-representation-ladder" role="img" aria-label="现实中的四天学习时长，变成 Python 中的四个整数，再按顺序组织为列表，程序由此可以按下标访问或逐项扫描。">
  <span>现实信息<br><b>四天时长</b></span>
  <i aria-hidden="true">→</i>
  <span>程序中的值<br><b>2、5、3、4</b></span>
  <i aria-hidden="true">→</i>
  <span>一种表示<br><b>[2, 5, 3, 4]</b></span>
  <i aria-hidden="true">→</i>
  <span>允许的操作<br><b>访问、扫描</b></span>
</div>

!!! abstract "先记住这个关系"
    数据怎样组织，会影响程序怎样读取它、怎样查找它，以及哪些位置可能出错。

</section>

<section id="concept-index" class="be-sample-learning-unit" data-learning-context="concept-index" data-context-type="concept" markdown="1">

## 下标从 0 开始

<div class="be-array-row" aria-label="列表值和下标对照">
  <div><span>下标 0</span><strong>2</strong></div>
  <div><span>下标 1</span><strong>5</strong></div>
  <div><span>下标 2</span><strong>3</strong></div>
  <div><span>下标 3</span><strong>4</strong></div>
</div>

```python
hours = [2, 5, 3, 4]
print(hours[2])
```

这里已经明确告诉程序“取下标 2”，所以它可以直接拿到值 `3`。如果问题变成“帮我找出 3 在哪里”，程序就得先寻找位置了。

!!! note "这张图不是内存布局图"
    方格只是帮助理解顺序和下标。Python 的 `list` 保存的是对象引用，还隐藏了扩容等实现细节；真实的内存结构会留到后面的系统课程。

</section>

<section id="example-access" class="be-sample-learning-unit" data-learning-context="example-access" data-context-type="example" markdown="1">

## 已知位置，直接取值

先预测下面三行：

```python
hours = [2, 5, 3, 4]
print(hours[0])
print(hours[-1])
print(len(hours))
```

??? question "预测后再展开"
    依次输出 `2`、`4`、`4`。`-1` 表示最后一个位置，`len(hours)` 是元素数量，不是最后一个有效下标。

如果把 `hours[0]` 改成 `hours[4]`，会发生什么？先别运行，把四个有效下标写出来再回答。

</section>

<section id="troubleshoot-boundary" class="be-sample-learning-unit" data-learning-context="troubleshoot-boundary" data-context-type="troubleshoot" markdown="1">

## 长度是 4，为什么不能访问下标 4

四个元素的有效下标是 `0、1、2、3`。访问 `hours[4]` 会触发：

```text
IndexError: list index out of range
```

遇到这个错误时，别只把数字减一碰碰运气。先检查有效范围：

```python
0 <= index < len(hours)
```

| 要检查的事实 | 当前值 |
| --- | ---: |
| `len(hours)` | 4 |
| 最小有效下标 | 0 |
| 最大有效下标 | 3 |
| 下标 4 是否满足边界 | 否 |

</section>

<section id="example-scan" class="be-sample-learning-unit" data-learning-context="example-scan" data-context-type="reproduce" markdown="1">

## 不知道位置，就一个个找

下面要找的是 `3`。每点一次“下一次比较”，程序就看一个位置，直到找到目标为止。开始前先猜一下：要比较几次？

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

无 JavaScript 时，完整轨迹仍然如下：

| 比较次数 | 下标 | 当前值 | 与目标 3 的关系 | 结果 |
| ---: | ---: | ---: | --- | --- |
| 1 | 0 | 2 | 不相等 | 继续 |
| 2 | 1 | 5 | 不相等 | 继续 |
| 3 | 2 | 3 | 相等 | 找到并停止 |

</section>

<section id="concept-cost" class="be-sample-learning-unit" data-learning-context="concept-cost" data-context-type="concept" markdown="1">

## 先数动作，再谈复杂度

对同一组数据：

- 已知位置 `2`：直接访问一次位置。
- 查找值 `3`：比较了三次才找到。
- 查找不存在的值 `9`：必须比较四次才能确认不存在。

现在不急着背 `O(1)` 或 `O(n)`。我更建议你先说清三件事：输入有多大，程序在重复什么动作，最坏时要重复多少次。符号只是把这些规律写得更短。

```python
target = 3
for index, value in enumerate(hours):
    if value == target:
        print("找到位置：", index)
        break
```

</section>

<section id="modify-data" class="be-sample-learning-unit" data-learning-context="modify-data" data-context-type="modify" markdown="1">

## 换一组数，再做一次

任选一组新的学习小时和目标值，例如：

```python
hours = [1, 4, 4, 7, 2]
target = 7
```

运行前先写下：

1. 第一个元素和最后一个元素分别是什么。
2. 目标第一次出现在哪个下标。
3. 顺序扫描需要比较几次。
4. 如果目标改成 `9`，最坏要比较几次。

写完预测再运行代码核对。猜错很正常，重要的是回头看看：是下标数错了，还是查找过程少算了一步。

</section>

<section id="project-records" class="be-sample-project-panel" data-learning-context="project-records" data-context-type="project" markdown="1">

## 报告器为什么需要多条记录

学习进度报告器 `v0.1` 只有一条档案。后续加入多门课程时，需要把多条记录组织起来，并执行汇总、查找和排序。

| 今天学到的 | 放进项目后解决什么 |
| --- | --- |
| 顺序表示 | 多条课程记录以固定顺序进入报告 |
| 下标访问 | 读取某个已知位置的记录 |
| 逐项扫描 | 找到某门课或汇总全部时长 |
| 边界 | 空记录、错误位置和目标不存在 |
| 操作成本 | 数据增加后，重复工作会怎样变化 |

等报告器开始管理多门课程，这些问题就会真正出现：记录怎样排、怎样找、空数据怎么办、数据多了以后要做多少次工作。后面的数据结构会继续回答这些问题。

</section>

??? info "新手补给：下标和第几个为什么总差一"
    日常说“第一个”通常从 1 开始，Python 下标从 0 开始。读代码时优先说“下标 0”，不要把它混成“第 0 个”。

??? note "深入理解：抽象会隐藏实现"
    Python `list` 已经替我们处理了很多底层细节，所以现在用起来很顺手。以后比较动态数组、链表和哈希时，我们会把这些被隐藏的取舍重新打开来看。

??? success "面试时怎样回答复杂度"
    别一上来只报一个符号。先说明数据规模和重复动作，再讲最好、最坏情况，最后给出复杂度结论。如果还有余力，再补充可以换什么结构。

## 完成检查

- [ ] 能区分现实信息、程序中的值和数据表示。
- [ ] 能解释列表长度与有效下标范围。
- [ ] 能比较已知位置访问和未知位置查找。
- [ ] 能复现并恢复一次 `IndexError`。
- [ ] 能用比较次数描述一次扫描成本。
- [ ] 能说明这些概念将怎样进入学习进度报告器。

下一页：[学习进度报告器阶段作品](study-progress-reporter.md)。
