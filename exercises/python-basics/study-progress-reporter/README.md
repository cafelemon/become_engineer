# 学习进度报告器

这是 Python 起步课程的阶段作品。第一课先做一份只会打印单条记录的学习档案，后面七节课不断给它增加判断、函数、数据结构、文件、模块和测试，最后形成一个可以重复运行的小型程序。

它不是长期项目。长期项目会跨越更多主线持续演进；本作品只负责证明学习者已经能独立组织、运行和检查一个小型 Python 程序。

## 关联课程

- [变量、基本类型、输入输出](../../../learning-paths/programming-languages/python-basics/01-variables-types-io.md)
- [条件、循环、布尔逻辑](../../../learning-paths/programming-languages/python-basics/02-conditions-loops-boolean.md)
- [函数、参数、返回值和作用域](../../../learning-paths/programming-languages/python-basics/03-functions-parameters-returns-scope.md)
- [字符串、列表、字典、集合和元组](../../../learning-paths/programming-languages/python-basics/04-strings-collections.md)
- [文件、路径、JSON 和简单目录操作](../../../learning-paths/programming-languages/python-basics/05-files-json-paths.md)
- [模块、导入和虚拟环境](../../../learning-paths/programming-languages/python-basics/06-modules-imports-venv.md)
- [异常、基本调试和最小自动化测试](../../../learning-paths/programming-languages/python-basics/07-errors-debugging-tests.md)

## 它是怎样长出来的

| 版本 | 程序新增了什么 | 对应课程 |
| --- | --- | --- |
| v0.1 | 用变量保存一条学习档案，打印昵称、课程和计划小时 | 变量、类型与输入输出 |
| v0.2 | 根据计划与完成情况判断状态 | 条件、循环与布尔逻辑 |
| v0.3 | 把报告逻辑整理成有参数和返回值的函数 | 函数、参数、返回值与作用域 |
| v0.4 | 保存和汇总多条学习记录 | 字符串与常用容器 |
| v0.5 | 从 JSON 读取记录并写出报告 | 文件、路径与 JSON |
| v0.6 | 按读取、分析、报告和入口拆分模块 | 模块、导入与虚拟环境 |
| v1.0 | 为输入错误设置退出码，并用自动化测试保护行为 | 异常、调试与测试 |

正式 v0.3 使用 `calculate_progress()` 计算完成比例、`build_status()` 生成状态，并由 `build_report_line()` 组合一条可显示的记录。课程示例先保持单条数据；v0.4 再把同一组函数应用到多条记录。

正式 v0.4 使用列表中的字典保存多条记录，由 `summarize_records()` 汇总目标、完成小时与课程状态，并用 `normalize_tags()` 得到稳定的唯一标签。下一版只改变数据来源，不改变这份内存数据的基本形状。

正式 v0.5 从 `data/study_records.json` 读取同一形状的数据，把报告写到 `output/study_report.txt`，并保持输入文件只读。路径、编码、JSON 解析与字段访问的失败位置分开记录，为最终异常处理留下清楚边界。

正式 v0.6 把读取写入、业务计算、报告排版和启动编排分别放入四个模块。入口通过脚本位置确定项目根目录，四个模块可单独导入且不产生输出或文件副作用；虚拟环境用实际解释器路径验证，不提交 `.venv/`。

正式 v1.0 在数据边界拒绝缺字段、错误类型和非法数值，入口只捕获可解释的文件、JSON 与校验错误。正常运行返回 0，已知输入错误返回 1；14 项 `unittest` 覆盖计算、文件、报告、输入只读、标准错误和退出码。

课程里的每个版本都应能单独运行。学到后面时，不需要推翻前面的程序，只需要说明这次新增了什么、为什么值得加，以及怎样确认旧行为没有被破坏。

## 能力目标

完成后，你应该能够：

- 从 UTF-8 JSON 文件读取并校验多条学习记录。
- 使用多个职责单一的模块完成读取、计算、报告与流程编排。
- 对可以预期的输入错误给出清楚提示和非零退出码。
- 保留意外编程错误的 traceback，不用宽泛捕获隐藏缺陷。
- 使用 `unittest` 与临时目录验证正常、边界和失败场景。
- 证明输入文件不会被程序修改，导入模块也不会触发主流程。

## 目录结构

```text
study-progress-reporter/
├── data/
│   └── study_records.json
├── tests/
│   ├── test_analysis.py
│   ├── test_data_io.py
│   ├── test_main.py
│   └── test_reporting.py
├── .gitignore
├── analysis.py
├── data_io.py
├── main.py
└── reporting.py
```

## 环境与运行

- Python 3.11 或更高版本。
- 只使用标准库，无需安装第三方依赖。
- 从本目录执行命令。

运行程序：

```bash
python main.py
```

运行测试：

```bash
python -m unittest discover -s tests -v
```

也可以先创建项目专属虚拟环境：

```bash
python -m venv .venv
.venv/bin/python main.py
.venv/bin/python -m unittest discover -s tests -v
```

Windows PowerShell 使用：

```powershell
python -m venv .venv
.venv\Scripts\python.exe main.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

程序会在终端打印报告，并生成 `output/study_report.txt`。`output/` 是可再生结果，已由局部 `.gitignore` 排除。

## 失败场景

可以在临时副本中尝试以下修改：

- 删除输入文件，观察 `FileNotFoundError` 如何变成可理解提示。
- 删除 JSON 中的一个逗号，观察错误行列位置。
- 删除记录的 `tags` 字段，观察结构校验。
- 把 `target_hours` 改成字符串或零，观察类型和范围校验。
- 故意改错一个测试期望，确认测试会先失败，恢复后再通过。

不要直接破坏仓库中的固定样例；练习失败路径时使用临时副本。

## AI 协作边界

AI 可以帮助生成校验条件、测试候选和重构建议，但学习者必须亲自完成：

- 说明每个被捕获异常为什么属于可预期输入错误。
- 检查是否存在 `except Exception` 等过宽捕获。
- 让新增测试先在缺少修复时失败，再完成最小修复。
- 主动增加一个边界用例，并解释测试证明了什么。
- 运行全部测试，审阅实际输出和退出码。

学习记录只需保留任务、约束、AI 产出摘要、人工修改和验证证据，不需要公开私人对话。

## 验收

- `python main.py` 返回退出码 `0` 并生成预期报告。
- `python -m unittest discover -s tests -v` 全部通过。
- 缺失文件、坏 JSON 和非法记录返回非零退出码，错误写入标准错误。
- 测试使用临时目录，不依赖个人绝对路径。
- 运行前后 `data/study_records.json` 内容一致。
- 单独导入 `analysis`、`data_io`、`reporting` 和 `main` 时不打印、不读写文件、不创建目录。

## 后续去向

完成本作品后，默认进入 [Python / C++ 双主修](../../../learning-paths/programming-languages/README.md)。同时已经具备开始 [Python 内容分析工具](../../../projects/python-content-analysis/README.md) P1.1 的前置能力；后续会在真实项目中继续加入 CLI、日志、配置和 CI。
