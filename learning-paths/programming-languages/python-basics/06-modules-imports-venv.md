<div class="be-tutor-mount" data-tutor-lesson="python-basics-06" aria-hidden="true"></div>

<section id="overview-modules" class="be-page-hero be-lesson-hero" data-learning-context="overview-modules" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 起步 · 第六课 · 学习进度报告器 v0.6</span>

# 模块、导入和虚拟环境

## 输出没变，程序已经分工

直接运行 `main.py`，报告仍与上一版一致：

```text
学习进度报告
总计划：10 小时
总完成：8 小时
课程状态：
- Python 起步: 60%，还需 2 小时
- 复盘练习: 100%，已完成
- Git 复习: 100%，已完成
唯一标签：Python, 复盘, 工具, 起步
报告文件：output/study_report.txt
```

变化发生在程序内部：读取写入放到 `data_io.py`，计算放到 `analysis.py`，排版放到 `reporting.py`，`main.py` 只负责把它们按顺序接起来。单独导入这四个模块时，不会打印报告，也不会创建输出目录。

<div class="be-page-actions" markdown="1">
[先看四个模块怎样分工](#concept-boundaries){ .md-button .md-button--primary }
[查看阶段作品](../../../exercises/python-basics/study-progress-reporter/README.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 起步 · 6 / 7</strong></div>
  <div><span>使用环境</span><strong>Python 3.11+，标准库 venv</strong></div>
  <div><span>完成后留下</span><strong>四模块报告器与可重建 .venv</strong></div>
</div>

## 开始前

- 已完成[文件、路径、JSON 和简单目录操作](05-files-json-paths.md)，报告器能从 JSON 生成文本结果。
- 能在上一版中指出读取、计算、排版和启动代码分别在哪里。
- 已理解 `.venv/` 是本地可重建环境，并确认根目录 `.gitignore` 会忽略它。
- 本课没有第三方依赖；创建虚拟环境是为了确认解释器归属，而不是为了安装更多工具。

<section id="concept-boundaries" data-learning-context="concept-boundaries" data-context-type="concept" markdown="1">

## 按变化原因拆，不按函数数量拆

<div class="be-module-map" role="img" aria-label="main.py 位于上层，依赖下方三个能力模块：data_io.py 负责输入输出，analysis.py 负责计算汇总，reporting.py 负责报告文本。能力模块不反向导入 main.py。">
  <article class="be-module-map__entry"><span>唯一入口</span><strong>main.py</strong><small>选择路径、安排调用、显示结果</small></article>
  <article><span>数据边界</span><strong>data_io.py</strong><small>读取 JSON、写入报告</small></article>
  <article><span>业务计算</span><strong>analysis.py</strong><small>进度、状态、汇总</small></article>
  <article><span>文本表现</span><strong>reporting.py</strong><small>把汇总结果排成报告</small></article>
</div>

模块不是“一个函数一个文件”。更实用的判断是：这些代码会不会因为同一种原因变化？

- 输入格式或写入方式变化，主要影响 `data_io.py`。
- 进度规则变化，主要影响 `analysis.py`。
- 报告文字变化，主要影响 `reporting.py`。
- 运行顺序或路径选择变化，主要影响 `main.py`。

依赖保持从入口指向能力模块。`analysis.py` 不读取文件，`reporting.py` 不反向调用 `main.py`。数据通过参数传入，结果通过返回值传出。

</section>

<section id="example-imports" data-learning-context="example-imports" data-context-type="example" markdown="1">

## 导入模块，还是导入一个名称

一个 `.py` 文件可以成为模块。`analysis.py` 对应模块名 `analysis`。

```python
import analysis

summary = analysis.summarize_records(records)
```

保留 `analysis.` 前缀后，读者能直接看出函数来源。另一种写法把指定名称放进当前模块：

```python
from reporting import build_report

report = build_report(summary)
```

两种写法都正常：

| 写法 | 调用处 | 更适合什么情况 |
| --- | --- | --- |
| `import analysis` | `analysis.summarize_records()` | 来源需要长期保持清楚，或模块中会用多个名称 |
| `from reporting import build_report` | `build_report()` | 只取少量、不易重名的能力 |

本课不使用 `from analysis import *`。它会一次带入一组不明显的名称，可能覆盖当前名称，也让代码来源变得难追踪。

导入失败时先判断来源：`json`、`pathlib` 是标准库；`analysis` 是本地模块；`requests` 一类才是第三方依赖。看到 `ModuleNotFoundError` 不代表应该立刻联网安装。

</section>

<section id="concept-import-time" data-learning-context="concept-import-time" data-context-type="concept" markdown="1">

## 导入会执行模块顶层语句

假设 `welcome.py` 写成：

```python
print("welcome 正在加载")


def build_message(name):
    return f"你好，{name}"
```

另一个文件只写 `import welcome`，顶层 `print()` 仍会在第一次导入时执行。函数体要等调用才执行，模块顶层语句则在加载模块时运行。

因此，业务模块顶层通常只放：

- `import`。
- 常量。
- 函数和类定义。

读取大文件、创建目录、写报告、发送请求和启动主流程，都应该由入口显式调用，而不是藏在导入过程中。

</section>

<section id="example-main-guard" data-learning-context="example-main-guard" data-context-type="example" markdown="1">

## 直接运行时才启动

```python
def main():
    print("程序开始运行")


if __name__ == "__main__":
    main()
```

直接执行 `python main.py` 时，当前顶层模块的 `__name__` 是 `"__main__"`，条件成立。执行 `python -c "import main"` 时，模块名是 `"main"`，不会调用入口函数。

入口保护不是要求每个模块都写一个 `main()`。本项目只有 `main.py` 启动流程；三个能力模块只提供函数。

用下面两条命令验证：

```bash
python main.py
python -c "import analysis, data_io, reporting, main"
```

第二条命令应该没有终端输出，也不创建 `output/`。这比“我已经加了 main guard”更可靠，因为它检查了实际副作用。

</section>

<section id="reproduce-v06" data-learning-context="reproduce-v06" data-context-type="reproduce" markdown="1">

## 跑起四模块报告器

目录调整为：

```text
practice/python-basics/
├── data/
│   └── study_records.json
├── analysis.py
├── data_io.py
├── main.py
└── reporting.py
```

=== "analysis.py"

    ```python
    --8<-- "examples/python-basics/v06/analysis.py"
    ```

=== "data_io.py"

    ```python
    --8<-- "examples/python-basics/v06/data_io.py"
    ```

=== "reporting.py"

    ```python
    --8<-- "examples/python-basics/v06/reporting.py"
    ```

=== "main.py"

    ```python
    --8<-- "examples/python-basics/v06/main.py"
    ```

复制上一课的 JSON 到 `data/study_records.json`，然后运行：

=== "Windows PowerShell"

    ```powershell
    Set-Location .\practice\python-basics
    ..\..\.venv\Scripts\python.exe .\main.py
    ```

=== "macOS / Linux"

    ```bash
    cd ./practice/python-basics
    ../../.venv/bin/python ./main.py
    ```

`main.py` 使用 `Path(__file__).resolve().parent` 找到项目根目录，所以从别的当前目录执行它，仍会读取脚本旁边的 `data/`。这与上一课依赖 cwd 的版本形成一次清楚升级。

重构完成后，报告内容应逐字保持不变。拆文件是内部结构修改，不应该悄悄改变业务输出。

</section>

<section id="modify-module" data-learning-context="modify-module" data-context-type="modify" markdown="1">

## 给数据模块加一个小能力

把上一课的受限扫描放进 `data_io.py`：

```python
def find_json_files(data_dir):
    return sorted(data_dir.glob("*.json"))
```

在 `main.py` 中明确导入并调用：

```python
from data_io import find_json_files, load_records, write_report


for path in find_json_files(PROJECT_ROOT / "data"):
    print("发现：", path.name)
```

这次修改同时碰到两个模块，但职责仍清楚：怎样查找文件属于数据边界，何时显示文件清单属于入口编排。

再做一次选择题：如果要修改“完成比例最多显示 100%”的规则，应该进入哪个模块？如果要改“学习进度报告”标题，又应该进入哪个模块？请先回答，再动代码。

</section>

<section id="concept-venv" data-learning-context="concept-venv" data-context-type="concept" markdown="1">

## 虚拟环境让解释器归属可确认

虚拟环境提供项目自己的 Python 解释器入口和依赖安装位置。即使本课没有第三方包，也先建立检查习惯：

=== "Windows PowerShell"

    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -c "import sys; print(sys.executable)"
    python -m pip --version
    deactivate
    ```

=== "macOS / Linux"

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -c "import sys; print(sys.executable)"
    python -m pip --version
    deactivate
    ```

不要只看提示符前有没有 `(.venv)`。`sys.executable` 应指向项目 `.venv` 中的解释器，`python -m pip --version` 应显示与同一解释器关联的位置。

激活只是让当前终端优先选择这个解释器。即使不激活，也可以直接运行：

```bash
.venv/bin/python main.py
```

Windows 对应 `.venv\Scripts\python.exe main.py`。直接路径在自动化脚本中尤其清楚。

`.venv/` 包含平台相关文件，体积大且不可移植，不应提交 Git。提交创建命令、Python 版本和依赖说明，其他人可以重新生成环境。

</section>

<section id="troubleshoot-imports" data-learning-context="troubleshoot-imports" data-context-type="troubleshoot" markdown="1">

## 导入失败时先分清是哪一类

| 现象 | 常见原因 | 怎样回来 |
| --- | --- | --- |
| `ModuleNotFoundError: analysis` | 本地文件名、运行目录或导入名不一致 | 确认 `analysis.py` 与 `main.py` 同级，并从项目目录运行 |
| `json` 没有预期属性 | 本地 `json.py` 遮蔽标准库 | 重命名本地文件，确认 `json.__file__` 来源，清理对应缓存 |
| `partially initialized module` | 两个模块互相导入 | 重新划分职责，让 `main.py` 组合能力模块 |
| 导入 `main` 就生成报告 | 启动调用仍在模块顶层 | 把动作放进 `main()`，加入入口保护并重新做副作用检查 |
| 安装了包仍然导入失败 | pip 与运行用的 Python 不是同一环境 | 检查 `sys.executable`，使用 `python -m pip` |
| Git 出现大量环境文件 | `.venv/` 或 `__pycache__/` 没被忽略 | 补充 `.gitignore`，只撤下索引中的可再生文件 |

可以在临时练习副本里把文件命名为 `json.py`，观察标准库被遮蔽后的实际错误，再恢复有业务含义的文件名。不要在正式目录留下冲突模块。

本课不修改 `sys.path`，也不设置 `PYTHONPATH`。四个模块同级时，这些绕路只会把结构问题藏起来。

</section>

<section id="project-v06" data-learning-context="project-v06" data-context-type="project" markdown="1">

## 报告器 v0.6

| 上一版 | 这节课增加 | 涉及文件 | 需要保存 | 下一版 |
| --- | --- | --- | --- | --- |
| v0.5：单文件完成 JSON 到报告 | 四个职责模块、稳定项目根目录、入口保护与虚拟环境验证 | `analysis.py`、`data_io.py`、`reporting.py`、`main.py`、`.gitignore` | 重构前后同一输出、无副作用导入、解释器路径和一次导入错误修复 | 异常、退出码与自动化测试 |

提交前确认 `.venv/` 与 `__pycache__/` 没有进入暂存区：

```bash
git add practice/python-basics/*.py notes/learning-log.md
git diff --cached
git status --short
git commit -m "split study reporter into modules"
```

学习记录里画出依赖箭头，并解释为什么 `analysis.py` 不导入 `reporting.py`，三个能力模块也不导入 `main.py`。

</section>

<section id="deepen-dependencies" data-learning-context="deepen-dependencies" data-context-type="deepen" markdown="1">

## 再深入一点：依赖方向决定修改范围

如果 `analysis.py` 和 `reporting.py` 互相导入，两个模块就不再是独立能力，而是一组绕圈的加载过程。更稳妥的结构是让计算返回数据，让排版接收数据，入口负责安排先后。

同样，导入时无副作用不是为了追求“纯粹”，而是为了让模块能被测试、复用和检查。读取文件或写报告都是真实需要，只是应该在调用链上明确发生。

模块边界最终要靠行为验证：重构前后输出相同；每个模块能单独导入；修改报告标题不碰读取代码；修改进度规则不碰输出路径。

</section>

<section id="career-module-story" data-learning-context="career-module-story" data-context-type="career" markdown="1">

## 被问到“为什么要拆模块”时

可以说明原程序把文件、计算、排版和启动混在一起，任何改动都需要通读整份文件；你按变化原因拆成四个模块，让依赖保持单向，并用入口保护消除导入副作用。重构后从任意 cwd 运行仍读到项目数据，报告输出逐字一致；虚拟环境通过 `sys.executable` 验证，而不是只看提示符。

这段叙事的重点不是“文件更多”，而是修改范围、依赖方向、环境复现和回归结果都可以被检查。

</section>

## 完成检查

- [ ] 我能用一句话说明四个模块各自负责什么。
- [ ] 我使用过 `import module` 和 `from module import name`，并能解释选择理由。
- [ ] 我能区分标准库、本地模块和第三方依赖。
- [ ] 我验证了直接运行会启动，而单独导入四个模块没有副作用。
- [ ] 我从不同 cwd 运行 `main.py`，确认项目根目录仍然正确。
- [ ] 我给 `data_io.py` 增加了受限 JSON 文件发现能力。
- [ ] 我复现并修复了一次模块拼写或标准库遮蔽问题。
- [ ] 我创建 `.venv`，用 `sys.executable` 和 `python -m pip` 核对环境。
- [ ] 我确认 `.venv/` 与 `__pycache__/` 没有进入 Git。
- [ ] 我保存了重构前后相同输出，并提交报告器 v0.6。

## 来源与版本

- 适用版本：Python 3.11 及以上；业务示例只使用标准库。
- 核查日期：2026-07-17。
- 事实来源：[Python 模块教程](https://docs.python.org/3.11/tutorial/modules.html)说明模块、导入、模块搜索、顶层执行、`__name__` 和缓存；[虚拟环境教程](https://docs.python.org/3.11/tutorial/venv.html)与 [`venv` 文档](https://docs.python.org/3.11/library/venv.html)说明环境创建和解释器隔离。
- 代码验证：仓库脚本在临时副本中检查四模块导入无副作用、重构前后输出、任意 cwd、真实 venv 解释器和标准库遮蔽失败；自动测试不联网，也不安装第三方包。

## 下一步

结构已经可以单独检查，最后一课进入[异常、基本调试和最小自动化测试](07-errors-debugging-tests.md)，把缺失文件、坏 JSON 与非法记录变成清楚退出码，并用测试保护这六次演进留下的行为。

[进入下一课](07-errors-debugging-tests.md){ .md-button .md-button--primary }
