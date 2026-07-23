<div class="be-tutor-mount" data-tutor-lesson="career-algorithm-03" aria-hidden="true"></div>

<section id="overview-algorithm-retrospective" class="be-page-hero be-lesson-hero" data-learning-context="overview-algorithm-retrospective" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">算法求职加练 · 第 3 / 3 课 · 演练运行器 v0.3</span>

# 错因分类、最小反例与回归复盘

## 一次失败要留下下一次能自动检查的资产

v0.3 把判题状态和限时事件关联为五类复盘记录：

```text
failure=count-mismatch category=contract before=runtime-error after=regression-pass regression=test_contract_count_mismatch
failure=empty-sequence category=boundary before=wrong-answer after=regression-pass regression=test_boundary_empty_sequence
failure=visited-too-late category=implementation before=wrong-answer after=regression-pass regression=test_implementation_bfs_shared_neighbor
failure=repeated-linear-scan category=complexity before=timeout after=regression-pass regression=test_complexity_membership_operation_bound
failure=late-switch category=strategy before=switched after=regression-pass regression=test_strategy_checkpoint_switch_rule
coverage categories=boundary,complexity,contract,implementation,strategy
gate=pass records=5
claim=counterexample-candidate-not-proof-of-global-minimality
```

重点不是给失败贴标签，而是形成“观察状态 → 反例候选 → 更小探针 → 原因 → 修复 → 回归通过”的可检查链。

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>算法求职加练 · 3 / 3</strong></div>
  <div><span>前置</span><strong>固定判题契约 + 限时策略日志</strong></div>
  <div><span>环境</span><strong>Python 3.11+ 标准库</strong></div>
  <div><span>完成后留下</span><strong>五类错因、反例探针、12 项测试与复盘报告</strong></div>
</div>

## 开始前

- 你能稳定区分答案错误、运行错误、执行超时和主动换题。
- 你保留了一次失败输入或策略事件，而不是只保留修复后的版本。
- 本课不会自动证明反例在数学意义上全局最小。

## 学习目标

- 用互相可区分的五类错因缩小排查范围。
- 把失败输入继续缩小，并记录更小探针的结果。
- 让每个修复关联唯一回归测试。
- 用操作计数替代不稳定耗时断言复杂度改进。
- 把一次模拟整理成可复现、不过度声称的技术复盘。

<section id="concept-five-failure-categories" data-learning-context="concept-five-failure-categories" data-context-type="concept" markdown="1">

## 状态告诉你发生了什么，错因解释为什么

| 类别 | 典型证据 | 本课例子 | 不应直接推断 |
| --- | --- | --- | --- |
| contract | 输入解析、输出格式、参数边界 | 声明 2 个值却只给 1 个 | 所有非零退出都是契约错 |
| boundary | 空、单元素、极值、重复 | 空序列输出失败 | 主体算法一定正确 |
| implementation | 状态更新、访问时机、不变量 | BFS 入队时机错误 | 算法选择一定错误 |
| complexity | 操作数随规模增长过快 | 每次查询都线性扫描 | 一次超时就证明复杂度 |
| strategy | 检查点和止损规则 | 没有进展仍拖到最后 | 换题本身就是失败 |

分类是当前最好假设，不是永久真相。修复后若回归仍失败，应更新类别和原因，而不是为了维护旧标签继续补丁。

```mermaid
flowchart LR
    O["观察状态"] --> C["提出错因类别"]
    C --> E["缩小反例候选"]
    E --> P["尝试更小探针"]
    P --> H["写出原因假设"]
    H --> F["一次修复"]
    F --> R["唯一回归测试"]
    R -->|仍失败| C
    R -->|通过| G["保留证据与剩余风险"]
```

</section>

<section id="example-counterexample-probe" data-learning-context="example-counterexample-probe" data-context-type="example" markdown="1">

## “最小反例”先写成可反驳的候选

空序列例子：

```json
{
  "counterexample": "0\n\n",
  "smaller_probe": "no smaller valid count exists",
  "cause": "output code assumed at least one unique value",
  "fix": "emit a zero count and an empty second line",
  "regression_id": "test_boundary_empty_sequence"
}
```

对于合法数量，0 的确没有更小非负整数；但工具仍只输出：

```text
claim=counterexample-candidate-not-proof-of-global-minimality
```

因为“最小”依赖你声明的输入域和比较方式。图反例的节点数、边数和标签可以有不同偏序，自动检查器无法只凭一段字符串证明全局最小。

可接受的做法是：明确输入域，记录缩小步骤，给出尝试过的更小探针，并把结论表述为当前搜索范围内的候选。

</section>

<section id="reproduce-retrospective-v03" data-learning-context="reproduce-retrospective-v03" data-context-type="reproduce" markdown="1">

## 运行修复回归与复盘检查器

从仓库根目录执行：

```bash
cd site-src/examples/career-algorithm/algorithm-rehearsal-v03
../../../../.venv/bin/python -m unittest -v test_regression_cases.py test_retrospective.py
../../../../.venv/bin/python retrospective.py
```

12 项测试分两层：

- 5 项真实回归：数量契约、空序列、BFS 共享邻居、集合查询操作上限、检查点换题规则。
- 7 项复盘结构：五类覆盖、未知类别、未知状态、重复回归 ID、缺失更小探针、未解决记录和缺失时间线链接。

复盘通过要求每条 `after` 都是 `regression-pass`。这只证明登记的回归已通过，不代表实现不存在其他缺陷。

</section>

<section id="concept-regression-evidence" data-learning-context="concept-regression-evidence" data-context-type="concept" markdown="1">

## 修复必须改变可观察证据

五项示例修复分别留下：

