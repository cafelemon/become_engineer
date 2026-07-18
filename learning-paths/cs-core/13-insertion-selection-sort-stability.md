<div class="be-tutor-mount" data-tutor-lesson="cs-core-13" aria-hidden="true"></div>

<section id="overview-elementary-output" class="be-page-hero be-lesson-hero" data-learning-context="overview-elementary-output" data-context-type="overview" markdown="1">

<span class="be-lesson-kicker">共同算法基础 · 第 9 课 · 可追踪查找与排序实验</span>

# 插入排序、选择排序与稳定性

## 两个结果都升序，为什么标签顺序不同

```text
data：3A, 1B, 3C, 2D
insertion：1B, 2D, 3A, 3C   stable=yes
selection：1B, 2D, 3C, 3A   stable=no
```

只看键，两份结果都是 `1,2,3,3`；看标签，选择排序让原本在前的 3A 跑到了 3C 后面。稳定性描述的正是相等键之间的相对顺序。

[看两种排序怎样变化](#example-sort-passes){ .md-button .md-button--primary }
[运行确定性轨迹](#reproduce-elementary-micro){ .md-button }

<div class="be-lesson-facts" markdown="1"><span>课程位置<strong>共同算法基础 · 9 / 16</strong></span><span>前置<strong>有序结果与比较次数</strong></span><span>完成后留下<strong>比较、右移、交换和稳定性证据</strong></span></div>

</section>

## 开始前

- 知道排序方向只约束键的先后，不自动说明相等元素的顺序。
- 本课给重复键加 A、C 标签，只为追踪身份；标签不参与比较。
- 所有排序返回副本，不能为了生成结果修改调用方输入。

<section id="concept-stability" data-learning-context="concept-stability" data-context-type="concept" markdown="1">

## 有序与稳定是两份契约

有序：相邻键满足目标方向。稳定：键相等的元素仍保持输入中的相对顺序。一个结果可以完全有序，同时不稳定。

```text
输入中的 key=3：A → C
稳定结果：        A → C
不稳定结果：      C → A
```

</section>

<section id="concept-tagged-evidence" data-learning-context="concept-tagged-evidence" data-context-type="concept" markdown="1">

## 不加标签，就看不见稳定性

`3` 与另一个 `3` 数值相同，排序后无法区分身份。`TaggedValue(3,"A")` 与 `TaggedValue(3,"C")` 让测试可以断言 A 是否仍在 C 前，同时比较函数只读取 `key`。

</section>

<section id="concept-insertion" data-learning-context="concept-insertion" data-context-type="concept" markdown="1">

## 插入排序把当前元素放进已排好前缀

每轮先保存 `current`，再把严格排在它后面的前项向右移动。升序时只有 `current.key < previous.key` 才移动；相等就停，因此 3C 不会越过左侧的 3A。

`comparisons` 数键比较，`shifts` 数前项右移；最后把 current 写回空位不算 shift。

</section>

<section id="concept-selection" data-learning-context="concept-selection" data-context-type="concept" markdown="1">

## 选择排序每轮找一个最小项

第 1 轮扫描 4 项里的后三项，选中 1B 与轮首 3A 交换；第 2 轮在剩余项中选中 2D。四项固定比较 `3+2+1=6` 次，只有选中位置不同于轮首时才算真实交换。

</section>

<section id="example-sort-passes" data-learning-context="example-sort-passes" data-context-type="example" markdown="1">

## 同一份输入的三轮变化

### 插入排序

<div class="be-sort-steps" role="img" aria-label="插入排序三轮保持3A在3C之前">
  <div><strong>pass 1 · 1B</strong><code>1B,3A,3C,2D</code><span>1 比较 · 1 右移</span></div>
  <div><strong>pass 2 · 3C</strong><code>1B,3A,3C,2D</code><span>相等停止，不越过 A</span></div>
  <div><strong>pass 3 · 2D</strong><code>1B,2D,3A,3C</code><span>累计 5 比较 · 3 右移</span></div>
</div>

### 选择排序

<div class="be-sort-steps" data-unstable="true" role="img" aria-label="选择排序长距离交换后3C跑到3A之前">
  <div><strong>pass 1 · 选 1B</strong><code>1B,3A,3C,2D</code><span>3 比较 · 1 交换</span></div>
  <div><strong>pass 2 · 选 2D</strong><code>1B,2D,3C,3A</code><span>C 已经越过 A</span></div>
  <div><strong>pass 3 · 选 3C</strong><code>1B,2D,3C,3A</code><span>累计 6 比较 · 2 交换</span></div>
</div>

</section>

<section id="concept-selection-instability" data-learning-context="concept-selection-instability" data-context-type="concept" markdown="1">

## 不稳定来自长距离交换

选择排序不是把 3A 与 3C 直接交换。第 2 轮把较小的 2D 从末尾换到 3A 所在位置，3A 被送到末尾，于是 3C 留在它前面。

稳定性是具体算法与实现的性质，不是“比较排序”自动拥有的标签。

</section>

<section id="reproduce-elementary-micro" data-learning-context="reproduce-elementary-micro" data-context-type="reproduce" markdown="1">

## 运行两种排序的逐轮轨迹

```bash
.venv/bin/python site-src/examples/algorithm-foundation/elementary_sort_trace.py
```

运行前先预测每轮标签顺序和累计操作数。最终 insertion 为 `1B,2D,3A,3C`，selection 为 `1B,2D,3C,3A`。

</section>

<section id="reproduce-bilingual-elementary" data-learning-context="reproduce-bilingual-elementary" data-context-type="reproduce" markdown="1">

## 回归双语言阶段作品

```bash
cd exercises/cs-core/traceable-search-sort-lab/python
PYTHONPATH=src ../../../../.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src ../../../../.venv/bin/python -m mypy --strict src tests
PYTHONPATH=src ../../../../.venv/bin/python -m traceable_search_sort_lab elementary
```

```bash
cd exercises/cs-core/traceable-search-sort-lab/cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --build-config Debug --output-on-failure
./build/traceable_search_sort_lab elementary
```

同时回归 `search` 与 `merge`，两种语言三种报告逐字一致。

</section>

<section id="modify-stable-descending" data-learning-context="modify-stable-descending" data-context-type="modify" markdown="1">

## 直接实现稳定降序

降序插入排序只改变“current 是否应排在 previous 前面”的严格方向；相等仍停止移动。不要先升序再整体反转，因为反转会把相等标签一起倒过来。

固定输入的降序标签应为 `A,C,D,B`，其中 3A 仍在 3C 前。

</section>

<section id="modify-boundary-data" data-learning-context="modify-boundary-data" data-context-type="modify" markdown="1">

## 用边界数据核对操作数

覆盖空、单元素、已排序、逆序、负数和全部相等。已排序插入排序没有右移，逆序会产生最多右移；单元素选择排序没有比较也没有交换。

每次都保存输入快照，确认结果和轨迹没有改写源序列。

</section>

<section id="troubleshoot-sort-stability" data-learning-context="troubleshoot-sort-stability" data-context-type="troubleshoot" markdown="1">

## 标签倒序或操作数不对

| 现象 | 常见原因 | 改法 |
| --- | --- | --- |
| 插入排序相等标签倒序 | 移动条件包含等号 | 相等时停止移动 |
| swaps 多一项 | 自己与自己也计数 | 只在位置不同才交换 |
| 降序标签反转 | 反转升序结果 | 直接改变严格比较方向 |
| 原输入发生变化 | 在调用方序列上原地排 | 先复制，再操作副本 |
| 看不出稳定性 | 只保存 key | 给重复键保留身份标签 |

</section>

<section id="project-search-sort-v02" data-learning-context="project-search-sort-v02" data-context-type="project" markdown="1">

## 阶段作品开始记录排序行为

```text
上一版：有序输入 → linear / lower / upper
这一版：带标签输入 → insertion / selection
                         ↘ comparisons / shifts / swaps / stable
```

查找课冻结位置与比较次数，本课加入排序结果和稳定性证据。下一课用同一输入进入自底向上归并，观察每轮宽度与 `Θ(n log n)`。

[查看可追踪查找与排序实验](../../exercises/cs-core/traceable-search-sort-lab/README.md){ .md-button .md-button--primary }

</section>

<section id="deepen-elementary-cost" data-learning-context="deepen-elementary-cost" data-context-type="deepen" markdown="1">

## 基础排序的成本不只是一句平方级

插入排序在已排序输入上只做相邻检查、没有右移，可以接近线性；逆序输入会产生平方级比较与移动。标准选择排序无论输入原本多有序，仍扫描全部未排序区，比较次数固定为 `n(n-1)/2`。

二分只能帮助插入排序找位置，连续数组的右移仍是线性，所以整体最坏不会因此变成 `Θ(n log n)`。

</section>

<section id="career-stability-evidence" data-learning-context="career-stability-evidence" data-context-type="career" markdown="1">

## 用标签和操作轨迹解释稳定性

先展示 3A、3C 的相对顺序，再指出选择排序的长距离交换怎样让 C 越过 A；插入排序则因相等时停止移动而保持顺序。

补充比较、右移、真实交换的计数口径，以及稳定降序为什么不能靠反转。这样回答同时有定义、反例和可运行证据。

</section>

## 完成检查

- [ ] 能区分有序与稳定，并用标签观察相等键身份。
- [ ] 固定插入排序得到 5 次比较、3 次右移且保持 3A、3C。
- [ ] 固定选择排序得到 6 次比较、2 次真实交换并复现不稳定。
- [ ] 稳定降序直接改变严格比较方向，不反转升序结果。
- [ ] 空、单项、已排序、逆序、负数和重复键均有测试，输入保持不变。
- [ ] Python 类型检查与单元测试、C++ 构建与 CTest、三种双语言报告全部通过。

## 来源与版本

| 来源 | 用于核查 | 版本或日期 |
| --- | --- | --- |
| [Python Sorting HOWTO](https://docs.python.org/3.11/howto/sorting.html) | 键函数、排序副本与稳定性 | Python 3.11，2026-07-17 核查 |
| [C++ 稳定算法要求](https://eel.is/c++draft/algorithm.stable) | 标准稳定算法语义对照 | C++20 教学基线，2026-07-17 核查 |
| [MIT 6.006 Sorting](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/6d1ae5278d02bbecb5c4428928b24194_MIT6_006S20_lec3.pdf) | 插入排序与比较模型 | 2020 课程，2026-07-17 核查 |

教学实现用于观察行为；实际工程应优先使用语言标准库的成熟排序接口。

## 下一步

进入[自底向上归并排序与稳定复杂度](14-bottom-up-merge-sort-stable-complexity.md)，把稳定合并扩展为 `Θ(n log n)` 的完整排序。
