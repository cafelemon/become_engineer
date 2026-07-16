# 可追踪线性结构实验

这是 CS 核心的第二条连续成果线。Python 与 C++ 使用相同固定数据和公开契约，依次验证单链表节点访问、链式栈 LIFO 和链式队列 FIFO；既有[可追踪数组实验](../traceable-array-lab/README.md)不作修改。

## 对应课程

- [单链表、节点链接与所有权](../../../learning-paths/cs-core/06-singly-linked-list-nodes-ownership.md)
- [栈、LIFO 接口与空栈边界](../../../learning-paths/cs-core/07-stack-lifo-interface-underflow.md)
- [队列、FIFO 与首尾不变量](../../../learning-paths/cs-core/08-queue-fifo-head-tail-invariants.md)

## 公开契约

- Python 3.11+、C++20、CMake 3.20+，运行依赖均为标准库。
- Python 包名为 `traceable_linear_structures_lab`；C++ 公开类型位于同名命名空间。
- 无参数等价于 `linked`，另有 `stack`、`queue`；未知模式只写标准错误并返回 2。
- Python 空结构操作抛出 `IndexError`，C++ 抛出 `std::out_of_range`；失败不改变状态。
- C++ 容器只允许移动，不允许复制；节点由 `std::unique_ptr` 单一拥有，队列尾指针不拥有节点。

## Python 验证

```bash
cd exercises/cs-core/traceable-linear-structures-lab/python
python -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m mypy --strict src tests
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m traceable_linear_structures_lab
.venv/bin/python -m traceable_linear_structures_lab stack
.venv/bin/python -m traceable_linear_structures_lab queue
```

构建 wheel 后应在项目目录外安装并重复三种模块入口：

```bash
.venv/bin/python -m build --wheel
```

## C++ 验证

```bash
cmake -S exercises/cs-core/traceable-linear-structures-lab/cpp -B /tmp/traceable-linear-build -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/traceable-linear-build
ctest --test-dir /tmp/traceable-linear-build --output-on-failure
/tmp/traceable-linear-build/traceable_linear_structures_lab
/tmp/traceable-linear-build/traceable_linear_structures_lab stack
/tmp/traceable-linear-build/traceable_linear_structures_lab queue
```

## 三种固定输出

```text
可追踪线性结构实验
链表：7 -> 3 -> 9
find=3：index=1，visits=2
pop_front=7
remaining：3 -> 9
```

```text
栈实验
push：7, 3, 9
top=9，size=3
pop=9
remaining(top->bottom)：3, 7
```

```text
队列实验
enqueue：7, 3, 9
front=7，back=9，size=3
dequeue=7
remaining(front->back)：3, 9
```

## 学习边界

本实验只实现单向拥有链、链式栈和带尾观察指针的链式队列。不进入双向链表、循环链表、环形缓冲区、优先队列、哈希、排序、递归或正式机考题。
