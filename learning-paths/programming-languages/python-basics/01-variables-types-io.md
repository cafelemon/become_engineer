# 变量、基本类型、输入输出

<div class="be-tutor-mount" data-tutor-lesson="python-basics-01" aria-hidden="true"></div>

本节是 Python 起步的第一课。你不会先背完变量和类型，而是连续完成一个可以运行的“个人学习档案”。每一步都只引入当前任务需要的知识，并立刻用输出或错误信息检查结果。

## 本节产出

完成后，你将拥有一个能够接收输入、保存学习信息、计算计划并输出结果的 `learning_profile.py`，同时保留一次成功运行和一次失败排查记录。

<div class="be-lesson-goals" markdown="1">

- **首次反馈**：10 分钟内运行第一个版本。
- **主动修改**：改变昵称、课程和计划，观察输出同步变化。
- **失败练习**：故意触发并定位一次 `ValueError`。
- **迁移验收**：独立增加一个字段，而不是照抄固定答案。

</div>

## 开始前检查

- 已完成[工程基础入门](../../engineering-foundation/stage-0/README.md)。
- 能用编辑器创建 `.py` 文件，并在终端进入文件所在目录。
- 执行 `python3 --version` 能显示版本；Windows 也可以使用 `python --version`。

本节只使用 Python 标准库，不需要安装第三方依赖。下面命令默认使用 `python3`，如果你的环境只有 `python`，请统一替换。

## 七步任务路线

<div class="be-task-route" role="list" aria-label="本课七步任务">
  <span role="listitem">1 首次运行</span>
  <span role="listitem">2 主动修改</span>
  <span role="listitem">3 认识类型</span>
  <span role="listitem">4 接收输入</span>
  <span role="listitem">5 转换计算</span>
  <span role="listitem">6 定位错误</span>
  <span role="listitem">7 迁移验收</span>
</div>

<section id="step-1" class="be-task-step" data-step-id="step-1" markdown="1">

## 第一步：先让学习档案运行起来

**当前任务：** 创建 `learning_profile.py`，复制下面的第一个版本并运行。现在不用先理解每一行。

**文件：`learning_profile.py`**

```python
name = "Lemon"
course = "Python 起步"

print("学习档案")
print("昵称：", name)
print("课程：", course)
```

**运行：**

```bash
python3 learning_profile.py
```

**预期输出：**

```text
学习档案
昵称： Lemon
课程： Python 起步
```

**即时反馈：** 文件存在、命令正常结束、三行输出一致，就说明第一次闭环完成了。先记录文件名、命令和输出，再继续。

??? tip "提示一：命令提示找不到文件"
    先用 `pwd` 或 Windows PowerShell 的 `Get-Location` 确认当前位置，再用 `ls` 或 `dir` 确认当前目录里能看到 `learning_profile.py`。

??? tip "提示二：运行后没有最新内容"
    确认编辑器已经保存文件，再重新运行命令。编辑器标签上的圆点通常表示尚未保存。

??? example "局部示例"
    如果文件放在 `python-study` 目录，先进入它：`cd python-study`，再执行运行命令。

</section>

<section id="step-2" class="be-task-step" data-step-id="step-2" markdown="1">

## 第二步：修改昵称和课程

**当前任务：** 把 `Lemon` 和 `Python 起步` 改成你自己的内容，再次运行。

刚才使用了两个变量：

```python
name = "Lemon"
course = "Python 起步"
```

变量可以理解为给一个值起名字。等号左边是变量名，右边是当前保存的值。文本需要放在引号中，这种值叫字符串。

**必须主动修改：**

- 将 `name` 改成你的昵称。
- 将 `course` 改成你正在学习的内容。
- 再增加一行 `print()`，输出一句自己的学习目标。

**成功标准：** 三处修改都能在终端输出中看到，而不是只改了代码但没有重新运行。

??? tip "提示一：文本为什么需要引号"
    没有引号时，Python 会把内容当作变量名查找。普通文字应写成 `"文字"`。

??? tip "提示二：新增输出放在哪里"
    可以在最后一行下面继续调用 `print()`，括号中放要显示的字符串。

??? example "局部示例"
    `print("目标：完成第一个可运行程序")`

</section>

<section id="step-3" class="be-task-step" data-step-id="step-3" markdown="1">

## 第三步：给档案增加不同类型的数据

**当前任务：** 在文件顶部增加三个变量，并在末尾输出它们。

