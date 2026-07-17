<div class="be-tutor-mount" data-tutor-lesson="python-basics-05" aria-hidden="true"></div>

<section id="overview-file-flow" class="be-page-hero be-lesson-hero" data-learning-context="overview-file-flow" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 起步 · 第五课 · 学习进度报告器 v0.5</span>

# 文件、路径、JSON 和简单目录操作

## 改数据，不再改程序

上一版把三条记录直接写在 `.py` 文件里。这一版把它们移到 `data/study_records.json`，程序读取后生成：

```text
发现 JSON：study_records.json
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

只改 JSON 中的完成小时，再运行程序，报告会跟着变化；Python 代码不需要动。输入放在 `data/`，生成结果放在 `output/`，两边不会互相覆盖。

<div class="be-page-actions" markdown="1">
[先看文件怎样进入程序](#concept-cwd-path){ .md-button .md-button--primary }
[查看阶段作品](../../../exercises/python-basics/study-progress-reporter/README.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 起步 · 5 / 7</strong></div>
  <div><span>使用环境</span><strong>Python 3.11+，pathlib 与 json</strong></div>
  <div><span>完成后留下</span><strong>JSON 输入、文本报告与失败记录</strong></div>
</div>

## 开始前

- 已完成[字符串、列表、字典、集合和元组](04-strings-collections.md)，能解释列表中的字典是什么形状。
- 能在终端用 `pwd`/`Get-Location` 和 `ls`/`Get-ChildItem` 确认当前位置与文件。
- 继续在 `practice/python-basics/` 中演进报告器，新建 `data/` 和 `output/` 两个子目录。
- 页面上的 JSON 小例子可以直接运行；真正的文件读写必须在本地终端完成。

<section id="concept-cwd-path" data-learning-context="concept-cwd-path" data-context-type="concept" markdown="1">

## 相对路径从当前工作目录出发

先建立下面的目录：

```text
practice/python-basics/
├── data/
│   └── study_records.json
├── output/
└── learning_profile.py
```

程序中写：

```python
from pathlib import Path

input_path = Path("data") / "study_records.json"
```

`Path("data")` 是相对路径。它从**运行命令时所在的当前工作目录**开始解释，不会自动寻找 `.py` 文件所在目录。

```python
print("当前目录：", Path.cwd())
print("输入路径：", input_path)
print("是否存在：", input_path.exists())
```

如果你先进入 `practice/python-basics/` 再运行 `python learning_profile.py`，这条路径会指向预期文件。若站在上一级目录运行同一个脚本，相对路径的起点变了，文件就可能找不到。

这里先统一从练习目录运行。用 `__file__` 固定项目根目录会在下一课拆分模块时加入，现在先把“命令站在哪里”这件事看清楚。

</section>

<section id="example-path" data-learning-context="example-path" data-context-type="example" markdown="1">

## `Path` 把路径当成路径处理

不要手工拼接 `/` 或 `\\`：

```python
data_dir = Path("data")
input_path = data_dir / "study_records.json"

print(input_path.name)       # study_records.json
print(input_path.suffix)     # .json
print(input_path.parent)     # data
print(input_path.is_file())
```

`Path` 会使用当前操作系统合适的路径规则。常用检查各自回答不同问题：

| 写法 | 回答的问题 |
| --- | --- |
| `path.exists()` | 这个路径现在存在吗 |
| `path.is_file()` | 它存在，并且是普通文件吗 |
| `path.is_dir()` | 它存在，并且是目录吗 |
| `path.resolve()` | 以当前目录为起点，它的绝对位置是什么 |

这些检查适合排错，但不是读取成功的保证。真正读取时仍可能遇到权限、编码或文件变化；后面的异常课程会设计恢复方式。

</section>

<section id="concept-text-json" data-learning-context="concept-text-json" data-context-type="concept" markdown="1">

## 文件先读成文本，JSON 再变成对象

完整数据流分成几步：

<div class="be-file-data-flow" role="img" aria-label="程序用 Path 定位 data 下的 JSON 文件，按 UTF-8 读取成字符串，再用 json.loads 解析为列表和字典，交给汇总函数生成报告字符串，最后写到 output 目录。">
  <div><span>磁盘路径</span><strong>data/study_records.json</strong></div>
  <b aria-hidden="true">→</b>
  <div><span>读取 UTF-8</span><strong>str 文本</strong></div>
  <b aria-hidden="true">→</b>
  <div><span>解析 JSON</span><strong>dict + list</strong></div>
  <b aria-hidden="true">→</b>
  <div><span>汇总与格式化</span><strong>报告字符串</strong></div>
  <b aria-hidden="true">→</b>
  <div><span>写入 UTF-8</span><strong>output/study_report.txt</strong></div>
</div>

```python
import json

