# C++：对象生命周期与 RAII

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-cpp-raii" aria-hidden="true"></div>

<section id="overview-raii-output" class="be-sample-hero" data-learning-context="overview-raii-output" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">系统工程样板 · 学习进度报告器审计导出</span>

## 函数结束时，文件也该收好

```text
进入：write_audit
离开：write_audit
写入：成功
```

这三行不是装饰。它们告诉我们对象什么时候活着、什么时候离开作用域。RAII 就从这里开始：让资源跟着对象的一生走，而不是靠人记住每一条退出路径。

<div class="be-sample-actions" markdown="1">
[跟着生命周期走一遍](#concept-object-lifetime){ .md-button .md-button--primary }
[编译小例子](#reproduce-raii-scope){ .md-button }
</div>

</section>

<section id="concept-object-lifetime" class="be-sample-learning-unit" data-learning-context="concept-object-lifetime" data-context-type="concept" markdown="1">

## 先问：谁拥有它，它能活多久

<div class="be-lifetime-strip" role="img" aria-label="对象构造、被临时借用、离开作用域并析构的时间线">
  <div data-state="alive"><strong>构造</strong><span>对象开始存活</span></div>
  <div data-state="borrow"><strong>借用</strong><span>引用或指针临时访问</span></div>
  <div data-state="alive"><strong>使用</strong><span>拥有者仍在作用域内</span></div>
  <div data-state="dead"><strong>析构</strong><span>作用域结束，不再访问</span></div>
</div>

引用和非拥有指针不会替对象续命。它们能安全使用多久，取决于真正拥有对象的地方还在不在。

</section>

<section id="example-scope-note" class="be-sample-learning-unit" data-learning-context="example-scope-note" data-context-type="example" markdown="1">

## 用一个会报到的对象观察作用域

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

构造函数在对象建立时运行，析构函数在对象离开作用域时运行。真实资源类会在这两个位置获取和释放文件、锁或内存；这个小类先把时间顺序打印出来。

</section>

<section id="reproduce-raii-scope" class="be-sample-learning-unit" data-learning-context="reproduce-raii-scope" data-context-type="reproduce" markdown="1">

## 编译并观察成功和失败

```bash
mkdir -p /tmp/be-cpp-raii
clang++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wshadow \
  reviews/course-content/batch-b/examples/cpp-raii/raii_scope.cpp \
  -o /tmp/be-cpp-raii/raii_scope
cd /tmp/be-cpp-raii
./raii_scope audit.txt
cat audit.txt
```

再给它一个不存在的父目录：

```bash
./raii_scope missing/audit.txt
```

第二次会返回失败，但局部对象仍会按作用域析构。RAII 负责资源释放，不负责把打开失败变成成功；错误仍然要检查。

<div class="be-trace-demo" data-trace-demo="lifetime" aria-label="文件流从构造到析构的单步演示"></div>

</section>

<section id="modify-raii-audit" class="be-sample-learning-unit" data-learning-context="modify-raii-audit" data-context-type="modify" markdown="1">

## 给审计文件加一行

在 `output << "学习审计快照\n";` 后增加当前课程和计划小时。重新编译，先验证成功文件，再验证缺失目录仍返回失败。

我更建议同时保留两条检查：函数返回值说明写入是否完成，文件内容说明写进去的东西是否正确。

</section>

<section id="troubleshoot-dangling" class="be-sample-learning-unit" data-learning-context="troubleshoot-dangling" data-context-type="troubleshoot" markdown="1">

## 不要运行悬空引用来“看看会不会崩”

```cpp
const ScopeNote& bad_note() {
    ScopeNote local{"临时对象"};
    return local;
}
```

函数结束后 `local` 已经析构，返回的引用指向不再存活的对象。后续读取属于未定义行为：这台电脑上恰好没崩，也不能证明正确。

安全做法通常是按值返回，或者由调用者先拥有对象，再把引用短暂传进函数。这个反例只用于阅读编译器诊断和生命周期图，不会加入运行测试。

</section>

<section id="project-raii-audit" class="be-sample-project-panel" data-learning-context="project-raii-audit" data-context-type="project" markdown="1">

## 报告器多了一份可选审计文件

C++ 起步样板只会打印状态卡。正式阶段作品已经能处理多条记录；这个样板给它补上文件资源这一层：

```text
学习记录 → 主报告保持不变
         └→ ofstream 审计快照 → 离开作用域自动关闭
```

项目里真正值得讲的不是“用了 RAII”这四个字，而是为什么主输出不能被调试信息污染、打开失败怎样返回、测试怎样证明旧功能没有改变。

[查看正式 C++ 阶段作品](../../../exercises/programming-languages/study-progress-reporters/README.md){ .md-button }

</section>

??? info "再深入一点：RAII 不只用于文件"
    `std::vector` 管理动态内存，`std::lock_guard` 管理互斥锁，智能指针管理动态对象。共同点是资源释放由对象析构触发，而不是把清理代码散落在每个 `return` 前。

## 完成检查

- [ ] 能用作用域说明对象何时构造、何时析构。
- [ ] 能区分拥有对象和临时借用。
- [ ] 能验证文件写入成功与打开失败。
- [ ] 能解释 RAII 为什么不等于忽略错误。
- [ ] 不通过运行未定义行为判断悬空引用是否安全。

下一页：[GPIO、中断与设备事件](gpio-interrupts.md)。
