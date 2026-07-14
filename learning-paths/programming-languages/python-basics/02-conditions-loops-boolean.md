# 条件、循环、布尔逻辑

上一节的脚本基本是从上到下一行一行执行。本节开始学习两个关键能力：让程序根据条件选择不同分支，让程序重复执行某段逻辑。

条件和循环是后续所有项目的基础。数据清洗、文件扫描、接口处理、模型评估都会大量使用它们。

## 前置知识

开始前应完成：

- [变量、基本类型、输入输出](01-variables-types-io.md)
- 能创建并运行 `.py` 文件。
- 能使用变量保存数字和字符串。
- 能使用 `input()` 接收输入，并用 `int()` 做基本转换。
- 能记录代码、输入、输出和错误信息。

## 学习目标

完成本节后，你应该能做到：

- 使用 `if`、`elif`、`else` 写分支判断。
- 使用比较运算得到布尔结果。
- 使用 `and`、`or`、`not` 组合条件。
- 使用 `for` 重复处理一组数据或一段范围。
- 使用 `while` 在条件成立时持续执行。
- 使用 `break` 退出循环。
- 识别缩进、冒号、死循环和范围边界错误。

## 学习顺序

按下面顺序学习：

1. 先理解布尔值和比较。
2. 再写 `if` 分支。
3. 接着组合多个条件。
4. 然后学习 `for` 循环。
5. 再学习 `while` 循环和退出。
6. 最后完成一个带判断和循环的小脚本。

## 布尔值和比较

比较会得到布尔值，也就是 `True` 或 `False`。

```python
age = 18

print(age >= 18)
print(age < 18)
print(age == 18)
print(age != 18)
```

常见比较：

| 写法 | 含义 |
| --- | --- |
| `a == b` | a 是否等于 b |
| `a != b` | a 是否不等于 b |
| `a > b` | a 是否大于 b |
| `a >= b` | a 是否大于等于 b |
| `a < b` | a 是否小于 b |
| `a <= b` | a 是否小于等于 b |

注意：判断相等用 `==`，不是 `=`。`=` 是给变量赋值。

## 条件分支

`if` 用来判断一个条件是否成立。

```python
age_text = input("年龄：")
age = int(age_text)

if age >= 18:
    print("已经成年")
else:
    print("还未成年")
```

Python 用缩进表示代码属于哪个分支。通常使用 4 个空格。

多个分支可以使用 `elif`：

```python
score_text = input("分数：")
score = int(score_text)

if score >= 90:
    print("优秀")
elif score >= 60:
    print("通过")
else:
    print("需要继续练习")
```

程序会从上往下判断，命中一个分支后就不会继续进入后面的分支。

## 布尔逻辑

有时一个判断需要多个条件。

```python
score = 85
attendance = 90

if score >= 60 and attendance >= 80:
    print("课程通过")
else:
    print("课程未通过")
```

常见逻辑：

| 写法 | 含义 |
| --- | --- |
| `a and b` | a 和 b 都成立 |
| `a or b` | a 或 b 至少一个成立 |
| `not a` | a 不成立 |

示例：

```python
has_python = True
has_cpp = False

print(has_python and has_cpp)
print(has_python or has_cpp)
print(not has_cpp)
```

学习阶段不要把条件写得太长。如果一行条件读起来很费劲，可以先拆成几个变量。

## for 循环

`for` 常用于遍历一组数据。

```python
courses = ["工程基础入门", "Python 起步", "CS 最小核心"]

for course in courses:
    print(course)
```

也可以和 `range()` 配合，重复固定次数。

```python
for number in range(1, 6):
    print(number)
```

输出：

```text
1
2
3
4
5
```

`range(1, 6)` 包含 1，不包含 6。这个边界很容易出错，练习时要把输出记录下来。

## while 循环

`while` 会在条件成立时持续执行。

```python
count = 1

while count <= 5:
    print(count)
    count = count + 1
```

如果忘记更新 `count`，条件会一直成立，程序就可能停不下来。

## 退出循环

`break` 可以提前退出循环。

```python
answer = "python"

while True:
    guess = input("输入答案：")
    if guess == answer:
        print("答对了")
        break
    else:
        print("再试一次")
```

