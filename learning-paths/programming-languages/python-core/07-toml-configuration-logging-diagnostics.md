<div class="be-tutor-mount" data-tutor-lesson="python-core-07" aria-hidden="true"></div>

<section id="overview-three-channels" class="be-page-hero be-lesson-hero" data-learning-context="overview-three-channels" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 工程化 · 第二课 · 让人和脚本都看懂程序结果</span>

# Python TOML 配置、日志与可诊断执行契约

## 同一次运行，留下三种不同答案

~~~text
stdout：学习进度报告……
stderr：INFO study_progress_reporter: 执行命令：report
退出码：0
~~~

stdout 是程序交付的业务结果；stderr 说明程序怎样运行或为什么失败；退出码让 shell、CI 和其他程序判断下一步是否继续。混在一起，人还能勉强读，自动化却很难可靠使用。

<div class="be-page-actions" markdown="1">
[先分清三个通道](#concept-stream-contract){ .md-button .md-button--primary }
[跑完配置与失败矩阵](#reproduce-config-diagnostics){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 工程化 · 2 / 2</strong></div>
  <div><span>前置</span><strong>可安装 CLI、dataclass、Path、异常和自动化测试</strong></div>
  <div><span>完成后留下</span><strong>显式 TOML、固定优先级、命名日志、标准流和退出码契约</strong></div>
</div>

## 开始前

- 已经能从项目目录外运行 `study-progress`。
- 知道 `main(argv) -> int` 的返回值会成为进程退出状态。
- 能用 `TemporaryDirectory` 构造不会污染机器的文件测试。
- 本课使用 Python 3.11 标准库 `tomllib` 与 `logging`，不引入配置框架。

<section id="concept-stream-contract" data-learning-context="concept-stream-contract" data-context-type="concept" markdown="1">

## 三个通道回答三个问题

| 通道 | 回答的问题 | 当前项目 |
| --- | --- | --- |
| stdout | 业务结果是什么 | 完整学习报告 |
| stderr | 程序怎样运行、为什么失败 | INFO 日志与错误说明 |
| 退出码 | 调用方是否应继续 | `0` 成功、`1` 业务失败、`2` 参数语法错误 |

用重定向把它们拆开：

~~~bash
study-progress report >report.txt 2>diagnostics.txt
echo $?
~~~

默认成功时，`report.txt` 有报告，`diagnostics.txt` 为空，退出码是 0。调用方不需要解析中文报告来判断成功。

</section>

<section id="example-exit-codes" data-learning-context="example-exit-codes" data-context-type="example" markdown="1">

## 0、1、2 不是三种随意编号

~~~bash
study-progress report              # 0：完成业务
study-progress audit               # 1：请求合法，但缺少输出路径
study-progress unknown             # 2：命令语法不成立
~~~

`argparse` 已经为语法错误提供 usage 和退出码 2。配置文件坏了、审计路径写不了等情况，是程序理解请求后遇到的业务失败，`main()` 返回 1。

不要让所有错误都返回 0，也不要把业务失败伪装成 argparse 语法错误。稳定的退出码比错误文字更适合脚本判断。

</section>

<section id="concept-explicit-toml" data-learning-context="concept-explicit-toml" data-context-type="concept" markdown="1">

## 配置从哪里来，命令行上要看得见

~~~toml
[report]
tag = "基础"

[audit]
output = "audit.txt"

[logging]
level = "INFO"
~~~

只有显式提供时才读取：

~~~bash
study-progress --config config.example.toml report
~~~

Python 3.11 的 `tomllib` 用二进制文件读取：

~~~python
with path.open("rb") as config_file:
    raw = tomllib.load(config_file)
~~~

本项目不自动搜索当前目录、用户家目录或环境变量。这样同一条命令的输入来源清楚，换机器也不会因为某个隐藏配置突然改变结果。

</section>

<section id="concept-parse-validate" data-learning-context="concept-parse-validate" data-context-type="concept" markdown="1">

## TOML 能解析，不代表配置适合这个程序

`tomllib` 只负责把合法 TOML 变成普通字典。下面的文件语法都正确，却不符合本应用：

~~~toml
[report]
tag = 3

[network]
timeout = 10
~~~

应用只接受：

~~~text
report.tag      -> 非空字符串或缺省
audit.output    -> 非空字符串，随后转换为 Path，或缺省
logging.level   -> DEBUG / INFO / WARNING / ERROR / CRITICAL
~~~

未知表、未知字段、错误类型和空字符串都要拒绝，不能悄悄转成字符串或回退默认值。

</section>

<section id="example-frozen-config" data-learning-context="example-frozen-config" data-context-type="example" markdown="1">

## 校验通过以后，再进入明确的 AppConfig

~~~python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    report_tag: str | None = None
    audit_output: Path | None = None
    log_level: str = "WARNING"
~~~

外部字典只存在于输入边界。通过表名、字段名、类型和取值检查后，核心代码只接触 `AppConfig`，不必在每个调用点重复猜 `dict[str, object]` 里有什么。

`frozen=True` 防止执行过程中随手修改配置，但它不是秘密保护，也不会让 `Path` 指向的文件自动存在。

</section>

<section id="concept-precedence" data-learning-context="concept-precedence" data-context-type="concept" markdown="1">

## 优先级只在一个地方合并

固定顺序：

~~~text
命令行参数 > 显式 TOML > 默认值
~~~

例如配置里是 `tag = "基础"`，命令行又写：

~~~bash
study-progress --config reporter.toml report --tag 工程
~~~

最终使用“工程”。`argparse` 的可选值先保持 `None`，再由 `apply_cli_overrides()` 集中覆盖数据类；不要让 report 和 audit 各自写一套优先级。

</section>

<section id="concept-named-logger" data-learning-context="concept-named-logger" data-context-type="concept" markdown="1">

## 库不抢全局日志，应用只配置自己的名字

~~~python
logger = logging.getLogger("study_progress_reporter")
logger.handlers.clear()
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(level)
logger.propagate = False
~~~

库模块可以取得命名 logger 或接受事件 sink，但不应在导入时调用 `basicConfig()` 改动调用者的 root logger。

重复配置前清理本 logger 的 handler，避免测试或同一进程多次运行后日志成倍出现。`propagate = False` 防止同一事件再交给 root logger 打一遍。

</section>

<section id="example-log-separation" data-learning-context="example-log-separation" data-context-type="example" markdown="1">

## 打开 INFO，报告文字仍然不变

~~~bash
study-progress --log-level INFO report >report.txt 2>diagnostics.txt
~~~

- `report.txt` 与默认报告逐字一致。
- `diagnostics.txt` 包含“执行命令：report”。
- 不传 `--log-level` 时默认 WARNING，成功运行保持安静。

日志使用参数化消息：

~~~python
logger.info("执行命令：%s", arguments.command)
~~~

不要记录完整学习记录、配置全文、环境变量或密钥。能排错不等于应把所有输入都写进日志。

</section>

<section id="troubleshoot-bad-config" data-learning-context="troubleshoot-bad-config" data-context-type="troubleshoot" markdown="1">

## 坏配置要在执行业务之前停下来

三种常见失败：

~~~toml
[report                 # TOML 语法错误
tag = "基础"
~~~

~~~toml
[report]
colour = "blue"         # 未知字段
~~~

~~~toml
[logging]
level = "TRACE"         # 不支持的取值
~~~

CLI 应在 stderr 写清楚错误，返回 1，stdout 为空，也不开始生成审计文件。修复配置后重新运行，不要靠忽略未知字段让拼写错误静默生效。

</section>

<section id="troubleshoot-audit-io" data-learning-context="troubleshoot-audit-io" data-context-type="troubleshoot" markdown="1">

## 审计路径写不了，旧文件仍要安全

~~~bash
study-progress audit --output missing/audit.txt
~~~

本项目不会自动创建父目录。缺失目录时：

- stdout 为空。
- stderr 说明无法写入审计文件。
- 退出码为 1。
- 已有正式文件不变。
- 同目录没有残留 `.tmp`。

配置必须全部校验通过后才开始文件副作用；审计仍使用上一课的分阶段写入边界。

</section>

<section id="reproduce-config-diagnostics" data-learning-context="reproduce-config-diagnostics" data-context-type="reproduce" markdown="1">

## 跑完一张配置与诊断矩阵

在项目目录执行：

~~~bash
python -m mypy --strict .
PYTHONPATH=src python -m unittest discover -s tests -v
~~~

再依次观察：

| 输入 | stdout | stderr | 退出码 |
| --- | --- | --- | ---: |
| 默认 `report` | 完整报告 | 空 | 0 |
| INFO `report` | 完整报告 | INFO 事件 | 0 |
| 坏 TOML | 空 | 配置错误 | 1 |
| `audit` 无路径 | 空 | 需要输出路径 | 1 |
| 未知子命令 | 空 | usage | 2 |

仓库脚本还会验证命令行覆盖 TOML、重复配置 logger 不重复输出、失败前旧文件不变，以及程序不会自动读取工作目录中的配置。

</section>

<section id="modify-report-title" data-learning-context="modify-report-title" data-context-type="modify" markdown="1">

## 给报告标题增加一个可配置选项

增加 `[report].title` 和对应 `--title`，要求：

1. 缺省时仍输出“学习进度报告”。
2. TOML 接受非空字符串，拒绝数字和空白。
3. 命令行标题覆盖 TOML 标题。
4. 未知字段仍然失败。
5. 标题只进入 stdout，不写成 INFO 日志。

若 `build_report()` 需要标题参数，用关键字专用参数表达，并保持默认值兼容现有调用。不要让业务函数读取全局配置对象。

</section>

<section id="project-diagnostic-cli" data-learning-context="project-diagnostic-cli" data-context-type="project" markdown="1">

## Python 工程化闭环完成

学习进度报告器现在可以：

~~~text
显式 CLI / TOML / 默认值
        -> 校验并合并 AppConfig
        -> report 或 audit
        -> stdout 业务结果
        -> stderr 诊断
        -> 0 / 1 / 2 退出状态
~~~

当前 30 项测试覆盖配置、优先级、标准流、日志、参数错误、审计成功与失败；包化测试还会构建 wheel，在干净环境从项目目录外运行。

这节课不自动读取 `.env`，不记录秘密，也不引入远程日志平台。配置来源和数据边界保持小而清楚，后续 Web、AI 与 Agent 项目才能在此基础上继续扩展。

</section>

<section id="deepen-operability" data-learning-context="deepen-operability" data-context-type="deepen" markdown="1">

## 可诊断不等于日志越多越好

好的诊断应该帮助回答：执行了哪个命令、选择了什么公开模式、在哪个边界失败。过多日志会淹没信号，还可能泄露路径、记录内容和秘密。

以后进入服务端系统，还需要结构化日志、请求标识、指标、追踪、日志轮转和隐私策略。本课先建立更基础的约束：

- 业务输出与诊断分流。
- 默认安静，按需打开级别。
- 失败返回非零。
- 日志内容最小化。

</section>

<section id="career-diagnostic-evidence" data-learning-context="career-diagnostic-evidence" data-context-type="career" markdown="1">

## 讲配置和日志时，把失败契约说出来

可以这样表达：

> 我为可安装 CLI 增加了显式 TOML 配置，解析后严格校验未知字段、类型和日志级别，再按“命令行、配置、默认值”集中合并。报告只写 stdout，命名 logger 写 stderr，成功、业务失败和语法错误分别返回 0、1、2。测试覆盖坏 TOML、参数覆盖、重复 handler、缺失路径和旧审计文件保护。

这能说明你设计的是可被人和自动化稳定调用的工具，而不只是“加了 logging”。

</section>

## 完成检查

- [ ] 我能说明 stdout、stderr 和退出码各自服务谁。
- [ ] 我区分了成功 0、业务失败 1 和参数语法错误 2。
- [ ] 配置只通过 `--config` 显式读取，并以二进制模式交给 `tomllib`。
- [ ] 我知道解析成功不等于字段、类型和取值合法。
- [ ] 优先级只在一个函数中实现：命令行大于 TOML，大于默认值。
- [ ] 命名 logger 不污染 root，也不会重复添加 handler。
- [ ] 开启 INFO 后 stdout 报告保持不变。
- [ ] 坏配置和审计失败都在副作用前或安全边界内停止。
- [ ] 我跑完配置与诊断矩阵，并断言三个通道。
- [ ] 我完成了报告标题配置及默认回归。
- [ ] Python 工程化 30 项测试、wheel 和干净安装回归全部通过。

## 来源与版本

- 适用版本：Python 3.11 及以上；mypy 2.2.0。
- 核查日期：2026-07-17。
- 事实来源：[`tomllib`](https://docs.python.org/3.11/library/tomllib.html)用于二进制读取、解析结果和异常；[Logging HOWTO](https://docs.python.org/3.11/howto/logging.html)与[`logging` 参考](https://docs.python.org/3.11/library/logging.html)用于 logger、handler、级别和传播；[`sys.exit`](https://docs.python.org/3.11/library/sys.html#sys.exit)用于进程状态；[`argparse`](https://docs.python.org/3.11/library/argparse.html)用于帮助和语法错误。
- 代码验证：仓库脚本覆盖严格 mypy、30 项测试、显式配置、结构与类型拒绝、优先级、标准流、日志级别、重复 handler、退出码、审计保护、wheel 和干净安装；不联网。

## 下一步

Python 核心与工程化七课已经形成完整成果线。系统方向下一步进入[C++ 起步与核心](../cpp-core/README.md)；算法方向可以进入[共同算法与数据结构基础](../../cs-core/README.md)。两条路线都会继续使用可复现代码、失败路径和项目证据。
