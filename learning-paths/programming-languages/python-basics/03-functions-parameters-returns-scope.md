<div class="be-tutor-mount" data-tutor-lesson="python-basics-03" aria-hidden="true"></div>

<section id="overview-functions" class="be-page-hero be-lesson-hero" data-learning-context="overview-functions" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 起步 · 第三课 · 学习进度报告器 v0.3</span>

# 函数、参数、返回值和作用域

## 把一段做法叫出名字

这一次，报告器会输出两条不同的学习记录：

```text
学习档案
昵称： 小码
- Python 起步: 60%，还需 2 小时
* 复盘练习: 100%，已完成
```

两行记录的课程、小时和前缀都不同，计算进度和判断状态的规则却只写了一份。它们已经有了名字：`calculate_progress()`、`build_status()` 和 `build_report_line()`。

函数的用处就在这里：把一段值得重复使用的做法收好，给它一个能读懂的名字，再把每次会变化的数据交给它。

<div class="be-page-actions" markdown="1">
[先看一次函数调用](#concept-call){ .md-button .md-button--primary }
[查看阶段作品](../../../exercises/python-basics/study-progress-reporter/README.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 起步 · 3 / 7</strong></div>
  <div><span>使用环境</span><strong>Python 3.11+，只用标准能力</strong></div>
  <div><span>完成后留下</span><strong>报告器 v0.3 与函数调用结果</strong></div>
</div>

## 开始前

- 已完成[条件、循环与布尔逻辑](02-conditions-loops-boolean.md)，本地有 `practice/python-basics/learning_profile.py`。
- 能读懂上一版里的状态判断，并知道 `print()` 会把内容显示在终端。
- 继续使用同一个 `learning-workspace`，不要另建一套脱节的练习目录。
- 页面运行器适合验证固定数据；最终代码仍要在本地终端运行并提交。

<section id="concept-call" data-learning-context="concept-call" data-context-type="concept" markdown="1">

## 定义以后，还要调用

先看一个很小的函数：

```python
def build_welcome(name):
    return f"欢迎回来，{name}"


message = build_welcome("小码")
print(message)
```

读到 `def build_welcome(name):` 时，Python 会把这段做法记在名字 `build_welcome` 下，但不会立即执行缩进部分。读到 `build_welcome("小码")`，这次调用才真正开始。

<div class="be-function-flow" role="img" aria-label="调用者把小码传给函数的 name 参数，函数在局部空间中生成欢迎语，再把结果返回给调用者。">
  <div><span>调用者准备数据</span><strong>"小码"</strong></div>
  <b aria-hidden="true">→</b>
  <div><span>参数接住数据</span><strong>name = "小码"</strong></div>
  <b aria-hidden="true">→</b>
  <div><span>函数内部处理</span><strong>生成欢迎语</strong></div>
  <b aria-hidden="true">→</b>
  <div><span>结果回到调用处</span><strong>message</strong></div>
</div>

函数名最好能说清动作。`build_status`、`calculate_progress` 比 `do_it`、`handle` 更容易让下一个读代码的人知道它负责什么。

</section>

<section id="example-small-functions" data-learning-context="example-small-functions" data-context-type="example" markdown="1">

## 先拆出两个小函数

报告器里有两件相对独立的事：计算完成比例，以及根据小时数生成状态。

```python
def calculate_progress(target_hours, finished_hours):
    return min(finished_hours / target_hours, 1.0)


def build_status(target_hours, finished_hours):
    if finished_hours >= target_hours:
        return "已完成"
    return f"还需 {target_hours - finished_hours:g} 小时"
```

`calculate_progress(5, 3)` 返回 `0.6`；`build_status(5, 3)` 返回“还需 2 小时”。同样的函数换一组数字就能继续使用，不需要复制判断规则。

这里先约定 `target_hours` 必须是正数。输入校验会在后面的异常处理课程中补上；现在若把目标写成 `0`，除法自然会报 `ZeroDivisionError`，不要用一个随意的默认值把问题藏起来。

</section>

<section id="concept-parameters" data-learning-context="concept-parameters" data-context-type="concept" markdown="1">

## 参数是函数的入口

写在函数定义括号里的 `target_hours`、`finished_hours` 叫**形参**；调用时传入的 `5`、`3` 叫**实参**。

```python
progress = calculate_progress(5, 3)
```

位置参数按顺序对应。上面把 `5` 交给 `target_hours`，把 `3` 交给 `finished_hours`。两个值都是数字时，交换顺序不会出现语法错误，却会改变含义。这里更建议使用关键字参数：

```python
progress = calculate_progress(
    target_hours=5,
    finished_hours=3,
)
```

关键字把数据属于谁写得更清楚，也减少了同类型参数传反的机会。

函数还可以给不常变化的数据设置默认值：

```python
def build_report_line(course, target_hours, finished_hours, prefix="- "):
    progress = calculate_progress(target_hours, finished_hours)
    status = build_status(target_hours, finished_hours)
    return f"{prefix}{course}: {progress:.0%}，{status}"
```

大多数记录沿用 `"- "`；需要换成星号时再明确传入：

```python
print(build_report_line("复盘练习", 2, 2, prefix="* "))
```

默认值应当代表一个安全、常用而且容易理解的选择。它不是为了把所有参数都省掉。

</section>

<section id="example-return-print" data-learning-context="example-return-print" data-context-type="example" markdown="1">

## `return` 不是另一种 `print()`

下面两个函数看起来都处理了状态，但交给后续代码的东西并不一样：

```python
--8<-- "examples/python-basics/return_vs_print.py"
```

运行后会看到：

```text
进行中
show_status 的调用结果： None
get_status 的调用结果： 进行中
```

`print()` 把文字送到终端，适合给人看；没有写 `return` 的函数会隐式返回 `None`。`return` 则把值交回调用位置，后续代码可以保存、比较、拼接或测试它。

`return` 还会立即结束本次函数调用。写在同一路径的 `return` 后面的语句不会执行，因此不要把必要操作放在那里。

</section>

<section id="reproduce-v03" data-learning-context="reproduce-v03" data-context-type="reproduce" markdown="1">

## 跑起报告器 v0.3

下面是完整的固定数据版。先顺着主流程读最后五行，再回头看三个函数分别负责什么：

```python
--8<-- "examples/python-basics/learning_profile_v03.py"
```

<div class="be-python-runner" data-python-runner data-python-source="../../../../examples/python-basics/learning_profile_v03.py">
  <p class="be-python-runner__fallback">页面运行器正在准备。若它没有出现，请把上面的代码复制到本地文件运行。</p>
</div>

把代码保存到上一课的文件：

=== "Windows PowerShell"

    ```powershell
    .\.venv\Scripts\python.exe .\practice\python-basics\learning_profile.py
    ```

=== "macOS / Linux"

    ```bash
    ./.venv/bin/python ./practice/python-basics/learning_profile.py
    ```

输出应与页面开头一致。接着只改 `finished_hours`，不要改函数内部规则，确认进度和状态会一起变化。这样才能说明主流程真的在使用函数返回的结果。

</section>

<section id="modify-report-line" data-learning-context="modify-report-line" data-context-type="modify" markdown="1">

## 给报告行加上自己的选择

先完成三处修改：

1. 把 `name`、`course` 和小时数换成自己的数据。
2. 用关键字参数再次调用 `build_report_line()`，故意调整参数书写顺序，确认输出含义不变。
3. 把默认前缀改成你愿意长期使用的样式，再给另一条记录单独传入不同前缀。

然后新写一个函数，把“是否可以复盘”的判断从主流程中拿出来：

```python
def can_review(target_hours, finished_hours, ran_program):
    return finished_hours >= target_hours and ran_program
```

至少运行这三组数据：未完成但运行过、完成但没有运行、完成且运行过。只有最后一组应该返回 `True`。不要只复制示例；请把参数名和输出说明写到自己一周后仍能读懂。

</section>

<section id="concept-scope" data-learning-context="concept-scope" data-context-type="concept" markdown="1">

## 函数里的名字有自己的范围

每次调用函数时，参数和函数内部创建的变量都属于这次调用的局部范围。下面的 `message` 在 `build_message()` 内能用，离开函数后却不能直接访问：

```python
--8<-- "examples/python-basics/local_scope_name_error.py"
```

第一行会正常打印，第二个 `print(message)` 会触发：

```text
NameError: name 'message' is not defined
```

修复方式不是把 `message` 变成全局变量，而是在调用处接住返回值：

```python
returned_message = build_message("Python 起步")
print(returned_message)
```

局部范围让不同函数可以放心使用 `message`、`result` 这样的临时名字，也避免一个函数无意中改坏另一个函数的中间数据。

</section>

<section id="troubleshoot-functions" data-learning-context="troubleshoot-functions" data-context-type="troubleshoot" markdown="1">

## 函数没有按预期工作时

| 现象 | 常见原因 | 怎样回来 |
| --- | --- | --- |
| 写了 `def` 却没有任何输出 | 只定义了函数，没有调用 | 在主流程中写出 `函数名(...)`，并检查返回值怎样使用 |
| `TypeError` 提示缺少参数 | 调用时少传了必需实参 | 对照定义括号中的形参逐一补齐 |
| 数字没有报错但结果不对 | 两个位置参数传反 | 改用 `target_hours=...`、`finished_hours=...` |
| 调用结果是 `None` | 函数只 `print()`，没有返回需要的值 | 保留必要显示，把可复用结果用 `return` 交出 |
| `NameError` 指向函数外的名字 | 访问了函数内部的局部变量 | 用 `return` 返回，并在调用处保存 |
| `ZeroDivisionError` | 目标小时是 0 | 回到输入数据，先满足本课“目标为正数”的约定 |
| 某行永远执行不到 | 它写在同一路径的 `return` 后面 | 调整顺序，或把不同返回路径写清楚 |

故意在一次调用中漏掉 `finished_hours`，完整读一遍 `TypeError`；恢复参数后再运行。报错中的函数名和缺失参数名，就是 Python 已经替你标出的第一条线索。

</section>

<section id="project-v03" data-learning-context="project-v03" data-context-type="project" markdown="1">

## 报告器 v0.3

| 上一版 | 这节课增加 | 涉及文件 | 需要保存 | 下一版 |
| --- | --- | --- | --- | --- |
| v0.2：主流程直接判断和打印 | 进度、状态与报告行函数；参数、返回值和局部范围 | `learning_profile.py`、`notes/learning-log.md` | 两组报告行、关键字参数调用、一次函数报错与修复 | 用容器管理多条学习记录 |

在 `notes/learning-log.md` 写下三个函数各自负责什么，以及你为什么选择返回值而不是在函数内部直接打印。提交前检查：

```bash
git add practice/python-basics/learning_profile.py notes/learning-log.md
git diff --cached
git commit -m "refactor study profile into functions"
git status --short
```

如果一次修改既调整了函数内部，又改变了调用方式，请把两组输入重新跑一遍。函数减少了重复代码，但不会自动替你保证调用正确。

</section>

<section id="deepen-function-contract" data-learning-context="deepen-function-contract" data-context-type="deepen" markdown="1">

## 再深入一点：函数也有约定

看到 `calculate_progress(target_hours, finished_hours)`，调用者应该能知道要提供什么；看到返回的浮点数，后续代码应该知道它表示 `0.0` 到 `1.0` 的完成比例。这就是一个最小的函数约定。

起步阶段先坚持三件事：

- 一个函数名只承担一件主要工作。
- 相同输入应得到相同的计算结果，不偷偷读取无关全局变量。
- 计算函数返回数据，最外层再决定怎样输入和显示。

这样写出来的函数更容易单独测试，也更容易在 Web 接口、文件处理或另一种界面中重复使用。

</section>

<section id="career-function-story" data-learning-context="career-function-story" data-context-type="career" markdown="1">

## 被问到“为什么要这样拆函数”时

不要只回答“代码更整洁”。可以拿报告器说明：原来进度计算、状态判断和显示混在主流程中，规则一改就容易漏；拆分后，每个函数有明确输入和返回值，可以分别覆盖未完成、完成和超额三组数据，主流程只负责组合结果。

这个例子很小，但“说明职责—定义接口—验证边界—再组合”的表达方式，会继续用在模块、接口和项目设计中。

</section>

## 完成检查

- [ ] 我能说明定义函数和调用函数发生在不同时间。
- [ ] 我能区分形参、实参、位置参数和关键字参数。
- [ ] 我运行了报告器 v0.3，并用两组小时数据检查结果。
- [ ] 我能用实际输出解释 `return` 和 `print()` 的区别。
- [ ] 我给 `build_report_line()` 使用了默认参数和自定义关键字参数。
- [ ] 我新增并验证了 `can_review()`。
- [ ] 我触发并修复了一次缺少参数或局部作用域错误。
- [ ] 我提交了报告器 v0.3 和学习记录。

## 来源与版本

- 适用版本：Python 3.11 及以上；示例只使用内置类型与函数。
- 核查日期：2026-07-17。
- 事实来源：[Python 函数定义教程](https://docs.python.org/3.11/tutorial/controlflow.html#defining-functions)说明函数定义、调用、局部符号表、默认参数和关键字参数；[`return` 语句](https://docs.python.org/3.11/reference/simple_stmts.html#the-return-statement)说明返回与结束函数的语义；[名称解析](https://docs.python.org/3.11/reference/executionmodel.html#resolution-of-names)说明局部名称与 `NameError`。
- 代码验证：仓库脚本检查报告器固定输出、默认与关键字参数、`return`/`print()` 差异和局部作用域失败；自动测试不联网，也不安装第三方包。

## 下一步

函数已经能处理一条记录。下一课进入[字符串、列表、字典、集合和元组](04-strings-collections.md)，把一条学习档案扩展成多条记录，并选择合适的容器组织数据。

[进入下一课](04-strings-collections.md){ .md-button .md-button--primary }
