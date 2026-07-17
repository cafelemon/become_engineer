<div class="be-tutor-mount" data-tutor-lesson="python-basics-01" aria-hidden="true"></div>

<section id="overview-profile" class="be-page-hero be-lesson-hero" data-learning-context="overview-profile" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 起步 · 第一课 · 学习进度报告器 v0.1</span>

# 变量、基本类型、输入输出

## 先让程序介绍一下你

今天结束时，你会得到这样一段真实输出：

```text
学习档案
昵称： 小码
课程： Python 起步
本周计划： 5 小时
```

它现在只会记住一条学习档案，但后面六节课都会在这份数据上继续加功能。先让它跑起来，再慢慢看懂变量、类型和输入怎样配合。

<div class="be-page-actions" markdown="1">
[先理解变量和值](#concept-variable){ .md-button .md-button--primary }
[查看阶段作品](../../../exercises/python-basics/study-progress-reporter/README.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 起步 · 1 / 7</strong></div>
  <div><span>使用环境</span><strong>Python 3.11+，只用标准能力</strong></div>
  <div><span>完成后留下</span><strong>learning_profile.py 与两次运行结果</strong></div>
</div>

## 开始前

- 已完成[工程基础入门](../../engineering-foundation/stage-0/README.md)，能打开 `learning-workspace` 并使用项目虚拟环境。
- 在工作区中新建 `practice/python-basics/`，这七节课的代码都放在这里。
- Windows 下使用 `.venv\\Scripts\\python.exe`；macOS／Linux 下使用 `.venv/bin/python`。如果虚拟环境不在，请先回到[开发环境](../../engineering-foundation/stage-0/07-development-environment.md)补齐。
- 页面运行器只适合立即试一小段代码。键盘输入、文件和正式项目仍在本地终端完成。

<section id="concept-variable" data-learning-context="concept-variable" data-context-type="concept" markdown="1">

## 变量名和值

先看最短的一行：

```python
name = "小码"
```

<div class="be-variable-model" role="img" aria-label="赋值关系：先计算右侧的字符串值小码，再把名称 name 绑定到这个值，值的类型是 str。">
  <div><span>名称</span><strong>name</strong></div>
  <b aria-hidden="true">绑定到 →</b>
  <div><span>当前值</span><strong>"小码"</strong></div>
  <b aria-hidden="true">它的类型是 →</b>
  <div><span>类型</span><strong>str</strong></div>
</div>

Python 会先得到等号右边的值，再把左边的名称绑定到这个值。起步时可以把变量理解成“程序里用来找到当前值的名字”。这里先别把它想成一个永远装着同一种东西的固定盒子。

- `name` 是程序里使用的名称。
- `"小码"` 是字符串值，引号标出文本的开始和结束。
- `str` 描述这个值的类型，也决定它适合参加哪些操作。

</section>

<section id="example-reassignment" data-learning-context="example-reassignment" data-context-type="example" markdown="1">

## 再赋值以后会怎样

先预测下面程序会输出“小码”还是“贾飞”：

```python
name = "小码"
name = "贾飞"
print(name)
```

??? question "先说出答案，再展开"
    输出 `贾飞`。第二次赋值让 `name` 绑定到新值；`print(name)` 读取的是它此刻对应的值。

如果忘了给文字加引号：

```python
name = 小码
```

Python 会把 `小码` 当作另一个名称去查找，找不到时出现 `NameError`。普通文本要写成字符串：`"小码"`。

</section>

<section id="example-types" data-learning-context="example-types" data-context-type="example" markdown="1">

## 四种常见的值

| 值 | Python 类型 | 适合表达 | 容易混淆的地方 |
| --- | --- | --- | --- |
| `"Python 起步"` | `str` | 名字、课程、路径等文本 | 看起来像数字的文本仍然不能直接计算 |
| `5` | `int` | 次数、数量、整小时 | 它和字符串 `"5"` 不是同一种值 |
| `0.2` | `float` | 比例、测量值和小数 | 不适合直接承担严格的金额规则 |
| `True` | `bool` | 是／否、成立／不成立 | 首字母必须大写；`"True"` 是文本 |

拿不准时，不用猜。把下面代码保存为临时文件运行，或者直接看正式示例：

```python
--8<-- "examples/python-basics/learning_profile_types.py"
```

预期会看到：

```text
小码 <class 'str'>
5 <class 'int'>
0.2 <class 'float'>
True <class 'bool'>
```

`type()` 适合这节课观察实际类型。以后写需要兼容继承关系的判断时，会再学习 `isinstance()`，现在不用提前展开。

</section>

<section id="reproduce-first-run" data-learning-context="reproduce-first-run" data-context-type="reproduce" markdown="1">

## 先猜输出，再运行

这就是报告器 v0.1 的正式示例。完整读一遍，猜它会打印几行、每行是什么，再点运行：

```python
--8<-- "examples/python-basics/learning_profile_v01.py"
```

<div class="be-python-runner" data-python-runner data-python-source="../../../../examples/python-basics/learning_profile_v01.py">
  <p class="be-python-runner__fallback">浏览器运行器需要 JavaScript 和网络。你仍可把上方代码保存为 <code>learning_profile.py</code>，再用本地 Python 运行。</p>
</div>

第一次点击才会从 CDN 加载 Pyodide 0.29.4，约 12MB。代码在独立 Worker 中运行，超过 3 秒会停止；页面不会把你的修改保存到浏览器存储。CDN 不可用时，直接走下面的本地路径。

把代码复制到 `learning-workspace/practice/python-basics/learning_profile.py`，从工作区根目录运行：

=== "Windows PowerShell"

    ```powershell
    .\.venv\Scripts\python.exe .\practice\python-basics\learning_profile.py
    ```

=== "macOS / Linux"

    ```bash
    .venv/bin/python practice/python-basics/learning_profile.py
    ```

命令正常结束并显示第一屏的四行内容，就完成了第一次运行。若输出不同，先逐行比较代码，不要立即换一份更长的程序。

</section>

<section id="modify-profile" data-learning-context="modify-profile" data-context-type="modify" markdown="1">

## 改成你的学习档案

现在改自己的本地文件：

1. 把 `name` 改成你的昵称。
2. 把 `course` 改成你现在学习的内容。
3. 把 `weekly_hours` 改成你的计划小时。
4. 自己新增一个字段，例如 `goal`、`city` 或 `favorite_topic`，并用 `print()` 输出。

运行前先写下你预计改变的两行输出，运行后再对照。代码和输出都要保存，仅仅在编辑器里改完还不算结束。

<div class="be-editor-check" role="status">
  <strong>想一想</strong>
  <span>如果把 <code>weekly_hours = 5</code> 改成 <code>weekly_hours = "5"</code>，打印结果看起来很接近，但它还能直接加一吗？</span>
</div>

</section>

<section id="reproduce-input" data-learning-context="reproduce-input" data-context-type="reproduce" markdown="1">

## 为什么输入 `5`，得到的却是文字

`input()` 会显示提示并等你键入一行内容。它去掉结尾的换行后，返回一个字符串。键盘上敲出的 `5` 因此先是文本，不会自动变成整数。

<div class="be-python-input-flow" role="img" aria-label="键盘输入字符串 5，input 返回 str，int 转换后得到整数 5，整数才能进行数字加法。">
  <div><span>键盘输入</span><strong>"5"</strong></div>
  <b aria-hidden="true">input() →</b>
  <div><span>程序先收到</span><strong>str</strong></div>
  <b aria-hidden="true">int() →</b>
  <div><span>转换后得到</span><strong>5 · int</strong></div>
</div>

正式输入版本如下：

```python
--8<-- "examples/python-basics/learning_profile_input.py"
```

把它复制到本地的 `learning_profile.py` 后运行。页面微型运行器不模拟键盘输入。

第一次依次输入：

```text
小码
Python 起步
5
```

应该看到 `本周计划： 5 小时` 和 `下周建议： 6 小时`。然后再输入一次 `five`，保留终端出现的错误。

!!! note "程序停在输入提示处，不一定是卡住"
    如果光标停在“请输入昵称：”后面，程序正在等你输入。键入内容并按回车即可。真要停止当前程序，可以在终端按 `Ctrl+C`。

</section>

<section id="troubleshoot-valueerror" data-learning-context="troubleshoot-valueerror" data-context-type="troubleshoot" markdown="1">

## 遇到 `ValueError`，先读最后一行

输入 `five` 时会看到类似结果：

```text
ValueError: invalid literal for int() with base 10: 'five'
```

按这个顺序读：

1. 最后一行先告诉你错误类型是 `ValueError`。
2. 向上找到自己的文件和 `int(weekly_hours_text)` 所在行。
3. `input()` 已经成功读取了文字 `"five"`；失败的是 `int()` 无法把它解释成十进制整数。
4. 重新输入 `5`。程序恢复成功后，你的判断才算经过检查。

这里先保留 traceback，不急着用 `try` 隐藏它。异常处理会在 Python 起步最后一课专门学习。

| 现象 | 先看哪里 | 怎样回来 |
| --- | --- | --- |
| 找不到 `learning_profile.py` | 当前目录与命令里的相对路径 | 回到 `learning-workspace` 根目录再运行 |
| 修改后输出没变化 | 文件是否保存、命令是否运行了同名的另一个文件 | 保存文件，核对路径后重跑 |
| `NameError` | 文本是否漏了引号，变量名拼写是否一致 | 给文本加引号或统一名称 |
| `TypeError` | 运算两边的实际类型 | 用 `type()` 检查；数字输入先经过 `int()` |
| `ValueError` | 传给 `int()` 的具体文本 | 改用能表示整数的输入，再运行一次 |

</section>

<section id="project-v01" data-learning-context="project-v01" data-context-type="project" markdown="1">

## 报告器的第一个版本：v0.1

工程基础阶段只有学习工作区，没有真正的 Python 程序。这节课给它增加第一条能运行的学习记录：

| 上一版 | 这节课增加 | 涉及文件 | 需要保存 | 下一版 |
| --- | --- | --- | --- | --- |
| 工程学习工作台 v1.0 | 昵称、课程、计划小时和一个自选字段 | `practice/python-basics/learning_profile.py` | 代码、一次成功输出、一次 `ValueError` 与恢复结果 | 用条件判断“进行中／已完成” |

在 `notes/learning-log.md` 追加本课记录，然后提交：

```bash
git add practice/python-basics/learning_profile.py notes/learning-log.md
git diff --cached
git commit -m "build study profile v0.1"
git status --short
```

提交前不要跳过 `git diff --cached`：确认里面只有准备公开的学习代码和记录，没有私人绝对路径、账号、密钥或无关文件。

[查看阶段作品的最终版本](../../../exercises/python-basics/study-progress-reporter/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-values-have-types" data-learning-context="deepen-values-have-types" data-context-type="deepen" markdown="1">

## 再深入一点：类型属于值

Python 允许同一个名称先后绑定到不同类型的值：

```python
weekly_hours = 5
weekly_hours = "five"
```

语法允许，不代表这样写容易维护。一个名称的含义和数据形态越稳定，后面阅读、排错和测试越轻松。起步阶段更建议使用 `weekly_hours_text` 保存原始输入，再用 `weekly_hours` 保存转换后的整数，让转换前后清楚分开。

</section>

<section id="career-explain-input" data-learning-context="career-explain-input" data-context-type="career" markdown="1">

## 被问到输入和类型时，可以这样讲

不要只背 `str`、`int`、`float`、`bool` 四个名字。拿这段程序说明一条数据怎样流动：键盘输入由 `input()` 读成字符串，程序在需要计算的位置调用 `int()`，非法文本触发 `ValueError`，你通过 traceback 找到转换行并用合法输入验证恢复。

这还不是复杂项目，但它已经能说明你会运行、观察、解释和修复，而不只是记住语法表。

</section>

## 完成检查

- [ ] 我能解释名称、值和类型之间的关系。
- [ ] 我在本地运行了 `learning_profile.py`，而不只使用页面运行器。
- [ ] 我修改了昵称、课程、计划小时，并独立增加一个字段。
- [ ] 我用 `type()` 看过 `str`、`int`、`float` 和 `bool`。
- [ ] 我能说明为什么 `input()` 返回字符串，以及转换发生在哪一行。
- [ ] 我保留了一次 `ValueError`，并用合法输入恢复成功。
- [ ] 我提交了报告器 v0.1 的代码和学习记录。

## 来源与版本

- 适用版本：Python 3.11 及以上；示例只使用内置类型与函数。
- 页面微型运行器：Pyodide 0.29.4，点击后加载；加载失败时使用本地 Python。
- 核查日期：2026-07-17。
- 事实来源：[赋值语句](https://docs.python.org/3.11/reference/simple_stmts.html#assignment-statements)、[内置函数 `input()`、`int()` 与 `type()`](https://docs.python.org/3.11/library/functions.html)、[内置异常 `ValueError`](https://docs.python.org/3.11/library/exceptions.html#ValueError)。
- 代码验证：仓库脚本分别检查固定输出、四种类型、合法输入和 `ValueError`；自动测试不联网，也不安装第三方包。

<div class="be-next-panel" markdown="1">

## 下一步

现在的档案只会照原样打印数据。下一课进入[条件、循环、布尔逻辑](02-conditions-loops-boolean.md)，让程序根据完成小时判断状态，并开始处理重复记录。

[进入下一课](02-conditions-loops-boolean.md){ .md-button .md-button--primary }

</div>
