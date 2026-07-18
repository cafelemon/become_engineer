<div class="be-tutor-mount" data-tutor-lesson="cpp-core-05" aria-hidden="true"></div>

<section id="overview-raii-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-raii-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">C++ 核心 · 第三课 · 双语言学习进度报告器</span>

# C++ 对象、引用、指针、生命周期与 RAII

## 函数结束时，文件也该收好

```text
进入：write_audit
离开：write_audit
写入：成功
```

这三行把对象的一生打印了出来：进入作用域时构造，离开时析构。文件流也遵守这条时间线。我们仍然检查打开和写入是否成功，但不用在每条返回路径前手工补一遍清理代码。

[跟着生命周期走一遍](#concept-object-lifetime){ .md-button .md-button--primary }
[直接编译小例子](#reproduce-raii-scope){ .md-button }

<div class="be-lesson-facts" markdown="1">
<span>课程位置<strong>C++ 核心 · 3 / 3</strong></span>
<span>前置<strong>STL、引用、CMake 与 CTest</strong></span>
<span>完成后留下<strong>对象借用、可空查找、审计文件和失败测试</strong></span>
</div>

</section>

## 开始前

- 上一课的多记录报告器能够从全新目录构建，并且 CTest 通过。
- 已经知道按值参数会复制输入，`const&` 可以表达只读借用。
- 本课只讨论栈上对象、容器元素和文件流，不提前展开手写内存分配、智能指针实现或继承体系。

<section id="concept-object-lifetime" data-learning-context="concept-object-lifetime" data-context-type="concept" markdown="1">

## 先问：谁拥有它，它能活多久

<div class="be-lifetime-strip" role="img" aria-label="对象构造、被临时借用、继续使用、离开作用域并析构的时间线">
  <div data-state="alive"><strong>构造</strong><span>对象开始存活</span></div>
  <div data-state="borrow"><strong>借用</strong><span>引用或指针临时访问</span></div>
  <div data-state="alive"><strong>使用</strong><span>拥有者仍在作用域内</span></div>
  <div data-state="dead"><strong>析构</strong><span>作用域结束，不再访问</span></div>
</div>

对象的生命周期是它可以被安全使用的时间范围。引用和非拥有指针不会替对象续命；它们只是暂时指向别人拥有的对象。

在报告器里，`std::vector<StudyRecord>` 拥有记录。函数参数可以复制记录、只读借用记录或修改同一条记录，但必须先把这三种意图分清楚。

</section>

<section id="example-scope-note" data-learning-context="example-scope-note" data-context-type="example" markdown="1">

## 用一个会报到的对象看作用域

```cpp
class ScopeNote {
public:
    explicit ScopeNote(std::string name) : name_{std::move(name)} {
        std::cout << "进入：" << name_ << '\n';
    }

    ~ScopeNote() {
        std::cout << "离开：" << name_ << '\n';
    }

private:
    std::string name_;
};
```

构造函数在对象建立时运行，析构函数在对象离开作用域时运行。`ScopeNote` 只打印时间顺序；真实资源类会在这两个位置取得和释放文件、锁或内存。

</section>

<section id="concept-value-reference-pointer" data-learning-context="concept-value-reference-pointer" data-context-type="concept" markdown="1">

## 值、引用和指针表达三种不同关系

| 写法 | 这节课里的意思 | 调用者要注意什么 |
| --- | --- | --- |
| `StudyRecord record` | 函数得到一份副本 | 修改副本不会改变原对象 |
| `const StudyRecord& record` | 必定存在的只读借用 | 拥有者必须仍然存活 |
| `StudyRecord& record` | 必定存在的可修改借用 | 修改会反映到原对象 |
| `StudyRecord* record` | 可能为空的非拥有借用 | 先判空，不 `delete` |

按值并不低级。上一课的 `sort_by_progress(std::vector<StudyRecord> records)` 故意复制整组记录，因为函数要排序自己的工作副本，同时保留调用者的原始顺序。

</section>

<section id="example-reference-mutation" data-learning-context="example-reference-mutation" data-context-type="example" markdown="1">

## 确定存在、需要修改时，用引用

```cpp
void add_completed_hours(
    StudyRecord& record,
    double additional_hours
) {
    record.completed_hours += additional_hours;
}
```

测试不能只看函数内部打印了什么，要回到调用者拥有的容器检查：

```cpp
std::vector<StudyRecord> records{sample_records()};
add_completed_hours(records.front(), 1.5);
expect_close(records.front().completed_hours, 9.0);
```

如果参数少了 `&`，函数仍能编译，也可能在内部显示 `9.0`，但容器里的原对象还是 `7.5`。这类错误靠调用者侧断言最容易抓住。

</section>

<section id="example-nullable-pointer" data-learning-context="example-nullable-pointer" data-context-type="example" markdown="1">

## 可能找不到时，用可空的非拥有指针

```cpp
StudyRecord* find_record_by_name(
    std::vector<StudyRecord>& records,
    const std::string& course_name
) {
    const auto iterator{std::find_if(
        records.begin(), records.end(),
        [&course_name](const StudyRecord& record) {
            return record.course_name == course_name;
        }
    )};

    return iterator == records.end() ? nullptr : &*iterator;
}
```

找到时，返回的是容器元素的地址；所有权仍属于 `records`，所以调用者不能 `delete`。找不到时返回 `nullptr`：

```cpp
if (StudyRecord* record{find_record_by_name(records, "Python 起步")}) {
    add_completed_hours(*record, 0.5);
}
```

这里先用裸指针讲清“可能没有”和“非拥有”。若接口更适合返回迭代器、索引或 `std::optional<std::reference_wrapper<T>>`，可以在后续工程中重新权衡。

</section>

<section id="concept-container-invalidation" data-learning-context="concept-container-invalidation" data-context-type="concept" markdown="1">

## 容器还活着，不代表旧地址一直有效

`find_record_by_name()` 返回的地址指向 `vector` 元素。只要发生可能重新分配的增长，元素就可能被搬到新存储，过去取得的引用、指针和迭代器都可能失效。

```cpp
StudyRecord* found{find_record_by_name(records, "Python 起步")};
records.push_back(new_record);  // 可能重新分配
// 不要继续使用 found；需要时重新查找。
```

我更建议让借用保持短暂：查到以后立即使用，不跨越容器结构变化，也不把地址长期保存在另一个对象里。

</section>

<section id="reproduce-raii-scope" data-learning-context="reproduce-raii-scope" data-context-type="reproduce" markdown="1">

## 编译并观察成功和失败

```bash
mkdir -p /tmp/be-cpp-raii
c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wshadow \
  site-src/examples/cpp-core/raii_scope.cpp \
  -o /tmp/be-cpp-raii/raii_scope

cd /tmp/be-cpp-raii
./raii_scope audit.txt
cat audit.txt
```

再给它一个不存在的父目录：

```bash
./raii_scope missing/audit.txt
echo $?
```

第二次会打印“写入：失败”并返回 `1`，但 `ScopeNote` 仍会离开作用域。RAII 负责清理已经取得的资源，不负责把打开失败变成成功。

</section>

<section id="troubleshoot-dangling" data-learning-context="troubleshoot-dangling" data-context-type="troubleshoot" markdown="1">

## 不要运行悬空引用来“看看会不会崩”

```cpp
const StudyRecord& bad_record() {
    StudyRecord local{"临时", 1.0, 1.0, {}};
    return local;
}
```

函数结束后 `local` 已经销毁，返回的引用指向不再存活的对象。后续读取属于未定义行为：这台电脑上恰好没崩，也不能证明正确。

把反例保存在临时文件，用严格警告编译并阅读诊断即可。安全替代通常是按值返回，或者由调用者先拥有对象，再把引用短暂传进函数。

</section>

<section id="concept-raii-file" data-learning-context="concept-raii-file" data-context-type="concept" markdown="1">

## `ofstream` 把文件关闭交给析构

```cpp
bool write_audit_snapshot(
    const std::vector<StudyRecord>& records,
    const std::filesystem::path& output_path
) {
    std::ofstream output{output_path};
    if (!output) {
        return false;
    }

    output << "学习审计快照\n";
    for (const StudyRecord& record : records) {
        output << record.course_name << '\t'
               << record.target_hours << '\t'
               << record.completed_hours << '\n';
    }
    return static_cast<bool>(output);
}
```

函数没有显式调用 `close()`。正常返回、提前返回或未来的异常路径离开时，局部 `output` 都会析构。错误检查仍然保留：构造后检查能否打开，写完再检查流状态。

</section>

<section id="reproduce-formal-project" data-learning-context="reproduce-formal-project" data-context-type="reproduce" markdown="1">

## 回到正式报告器验证完整契约

```bash
cd exercises/programming-languages/study-progress-reporters/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/study_report_app
```

CTest 会检查五件事：引用修改了原记录、查找同时覆盖命中和未命中、审计文件包含标题与记录、缺失目录返回失败、主报告文字仍和 Python 版本一致。

Windows 使用 Visual Studio 多配置生成器时，应用通常位于 `build/Debug/study_report_app.exe`，并在构建和测试命令中保留 `--config Debug`。

</section>

<section id="modify-audit-field" data-learning-context="modify-audit-field" data-context-type="modify" markdown="1">

## 给审计文件增加状态列

在审计快照每条记录末尾增加 `build_status(record)`，然后补两类检查：

1. 审计文件里同时出现“已完成”和“进行中”。
2. `build_report(records)` 的完整标准输出与修改前逐字相同。

审计输出和主报告是两个接口。给一个接口加字段，不应顺手改变另一个接口；这也是把调试文字留在文件、而不是打印到 stdout 的原因。

</section>

<section id="troubleshoot-file-output" data-learning-context="troubleshoot-file-output" data-context-type="troubleshoot" markdown="1">

## 文件没出现时，从路径和流状态查起

| 现象 | 先看哪里 | 怎样恢复 |
| --- | --- | --- |
| 返回 `false`，没有文件 | 父目录、权限、打开状态 | 建立正确目录，保留失败返回 |
| 文件存在但内容不全 | 写入后的流状态 | 检查磁盘或编码错误，不只检查打开成功 |
| 测试偶尔读到旧内容 | 流还没离开作用域 | 在读取前结束输出流作用域 |
| 主报告测试变化 | 审计文字混进 stdout | 审计只写文件，保持主报告契约 |
| 查到记录后结果异常 | 指针为空或位置已失效 | 先判空；修改容器后重新查找 |

</section>

<section id="project-cpp-v05" data-learning-context="project-cpp-v05" data-context-type="project" markdown="1">

## 双语言报告器完成 C++ 核心层

```text
学习记录容器拥有 StudyRecord
├── 值副本：排序，不改原输入
├── 引用：确定存在时原地更新
├── 非拥有指针：查找可能失败
└── ofstream：可选审计快照，离开作用域自动关闭
```

从第一课的一张状态卡到现在，C++ 版本已经经历编译链、函数接口、多文件 CMake、STL 多记录处理和 RAII 资源管理。Python 与 C++ 的主报告仍逐字一致，但内部用各自语言更自然的方式实现。

[查看双语言阶段作品](../../../exercises/programming-languages/study-progress-reporters/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-ownership-tools" data-learning-context="deepen-ownership-tools" data-context-type="deepen" markdown="1">

## RAII 不只用在文件

`std::vector` 管理动态存储，`std::lock_guard` 管理互斥锁，智能指针管理动态对象。共同点不是“自动”二字，而是把释放责任绑定到一个拥有资源的对象。

这节课没有使用 `new`、`delete` 或智能指针，因为当前记录本来就由值和容器拥有。不要为了展示工具而制造额外所有权问题；真正出现共享、转移或多态所有权时再选择相应类型。

</section>

<section id="career-raii-evidence" data-learning-context="career-raii-evidence" data-context-type="career" markdown="1">

## 讲 RAII 时，把失败路径也讲出来

求职表达可以沿着这条线说：

- 报告器需要可选审计文件，但主报告输出不能变化。
- 用局部 `ofstream` 绑定文件生命周期，同时检查打开和写入状态。
- 用失败路径证明缺失目录返回 `false`，旧功能仍通过 CTest。
- 查找函数返回非拥有指针，调用方判空，容器变化后不复用旧位置。

这样的叙述说明你理解所有权、接口和验证，而不只是记住“RAII 会自动释放”。

</section>

## 完成检查

- [ ] 能用作用域说明对象何时构造、何时析构。
- [ ] 能解释值副本、只读引用、可修改引用和可空非拥有指针的区别。
- [ ] 能验证按引用修改，以及查找命中和未命中两条路径。
- [ ] 不运行悬空引用来判断它是否安全，也不对容器元素地址调用 `delete`。
- [ ] 审计文件成功写出，错误路径返回失败，主报告输出保持不变。
- [ ] 能从全新构建目录通过严格编译和 CTest。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [C++ 工作草案：对象生命周期](https://eel.is/c++draft/basic.life) | 对象创建、销毁与生命周期 | C++20 教学基线，2026-07-17 核查 |
| [C++ 工作草案：引用](https://eel.is/c++draft/dcl.ref) | 引用绑定与生命周期关系 | 2026-07-17 核查 |
| [C++ 工作草案：文件流](https://eel.is/c++draft/fstreams) | `std::ofstream` 与文件资源 | 2026-07-17 核查 |
| [C++ Core Guidelines：资源管理](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#S-resource) | RAII、所有权和资源责任 | 2026-07-17 核查 |

## 下一步

C++ 起步与核心已经连成一条完整入口。接下来进入[共同算法与数据结构基础](../../cs-core/README.md)，继续使用人工轨迹、操作计数和边界测试；也可以对照 Python 的[数据类与上下文管理](../python-core/04-data-model-dataclasses-context-managers.md)，比较两种语言怎样表达对象和资源范围。
