<div class="be-tutor-mount" data-tutor-lesson="cs-core-14" aria-hidden="true"></div>

<section id="overview-merge-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-merge-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">共同算法基础 · 第 10 课 · 可追踪查找与排序实验</span>

# 自底向上归并排序与稳定复杂度

## 四个单项段，两轮以后变成完整有序序列

```text
data：3A, 1B, 3C, 2D
width=1：1B, 3A | 2D, 3C
width=2：1B, 2D, 3A, 3C
comparisons=5，writes=8，passes=2
stable=yes，input_unchanged=yes
```

第一轮把相邻单项合成长度 2 的有序段；第二轮再合成长度 4。3A、3C 最终仍保持原顺序，稳定性来自合并时“相等先取左侧”。

[看两轮怎样合并](#example-merge-passes){ .md-button .md-button--primary }
[运行完整轨迹](#reproduce-merge-micro){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>共同算法基础 · 10 / 16</strong></span><span>前置<strong>基础排序与稳定性</strong></span><span>完成后留下<strong>宽度快照、比较写入和稳定归并</strong></span></div>

</section>

## 开始前

- 能用标签判断相等键的相对顺序。
- 知道两个已经有序的段可以用左右游标合并。
- 自底向上不使用递归，但时间复杂度仍由每轮工作量和轮数决定。

<section id="concept-merge-two-runs" data-learning-context="concept-merge-two-runs" data-context-type="concept" markdown="1">

## 先把两个有序段可靠地合起来

左右段各有一个游标。两侧都未耗尽时比较当前键，写入顺序更靠前的元素并移动对应游标；一侧耗尽后，另一侧剩余项已经有序，直接依次写出。

```text
left  [1B,3A]  +  right [2D,3C]
       ↑                 ↑
result [1B,2D,3A,3C]
```

</section>

<section id="concept-merge-counts" data-learning-context="concept-merge-counts" data-context-type="concept" markdown="1">

## 比较和写入不是同一个计数

只有两侧都还有元素、需要决定取谁时才增加 `comparisons`。任何元素进入目标序列都增加一次 `writes`，包括一侧耗尽后的剩余复制。

合并 `3L` 与 `3R` 只比较 1 次，却写入 2 次。

</section>

<section id="concept-left-first" data-learning-context="concept-left-first" data-context-type="concept" markdown="1">

## 相等时先取左段

左右段来自原序列中的相邻区间，左段的同键元素原本更早。相等时若先取右侧，3R 会越过 3L；先取左侧则保持原相对顺序。

```python
if right.key < left.key:
    take_right()
else:
    take_left()   # 相等也走这里
```

</section>

<section id="concept-bottom-up" data-learning-context="concept-bottom-up" data-context-type="concept" markdown="1">

## 从宽度 1 开始逐轮翻倍

单个元素天然有序，所以初始段宽为 1。每轮合并相邻的两个 `width` 段，完成后把 width 翻倍；当 `width >= n` 时，整份数据已经属于同一个有序段。

```text
width 1 → 段长最多 2
width 2 → 段长最多 4
width 4 → 段长最多 8
```

</section>

<section id="example-merge-passes" data-learning-context="example-merge-passes" data-context-type="example" markdown="1">

## 固定输入只需要两轮

<div class="be-merge-passes" role="img" aria-label="宽度1先得到两个长度2的有序段，宽度2再得到完整有序序列">
  <div><strong>width 1</strong><code>1B,3A | 2D,3C</code><span>累计 2 比较 · 4 写入</span></div>
  <div><strong>width 2</strong><code>1B,2D,3A,3C</code><span>累计 5 比较 · 8 写入</span></div>
</div>

每轮所有元素都写入新缓冲，因此四项、两轮得到 8 次写入。比较数取决于各次合并何时有一侧耗尽。

</section>

<section id="concept-odd-tail" data-learning-context="concept-odd-tail" data-context-type="concept" markdown="1">

## 尾部不满一对也不能丢

五项数据在某轮可能只剩一个左段，没有右段。段末尾必须用 `min(..., n)` 截断；空右段与普通合并走同一接口，左段元素原样写入下一轮。

这比为奇数长度另写一套排序逻辑更安全。

</section>

<section id="reproduce-merge-micro" data-learning-context="reproduce-merge-micro" data-context-type="reproduce" markdown="1">

## 运行宽度快照

```bash
.venv/bin/python site-src/examples/algorithm-foundation/bottom_up_merge_trace.py
```

运行前预测每轮分组、累计 comparisons 和 writes。最后应得到 `1B,2D,3A,3C`，且 A 仍在 C 前。

</section>

<section id="reproduce-bilingual-merge" data-learning-context="reproduce-bilingual-merge" data-context-type="reproduce" markdown="1">

## 回归双语言阶段作品

```bash
cd exercises/cs-core/traceable-search-sort-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_search_sort_lab merge
```

```bash
cd exercises/cs-core/traceable-search-sort-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_search_sort_lab merge
```

同时回归 `search` 与 `elementary`，两种语言三份报告逐字一致，完成查找排序组三课闭环。

</section>

<section id="modify-stable-descending" data-learning-context="modify-stable-descending" data-context-type="modify" markdown="1">

## 迁移成稳定降序

只改变不相等键的先后判断；相等仍先取左段。不要排序升序后反转，也不要改写成递归或调用标准排序。

`[2A,1B,2C]` 的降序结果应为 `2A,2C,1B`，每轮快照也必须按降序有序。

</section>

<section id="modify-five-items" data-learning-context="modify-five-items" data-context-type="modify" markdown="1">

## 用五项数据观察孤立尾段

加入第五个带标签元素，逐轮写下左右段范围。核对每一项在每轮恰好写入一次，尾部没有完整右段时仍保留，输入快照始终不变。

</section>

<section id="troubleshoot-merge" data-learning-context="troubleshoot-merge" data-context-type="troubleshoot" markdown="1">

## 标签反转、尾项丢失或循环不结束

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 相等标签反转 | 相等时先取右侧 | 相等固定先取左段 |
| 奇数长度丢尾项 | 假设左右段都完整 | 用长度截断段端点 |
| writes 少于预期 | 剩余复制没有计数 | 每个输出项都计一次 |
| 宽度循环不结束 | 忘记翻倍 | 每轮结束执行 `width *= 2` |
| 输入被覆盖 | 直接复用调用方序列 | 复制输入，在轮间替换工作缓冲 |

</section>

<section id="project-search-sort-v03" data-learning-context="project-search-sort-v03" data-context-type="project" markdown="1">

## 查找与排序组三课闭环

```text
有序输入与边界 → 基础排序与稳定反例
                           ↓
                迭代归并、宽度快照、n log n
```

项目现在能解释查找位置、基础排序操作和稳定归并的完整演进。后续快速排序、堆排序与非比较排序进入深化，不挤进共同基础。

[查看可追踪查找与排序实验](../../exercises/cs-core/traceable-search-sort-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-merge-cost" data-learning-context="deepen-merge-cost" data-context-type="deepen" markdown="1">

## 不递归仍然是 `Θ(n log n)`

每轮处理并写入全部 `n` 个元素，工作量 `Θ(n)`；段宽每次翻倍，从 1 增长到至少 n 需要 `Θ(log n)` 轮，因此总时间 `Θ(n log n)`。

教学实现使用新的目标序列，额外空间 `Θ(n)`。递归与迭代只是控制流不同，不改变这组时间和空间推导。

</section>

<section id="career-merge-evidence" data-learning-context="career-merge-evidence" data-context-type="career" markdown="1">

## 用两轮快照讲清归并

先说明左右游标与相等左侧优先，再展示 width=1、2 的完整快照，以及 5 次比较、8 次写入。最后用“每轮线性、轮数对数”推导复杂度，并补充辅助空间和奇数尾段。

这样的回答同时说明正确性、稳定性、边界和成本，不依赖背诵一句结论。

</section>

## 完成检查

- [ ] 能用左右游标合并两个有序段，并正确处理任一侧为空。
- [ ] 相等键固定先取左段，`3L+3R` 保持 L、R。
- [ ] 固定输入记录 width=1、2，累计 5 次比较、8 次写入。
- [ ] 五项输入的孤立尾段不会丢失，每轮宽度严格翻倍。
- [ ] 稳定降序不靠反转、递归或标准排序，输入保持不变。
- [ ] Python 类型检查与单元测试、C++ 构建与 CTest、三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [MIT 6.006 Sorting](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/6d1ae5278d02bbecb5c4428928b24194_MIT6_006S20_lec3.pdf) | 归并排序与渐近成本 | 2020 课程，2026-07-17 核查 |
| [Python Sorting HOWTO](https://docs.python.org/3.11/howto/sorting.html) | 稳定排序语义对照 | Python 3.11，2026-07-17 核查 |
| [C++ 稳定算法要求](https://eel.is/c++draft/algorithm.stable) | 稳定算法契约对照 | C++20 教学基线，2026-07-17 核查 |

本课独立实现用于观察合并过程；真实工程优先使用标准库成熟排序接口。

## 下一步

进入[二叉树形状、链接所有权与槽位表示](15-binary-tree-shape-linked-ownership.md)，从线性序列进入有分支的层级结构。