```python
weekly_hours = 5
completion_rate = 0.2
foundation_finished = True
```

```python
print("本周计划小时：", weekly_hours)
print("当前完成比例：", completion_rate)
print("是否完成工程基础：", foundation_finished)
```

这里出现了四种起步阶段最常用的类型：

| 类型 | 当前示例 | 适合表达 |
| --- | --- | --- |
| 字符串 `str` | `"Python 起步"` | 名字、课程、路径等文本 |
| 整数 `int` | `5` | 次数、数量、整小时 |
| 浮点数 `float` | `0.2` | 比例、价格、带小数的数 |
| 布尔值 `bool` | `True` | 是或否、成立或不成立 |

用下面的临时输出检查类型：

```python
print(type(course))
print(type(weekly_hours))
print(type(completion_rate))
print(type(foundation_finished))
```

**必须主动修改：** 改变计划小时和完成比例，确认值和类型分别发生了什么变化。

**成功标准：** 能指出四个变量分别保存什么类型，并解释为什么 `True` 没有引号且首字母必须大写。

??? tip "提示一：先看值的外形"
    有引号的文本通常是字符串；不带小数点的数字是整数；带小数点的是浮点数；`True` 和 `False` 是布尔值。

??? tip "提示二：检查而不是猜"
    在不确定时调用 `type(变量名)`，再用 `print()` 显示检查结果。

??? example "局部示例"
    `print(type(weekly_hours))` 应显示 `<class 'int'>`。

</section>

<section id="step-4" class="be-task-step" data-step-id="step-4" markdown="1">

## 第四步：让档案接收输入

**当前任务：** 把固定昵称和课程替换为运行时输入。

```python
name = input("请输入昵称：")
course = input("请输入当前课程：")
```

运行后，程序会停下来等待你输入。`input()` 返回的内容默认都是字符串，即使你键入的是数字。

用下面的代码验证，而不是只记住结论：

```python
weekly_hours_text = input("请输入本周计划小时：")
print("输入内容：", weekly_hours_text)
print("输入类型：", type(weekly_hours_text))
```

**必须主动修改：** 分别输入 `5` 和 `five`，观察两次的类型是否不同。

**成功标准：** 能通过实际输出说明为什么键盘输入的 `5` 仍然是字符串。

??? tip "提示一：程序像是卡住了"
    如果终端显示输入提示并停住，通常不是卡死，而是在等待你键入内容并按回车。

??? tip "提示二：数字为什么不是整数"
    键盘输入先以文本形式进入程序。需要计算时，程序必须明确决定要转换成哪种数字。

??? example "局部示例"
    输入 `5` 后，`type(weekly_hours_text)` 仍显示 `<class 'str'>`。

</section>

<section id="step-5" class="be-task-step" data-step-id="step-5" markdown="1">

## 第五步：转换输入并计算计划

**当前任务：** 把计划小时转换为整数，再计算下周增加一小时后的计划。

```python
weekly_hours_text = input("请输入本周计划小时：")
weekly_hours = int(weekly_hours_text)
next_week_hours = weekly_hours + 1

print("本周计划小时：", weekly_hours)
print("下周建议小时：", next_week_hours)
```

常见转换：

| 写法 | 结果 |
| --- | --- |
| `int("5")` | 整数 `5` |
| `float("2.5")` | 浮点数 `2.5` |
| `str(5)` | 字符串 `"5"` |

**必须主动修改：** 把下周增加量从 `1` 改成 `2`，重新运行并确认输出变化。

**成功标准：** 输入 `5` 时得到下周建议小时 `7`，并能说明转换发生在哪一行。

??? tip "提示一：先区分转换前后变量"
    名字带 `_text` 的变量保存原始字符串，转换后的数字保存在另一个变量中，便于观察边界。

??? tip "提示二：计算报 TypeError"
    检查参与加法的两边是否都是数字。可以分别打印它们的 `type()`。

??? example "局部示例"
    `weekly_hours = int(weekly_hours_text)` 负责把可转换的数字文本变成整数。

</section>

<section id="step-6" class="be-task-step" data-step-id="step-6" markdown="1">

## 第六步：故意触发并定位错误

**当前任务：** 运行第五步代码，在计划小时处输入 `abc`。

你会看到类似下面的信息：

```text
ValueError: invalid literal for int() with base 10: 'abc'
```

这次不要马上删除错误。按下面顺序记录：