text = input_path.read_text(encoding="utf-8")
document = json.loads(text)
records = document["records"]
```

`read_text()` 只负责把文件字节按 UTF-8 解码成字符串；`json.loads()` 才负责理解 JSON 语法并建立 Python 对象。两步分开后，错误发生在哪一层会更容易判断。

JSON 与 Python 看起来相近，但不是同一种语言：

| JSON 写法 | 解析后的 Python | 容易写错的地方 |
| --- | --- | --- |
| 对象 `{}` | `dict` | 键和字符串必须用双引号 |
| 数组 `[]` | `list` | 末项后不能保留逗号 |
| `true` / `false` | `True` / `False` | JSON 使用小写 |
| `null` | `None` | JSON 不写 `None` |

标准 JSON 不支持注释。需要说明字段时，把说明写在课程文档，或使用含义清楚的数据字段。

</section>

<section id="example-json-micro" data-learning-context="example-json-micro" data-context-type="example" markdown="1">

## 先在一段短文本里看解析

下面的程序不读文件，只把一段固定 JSON 文本转成 Python 字典，再重新生成 JSON 文本：

```python
--8<-- "examples/python-basics/json_text_micro.py"
```

<div class="be-python-runner" data-python-runner data-python-source="../../../../examples/python-basics/json_text_micro.py">
  <p class="be-python-runner__fallback">页面运行器正在准备。若它没有出现，请把上面的代码复制到本地文件运行。</p>
</div>

`json.loads(text)` 中的 `s` 可以先记成 string：输入是一段字符串。`json.dumps(record)` 同样返回字符串，并不会自动写文件。

`ensure_ascii=False` 让中文直接显示，`indent=2` 让嵌套结构更容易阅读。它们改变的是输出形式，不改变字典里的业务含义。

</section>

<section id="reproduce-v05" data-learning-context="reproduce-v05" data-context-type="reproduce" markdown="1">

## 跑起报告器 v0.5

把下面的 JSON 保存到 `data/study_records.json`：

```json
--8<-- "examples/python-basics/v05/data/study_records.json"
```

把程序保存为 `learning_profile.py`：

```python
--8<-- "examples/python-basics/v05/study_report_v05.py"
```

先进入练习目录，再运行：

=== "Windows PowerShell"

    ```powershell
    Set-Location .\practice\python-basics
    ..\..\.venv\Scripts\python.exe .\learning_profile.py
    Get-Content .\output\study_report.txt
    ```

=== "macOS / Linux"

    ```bash
    cd ./practice/python-basics
    ../../.venv/bin/python ./learning_profile.py
    cat ./output/study_report.txt
    ```

如果你的虚拟环境不在示例中的相对位置，先用上一阶段学过的命令找到实际解释器，不要照抄一条不属于自己目录的绝对路径。

运行后检查三件事：终端报告与输出文件一致；中文没有乱码；`data/study_records.json` 没有被程序改写。

</section>

<section id="modify-json" data-learning-context="modify-json" data-context-type="modify" markdown="1">

## 只改 JSON，再跑一次

保持 Python 文件不动，完成这些修改：

1. 把三条记录换成自己的课程、小时和标签。
2. 只修改一条 `finished_hours`，确认状态、总完成和输出文件同时变化。
3. 把 `records` 暂时改为空列表，确认报告显示 0 小时、暂无课程和无标签。
4. 恢复数据，再加入中文课程名与重复标签，确认 UTF-8 和去重行为不变。

接着在 `data/` 新建 `archive.json`，内容可以先是 `{}`。`glob("*.json")` 应按排序显示两个文件，但主流程仍只读取明确的 `study_records.json`。扫描到文件不等于所有文件都应该被当成主输入。

</section>

<section id="concept-glob" data-learning-context="concept-glob" data-context-type="concept" markdown="1">

## 只扫描任务允许的目录

```python
data_dir = Path("data")

for path in sorted(data_dir.glob("*.json")):
    if path.is_file():
        print(path.name)
