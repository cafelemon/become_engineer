# C++：源码怎样变成程序

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-cpp-build" aria-hidden="true"></div>

<section id="overview-cpp-output" class="be-sample-hero" data-learning-context="overview-cpp-output" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">系统工程起步 · 学习进度报告器 C++ v0.1</span>

## 先跑出这张状态卡

```text
学习状态卡
课程：C++ 起步
本周计划：5 小时
```

它和 Python 小程序看起来很像，启动方式却不同。C++ 源文件要先交给编译器，变成当前电脑能执行的程序，然后才能运行。

<div class="be-sample-actions" markdown="1">
[先看构建过程](#concept-build-pipeline){ .md-button .md-button--primary }
[直接检查编译器](#reproduce-toolchain){ .md-button }
</div>

</section>

<section id="concept-build-pipeline" class="be-sample-learning-unit" data-learning-context="concept-build-pipeline" data-context-type="concept" markdown="1">

## 源文件不会自己运行

<div class="be-build-pipeline" role="img" aria-label="C++ 源文件经过编译和链接后变成可执行程序">
  <div><strong>study_status.cpp</strong><span>你写的源文件</span></div>
  <div><strong>编译</strong><span>检查语法和类型</span></div>
  <div><strong>链接</strong><span>接上标准库等代码</span></div>
  <div><strong>study_status</strong><span>操作系统能运行的程序</span></div>
</div>

起步时先记住两类失败就够了：

- **编译错误**：某个源文件的语法或类型有问题，通常能看到文件名和行号。
- **链接错误**：代码里提到了某个函数，但链接器没有找到它的实现。

我建议第一次先把编译和链接合在一条命令里。等程序能跑，再把两段拆开观察。

</section>

<section id="example-cpp-program" class="be-sample-learning-unit" data-learning-context="example-cpp-program" data-context-type="example" markdown="1">

## 先读懂这个小程序

```cpp
#include <iostream>
#include <string>

int main() {
    const std::string course{"C++ 起步"};
    const int planned_hours{5};

    std::cout << "学习状态卡\n";
    std::cout << "课程：" << course << '\n';
    std::cout << "本周计划：" << planned_hours << " 小时\n";
    return 0;
}
```

现在不用把每个符号背下来：

- `#include` 让程序使用标准库提供的字符串和输出工具。
- `main()` 是程序开始执行的位置。
- 花括号初始化会让一些危险的数值缩窄更早暴露出来。
- `const` 表示这两个值设好以后不再改变。
- `return 0` 告诉操作系统程序正常结束。

</section>

<section id="reproduce-toolchain" class="be-sample-learning-unit" data-learning-context="reproduce-toolchain" data-context-type="reproduce" markdown="1">

## 先确认电脑里有编译器

=== "macOS"

    打开“终端”，运行：

    ```bash
    xcode-select --install
    clang++ --version
    ```

    如果第一条命令提示工具已经安装，继续运行版本命令即可。

=== "Windows"

    安装 Visual Studio Build Tools，勾选“使用 C++ 的桌面开发”。安装完成后，从开始菜单打开 **Developer PowerShell for VS 2022**：

    ```powershell
    cl
    ```

    普通 PowerShell 找不到 `cl` 时，先确认自己打开的是开发者终端。

=== "Linux"

    Ubuntu／Debian 可以安装 GCC：

    ```bash
    sudo apt update
    sudo apt install build-essential
    g++ --version
    ```

在仓库根目录编译样例：

```bash
mkdir -p /tmp/be-cpp-build
clang++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wshadow \
  reviews/course-content/batch-b/examples/cpp-build/study_status.cpp \
  -o /tmp/be-cpp-build/study_status
/tmp/be-cpp-build/study_status
```

Linux 把 `clang++` 换成 `g++`。Windows 开发者终端使用：

```powershell
cl /std:c++20 /W4 /EHsc /permissive- study_status.cpp /Fe:study_status.exe
.\study_status.exe
```

</section>

<section id="modify-cpp-card" class="be-sample-learning-unit" data-learning-context="modify-cpp-card" data-context-type="modify" markdown="1">

## 把状态卡改成自己的

改三个地方：课程名、计划小时，再增加一个 `finished` 布尔值并把它打印出来。修改后必须重新编译；旧的可执行文件不会自动跟着源码变化。

```cpp
const bool finished{false};
std::cout << "是否完成：" << std::boolalpha << finished << '\n';
```

运行前先猜输出。看到新字段以后，可以再把 `false` 改成 `true`，确认源码、编译和运行确实连在一起。

</section>

<section id="troubleshoot-cpp-build" class="be-sample-learning-unit" data-learning-context="troubleshoot-cpp-build" data-context-type="troubleshoot" markdown="1">

## 编译失败时，从第一条错误开始看

故意把一行改成：

```cpp
const int planned_hours{2.5};
```

花括号初始化会提醒你 `2.5` 不能悄悄变成整数 `2`。修复时先决定业务上需要整数还是小数，而不是关闭警告。

| 屏幕上看到什么 | 更可能发生在哪一段 | 先检查什么 |
| --- | --- | --- |
| `command not found` | 编译器还没准备好 | 终端是否正确、安装是否完成 |
| 文件名、行号和类型信息 | 编译 | 从第一条错误开始读 |
| `undefined reference`／`unresolved external` | 链接 | 函数是否只有声明，没有实现 |
| 输出还是旧内容 | 运行 | 是否重新编译、是否运行了正确文件 |

</section>

<section id="project-cpp-v01" class="be-sample-project-panel" data-learning-context="project-cpp-v01" data-context-type="project" markdown="1">

## 这张状态卡以后会长成什么

现在只有一个源文件。后面的 C++ 课程会把记录拆成函数和多个文件，再加入容器、测试和审计导出。到了 RAII 样板，它会在不改变主报告的前提下安全地写出文件。

| 现在 | 下一次会加什么 | 仍然要保持什么 |
| --- | --- | --- |
| 单文件状态卡 | 多条学习记录和函数 | 编译命令可重复 |
| 直接打印 | 审计文件导出 | 主报告输出稳定 |
| 手工运行 | CMake 与测试 | 警告和失败都能读懂 |

</section>

??? info "再深入一点：编译和链接可以分开"
    `clang++ -c study_status.cpp -o study_status.o` 只生成目标文件；再运行 `clang++ study_status.o -o study_status` 完成链接。这样更容易看出多文件工程中哪一段出了问题。

## 完成检查

- [ ] 能找到正确终端并看到编译器版本。
- [ ] 能用一条命令编译并运行状态卡。
- [ ] 能解释源文件、编译、链接和可执行程序的顺序。
- [ ] 能修改字段、重新编译，并看到新输出。
- [ ] 能区分编译器没找到、编译错误和链接错误。

下一页：[C：变量、内存与第一次编译](c-memory.md)。