1. 输入了什么。
2. 错误类型是什么。
3. traceback 指向哪个文件和哪一行。
4. 这一行接收了什么值，试图得到什么结果。
5. 换成什么输入后重新运行成功。

**必须主动修改：** 输入一个合法整数让程序恢复成功，并保存失败与成功两次证据。

**成功标准：** 能说出错误不是 `input()` 无法读取，而是 `int()` 无法把 `abc` 转成整数。

??? tip "提示一：先看最后一行"
    traceback 最后一行通常给出错误类型和摘要；再向上找自己文件中的行号。

??? tip "提示二：检查数据流"
    原始输入先进入 `weekly_hours_text`，下一行才交给 `int()`。检查哪一步的输入不满足要求。

??? example "局部示例"
    `int("5")` 可以成功，`int("abc")` 会触发 `ValueError`。

</section>

<section id="step-7" class="be-task-step" data-step-id="step-7" markdown="1">

## 第七步：独立完成迁移任务

**当前任务：** 不复制固定答案，给档案增加一个新字段。

可以选择：

- 每天练习分钟数。
- 当前学习方向。
- 是否完成今天的练习。
- 自己定义的其他学习信息。

你的修改必须包含：

1. 一个含义清楚的变量名。
2. 输入或固定初始值。
3. 需要时完成类型转换。
4. 在最终档案中输出。
5. 一次正常输入和一次边界输入的检查。

**成功标准：** 新字段能正常显示，并且你能解释它为什么选择字符串、整数、浮点数或布尔值。

??? tip "提示一：先决定信息是什么"
    先用一句话说清这个字段表示什么，再选择变量名和类型，不要先随意写一个 `x`。

??? tip "提示二：判断是否需要计算"
    只显示文本通常保留字符串；需要加减比较的数字应先转换。

??? example "局部示例而非完整答案"
    如果记录每天分钟数，可以先取得 `minutes_text`，再思考是否需要 `int()`。

??? success "参考答案检查原则"
    本步骤没有唯一代码。只要字段语义清楚、类型合理、能够运行，并完成正常与边界检查，就可以通过。

</section>

## 一份可工作的组合版本

如果中途文件结构已经混乱，可以用下面版本核对缺失部分。请先完成自己的尝试，再对照；不要用它代替第七步的独立字段。

```python
name = input("请输入昵称：")
course = input("请输入当前课程：")
weekly_hours_text = input("请输入本周计划小时：")

weekly_hours = int(weekly_hours_text)
next_week_hours = weekly_hours + 2

print("学习档案")
print("昵称：", name)
print("课程：", course)
print("本周计划小时：", weekly_hours)
print("下周建议小时：", next_week_hours)
```

## 常见错误与排查

| 现象 | 可能原因 | 检查方式 | 修复方向 |
| --- | --- | --- | --- |
| 找不到文件 | 当前终端目录不对 | `pwd`、`ls` 或 `Get-Location`、`dir` | 进入文件目录后再运行 |
| 输出没有变化 | 文件未保存或运行错文件 | 检查标签状态和命令中的文件名 | 保存并重新运行正确文件 |
| `NameError` | 变量名拼写不同或文本缺少引号 | 对照定义和使用位置 | 统一名称，文本加引号 |
| `TypeError` | 字符串与数字直接计算 | 打印参与计算值的 `type()` | 先完成正确类型转换 |
| `ValueError` | 输入不能转换成目标数字 | 查看实际输入和报错行 | 使用可转换输入；异常处理留到后续课程 |
| `True`、`False` 报错 | 布尔值大小写错误或加了不合适的写法 | 对照 Python 布尔值语法 | 使用首字母大写的 `True`、`False` |

## 完成证据

- [ ] 记录了首次成功运行的文件名、命令和输出。
- [ ] 主动修改了昵称、课程、目标和计划值。
- [ ] 能用实际输出区分字符串、整数、浮点数和布尔值。
- [ ] 能说明 `input()` 的结果默认是字符串。
- [ ] 能使用 `int()` 或 `float()` 完成一次转换和计算。
- [ ] 保存了一次 `ValueError` 的输入、行号、判断和恢复结果。
- [ ] 独立增加了一个新字段，并完成正常与边界检查。

## 下一步

进入[条件、循环、布尔逻辑](02-conditions-loops-boolean.md)。下一节会在这份学习档案的基础上，让程序根据条件判断学习状态，并重复处理多项任务。