```

`glob("*.json")` 只查看 `data/` 当前层的 JSON 路径；`sorted()` 让显示与测试顺序稳定。

`rglob("*.json")` 会递归进入子目录。它不是更省事的默认选择：根目录过大时，可能扫到输出、缓存、本地素材或私人文件。本课没有递归需求，所以不用它。

如果以后确实需要递归，先明确扫描根目录、扩展名、排除目录、是否只读和最大范围。文件操作的第一条安全原则，是让程序碰到的范围与任务一样小。

</section>

<section id="troubleshoot-file-layers" data-learning-context="troubleshoot-file-layers" data-context-type="troubleshoot" markdown="1">

## 同样是“读不了”，失败位置并不一样

| 失败位置 | 常见错误 | 已经完成到哪一步 | 先检查什么 |
| --- | --- | --- | --- |
| 路径定位 | `FileNotFoundError` | 还没读到文本 | 当前目录、实际文件名、完整路径 |
| 文件读取 | `IsADirectoryError`、`UnicodeDecodeError` | 找到了路径，但没得到正确字符串 | 路径类型、实际编码 |
| JSON 解析 | `JSONDecodeError` | 文本已经读到 | 报错行列附近的引号、逗号、括号与 true/null |
| 字段访问 | `KeyError: 'records'` | JSON 已经成功解析 | 根结构和必填字段 |
| 输出写入 | `PermissionError`、父目录不存在 | 报告可能已经生成 | 输出目录、权限和写入路径 |

请亲手复现两次：先把输入文件名写错，读完 `FileNotFoundError` 中的路径；恢复后在 JSON 最后一项后多写一个逗号，读 `JSONDecodeError` 的行号与列号。

本课先保留完整 traceback，不加宽泛 `except Exception:`。下一阶段会学习怎样只处理预期错误，同时让真正的编程缺陷继续暴露。

</section>

<section id="project-v05" data-learning-context="project-v05" data-context-type="project" markdown="1">

## 报告器 v0.5

| 上一版 | 这节课增加 | 涉及文件 | 需要保存 | 下一版 |
| --- | --- | --- | --- | --- |
| v0.4：多条记录写在程序里 | JSON 输入、受控路径、UTF-8 文本输出和目录扫描 | `learning_profile.py`、`data/study_records.json`、`output/study_report.txt` | 正常报告、输入只读对比、缺失文件与坏 JSON traceback | 按职责拆分模块 |

提交时通常保留输入样例和程序；生成的报告是否入库取决于项目约定。本练习可以先保留一份结果作为学习记录，同时在日志中说明它由哪个输入生成：

```bash
git add practice/python-basics/learning_profile.py \
  practice/python-basics/data/study_records.json \
  practice/python-basics/output/study_report.txt \
  notes/learning-log.md
git diff --cached
git commit -m "load study records from json"
git status --short
```

不要提交包含个人隐私、访问令牌或真实企业数据的 JSON。公开练习只使用自己可以公开的教学数据。

</section>

<section id="deepen-file-boundary" data-learning-context="deepen-file-boundary" data-context-type="deepen" markdown="1">

## 再深入一点：读写边界比一行代码重要

`read_text()` 和 `write_text()` 很短，但程序是否可靠取决于几个明确约定：从哪里运行、允许读哪个目录、允许写哪个目录、采用什么编码、输入是什么结构、失败时保留什么信息。

本课坚持三条边界：

- `data/` 是输入，程序不覆盖它。
- `output/` 是生成结果，写入前明确创建目录。
- 主流程只读取指定文件，目录扫描只用于观察，不把任意 JSON 自动当成可信输入。

以后换成数据库、HTTP 接口或对象存储时，这种“定位—读取—解析—校验—处理—输出”的分层仍然存在。

</section>

<section id="career-file-story" data-learning-context="career-file-story" data-context-type="career" markdown="1">

## 被问到“怎样保证文件处理安全”时

可以说明你把输入和输出目录分开，路径使用 `Path` 组合并从约定工作目录运行，读写明确使用 UTF-8；正常流程只读取指定记录文件，扫描范围限制在 `data/*.json`；验证时比较输入前后内容，并分别复现缺失文件、坏 JSON 与缺失字段。

这仍然是一个小项目，但它已经具备数据处理程序最重要的叙事：数据从哪里来，经过哪些边界，失败发生在哪一层，结果写到哪里，以及怎样证明输入没有被破坏。

</section>

## 完成检查

- [ ] 我能说明相对路径为什么受当前工作目录影响。
- [ ] 我使用 `Path` 组合路径，并检查过 name、suffix、parent 和 is_file。
- [ ] 我明确使用 UTF-8 读取 JSON、写出报告。
- [ ] 我能区分 JSON 文本与解析后的列表、字典和布尔值。
- [ ] 我只修改 JSON 就让报告结果发生了变化。
- [ ] 我确认输入文件在运行前后内容一致，输出只写到 `output/`。
- [ ] 我用受限 `glob("*.json")` 查看文件，并解释为什么本课不用 `rglob()`。
- [ ] 我分别复现并定位了 `FileNotFoundError` 与 `JSONDecodeError`。
- [ ] 我验证了空记录、中文、重复标签和多个 JSON 文件。
- [ ] 我提交了报告器 v0.5、公开教学数据与学习记录。

## 来源与版本

- 适用版本：Python 3.11 及以上；示例只使用标准库 `pathlib` 与 `json`。
- 核查日期：2026-07-17。
- 事实来源：[pathlib 文档](https://docs.python.org/3.11/library/pathlib.html)说明 `Path`、文本读写、目录创建与 glob 行为；[json 文档](https://docs.python.org/3.11/library/json.html)说明 Python/JSON 类型映射、`loads()`、`dumps()` 与 `JSONDecodeError`。
- 代码验证：仓库脚本在临时目录中检查 UTF-8 往返、输入只读、受限扫描、输出文件、缺失输入和坏 JSON；自动测试不联网，也不安装第三方包。

## 下一步

程序已经能读写文件，但所有职责还挤在一个文件里。下一课进入[模块、导入和虚拟环境](06-modules-imports-venv.md)，把读取、分析、报告和入口拆开，并让运行位置不再依赖当前工作目录。

[进入下一课](06-modules-imports-venv.md){ .md-button .md-button--primary }
