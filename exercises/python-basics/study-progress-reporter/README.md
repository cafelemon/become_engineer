# 学习进度报告器

这是 Python 起步课程的阶段作品。它把连续课程中的函数、常用数据结构、文件与 JSON、模块、异常处理和自动化测试组合成一个可重复运行的小型程序。

它不是长期项目。长期项目会跨越更多主线持续演进；本作品只负责证明学习者已经能独立组织、运行和检查一个小型 Python 程序。

## 关联课程

- [函数、参数、返回值和作用域](../../../learning-paths/programming-languages/python-basics/03-functions-parameters-returns-scope.md)
- [字符串、列表、字典、集合和元组](../../../learning-paths/programming-languages/python-basics/04-strings-collections.md)
- [文件、路径、JSON 和简单目录操作](../../../learning-paths/programming-languages/python-basics/05-files-json-paths.md)
- [模块、导入和虚拟环境](../../../learning-paths/programming-languages/python-basics/06-modules-imports-venv.md)
- [异常、基本调试和最小自动化测试](../../../learning-paths/programming-languages/python-basics/07-errors-debugging-tests.md)

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

