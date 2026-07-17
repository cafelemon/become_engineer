# Python：变量、基本类型与输入输出

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-python-variables" aria-hidden="true"></div>

<section id="overview-profile" class="be-sample-hero" data-learning-context="overview-profile" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">编程起步样板 · 学习进度报告器 v0.1</span>

## 先看结果：一个会回应你的个人学习档案

这一页不会让你先背完四种类型。我们先理解下面三行信息如何进入程序，再通过预测、运行和修改把它做出来。

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

## 变量不是神秘盒子：它是值在程序里的名字

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

- 左边 `name` 是你给这个值起的名字。
- `=` 表示把右边的值赋给左边的名字。
- 引号说明 `"小码"` 是文本，也就是字符串 `str`。

先预测：下面程序会输出“小码”还是“贾飞”？

```python
name = "小码"
name = "贾飞"
print(name)
```

??? question "展开答案前先说出理由"
    输出 `贾飞`。第二次赋值后，名字 `name` 对应的当前值发生了变化。

</section>

<section id="example-types" class="be-sample-learning-unit" data-learning-context="example-types" data-context-type="example" markdown="1">

## 四种常见值，先看它们在解决什么问题

| 值 | Python 类型 | 适合表达 | 不适合误用为 |
| --- | --- | --- | --- |
| `"Python 起步"` | `str` | 名字、课程、路径等文本 | 可以直接计算的数字 |
| `5` | `int` | 次数、数量、整小时 | 带小数的比例 |
| `0.2` | `float` | 比例、测量值、小数 | 精确货币规则 |
| `True` | `bool` | 是／否、成立／不成立 | 带引号的普通文字 |

`type()` 可以让 Python 自己回答，而不是靠猜：

```python
weekly_hours = 5
print(type(weekly_hours))
```

预期输出：

```text
<class 'int'>
```

!!! tip "`True` 为什么没有引号"
    `True` 和 `False` 是 Python 的布尔值，首字母必须大写。写成 `"True"` 后，它只是四个字符组成的字符串。

</section>

<section id="reproduce-browser" class="be-sample-learning-unit" data-learning-context="reproduce-browser" data-context-type="reproduce" markdown="1">

## 微型复现：先预测，再在浏览器或本地运行

下面代码来自可执行源文件，而不是只存在于页面里：

```python
--8<-- "reviews/course-content/batch-a/examples/python-variables/profile_basic.py"
```

<div class="be-python-runner" data-python-runner data-python-source="examples/python-variables/profile_basic.py">
  <p class="be-python-runner__fallback">浏览器运行器需要 JavaScript 和网络。你仍可把上方代码保存为 <code>profile_basic.py</code>，执行 <code>python3 profile_basic.py</code>。</p>
</div>

本地运行：

```bash
cd reviews/course-content/batch-a/examples/python-variables
python3 profile_basic.py
```

第一次运行只检查三件事：命令正常结束、输出与预测一致、改动后重新运行能看到新值。

</section>

<section id="modify-profile" class="be-sample-learning-unit" data-learning-context="modify-profile" data-context-type="modify" markdown="1">

## 轮到你修改：让这份档案真正属于你

在浏览器运行器或本地文件中完成四处修改：

1. 把 `name` 改成你的昵称。
2. 把 `course` 改成你现在要学的内容。
3. 新增整数变量 `weekly_hours`。
4. 新增一个自选字段，例如 `goal`、`city` 或 `favorite_topic`，并输出它。

不要只看代码。修改后必须重新运行，并保存“代码 + 输出”作为证据。

<div class="be-sample-check" role="status">
  <strong>验收问题</strong>
  <span>如果把 <code>weekly_hours = 5</code> 改成 <code>weekly_hours = "5"</code>，屏幕看起来可能相似，但这个值还能直接加一吗？</span>
</div>

</section>

<section id="reproduce-input" class="be-sample-learning-unit" data-learning-context="reproduce-input" data-context-type="reproduce" markdown="1">

## 键盘输入先是文本，再由程序决定怎样解释

`input()` 会等待你输入并按回车。即使键入 `5`，它得到的仍然是字符串：

```python
weekly_hours_text = input("请输入本周计划小时：")
print(weekly_hours_text)
print(type(weekly_hours_text))
```

请在本地终端完成这一段，因为浏览器微型运行器故意不模拟交互输入：

```bash
cd reviews/course-content/batch-a/examples/python-variables
python3 profile_input.py
```

程序中的边界很清楚：

```text
键盘输入 "5"（str） → int("5") → 数字 5（int） → 可以参与计算
```

```python
weekly_hours = int(weekly_hours_text)
next_week_hours = weekly_hours + 1
```

先分别输入 `5` 和 `five`，不要急着修改代码。观察两次运行在哪一步开始不同。

</section>

<section id="troubleshoot-valueerror" class="be-sample-learning-unit" data-learning-context="troubleshoot-valueerror" data-context-type="troubleshoot" markdown="1">

## 保留错误现场：`ValueError` 在告诉你什么

输入 `five` 时会看到类似：

```text
ValueError: invalid literal for int() with base 10: 'five'
```

按这个顺序读，不要只复制最后一行去搜索：

1. **错误类型**：`ValueError`，操作本身存在，但收到的值不适合。
2. **文件和行号**：找到 `int(weekly_hours_text)` 所在行。
3. **输入证据**：这次变量里实际是字符串 `"five"`。
4. **恢复验证**：重新输入 `5`，程序正常输出下周建议。

本课只要求理解并定位错误。怎样给用户友好提示、怎样捕获异常，会在后面的错误与测试课程完成。

</section>

<section id="project-v01" class="be-sample-project-panel" data-learning-context="project-v01" data-context-type="project" markdown="1">

## 项目里程碑：学习进度报告器 v0.1

你现在拥有的不是完整报告系统，而是一条可以继续演进的数据线：

| 上一状态 | 本课增量 | 保存证据 | 下一版本 |
| --- | --- | --- | --- |
| 只有学习工作区 | 一条带名字、课程和计划小时的记录 | `profile_basic.py` 与一次运行输出 | 用条件表达“进行中／已完成” |

后续课程不会抛弃这份数据：条件会判断状态，函数会封装报告，多条记录会进入容器，JSON 会把数据移到文件，测试会固定行为。

[查看完整版本线](study-progress-reporter.md){ .md-button .md-button--primary }

</section>

??? info "新手补给：`python` 还是 `python3`"
    先执行 `python3 --version`；Windows 也可尝试 `python --version`。选择能显示 Python 3.11 或更高版本的命令，并在整节课中保持一致。

??? note "深入理解：类型属于值，不属于变量名"
    Python 名字可以在不同时间指向不同类型的值，但这不等于随意混用类型是好设计。清楚的名字、稳定的数据契约和后续类型检查会让程序更容易维护。

??? success "求职训练：不要只背四种类型"
    更有价值的表达是：说明输入边界为什么先得到字符串、在哪里转换、非法值怎样被定位，以及你用什么运行证据证明判断正确。

## 完成检查

- [ ] 能用自己的话解释变量、值和类型的关系。
- [ ] 能运行并主动修改个人学习档案。
- [ ] 能用 `type()` 验证四种常见值。
- [ ] 能解释 `input()` 与 `int()` 的边界。
- [ ] 能定位并恢复一次 `ValueError`。
- [ ] 保存 `v0.1` 代码和运行输出。

下一页：[CS：数据如何在程序中表示](cs-data-representation.md)。

