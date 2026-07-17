# CS 起步：数据如何在程序中表示

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-cs-data-representation" aria-hidden="true"></div>

<section id="overview-data" class="be-sample-hero" data-learning-context="overview-data" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">CS 概念样板 · 不要求 C++</span>

## 同一组学习小时，程序为什么能“按位置取值”也能“逐个查找”？

我们从 `[2, 5, 3, 4]` 出发，不实现容器、不背复杂度符号。先看清数据怎样表示、操作怎样发生、边界怎样失败，再数一数程序实际做了几次比较。

<div class="be-sample-actions" markdown="1">
[先看表示过程](#concept-representation){ .md-button .md-button--primary }
[直接操作扫描图](#example-scan){ .md-button }
</div>

</section>

<section id="concept-representation" class="be-sample-learning-unit" data-learning-context="concept-representation" data-context-type="concept" markdown="1">

## 数据与表示不是一回事

“四天分别学习了 2、5、3、4 小时”是现实信息。程序需要一种明确表示，才能保存和操作它：

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

!!! abstract "本课的第一个 CS 观点"
    选择一种数据表示，也就选择了一组容易执行的操作和需要处理的边界。

</section>

<section id="concept-index" class="be-sample-learning-unit" data-learning-context="concept-index" data-context-type="concept" markdown="1">

## 位置从 0 开始：下标是程序中的地址标签

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

程序已经知道“位置 2”，所以可以直接取得值 `3`。这和“我不知道 3 在哪里，请帮我找”是两类不同问题。

!!! note "Python `list` 的准确边界"
    本图解释的是语言层的顺序和下标，不声称 Python `list` 是“连续存放同类型原始值的数组”。它保存对象引用并隐藏了很多实现细节；底层内存会在后续系统课程展开。

</section>

<section id="example-access" class="be-sample-learning-unit" data-learning-context="example-access" data-context-type="example" markdown="1">

## 微型例子：已知位置时，程序做了什么

先预测下面三行：

```python
hours = [2, 5, 3, 4]
print(hours[0])
print(hours[-1])
print(len(hours))
```

??? question "预测后再展开"
    依次输出 `2`、`4`、`4`。`-1` 表示最后一个位置，`len(hours)` 是元素数量，不是最后一个有效下标。

把 `hours[0]` 改成 `hours[4]`，会发生什么？不要先运行，先用“元素数量”和“有效下标范围”解释。

</section>

<section id="troubleshoot-boundary" class="be-sample-learning-unit" data-learning-context="troubleshoot-boundary" data-context-type="troubleshoot" markdown="1">

## 边界实验：为什么长度是 4，却没有下标 4

四个元素的有效下标是 `0、1、2、3`。访问 `hours[4]` 会触发：

```text
IndexError: list index out of range
```

恢复时不要直接“减一试试”，而是先写出边界：

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

<section id="example-scan" class="be-sample-learning-unit" data-learning-context="example-scan" data-context-type="example" markdown="1">

## 不知道位置时：程序只能按规则寻找

下面的播放器查找目标值 `3`。每点一次“下一次比较”，程序访问一个位置并判断是否命中。

<div class="be-scan-demo" data-scan-demo data-values="2,5,3,4" data-target="3">
  <div class="be-scan-demo__header">
    <span>目标值 <strong data-scan-target>3</strong></span>
    <span>比较次数 <strong data-scan-count>0</strong></span>
  </div>
  <div class="be-scan-demo__cells" data-scan-cells aria-live="polite"></div>
  <p class="be-scan-demo__message" data-scan-message>还没有开始。先预测要比较几次。</p>
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

## 第一个操作成本模型：先数动作，再学习符号

对同一组数据：

- 已知位置 `2`：直接访问一次位置。
- 查找值 `3`：比较了三次才找到。
- 查找不存在的值 `9`：必须比较四次才能确认不存在。

现在还不需要背 `O(1)` 或 `O(n)`。先形成更可靠的习惯：**说清输入是什么、程序重复了哪个动作、最坏情况下会重复多少次。**

```python
target = 3
for index, value in enumerate(hours):
    if value == target:
        print("找到位置：", index)
        break
```

</section>

<section id="modify-data" class="be-sample-learning-unit" data-learning-context="modify-data" data-context-type="modify" markdown="1">

## 轮到你修改：让预测先于运行

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

再把数据填入自己的 Python 文件，通过实际输出验证。预测错了不等于失败；不能解释为什么错，才说明模型还没有建立。

</section>

<section id="project-records" class="be-sample-project-panel" data-learning-context="project-records" data-context-type="project" markdown="1">

## 回到项目：一条记录为什么会变成多条记录

学习进度报告器 `v0.1` 只有一条档案。后续加入多门课程时，需要把多条记录组织起来，并执行汇总、查找和排序。

| 本课概念 | 项目里的真实问题 |
| --- | --- |
| 顺序表示 | 多条课程记录以固定顺序进入报告 |
| 下标访问 | 读取某个已知位置的记录 |
| 逐项扫描 | 找到某门课或汇总全部时长 |
| 边界 | 空记录、错误位置和目标不存在 |
| 操作成本 | 数据增加后，重复工作会怎样变化 |

本课没有提前实现高级数据结构，而是让你在遇到项目需求时知道：表示方式、操作和成本是连在一起的。

</section>

??? info "新手补给：下标和第几个为什么总差一"
    日常说“第一个”通常从 1 开始，Python 下标从 0 开始。读代码时优先说“下标 0”，不要把它混成“第 0 个”。

??? note "深入理解：抽象会隐藏实现"
    Python `list` 给你统一的下标、追加和遍历接口。后续课程会比较动态数组、链表、哈希等表示怎样改变操作成本。

??? success "求职训练：复杂度回答从证据开始"
    面试中不要只报一个符号。先说明数据规模、核心重复动作、最好／最坏情况，再给复杂度结论和替代结构。

## 完成检查

- [ ] 能区分现实信息、程序中的值和数据表示。
- [ ] 能解释列表长度与有效下标范围。
- [ ] 能比较已知位置访问和未知位置查找。
- [ ] 能复现并恢复一次 `IndexError`。
- [ ] 能用比较次数描述一次扫描成本。
- [ ] 能说明这些概念将怎样进入学习进度报告器。

下一页：[学习进度报告器阶段作品](study-progress-reporter.md)。

