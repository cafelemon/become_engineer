<div class="be-tutor-mount" data-tutor-lesson="python-basics-07" aria-hidden="true"></div>

<section id="overview-failure" class="be-page-hero be-lesson-hero" data-learning-context="overview-failure" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 起步 · 第七课 · 学习进度报告器 v1.0</span>

# 异常、基本调试和最小自动化测试

## 程序结束了，答案却不一定对

这段计算没有报错：

~~~text
错误结果：1.5（规则上限应为 1.0）
~~~

如果完成进度最多显示 100%，<code>1.5</code> 就是错误结果。解释器不会替你判断业务规则，所以最后一课要补上三件事：看懂失败、拒绝不合法输入、让测试替你守住已经修好的行为。

完成后，报告器会有 14 项自动测试。正常输入返回 0，缺文件、坏 JSON 和非法记录返回 1；意外的编程错误仍保留 traceback，不会被一句“运行失败”藏起来。

<div class="be-page-actions" markdown="1">
[先分清三种问题](#concept-problem-kinds){ .md-button .md-button--primary }
[查看阶段作品](../../../exercises/python-basics/study-progress-reporter/README.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 起步 · 7 / 7</strong></div>
  <div><span>使用环境</span><strong>Python 3.11+，标准库 unittest</strong></div>
  <div><span>完成后留下</span><strong>报告器 v1.0、14 项测试与失败记录</strong></div>
</div>

## 开始前

- 已完成[模块、导入和虚拟环境](06-modules-imports-venv.md)，能运行四模块报告器。
- 能从 JSON 生成报告，并知道读取、计算、排版和入口分别在哪个模块。
- 本课沿用同一份阶段作品，不引入第三方测试框架。
- 建议先复制一份练习目录。故意改坏代码、修改坏 JSON 和观察红灯都在副本中完成。

<section id="concept-problem-kinds" data-learning-context="concept-problem-kinds" data-context-type="concept" markdown="1">

## 先看清“哪里不对”

程序不对，大致有三种样子：

| 现象 | 例子 | 先做什么 |
| --- | --- | --- |
| 解释器读不懂 | 少了冒号、括号没闭合 | 看 <code>SyntaxError</code> 指向的位置，先让文件能被解析 |
| 运行途中失败 | 文件不存在、除以零、键缺失 | 从 traceback 最后一行读异常类型，再向上看调用链 |
| 正常结束但结果错 | 进度显示 150% | 缩小成一组输入、实际结果和期望规则 |

第三种最容易漏掉。程序退出码是 0，只能说明进程正常结束，不能证明结果符合要求。

先运行这个短例子：

~~~python
--8<-- "examples/python-basics/failure_kinds.py"
~~~

~~~bash
python site-src/examples/python-basics/failure_kinds.py
~~~

它同时展示错误结果和一个被明确拒绝的输入。二者都需要修，但处理方式不同：错误结果靠规则与测试发现；非法输入在进入计算前用条件判断和 <code>raise</code> 拒绝。

</section>

<section id="example-traceback" data-learning-context="example-traceback" data-context-type="example" markdown="1">

## traceback 从最后一行开始读

运行：

~~~bash
python site-src/examples/python-basics/traceback_demo.py
~~~

你会看到类似内容：

~~~text
Traceback (most recent call last):
  File ".../traceback_demo.py", line 10, in <module>
    build_report()
  File ".../traceback_demo.py", line 7, in build_report
    return calculate_progress(0, 2)
  File ".../traceback_demo.py", line 2, in calculate_progress
    return finished_hours / target_hours
ZeroDivisionError: division by zero
~~~

阅读顺序可以很朴素：

1. 最后一行告诉你发生了什么：<code>ZeroDivisionError</code>。
2. 往上一层找到直接失败的位置：除法表达式。
3. 再往上看是谁传入了 0：<code>build_report()</code>。
4. 最后决定业务规则：目标小时为 0 是特殊状态，还是非法数据？

只看到“除以零”还不能决定怎样修。真正的修复取决于数据规则。本项目要求目标小时大于 0，所以校验应在 JSON 输入边界发生。

把完整 traceback、最小输入和你认为正确的结果一起交给 AI，比只复制最后一句更容易得到有用建议。建议仍要回到同一输入上验证。

</section>

<section id="concept-boundary" data-learning-context="concept-boundary" data-context-type="concept" markdown="1">

## 哪些错误应该由程序说明

报告器面对两类失败：

- 用户或文件带来的已知输入问题：文件不存在、JSON 语法错误、字段缺失、数值不合法。
- 程序员写错代码：变量拼错、函数参数错、模块职责被破坏。

第一类可以转成简短提示和非零退出码；第二类应该保留 traceback，方便修复。如果把所有异常都捕获，两个世界会混在一起。

<code>data_io.py</code> 先检查外部数据：

~~~python
def _validate_number(value, field_name, record_number):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            f"第 {record_number} 条记录的 {field_name} 必须是数字"
        )
~~~

这里特意排除布尔值。Python 中 <code>bool</code> 是 <code>int</code> 的子类，只检查数字类型会意外接受 JSON 中的 <code>true</code>。

同一个模块还要拒绝：

- JSON 根结构不是对象。
- 缺少 <code>records</code>。
- 记录或标签不是约定类型。
- 课程名为空。
- 目标小时小于等于 0。
- 完成小时小于 0。

越早指出具体记录和字段，后面的计算越简单。

</section>

<section id="example-narrow-except" data-learning-context="example-narrow-except" data-context-type="example" markdown="1">

## 入口只接住能解释的失败

<code>main.py</code> 的入口只处理三类已知问题：

~~~python
def main(input_path=INPUT_PATH, data_dir=DATA_DIR, output_path=OUTPUT_PATH):
    try:
        run(input_path, data_dir, output_path)
    except FileNotFoundError as error:
        print(f"输入错误：找不到文件 {error.filename}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as error:
        print(
            f"输入错误：JSON 格式无效，第 {error.lineno} 行，"
            f"第 {error.colno} 列",
            file=sys.stderr,
        )
        return 1
    except ValueError as error:
        print(f"输入错误：{error}", file=sys.stderr)
        return 1
    return 0
~~~

不要改成：

~~~python
try:
    run_program()
except Exception:
    print("运行失败")
~~~

这段代码连 <code>NameError</code>、错误参数类型和其他程序缺陷也会吞掉。学习者只看到一句模糊提示，真正能定位问题的调用链反而消失。

<code>try</code> 的范围也要尽量小。成功后才做的事可以放在 <code>else</code>；无论成功失败都必须发生的清理才放进 <code>finally</code>。本项目的文件读写已经由 <code>Path.read_text()</code> 和 <code>write_text()</code> 管理关闭，不需要为了“凑齐语法”硬加 <code>finally</code>。

</section>

<section id="reproduce-v10" data-learning-context="reproduce-v10" data-context-type="reproduce" markdown="1">

## 跑起报告器 v1.0

完整项目在[学习进度报告器目录](../../../exercises/python-basics/study-progress-reporter/README.md)。进入目录后运行：

~~~bash
cd exercises/python-basics/study-progress-reporter
python main.py
python -m unittest discover -s tests -v
~~~

正常运行应生成报告并返回 0。紧接着检查：

~~~bash
echo $?
~~~

Windows PowerShell 使用：

~~~powershell
$LASTEXITCODE
~~~

测试输出最后应看到：

~~~text
Ran 14 tests
OK
~~~

14 项测试分布在四个文件：

| 测试文件 | 它在保护什么 |
| --- | --- |
| <code>test_analysis.py</code> | 正常汇总、空记录、超额完成上限 |
| <code>test_data_io.py</code> | UTF-8、输入只读、缺文件、坏 JSON、字段与范围、输出目录 |
| <code>test_reporting.py</code> | 报告文字和空数据表现 |
| <code>test_main.py</code> | 标准输出、标准错误、退出码与输出文件 |

单独导入四个业务模块也应该保持安静：

~~~bash
python -c "import analysis, data_io, reporting, main"
~~~

这条命令不应打印报告，也不应创建 <code>output/</code>。它继续保护上一课建立的导入边界。

</section>

<section id="modify-validation" data-learning-context="modify-validation" data-context-type="modify" markdown="1">

## 自己补一条输入规则

示例已经拒绝空课程名。请在练习副本中再选一条没有现成答案的规则，例如：

- 标签字符串不能只包含空格。
- 完成小时不能超过某个合理的项目上限。
- 同一份输入中课程名不能重复。

先写下三件事：

~~~text
输入：
期望：
应该在哪个模块拒绝：
~~~

然后在 <code>test_data_io.py</code> 增加测试。先运行这一个测试，确认它确实失败；再在 <code>data_io.py</code> 做最小修改，最后运行全部 14 项加上你的新测试。

这里先别急着追求“覆盖所有情况”。一条规则、一条失败、一处修改，足以练清楚从需求到回归的完整过程。

</section>

<section id="concept-debugging" data-learning-context="concept-debugging" data-context-type="concept" markdown="1">

## 调试不是轮流猜写法

遇到问题时，可以按这条顺序来：

~~~mermaid
flowchart LR
    A["固定同一输入"] --> B["读错误或错误结果"]
    B --> C["缩小到一个函数"]
    C --> D["看真实值与类型"]
    D --> E["只改一处"]
    E --> F["重跑同一输入"]
    F --> G["补测试并跑全部"]
~~~

几个小工具已经够用：

- <code>repr(value)</code>：看清末尾空格、换行和转义。
- <code>type(value)</code>：确认运行时拿到的是字符串、数字、列表还是字典。
- <code>breakpoint()</code>：在可疑值进入计算前停下。
- <code>p expression</code>：在调试器里查看表达式。
- <code>n</code>：执行当前函数下一行。
- <code>s</code>：进入当前行调用的函数。
- <code>c</code>：继续运行。
- <code>q</code>：退出调试器。

断点是观察工具，不是修复。排查完成后删掉临时断点，把真正需要长期保留的判断写进测试。

</section>

<section id="example-unittest" data-learning-context="example-unittest" data-context-type="example" markdown="1">

## 第一份测试只检查一个规则

~~~python
--8<-- "examples/python-basics/test_progress_micro.py"
~~~

运行：

~~~bash
python -m unittest site-src/examples/python-basics/test_progress_micro.py -v
~~~

每个测试方法只讲一个场景：

- 超额完成时，结果上限是 1.0。
- 目标小时为 0 时，必须抛出 <code>ValueError</code>。

<code>unittest</code> 会把以 <code>test</code> 开头的方法识别为测试。<code>assertEqual</code> 检查结果，<code>assertRaises</code> 检查明确异常。

如果一个测试从来没见过红灯，你还不能确定它真的能抓住目标问题。在临时副本中把期望值改成 1.25，读一次失败中的 expected / actual 差异，然后恢复为 1.0。

</section>

<section id="troubleshoot-tests" data-learning-context="troubleshoot-tests" data-context-type="troubleshoot" markdown="1">

## 测试出问题时看这几处

| 现象 | 常见原因 | 怎样回来 |
| --- | --- | --- |
| 只显示“运行失败” | 捕获了所有 <code>Exception</code> | 改为明确异常，让未知缺陷继续抛出 |
| 测试一直是绿的 | 没有触发目标规则 | 临时破坏期望或实现，确认它能变红 |
| 单个测试通过，全部运行失败 | 测试共享可变状态或文件 | 每个测试独立准备数据，文件使用临时目录 |
| 测试改坏真实 JSON | 路径指向项目 <code>data/</code> | 使用 <code>TemporaryDirectory</code> 创建输入输出 |
| <code>assert</code> 没有运行 | Python 使用了优化模式 | 用户输入校验改用普通判断和 <code>raise</code> |
| 错误提示出现在 stdout | 没有指定输出流 | 面向失败的提示写到 <code>sys.stderr</code> |
| <code>main()</code> 返回 1，进程仍显示成功 | 返回值没有交给系统 | 入口使用 <code>raise SystemExit(main())</code> |
| 测试发现导入错了另一份代码 | 当前目录或环境不对 | 检查 cwd、<code>sys.executable</code> 与导入来源 |

文件测试使用 <code>tempfile.TemporaryDirectory</code>。它提供隔离目录，离开上下文后会清理；测试不需要依赖个人绝对路径，也不会污染项目输出。

普通 <code>assert</code> 适合开发者内部不变量，但优化模式可能移除它。用户输入、权限和安全相关检查必须使用正常条件判断。

</section>

<section id="project-v10" data-learning-context="project-v10" data-context-type="project" markdown="1">

## 报告器 v1.0

| 上一版 | 这节课增加 | 需要保存 | 下一步 |
| --- | --- | --- | --- |
| v0.6：四模块报告器 | 输入校验、明确错误出口、退出码、14 项自动测试 | 正常输出、一次 traceback、红灯与绿灯、测试命令、一次主动新增规则 | 进入 CS 起步，继续理解数据表示与操作成本 |

程序现在形成一条可以检查的数据流：

~~~mermaid
flowchart LR
    A["JSON 输入"] --> B["读取与校验"]
    B --> C["计算汇总"]
    C --> D["生成报告"]
    D --> E["写入文件"]
    T["14 项测试"] -.保护.-> B
    T -.保护.-> C
    T -.保护.-> D
    T -.保护.-> E
~~~

提交前保存：

- 一次正常运行和退出码 0。
- 一次坏 JSON 或非法记录，以及 stderr 和退出码 1。
- 一次测试先失败、修复后通过。
- 你的新增规则和对应测试。
- 输入文件运行前后字节一致的检查。

这还不是大型产品，但它已经能说明：你怎样划分模块、怎样建立输入边界、怎样处理已知失败，以及怎样用测试保护重构。

</section>

<section id="deepen-test-design" data-learning-context="deepen-test-design" data-context-type="deepen" markdown="1">

## 再深入一点：测试的是契约，不是代码行数

测试不应该只是追求“每行都跑过”。更重要的是把外部可见约定固定下来：

- 相同数据生成相同报告。
- 超额完成最多显示 100%。
- UTF-8 中文往返不乱码。
- 输入文件不被修改。
- 已知输入问题返回 1，并写入 stderr。
- 未预料的编程错误不被伪装成正常输入失败。
- 测试之间互不依赖，顺序变化仍能运行。

重构后测试不变，说明外部行为还在；需求变化时先修改契约和测试，再改实现。测试不是为了证明“永远没有 bug”，而是让已经确认的规则不容易悄悄退回去。

</section>

<section id="career-debug-story" data-learning-context="career-debug-story" data-context-type="career" markdown="1">

## 怎样讲一次真实的修复

可以用四句话组织：

1. **现象**：超额完成时报告显示 150%，程序没有抛异常。
2. **定位**：把问题缩成 <code>calculate_progress(2, 3)</code>，确认计算没有上限。
3. **修改**：用 <code>min(..., 1.0)</code>做最小修复，输入合法性仍留在读取边界。
4. **验证**：先看到测试红灯，再让它变绿，并运行 14 项回归确认报告、文件和退出码没有倒退。

如果讲文件错误，也要说明为什么只捕获明确输入异常，而不使用 <code>except Exception</code>。这里体现的是判断边界和验证能力，不是背异常名称。

</section>

## 完成检查

- [ ] 我能区分语法错误、运行时异常和错误结果。
- [ ] 我能从 traceback 最后一行向上解释调用链。
- [ ] 我为已知输入问题选择了明确异常，没有捕获所有 <code>Exception</code>。
- [ ] 我能说明 <code>repr()</code>、<code>type()</code> 和 <code>breakpoint()</code>各自看什么。
- [ ] 我知道普通 <code>assert</code> 不能代替用户输入校验。
- [ ] 我运行了微型测试，并亲眼看过一次红灯。
- [ ] 我运行了阶段作品 14 项测试。
- [ ] 我用临时目录验证文件行为，没有改坏真实输入。
- [ ] 我确认正常退出码为 0，输入错误为 1。
- [ ] 我新增了一条自己的输入规则和测试。
- [ ] 我保存了正常、失败、修复和完整回归结果。
- [ ] 我能用现象、定位、修改和验证讲清一次修复。

## 来源与版本

- 适用版本：Python 3.11 及以上；课程和阶段作品只使用标准库。
- 核查日期：2026-07-17。
- 事实来源：[Errors and Exceptions](https://docs.python.org/3.11/tutorial/errors.html)说明语法错误、异常、traceback、指定异常捕获、<code>raise</code>和清理；[unittest](https://docs.python.org/3.11/library/unittest.html)说明测试用例、断言、发现和独立性；[pdb](https://docs.python.org/3.11/library/pdb.html)说明 <code>breakpoint()</code>与单步调试；[assert 语句](https://docs.python.org/3.11/reference/simple_stmts.html#the-assert-statement)说明优化模式下断言可被移除；[tempfile](https://docs.python.org/3.11/library/tempfile.html#tempfile.TemporaryDirectory)用于隔离文件测试。
- 代码验证：仓库脚本检查三份微型例子、阶段作品 14 项测试、导入无副作用、正常与非法输入退出码、输入只读；自动测试不联网，也不安装第三方包。

## 下一步

Python 起步到这里完整收口。默认路线进入[CS 起步](../../cs-core/README.md)，先理解数据怎样表示、位置访问与扫描成本，再决定继续应用工程、系统工程或算法方向。

如果你更想先强化语言，也可以进入[Python / C++ 双主修说明](../README.md)。求职目标可以同时整理[学习进度报告器项目证据](../../../exercises/career-readiness/study-progress-reporter-evidence.md)，但不要只背话术，回答必须回到代码、失败记录和测试结果。

[进入 CS 起步](../../cs-core/README.md){ .md-button .md-button--primary }