`while True` 表示一直循环，所以必须有明确的退出条件。当前只在简单练习中使用它，真实项目里要更谨慎。

## 最小脚本

把下面代码保存为 `study_check.py`：

```python
target_hours_text = input("本周计划学习小时数：")
finished_hours_text = input("本周已经学习小时数：")

target_hours = float(target_hours_text)
finished_hours = float(finished_hours_text)

if finished_hours >= target_hours:
    print("本周学习目标已完成")
else:
    remaining_hours = target_hours - finished_hours
    print("还需要学习", remaining_hours, "小时")

print("学习检查清单：")
tasks = ["记录目标", "运行代码", "记录输出", "复盘问题"]

for task in tasks:
    print("-", task)
```

这个脚本包含：

- 输入和类型转换。
- 条件判断。
- 浮点数计算。
- 列表。
- `for` 循环。

列表后面会单独学习。这里先把它看成一组按顺序保存的文本。

## 实践练习

### 练习 1：成年判断

创建 `age_check.py`，输入年龄，输出是否成年。

需要产出：

```text
输入 1：
输出 1：
输入 2：
输出 2：
我如何判断两个分支都验证过：
```

要求至少测试一个成年输入和一个未成年输入。

### 练习 2：成绩等级

创建 `score_level.py`，输入分数：

- 90 及以上输出 `优秀`。
- 60 及以上输出 `通过`。
- 60 以下输出 `需要继续练习`。

需要产出：

```text
我测试的分数：
每个分数的输出：
是否覆盖了三个分支：
```

### 练习 3：输出 1 到 10

使用 `for` 和 `range()` 输出 1 到 10。

需要产出：

```text
range 写法：
输出第一行：
输出最后一行：
我如何判断边界正确：
```

### 练习 4：计算 1 到 100 的和

使用循环计算 1 到 100 的和。

提示：

```python
total = 0
```

需要产出：

```text
最终结果：
我使用的是 for 还是 while：
循环变量如何变化：
```

### 练习 5：最多猜三次

创建 `guess_word.py`，固定答案为 `python`。用户最多猜三次：

- 猜对就输出 `答对了` 并退出。
- 三次都没猜对就输出 `次数用完`。

需要产出：

```text
猜对时的输入和输出：
猜错三次时的输入和输出：
程序在哪里退出循环：
```

### 练习 6：记录一次缩进错误

故意去掉 `if` 下面一行的缩进，运行并记录错误。

需要产出：

```text
错误代码片段：
完整错误信息：
错误类型：
我如何修复：
```

## 常见错误与排查

| 错误 | 表现 | 怎么排查 |
| --- | --- | --- |
| 用 `=` 判断相等 | 语法错误或逻辑不对 | 判断相等必须写 `==` |
| 少写冒号 | `SyntaxError` | `if`、`elif`、`else`、`for`、`while` 后面通常需要 `:` |
| 缩进不一致 | `IndentationError` | 同一层级使用一致的 4 个空格 |
| `elif` 写在 `else` 后面 | 语法错误 | 顺序应是 `if`、若干 `elif`、最后 `else` |
| `range()` 边界不符合预期 | 少输出最后一个数 | 记住结束值不包含在范围内 |
| `while` 忘记更新条件 | 程序一直运行 | 检查循环里是否改变了条件相关变量 |
| 输入没有转换就比较数字 | 结果错误或报错 | 使用 `int()` 或 `float()` 转换后再比较 |
| 条件太长看不懂 | 修改时容易出错 | 拆成有意义的布尔变量 |

## 完成标准

完成本节需要同时满足：

- 能写出一个 `if/elif/else` 判断。
- 能说明 `==` 和 `=` 的区别。
- 能使用至少 3 种比较运算。
- 能使用 `and`、`or`、`not` 中至少 2 种逻辑运算。
- 能使用 `for` 遍历一组数据或一个 `range()`。
- 能使用 `while` 写一个有退出条件的循环。
- 能解释 `break` 的作用。
- 能记录一次覆盖多个分支的测试结果。
- 能识别并修复一次缩进错误。

## 下一步

下一步进入[函数、参数、返回值和作用域](03-functions-parameters-returns-scope.md)。函数会帮助你把重复代码整理成职责清楚、可调用和可验证的小块，也会为后续文件处理和项目里程碑打基础。
