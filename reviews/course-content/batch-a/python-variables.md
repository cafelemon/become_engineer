# Python：变量、基本类型与输入输出

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-python-variables" aria-hidden="true"></div>

<section id="overview-profile" class="be-sample-hero" data-learning-context="overview-profile" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">编程起步样板 · 学习进度报告器 v0.1</span>

## 先让程序介绍一下你

下面这几行就是今天要完成的小程序。它会记住你的昵称、正在学的课程和本周计划。先看结果，等会儿我们再把每一行拆开。

```text
学习档案
昵称： 小码
课程： Python 起步
本周计划： 5 小时
```

<div class="be-sample-actions" markdown="1">
[先理解变量](#concept-variable){ .md-button .md-button--primary }
[查看项目版本线](study-progress-reporter.md){ .md-button }
</div>

</section>

<section id="concept-variable" class="be-sample-learning-unit" data-learning-context="concept-variable" data-context-type="concept" markdown="1">

## 变量就是给值起一个名字

<div class="be-variable-model" role="img" aria-label="变量模型：变量名 name 通过赋值指向字符串值 小码，这个值的类型是 str。">
  <div><span>变量名</span><strong>name</strong></div>
  <b aria-hidden="true">=</b>
  <div><span>当前值</span><strong>"小码"</strong></div>
  <b aria-hidden="true">→</b>
  <div><span>值的类型</span><strong>str</strong></div>
</div>

```python
name = "小码"
```

- 左边的 `name` 是名字。
- `=` 把右边的值交给这个名字。
- 引号说明 `"小码"` 是一段文本，Python 把这类值叫作字符串 `str`。

先预测：下面程序会输出“小码”还是“贾飞”？

```python
name = "小码"
name = "贾飞"
print(name)
```

??? question "先说出答案，再展开"
    输出 `贾飞`。第二次赋值后，名字 `name` 对应的当前值发生了变化。

</section>

<section id="example-types" class="be-sample-learning-unit" data-learning-context="example-types" data-context-type="example" markdown="1">

## 四种常见的值

| 值 | Python 类型 | 适合表达 | 不适合误用为 |
| --- | --- | --- | --- |
| `"Python 起步"` | `str` | 名字、课程、路径等文本 | 可以直接计算的数字 |
| `5` | `int` | 次数、数量、整小时 | 带小数的比例 |
| `0.2` | `float` | 比例、测量值、小数 | 精确货币规则 |
| `True` | `bool` | 是／否、成立／不成立 | 带引号的普通文字 |

拿不准一个值是什么类型时，可以直接问 Python：

```python
weekly_hours = 5
print(type(weekly_hours))
```

预期输出：

```text
<class 'int'>
```

!!! tip "`True` 为什么没有引号"
    `True` 和 `False` 表示“是”和“否”，首字母必须大写。加上引号以后，`"True"` 就变成了普通文本，不再是布尔值。

</section>

<section id="reproduce-browser" class="be-sample-learning-unit" data-learning-context="reproduce-browser" data-context-type="reproduce" markdown="1">

## 先猜输出，再运行

先读一遍下面的代码，猜猜它会打印几行、每行是什么。想好以后再点运行：

```python
--8<-- "reviews/course-content/batch-a/examples/python-variables/profile_basic.py"
```

<div class="be-python-runner" data-python-runner data-python-source="../examples/python-variables/profile_basic.py">
  <p class="be-python-runner__fallback">浏览器运行器需要 JavaScript 和网络。你仍可把上方代码保存为 <code>profile_basic.py</code>，执行 <code>python3 profile_basic.py</code>。</p>
</div>

本地运行：

```bash
cd reviews/course-content/batch-a/examples/python-variables
python3 profile_basic.py
```

第一次运行不用想得太复杂：命令没有报错，输出和刚才猜的一样，就可以继续。如果不一样，回到代码逐行看看是哪一处理解错了。

</section>

<section id="modify-profile" class="be-sample-learning-unit" data-learning-context="modify-profile" data-context-type="modify" markdown="1">

## 把它改成你的学习档案

在浏览器运行器或本地文件中完成四处修改：

1. 把 `name` 改成你的昵称。
2. 把 `course` 改成你现在要学的内容。
3. 新增整数变量 `weekly_hours`。
4. 新增一个自选字段，例如 `goal`、`city` 或 `favorite_topic`，并输出它。

改完记得重新运行。把代码和这次输出一起保存下来，以后回看时才知道当时的程序真的跑到了哪一步。

<div class="be-sample-check" role="status">
  <strong>想一想</strong>
  <span>如果把 <code>weekly_hours = 5</code> 改成 <code>weekly_hours = "5"</code>，屏幕看起来可能相似，但这个值还能直接加一吗？</span>
</div>

</section>

<section id="reproduce-input" class="be-sample-learning-unit" data-learning-context="reproduce-input" data-context-type="reproduce" markdown="1">

## 为什么输入 `5`，得到的却是文字

`input()` 会停下来等你输入。即使键盘上敲的是 `5`，Python 收到的也会先是一段字符串：

```python
weekly_hours_text = input("请输入本周计划小时：")
print(weekly_hours_text)
print(type(weekly_hours_text))
```

这一段请放到本地终端运行。页面里的小运行器不模拟键盘输入：

```bash
cd reviews/course-content/batch-a/examples/python-variables
python3 profile_input.py
```

从键盘到计算，中间多了一次转换：

```text
键盘输入 "5"（str） → int("5") → 数字 5（int） → 可以参与计算
```

```python
weekly_hours = int(weekly_hours_text)
next_week_hours = weekly_hours + 1
```

分别输入一次 `5` 和 `five`。先别急着修，看看两次运行从哪一行开始走向不同的结果。

</section>

<section id="troubleshoot-valueerror" class="be-sample-learning-unit" data-learning-context="troubleshoot-valueerror" data-context-type="troubleshoot" markdown="1">

## 遇到 `ValueError`，先读它

输入 `five` 时会看到类似：

```text
ValueError: invalid literal for int() with base 10: 'five'
```

别急着关掉终端。按下面的顺序读一遍：

1. **错误类型**：`ValueError`，操作本身存在，但收到的值不适合。
2. **文件和行号**：找到 `int(weekly_hours_text)` 所在行。
3. **当时的输入**：变量里实际装着字符串 `"five"`。
4. **再试一次**：重新输入 `5`，程序应该能继续计算。

这里先学会看懂错误、找到出错的那一行。怎样接住异常并给用户更友好的提示，后面会专门讲。

</section>

<section id="project-v01" class="be-sample-project-panel" data-learning-context="project-v01" data-context-type="project" markdown="1">

## 报告器的第一个版本：v0.1

现在的程序只会处理一条学习档案，但这条记录会一直保留下来，后面每节课都在它的基础上继续加功能：

| 原来会什么 | 这节课加了什么 | 留下什么 | 接下来做什么 |
| --- | --- | --- | --- |
| 只有学习工作区 | 一条带名字、课程和计划小时的记录 | `profile_basic.py` 与一次运行输出 | 用条件表达“进行中／已完成” |

下一课会用条件判断学习状态，之后再把逻辑放进函数、处理多条记录、把数据写进 JSON，最后用测试保护已经完成的功能。

[查看完整版本线](study-progress-reporter.md){ .md-button .md-button--primary }

</section>

??? info "新手补给：`python` 还是 `python3`"
    先执行 `python3 --version`；Windows 也可尝试 `python --version`。选择能显示 Python 3.11 或更高版本的命令，并在整节课中保持一致。

??? note "深入理解：类型属于值，不属于变量名"
    Python 允许同一个名字在不同时刻指向不同类型的值，但我不建议为了省事随意混用。名字越清楚、数据变化越稳定，后面排错就越轻松。

??? success "面试时别只背四种类型"
    如果被问到输入和类型，可以结合这段程序讲：`input()` 为什么返回字符串、转换写在哪里、非法输入会出现什么错误，以及你怎样复现并定位它。

## 完成检查

- [ ] 能用自己的话解释变量、值和类型的关系。
- [ ] 能运行并主动修改个人学习档案。
- [ ] 能用 `type()` 验证四种常见值。
- [ ] 能解释 `input()` 与 `int()` 的边界。
- [ ] 能定位并恢复一次 `ValueError`。
- [ ] 保存 `v0.1` 代码和运行输出。

下一页：[CS：数据如何在程序中表示](cs-data-representation.md)。
