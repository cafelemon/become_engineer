<div class="be-tutor-mount" data-tutor-lesson="python-basics-02" aria-hidden="true"></div>

<section id="overview-status" class="be-page-hero be-lesson-hero" data-learning-context="overview-status" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 起步 · 第二课 · 学习进度报告器 v0.2</span>

# 条件、循环、布尔逻辑

## 档案开始会判断了

上一课的程序只能照原样打印数据。今天给它加上判断和重复处理，最终会看到：

```text
状态： 进行中
还需： 2 小时
本周行动：
1 继续学习
2 运行代码
3 记录结果
可以复盘： False
```

同一份程序把完成小时改成 `5` 时，状态会变成“已完成”。程序并不是提前知道答案，它只是按你写下的条件选择了一条路。

<div class="be-page-actions" markdown="1">
[先看程序怎样选择](#concept-boolean){ .md-button .md-button--primary }
[查看阶段作品](../../../exercises/python-basics/study-progress-reporter/README.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 起步 · 2 / 7</strong></div>
  <div><span>使用环境</span><strong>Python 3.11+，只用标准能力</strong></div>
  <div><span>完成后留下</span><strong>报告器 v0.2 与两类分支结果</strong></div>
</div>

## 开始前

- 已完成[变量、基本类型与输入输出](01-variables-types-io.md)，本地有 `practice/python-basics/learning_profile.py`。
- 能说明 `weekly_hours` 是整数，而 `input()` 的结果先是字符串。
- 继续从 `learning-workspace` 根目录运行代码，不另建一套脱节的练习目录。
- 页面运行器适合试固定数据；需要键盘输入的“最多猜三次”仍在本地终端完成。

<section id="concept-boolean" data-learning-context="concept-boolean" data-context-type="concept" markdown="1">

## 条件先回答一个问题

先只看这一行：

```python
finished_hours >= weekly_hours
```

如果 `finished_hours` 是 `3`，`weekly_hours` 是 `5`，这个问题的答案是 `False`；完成小时改成 `5` 或 `7`，答案就是 `True`。

| 表达式 | 它问什么 | 结果 |
| --- | --- | --- |
| `finished_hours >= weekly_hours` | 完成小时是否达到计划 | `True` 或 `False` |
| `finished_hours == weekly_hours` | 两个值是否相等 | `True` 或 `False` |
| `finished_hours != 0` | 完成小时是否不为零 | `True` 或 `False` |

`=` 是赋值，让名称绑定到一个值；`==` 才是在比较两个值是否相等。比较不会改动变量，它只产生一个布尔结果。

</section>

<section id="example-if" data-learning-context="example-if" data-context-type="example" markdown="1">

## `if` 按结果选一条路

```python
if finished_hours >= weekly_hours:
    status = "已完成"
else:
    status = "进行中"
```

<div class="be-control-flow" role="img" aria-label="程序先判断完成小时是否大于等于计划小时。结果为真时状态设为已完成；结果为假时状态设为进行中。">
  <article><span>先判断</span><strong>finished_hours &gt;= weekly_hours</strong></article>
  <b aria-hidden="true">→</b>
  <article data-branch="true"><span>结果是 True</span><strong>status = "已完成"</strong><small>只走这一边</small></article>
  <article data-branch="false"><span>结果是 False</span><strong>status = "进行中"</strong><small>只走这一边</small></article>
</div>

Python 会从上往下检查条件。`if` 成立就执行它下面缩进的代码；否则进入 `else`。冒号说明后面有一个代码块，统一的四个空格说明哪些语句属于这个分支。

先运行三组固定数据：

```python
--8<-- "examples/python-basics/learning_profile_status_cases.py"
```

你应该看到：

```text
3 小时：进行中
5 小时：已完成
7 小时：已完成
```

刚好达到 `5` 小时也应该完成，所以这里用 `>=`，而不是只用 `>`。

</section>

<section id="reproduce-v02" data-learning-context="reproduce-v02" data-context-type="reproduce" markdown="1">

## 跑起报告器 v0.2

下面是这节课的完整固定数据版。先找出两处 `if` 和一处 `for`，再预测输出：

```python
--8<-- "examples/python-basics/learning_profile_v02.py"
```

<div class="be-python-runner" data-python-runner data-python-source="../../../../examples/python-basics/learning_profile_v02.py">
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

先保留 `finished_hours = 3` 的“进行中”结果，再改成 `5`，确认“还需”这一行不再出现。两个分支都真实跑过，才说明判断经过了检查。

</section>

<section id="modify-status" data-learning-context="modify-status" data-context-type="modify" markdown="1">

## 给状态再加一档

现在把两档状态改成三档：

```python
if finished_hours >= weekly_hours:
    status = "已完成"
elif finished_hours > 0:
    status = "进行中"
else:
    status = "未开始"
```

`if`、`elif`、`else` 仍然只会命中一条。更严格的“达到计划”放在前面；如果先写 `finished_hours > 0`，完成了 `7` 小时也会过早落入“进行中”。

请用 `0`、`3`、`5` 三组数据运行，分别覆盖三条路。然后把状态名称改成你真正会使用的说法，例如“未开始／推进中／本周达标”。

</section>

<section id="concept-logic" data-learning-context="concept-logic" data-context-type="concept" markdown="1">

## 两个条件怎样合在一起

报告器只有在“小时达标”并且“至少运行过一次程序”时才允许进入复盘：

```python
hours_done = finished_hours >= weekly_hours
ran_program = True
ready_for_review = hours_done and ran_program
```

| 写法 | 什么时候为真 | 这份报告里的例子 |
| --- | --- | --- |
| `a and b` | 两边都为真 | 小时达标，并且运行过程序 |
| `a or b` | 至少一边为真 | 做过代码或写过复盘即可保留记录 |
| `not a` | `a` 为假 | `not ready_for_review` 表示还不能复盘 |

这里更建议先把长条件拆成有意义的布尔变量。读到 `hours_done and ran_program` 时，比读一串重复比较更容易判断意图。

</section>

<section id="example-for-range" data-learning-context="example-for-range" data-context-type="example" markdown="1">

## `for` 逐项处理行动清单

```python
actions = ["继续学习", "运行代码", "记录结果"]

for number in range(1, len(actions) + 1):
    print(number, actions[number - 1])
```

起步时先把列表看成一组有顺序的值，下一课组会专门深入容器。`for` 每轮取一个编号，缩进的 `print()` 重复执行一次。

`range(1, 4)` 会给出 `1、2、3`，包含起点但不包含结束值。这里写 `len(actions) + 1`，是为了让人看到的编号从 1 开始，同时让列表位置用 `number - 1` 回到 `0、1、2`。

请增加一项你自己的行动。运行后检查它只出现一次，而且最后一个编号与行动数量相同。

</section>

<section id="reproduce-while" data-learning-context="reproduce-while" data-context-type="reproduce" markdown="1">

## `while` 适合“还没结束就继续”

把下面代码保存为 `practice/python-basics/guess_word.py`：

```python
--8<-- "examples/python-basics/guess_word_three_times.py"
```

`while attempt <= 3` 每轮开始前都会重新检查次数。猜对时 `break` 立即离开循环；猜错时计数器加一，因此最多只会询问三次。

分别运行两次：

- 第一次输入 `java`、`python`，确认第二次猜对后不再询问。
- 第二次输入三个错误答案，确认最后显示“次数用完”。

这里不建议刚起步就写没有上限的 `while True`。先让循环边界直接写在条件里，更容易看出程序何时结束。

</section>

<section id="troubleshoot-flow" data-learning-context="troubleshoot-flow" data-context-type="troubleshoot" markdown="1">

## 走错时先看条件和缩进

| 现象 | 常见原因 | 怎样回来 |
| --- | --- | --- |
| `SyntaxError` 指向 `if` 附近 | 少了冒号，或把比较写成单个 `=` | 补上冒号；相等比较改用 `==` |
| `IndentationError` | 分支里的缩进不一致 | 统一使用四个空格，不混用 Tab |
| `elif` 永远进不去 | 上面更宽的条件先命中了 | 把更具体、更严格的条件放在前面 |
| `range(1, 4)` 没有输出 4 | 结束值不包含在范围内 | 先打印实际序列；需要 4 时写 `range(1, 5)` |
| `while` 一直运行 | 条件依赖的值没有更新 | 按 `Ctrl+C` 停止，检查计数器或 `break` |
| 数字比较出现 `TypeError` | 仍在拿 `input()` 返回的字符串和整数比较 | 先用 `int()` 转换，再进入条件 |

故意把 `attempt = attempt + 1` 暂时移出循环，再用三个错误答案试一次。发现它不停询问后按 `Ctrl+C`，恢复更新语句并重新验证“最多三次”。不要让故意的死循环留在提交中。

</section>

<section id="project-v02" data-learning-context="project-v02" data-context-type="project" markdown="1">

## 报告器 v0.2

| 上一版 | 这节课增加 | 涉及文件 | 需要保存 | 下一版 |
| --- | --- | --- | --- | --- |
| v0.1：打印一条学习档案 | 状态分支、剩余小时、行动清单和复盘条件 | `learning_profile.py`、`guess_word.py` | 未开始／进行中／已完成输出，提前猜对与次数用完结果 | 把重复判断整理成函数 |

在 `notes/learning-log.md` 追加本课记录，然后检查提交：

```bash
git add practice/python-basics/learning_profile.py \
  practice/python-basics/guess_word.py notes/learning-log.md
git diff --cached
git commit -m "add status checks to study profile"
git status --short
```

记录里要能回答三件事：哪些输入走了哪些分支；循环为什么能结束；你新增的状态与行动是什么。

</section>

<section id="deepen-short-circuit" data-learning-context="deepen-short-circuit" data-context-type="deepen" markdown="1">

## 再深入一点：条件会从左往右判断

`and` 左边已经是 `False` 时，整个表达式不可能为真，Python 不需要再计算右边；`or` 左边已经是 `True` 时，也不需要再计算右边。这叫短路求值。

这能帮助程序避免不必要的计算，但不要把带有文件写入或其他副作用的操作藏在复杂条件里。起步阶段先把条件拆成清楚的布尔变量，行为更容易检查。

</section>

<section id="career-branch-story" data-learning-context="career-branch-story" data-context-type="career" markdown="1">

## 被问到“怎样保证分支正确”时

不要只说“我会写 `if`”。可以拿报告器说明：你先列出未开始、进行中、刚好达标和超过目标四类输入，逐一运行；再检查最容易漏掉的等号边界；循环部分同时验证提前退出和次数耗尽。

这段程序很小，但“列分支—选输入—运行—比对结果”的方法会直接延伸到接口状态、数据校验和自动化测试。

</section>

## 完成检查

- [ ] 我能解释 `=`、`==` 和 `>=` 的区别。
- [ ] 我用 `0`、`3`、`5` 覆盖了三档状态。
- [ ] 我能说明 `if/elif/else` 为什么只进入一条路。
- [ ] 我使用 `and` 组合了“小时达标”和“运行过程序”。
- [ ] 我增加了一项行动，并检查 `range()` 的首尾编号。
- [ ] 我验证了猜词程序的提前 `break` 和三次耗尽。
- [ ] 我亲手恢复了一次缩进、范围或循环退出问题。
- [ ] 我提交了报告器 v0.2 的代码与学习记录。

## 来源与版本

- 适用版本：Python 3.11 及以上；示例只使用内置类型与函数。
- 核查日期：2026-07-17。
- 事实来源：[Python 复合语句](https://docs.python.org/3.11/reference/compound_stmts.html)说明 `if`、`while`、`for`、缩进代码块和 `break` 的执行语义；[内置类型](https://docs.python.org/3.11/library/stdtypes.html#truth-value-testing)说明真值、布尔运算和比较。
- 代码验证：仓库脚本检查固定报告、三组分支、提前退出与次数耗尽；自动测试不联网，也不安装第三方包。

## 下一步

现在的判断还都写在主流程里。下一课进入[函数、参数、返回值和作用域](03-functions-parameters-returns-scope.md)，把状态判断和报告生成整理成可以反复调用的小块。

[进入下一课](03-functions-parameters-returns-scope.md){ .md-button .md-button--primary }