1. 数量不匹配稳定抛出 `ValueError`，而不是越界崩溃。
2. 空输入得到空列表和明确的零数量输出。
3. BFS 节点在进入队列时标记，共享邻居只处理一次。
4. 查询先构建集合，100 次查询固定只有 100 次成员检查。
5. 到检查点既没有不变量也没有边界用例通过时，策略函数返回换题。

第四项没有断言“必须在 1 毫秒内完成”。耗时受机器、负载和解释器影响；操作计数直接对应本课实现的工作量边界。它仍不是完整复杂度证明，但比一次墙钟快慢更稳定、可解释。

</section>

<section id="modify-own-retrospective" data-learning-context="modify-own-retrospective" data-context-type="modify" markdown="1">

## 把一次真实失败缩成回归资产

复制 `failures.json` 为 `failures.local.json`，只保留你亲自复现过的一条记录：

1. 保存失败状态和原始输入。
2. 每次删除或简化一个输入元素，直到更小变化不再复现。
3. 把最后仍失败的输入写入 `counterexample`。
4. 把第一个不再失败的更小输入或无法继续缩小的原因写入 `smaller_probe`。
5. 先写原因假设，再做一次最小修复。
6. 新增唯一命名的测试，确认修复前失败、修复后通过。
7. 关联 v0.2 中最接近的事件。

```bash
../../../../.venv/bin/python retrospective.py --failures failures.local.json
```

如果修复同时重构多个函数、改输入格式并更换算法，你将无法判断哪项变化解决问题。回到更小差异后再运行回归。

</section>

<section id="troubleshoot-retrospective" data-learning-context="troubleshoot-retrospective" data-context-type="troubleshoot" markdown="1">

## 复盘最常见的失败是证据断链

| 现象 | 断点 | 恢复 |
| --- | --- | --- |
| 原因写“粗心” | 没有技术机制 | 指出具体状态、边界或更新时机 |
| 反例很大 | 无法定位必要条件 | 每次删一个元素并重跑 |
| 修复后没有测试 | 下次可能复发 | 先让测试在旧实现上失败 |
| 测试名重复 | 一条测试冒充多个修复 | 每个记录使用唯一 regression ID |
| `after=still-failing` | 闭环尚未完成 | 更新假设，不强行标记通过 |
| 超时改成更快机器 | 没有算法证据 | 增加操作计数或规模关系 |
| 策略问题改算法 | 层次混淆 | 回看时间线，确认卡点出现在哪一步 |
| 声称“已找到最小反例” | 未定义输入偏序与搜索范围 | 改称反例候选并记录更小探针 |

复盘不是为失败找体面的故事，而是让下一次同类问题更早被发现。

</section>

<section id="project-algorithm-rehearsal-v03" data-learning-context="project-algorithm-rehearsal-v03" data-context-type="project" markdown="1">

## 算法演练运行器 v0.3

- v0.1：固定输入输出，真实区分通过、答案错误、运行错误和超时。
- v0.2：固定总预算、检查点、任务优先级与策略事件。
- v0.3：关联错因、反例候选、更小探针、修复、回归与事件。
- 本版测试：5 项修复回归 + 7 项复盘结构，共 12 项。
- 三课合计：26 项 Python 测试、30 张小码卡、60 条固定问法和 6 条未知问题。

这套运行器是本机学习工具，不是在线判题平台，也不采集真实账号、面试录屏或企业题目。它交付的是可解释训练闭环，不预测录用概率。

</section>

## 四类学习者入口

- 零基础兴趣：选修一条空输入反例，完整经历失败、修复和回归。
- 有基础兴趣：审查分类是否互斥，尝试找出一条可能跨类别的记录并说明主次。
- 零基础求职：每次模拟至少留下一个真实失败和一个修复后回归测试。
- 有基础求职：为复杂度问题增加规模—操作数表，并在复盘中明确没有验证的上限。

<section id="career-retrospective-review" data-learning-context="career-retrospective-review" data-context-type="career" markdown="1">

## 求职加练：如何解释一次没有做出的题

原创追问：你在限时模拟中因 BFS 实现错误得到答案错误，修复后回归通过。请用两分钟说明观察到的状态、怎样缩小反例、真正的状态更新错误、为什么修复有效，以及当前仍不能证明什么。

合格回答必须把事实、假设、修改和剩余风险分开。公开招聘信号只用于选择“边界、解释、可复现证据”这些能力维度，不代表企业真实题目或评价结论。

</section>

## 完成检查

- 5 项修复回归和 7 项复盘结构测试全部通过。
- 五类错因都有一条可解释记录，但不把分类当成永久真相。
- 每条记录包含反例候选、更小探针、原因、修复、唯一回归和事件链接。
- 至少一条个人失败在旧实现上复现，并在修复后由测试阻止回归。
- 复杂度证据使用操作计数或规模关系，不依赖一次墙钟结果。
- 不声称工具自动证明全局最小反例。
- 能用两分钟解释一次未完成题目的技术证据和剩余风险。

## 来源与版本

- 适用 Python 3.11+，只使用标准库；核查日期 2026-07-23。
- [Python `collections.deque`](https://docs.python.org/3.11/library/collections.html#collections.deque)：BFS 队列回归。
- [Python `unittest`](https://docs.python.org/3.11/library/unittest.html)：修复前后行为与结构门槛。
- [Python `json`](https://docs.python.org/3.11/library/json.html)：可版本化复盘记录。
- 招聘参考只提供算法能力与证据方向；全部示例、反例、测试和追问均为原创。

## 下一步

算法求职加练三课到此闭环。继续算法方向可进入算法深化；该模块仍需正式建设，不创建空课。也可以回到[完整课程地图](../curriculum-map.md)，按方向实验选择系统、AI、LLM/Agent 或设备主线。
