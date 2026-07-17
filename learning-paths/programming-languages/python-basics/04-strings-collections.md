<div class="be-tutor-mount" data-tutor-lesson="python-basics-04" aria-hidden="true"></div>

<section id="overview-multiple" class="be-page-hero be-lesson-hero" data-learning-context="overview-multiple" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Python 起步 · 第四课 · 学习进度报告器 v0.4</span>

# 字符串、列表、字典、集合和元组

## 一条档案变成一组记录

报告器终于不只认识一门课程了：

```text
学习进度报告
总计划：10 小时
总完成：8 小时
课程状态：
- Python 起步: 60%，还需 2 小时
- 复盘练习: 100%，已完成
- Git 复习: 100%，已完成
唯一标签：Python, 复盘, 工具, 起步
```

这里同时出现了五种常见结构：文字用字符串，多条记录放在列表里，一条记录用字典说明字段，唯一标签用集合去重，汇总结果用元组返回。它们不是五份互不相干的语法，而是在同一份程序中各自解决一个问题。

<div class="be-page-actions" markdown="1">
[先看怎样选容器](#concept-choose){ .md-button .md-button--primary }
[查看阶段作品](../../../exercises/python-basics/study-progress-reporter/README.md){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Python 起步 · 4 / 7</strong></div>
  <div><span>使用环境</span><strong>Python 3.11+，只用内置类型</strong></div>
  <div><span>完成后留下</span><strong>报告器 v0.4 与多记录汇总</strong></div>
</div>

## 开始前

- 已完成[函数、参数、返回值和作用域](03-functions-parameters-returns-scope.md)，本地报告器已有进度与状态函数。
- 能用 `for` 逐项处理数据，并能接住函数返回值。
- 继续修改 `practice/python-basics/learning_profile.py`，不要为每一课建立互不关联的新程序。
- 页面运行器用于观察固定数据；最终版本仍要在本地终端运行并提交。

<section id="concept-choose" data-learning-context="concept-choose" data-context-type="concept" markdown="1">

## 先问数据要拿来做什么

假设要表示一条学习记录：

```python
{
    "course": "Python 起步",
    "target_hours": 5,
    "finished_hours": 3,
    "tags": ["Python", "起步", "工具"],
}
```

<div class="be-collection-model" role="img" aria-label="外层列表保存多条记录，每条记录由字典按字段名组织，tags 字段再保存一个列表；汇总时用集合得到唯一标签，并用元组返回固定的汇总结果。">
  <article><span>多条、有顺序</span><strong>list 记录列表</strong><small>可以追加下一门课程</small></article>
  <b aria-hidden="true">包含</b>
  <article><span>一条、有字段名</span><strong>dict 学习记录</strong><small>course、hours、tags</small></article>
  <b aria-hidden="true">再包含</b>
  <article><span>标签可重复</span><strong>list 标签</strong><small>保留原始输入顺序</small></article>
  <b aria-hidden="true">汇总为</b>
  <article><span>唯一成员</span><strong>set 标签集合</strong><small>展示前再排序</small></article>
</div>

选择结构时先看用途：

| 结构 | 最适合回答的问题 | 顺序 | 能否原地修改 | 重复 |
| --- | --- | --- | --- | --- |
| `str` | 这段文本是什么 | 有 | 不能 | 字符可重复 |
| `list` | 第几项是什么，要不要追加或修改 | 有 | 能 | 允许 |
| `tuple` | 这一组固定结果分别是什么 | 有 | 不能 | 允许 |
| `dict` | 某个字段名对应什么值 | 保留插入顺序 | 能 | 键唯一 |
| `set` | 某个成员是否存在，有哪些唯一成员 | 不依赖显示顺序 | 能 | 不允许 |

不要从“哪个结构更高级”开始。先说清读取方式、是否需要修改、是否允许重复，再选最贴合用途的一种。

</section>

<section id="example-text-tags" data-learning-context="example-text-tags" data-context-type="example" markdown="1">

## 字符串先把标签清理干净

字符串是有顺序、不可原地修改的字符序列：

```python
course = "Python 起步"

print(course[0])       # P
print(course[-1])      # 步
print(course[0:6])     # Python
```

索引从 `0` 开始；`-1` 表示最后一个字符。切片 `course[start:end]` 包含起点、不包含终点。索引越界会触发 `IndexError`，而超出末尾的切片会在可用位置停止。

真实输入常带有多余空格和分隔符。运行下面这段清理代码：

```python
--8<-- "examples/python-basics/normalize_tag_text.py"
```

这里有三次形状变化：

1. `split(",")` 把一段文本拆成字符串列表。
2. `strip()` 为每个标签返回去掉两端空白的新字符串。
3. `" | ".join(clean_tags)` 把字符串列表重新连接成可读文本。

字符串方法通常返回新值，不会改动原字符串：

```python
name = "  Python  "
name.strip()
print(repr(name))       # '  Python  '

name = name.strip()
print(repr(name))       # 'Python'
```

`join()` 的每一项都必须是字符串。如果列表里混入整数，会触发 `TypeError`；先决定整数应该怎样显示，再明确转换，不要在不理解数据含义时一股脑调用 `str()`。

</section>

<section id="concept-sequences" data-learning-context="concept-sequences" data-context-type="concept" markdown="1">

## 列表会变，元组保持固定

列表适合保存数量可能变化、需要按顺序处理的一组值：

```python
courses = ["工程基础", "Python 起步"]
courses.append("Git 复习")
courses[0] = "工程基础起步"

for course in courses:
    print(course)
```

几个容易混淆的操作：

| 写法 | 发生什么 | 返回值 |
| --- | --- | --- |
| `items.append(value)` | 把一个整体放到末尾 | `None` |
| `items.extend(values)` | 把另一组值逐项加到末尾 | `None` |
| `items.pop()` | 删除并返回最后一项 | 被删除的值 |
| `sorted(items)` | 生成一个排好序的新列表 | 新列表 |
| `items.sort()` | 原地调整当前列表 | `None` |

如果写成 `result = courses.sort()`，`result` 会是 `None`，不是排序后的列表。想保留原顺序时用 `sorted(courses)`；确认可以修改原列表时才调用 `.sort()`。

元组同样有顺序，也支持索引、切片和遍历，但不能替换其中的位置：

```python
summary = (10, 8, "进行中")
total_target, total_finished, status = summary
```

这种解包适合固定结构的返回结果。左右数量必须一致，否则会触发 `ValueError`。只有一个成员的元组要保留逗号：`("Python",)`；`("Python")` 仍然只是字符串。

</section>

<section id="example-list-dict" data-learning-context="example-list-dict" data-context-type="example" markdown="1">

## 列表中的字典表示多条记录

字典用键说明字段含义：

```python
record = {
    "course": "Python 起步",
    "target_hours": 5,
    "finished_hours": 3,
    "tags": ["Python", "起步"],
}

print(record["course"])
record["finished_hours"] = 4
```

多条结构相同的记录放进列表：

```python
records = [
    {"course": "Python 起步", "target_hours": 5, "finished_hours": 3},
    {"course": "复盘练习", "target_hours": 2, "finished_hours": 2},
]

for record in records:
    print(record["course"], record["finished_hours"])
```

`record["course"]` 适合必填字段：缺失时抛出 `KeyError`，能尽早暴露数据问题。真正允许缺失的字段再用 `.get()`：

```python
note = record.get("note", "未填写")
```

不要对所有字段都使用 `.get()`。如果课程名或目标小时是必填数据，安静地返回 `None` 只会把错误推迟到更难排查的位置。

</section>

<section id="concept-tuple-set" data-learning-context="concept-tuple-set" data-context-type="concept" markdown="1">

## 集合只关心唯一成员

多条记录可能重复出现同一标签：

```python
tags = {"Python", "工具"}
tags.add("复盘")
tags.add("Python")

print("Python" in tags)
```

第二次加入 `"Python"` 不会产生重复项。集合适合成员判断、去重和集合运算：

```python
current = {"Python", "工具", "复盘"}
required = {"Python", "Git"}

print(current & required)  # 两边都有
print(current | required)  # 合并所有唯一成员
print(required - current)  # 还缺什么
```

不要依赖集合打印出来的顺序。需要稳定输出或测试时，先 `sorted(tags)`。空集合必须写成 `set()`；`{}` 创建的是空字典。

本课的 `summarize_records()` 最后返回一个元组：总计划、总完成、课程行和唯一标签。集合负责收集唯一标签，元组负责把固定的四项结果交回调用者，两者用途并不冲突。

</section>

<section id="reproduce-v04" data-learning-context="reproduce-v04" data-context-type="reproduce" markdown="1">

## 跑起报告器 v0.4

先看 `records` 的形状，再沿 `for record in records` 追踪第一条记录：

```python
--8<-- "examples/python-basics/learning_records_v04.py"
```

<div class="be-python-runner" data-python-runner data-python-source="../../../../examples/python-basics/learning_records_v04.py">
  <p class="be-python-runner__fallback">页面运行器正在准备。若它没有出现，请把上面的代码复制到本地文件运行。</p>
</div>

把代码保存到原来的练习文件：

=== "Windows PowerShell"

    ```powershell
    .\.venv\Scripts\python.exe .\practice\python-basics\learning_profile.py
    ```

=== "macOS / Linux"

    ```bash
    ./.venv/bin/python ./practice/python-basics/learning_profile.py
    ```

请逐项核对：总计划是每条 `target_hours` 的和；总完成是每条 `finished_hours` 的和；课程行保持记录顺序；唯一标签去重后按稳定顺序显示。

</section>

<section id="modify-records" data-learning-context="modify-records" data-context-type="modify" markdown="1">

## 加入一条自己的记录

请做四处真实修改：

1. 把三条示例记录换成你最近学习的内容。
2. 为其中一条加入重复标签，确认课程原始标签列表仍保留输入，而汇总标签只显示一次。
3. 为部分记录增加可选字段 `note`，打印时使用 `record.get("note", "未填写")`。
4. 用 `sorted(records, key=course_name)` 按课程名生成新顺序，但不要破坏原列表。

排序函数先写成有名字的形式：

```python
def course_name(record):
    return record["course"]


sorted_records = sorted(records, key=course_name)
```

至少验证空列表、重复标签、超额完成和缺失 `note` 四种情况。空列表的汇总应该是 `0`、`0`、空课程行和空标签，而不是突然访问第一项。

</section>

<section id="troubleshoot-containers" data-learning-context="troubleshoot-containers" data-context-type="troubleshoot" markdown="1">

## 先看错误是在按位置还是按字段读取

| 现象 | 常见原因 | 怎样回来 |
| --- | --- | --- |
| `IndexError` | 列表或字符串位置超出范围 | 打印 `len()`，确认最后有效位置是 `len(...) - 1` |
| `KeyError: 'course'` | 必填字段缺失或拼写不同 | 检查实际字典和数据来源，修正字段，不要直接吞掉 |
| `TypeError` 提示不能修改字符串或元组 | 正在替换不可变对象中的位置 | 构造新字符串/元组，或确认是否本该使用列表 |
| `join()` 提示期待字符串 | 列表中混有整数或其他对象 | 先决定显示格式，再明确转换每一项 |
| `.sort()` 的结果是 `None` | 把原地修改方法当成新列表 | 直接检查原列表，或改用 `sorted()` |
| 集合输出每次看起来不同 | 依赖了集合显示顺序 | 展示与测试前使用 `sorted()` |
| 改了副本，原数据也变 | 变量仍共享同一列表或内层字典 | 先画出引用关系，再决定复制外层还是复制嵌套对象 |

错误类型已经在提示你访问方式：`IndexError` 通常对应位置，`KeyError` 通常对应字典键。先读 traceback 指向的表达式，再看容器当前真实内容。

</section>

<section id="project-v04" data-learning-context="project-v04" data-context-type="project" markdown="1">

## 报告器 v0.4

| 上一版 | 这节课增加 | 涉及文件 | 需要保存 | 下一版 |
| --- | --- | --- | --- | --- |
| v0.3：函数处理一条记录 | 列表中的字典、多记录汇总、唯一标签和固定汇总元组 | `learning_profile.py`、`notes/learning-log.md` | 多记录报告、四类边界输入、一次容器错误与恢复 | 从 JSON 文件读取记录 |

在学习记录中画出自己的数据形状：最外层是什么，每条记录是什么，标签又是什么。然后保存实际输出与四类验证结果：

```bash
git add practice/python-basics/learning_profile.py notes/learning-log.md
git diff --cached
git commit -m "summarize multiple study records"
git status --short
```

下一课会把同样的字典和列表写进 JSON。数据形状先在内存里理清，文件读写就不会同时混进两个新问题。

</section>

<section id="deepen-copy" data-learning-context="deepen-copy" data-context-type="deepen" markdown="1">

## 再深入一点：赋值、浅复制和内层共享

运行下面的短例子：

```python
--8<-- "examples/python-basics/list_aliasing.py"
```

`same_list = records` 没有创建列表，只让两个名字指向同一个对象。`records.copy()` 创建了新的外层列表，所以向副本追加记录不会改变原列表长度。

但这是**浅复制**：外层位置里原有的字典仍是同一批对象。修改 `outer_copy[0]["course"]`，原列表中的第一条记录也会看到变化。

这里先别急着把每次复制都换成 `copy.deepcopy()`。先判断你是否真的需要修改内层对象；很多时候，建立新的记录字典或让函数不修改输入，比无条件深复制更清楚。

</section>

<section id="career-data-shape" data-learning-context="career-data-shape" data-context-type="career" markdown="1">

## 被问到“为什么这样组织数据”时

可以沿着访问方式回答：多条记录需要保留顺序并逐项处理，所以外层用列表；每条记录要按课程、目标和完成小时读取，所以用字典；原始标签允许重复且要保留输入顺序，所以仍用列表；汇总只关心唯一标签，因此临时转成集合；固定的汇总结果用元组返回并解包。

这比“我会五种数据结构”更有说服力。真正的能力不是背方法表，而是能用程序行为解释结构选择，并说清共享、顺序和缺失字段的处理办法。

</section>

## 完成检查

- [ ] 我能根据用途区分字符串、列表、元组、字典和集合。
- [ ] 我用索引和切片读取过字符串或列表，并能说明结束位置不包含。
- [ ] 我用 `strip()`、`split()` 和 `join()` 清理过真实标签文本。
- [ ] 我能解释 `append()`/`extend()`、`sorted()`/`.sort()` 的差别。
- [ ] 我用列表中的字典保存并遍历了至少三条记录。
- [ ] 我只对可选字段使用 `.get()`，必填字段缺失仍会暴露问题。
- [ ] 我用集合去重，并在展示前排序。
- [ ] 我验证了空列表、重复标签、超额完成和缺失可选字段。
- [ ] 我能用输出解释直接赋值、外层复制和内层共享。
- [ ] 我提交了报告器 v0.4 和学习记录。

## 来源与版本

- 适用版本：Python 3.11 及以上；示例只使用内置类型与函数。
- 核查日期：2026-07-17。
- 事实来源：[Python 数据结构教程](https://docs.python.org/3.11/tutorial/datastructures.html)说明列表操作、元组与解包、集合、字典及循环方式；[内置类型](https://docs.python.org/3.11/library/stdtypes.html)说明字符串、序列、映射和集合的正式行为。
- 代码验证：仓库脚本检查多记录固定报告、标签清理、唯一标签顺序、列表共享与浅复制边界；自动测试不联网，也不安装第三方包。

## 下一步

现在的数据只活在程序运行期间。下一课进入[文件、路径、JSON 和简单目录操作](05-files-json-paths.md)，把同样的列表与字典从 JSON 文件读进来，并把报告写回文件。

[进入下一课](05-files-json-paths.md){ .md-button .md-button--primary }
