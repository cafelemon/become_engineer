<div class="be-tutor-mount" data-tutor-lesson="python-core-06" aria-hidden="true"></div>

<section id="overview-installed-command" class="be-page-hero be-lesson-hero" data-learning-context="overview-installed-command" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 工程化 · 第一课 · 离开源码目录也能运行</span>

# Python 包结构、可安装入口与 CLI

## 换到空目录，这条命令还认识你的程序

~~~bash
study-progress report
python -m study_progress_reporter report
~~~

两条命令都能输出同一份学习进度报告，而且当前目录里没有 `main.py`。这说明程序依赖的是已经安装的包，而不是“终端刚好站在源码旁边”。

<div class="be-page-actions" markdown="1">
[先分清三个名字](#concept-package-names){ .md-button .md-button--primary }
[做一次干净安装](#reproduce-wheel-install){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 工程化 · 1 / 2</strong></div>
  <div><span>前置</span><strong>模块、虚拟环境、函数接口、测试和资源边界</strong></div>
  <div><span>完成后留下</span><strong>可安装 wheel、模块入口、控制台命令和两个 CLI 子命令</strong></div>
</div>

## 开始前

- 能创建并激活虚拟环境，知道 `python -m pip` 使用的是哪个解释器。
- 能读懂包内绝对导入和 `main(argv) -> int`。
- 已完成学习进度报告器的核心五课，当前正式项目有 30 项测试。
- 本课运行依赖仍只有标准库；构建与类型检查属于开发工具。

<section id="concept-package-layers" data-learning-context="concept-package-layers" data-context-type="concept" markdown="1">

## 一个项目里有四个不同层次

~~~text
分发项目 study-progress-reporter
└── 导入包 study_progress_reporter
    ├── 模块 reporting.py / cli.py / config.py
    └── 对外接口 build_report() / StudyRecord

终端命令 study-progress
~~~

- **模块**通常对应一个 `.py` 文件。
- **导入包**是 Python 代码里的命名空间，名称必须是合法标识符。
- **分发项目**由安装器和项目元数据识别，可以使用连字符。
- **控制台命令**给终端用户使用，可以另取更短的名字。

名字不必相同，但映射必须在 `pyproject.toml`、源码和文档中一致。

</section>

<section id="concept-package-names" data-learning-context="concept-package-names" data-context-type="concept" markdown="1">

## 连字符、下划线和导入语句别混在一起

| 使用位置 | 本项目名称 | 例子 |
| --- | --- | --- |
| 安装和元数据 | `study-progress-reporter` | `pip install study-progress-reporter` |
| Python 导入 | `study_progress_reporter` | `from study_progress_reporter import build_report` |
| 终端调用 | `study-progress` | `study-progress report` |

`import study-progress-reporter` 会被 Python 当成减法表达式，当然不能工作。控制台命令也不是 Python 模块名，它由安装过程生成。

</section>

<section id="concept-src-layout" data-learning-context="concept-src-layout" data-context-type="concept" markdown="1">

## src 布局故意让“没安装也能导入”变难

~~~text
python/
├── pyproject.toml
├── src/
│   └── study_progress_reporter/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       └── reporting.py
└── tests/
~~~

若包直接放在项目根目录，终端站在这里时，当前目录会进入模块搜索路径。即使安装配置漏了文件，测试仍可能因为“源码就在脚边”而通过。

`src` 布局要求先安装，测试和使用者更接近真实安装边界。不要用 `sys.path.append("src")` 绕回去；那会把问题重新藏起来。

</section>

<section id="example-pyproject" data-learning-context="example-pyproject" data-context-type="example" markdown="1">

## pyproject.toml 告诉构建工具去哪里找包

~~~toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "study-progress-reporter"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
study-progress = "study_progress_reporter.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
~~~

`[project.scripts]` 的右侧是“导入模块 : 可调用对象”。安装器会生成 `study-progress` 命令，并在调用时执行 `cli.main()`。

版本、Python 要求和依赖都属于公开契约。不要为了“安装成功”漏写真实运行依赖；当前项目确实只用标准库，所以 `dependencies = []` 才成立。

</section>

<section id="concept-two-entrypoints" data-learning-context="concept-two-entrypoints" data-context-type="concept" markdown="1">

## 两个入口，最后只走一个 main

~~~mermaid
flowchart LR
    A["study-progress"] --> C["cli.main(argv)"]
    B["python -m study_progress_reporter"] --> D["__main__.py"]
    D --> C
    C --> E{"report / audit"}
    E --> F["build_report()"]
    E --> G["write_audit_snapshot()"]
~~~

`__main__.py` 保持很薄：

~~~python
from study_progress_reporter.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
~~~

不要分别复制两套参数解析和业务逻辑。入口越薄，帮助文本、退出码和输出越不容易漂移。

</section>

<section id="concept-cli-boundary" data-learning-context="concept-cli-boundary" data-context-type="concept" markdown="1">

## CLI 解析人的输入，业务函数处理业务

~~~text
study-progress report [--tag TAG]
study-progress audit [--output PATH]
~~~

`argparse` 负责子命令、参数、帮助和语法错误；报告计算和文件提交仍由普通函数完成：

~~~python
def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "report":
        print(build_report(records))
        return 0
    ...
~~~

让 `main()` 接收 `argv`，测试就能直接传 `['report', '--tag', '工程']`，不必修改全局 `sys.argv`。库模块也不要在导入时调用 `parse_args()` 或 `SystemExit`。

</section>

<section id="example-cli-help" data-learning-context="example-cli-help" data-context-type="example" markdown="1">

## 不记参数，先问 --help

~~~bash
study-progress --help
study-progress report --help
study-progress audit --help
~~~

帮助应列出 `report`、`audit`、`--tag` 和 `--output`。再运行：

~~~bash
study-progress report --tag 工程
~~~

报告里只出现“工程复盘”。随后执行无筛选的 `study-progress report`，四条记录应全部回来，证明筛选没有修改共享样例数据。

</section>

<section id="troubleshoot-direct-file" data-learning-context="troubleshoot-direct-file" data-context-type="troubleshoot" markdown="1">

## 直接运行 cli.py，为什么反而导入失败

~~~bash
python src/study_progress_reporter/cli.py
~~~

这条命令把包内模块当成孤立脚本。解释器没有通过已安装包进入，绝对导入可能报 `ModuleNotFoundError`。

正确恢复方式：

~~~bash
python -m pip install -e ".[dev]"
python -m study_progress_reporter report
study-progress report
~~~

不要把导入改成同目录裸导入，也不要在源码里追加机器路径。失败说明入口用错了，不说明包内绝对导入应该被拆掉。

</section>

<section id="troubleshoot-import-side-effect" data-learning-context="troubleshoot-import-side-effect" data-context-type="troubleshoot" markdown="1">

## 只 import 一下，不该突然打印报告

~~~bash
python -c "import study_progress_reporter"
~~~

这条命令应该安静退出，不创建文件、不配置全局日志、不解析命令行。

`__init__.py` 可以导出稳定接口：

~~~python
from study_progress_reporter.models import StudyRecord
from study_progress_reporter.reporting import build_report

__all__ = ["StudyRecord", "build_report"]
~~~

真正执行应用只留在 `cli.main()` 和 `__main__.py`。这样别人可以把报告器当库使用，而不会因为导入一个类型就启动程序。

</section>

<section id="reproduce-wheel-install" data-learning-context="reproduce-wheel-install" data-context-type="reproduce" markdown="1">

## 在干净环境里安装 wheel

从项目目录构建，但把产物放进临时目录：

~~~bash
python -m build --no-isolation
~~~

然后创建新虚拟环境，安装 wheel，并切到项目之外运行：

~~~bash
python -m venv /tmp/study-progress-smoke
/tmp/study-progress-smoke/bin/python -m pip install --no-deps dist/*.whl
cd /tmp
/tmp/study-progress-smoke/bin/study-progress report
/tmp/study-progress-smoke/bin/python -m study_progress_reporter report
~~~

两个入口都应包含 `总体进度：87.1%`，stderr 为空，退出码为 0。最后检查 `--help` 和错误子命令：未知子命令由 argparse 返回 2。

仓库验证脚本会在真正的临时目录中完成同样检查，不复用项目自己的虚拟环境或源码路径。

</section>

<section id="modify-status-filter" data-learning-context="modify-status-filter" data-context-type="modify" markdown="1">

## 增加 --status，但别碰默认报告

给 `report` 增加只读筛选：

~~~text
study-progress report --status 进行中
study-progress report --status 已完成
~~~

先写这些测试：

1. “进行中”只保留两条对应记录。
2. “已完成”只保留完成记录。
3. 非法状态由 argparse 或清楚的校验返回非零。
4. 无 `--status` 时报告逐字保持原样。
5. 模块入口和控制台入口输出一致。

筛选逻辑放在分析模块，CLI 只选择和调用。不要直接修改 `sample_records()` 返回的对象。

</section>

<section id="project-installable-reporter" data-learning-context="project-installable-reporter" data-context-type="project" markdown="1">

## 学习进度报告器现在是一件可安装工具

当前项目已经具备：

- `src/study_progress_reporter/` 常规包。
- `pyproject.toml` 项目元数据和控制台入口。
- `python -m study_progress_reporter` 模块入口。
- `report` 与 `audit` 子命令。
- 30 项单元测试和严格 mypy。

本课不改 `build_report()`、`write_audit_snapshot()` 和主报告文本。安装只是新增调用边界，不应迫使业务核心知道终端命令叫什么。

运行当前回归：

~~~bash
python -m mypy --strict .
PYTHONPATH=src python -m unittest discover -s tests -v
python -m build --no-isolation
~~~

再由干净环境安装 wheel。源码测试和安装测试缺一项，都不能证明发布物可用。

</section>

<section id="deepen-package-contract" data-learning-context="deepen-package-contract" data-context-type="deepen" markdown="1">

## editable 成功，不代表 wheel 一定完整

editable install 常把开发环境直接指向源码，适合快速迭代；wheel 是准备交给另一环境的实际产物。包发现规则、数据文件和入口声明有误时，editable 可能工作，wheel 却缺内容。

工程化验证至少分三层：

1. 源码静态检查和单元测试。
2. 构建产物内容与元数据。
3. 干净环境、项目目录外的安装后 smoke test。

上传 PyPI、版本兼容矩阵、锁定构建依赖和供应链签名属于后续发布工程，本课不把“本地 wheel 可安装”夸大为生产发布已经完成。

</section>

<section id="career-package-evidence" data-learning-context="career-package-evidence" data-context-type="career" markdown="1">

## 讲包化时，拿出项目目录外的结果

可以这样表达：

> 我把多模块报告器迁移为 `src` 布局的可安装包，使用同一个 `cli.main()` 支持控制台命令和 `python -m`。CLI 只处理参数与进程状态，报告和审计仍由业务函数负责。验证覆盖导入无副作用、帮助文本、筛选、退出码、wheel 内容，以及干净虚拟环境中从项目目录外运行两个入口；默认报告与 C++ 对照保持不变。

这比“我会写 pyproject.toml”更能说明你处理过安装边界和假成功。

</section>

## 完成检查

- [ ] 我能区分模块、导入包、分发项目和终端命令。
- [ ] 我知道 `src` 布局为什么要求先安装，也没有用 `sys.path` 绕过。
- [ ] 我能从 `[project.scripts]` 追到 `cli.main()`。
- [ ] 两个正式入口调用同一份业务逻辑。
- [ ] 导入包没有打印、写文件、解析参数或退出进程。
- [ ] 我会用 `--help` 查看子命令和参数。
- [ ] 我复现了直接运行包内文件的错误，并用正式入口恢复。
- [ ] 我在干净虚拟环境安装 wheel，并从项目目录外运行成功。
- [ ] 我完成了 `--status` 筛选及默认回归测试。
- [ ] 正式项目 30 项测试和严格 mypy 保持通过。

## 来源与版本

- 适用版本：Python 3.11 及以上；setuptools 68 及以上；mypy 2.2.0。
- 核查日期：2026-07-17。
- 事实来源：[Python 模块与包](https://docs.python.org/3.11/tutorial/modules.html)用于包、搜索路径和 `__main__`；[Python `-m`](https://docs.python.org/3.11/using/cmdline.html#cmdoption-m)用于模块入口；[`argparse`](https://docs.python.org/3.11/library/argparse.html)用于子命令、帮助和语法错误；[PyPA src 布局](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)用于安装边界；[编写 `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)用于项目元数据与控制台脚本。
- 代码验证：仓库脚本覆盖严格 mypy、30 项测试、无副作用导入、源码外构建、wheel 内容、临时虚拟环境安装、两个入口、帮助、筛选、stderr 和退出码；构建使用本机已安装依赖，不联网。

## 下一步

进入[TOML 配置、日志与可诊断执行契约](07-toml-configuration-logging-diagnostics.md)，让命令显式读取配置，并把业务输出、诊断信息和退出状态分开。
