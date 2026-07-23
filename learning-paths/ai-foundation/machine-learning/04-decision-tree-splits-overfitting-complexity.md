<div class="be-tutor-mount" data-tutor-lesson="machine-learning-04" aria-hidden="true"></div>
<section id="overview-tree-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-tree-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">机器学习 · 第 4 / 8 课 · 结构化数据机器学习系统 v0.4</span>
# 决策树、切分、过拟合与复杂度约束
## 用训练/验证差距和树结构观察模型容量
```text
model=decision-tree,criterion=gini,seed=20260723
unconstrained=depth:7,nodes:29,leaves:15,train_accuracy:1.000,validation_accuracy:0.567
constrained=max_depth:3,min_samples_leaf:5,depth:3,nodes:9,leaves:5
constrained_metrics=train_accuracy:0.867,validation_accuracy:0.600,recall:0.500
root_split=numeric__redundant_signal<=0.773
rule_lines=13
capacity_reduced=true
training_gap_unconstrained=0.433
training_gap_constrained=0.267
invariants=train-only-fit,fixed-seed,validation-for-comparison
```
不受约束的树把训练集拟合到 1.000，却只得到 0.567 的验证准确率。限制深度和叶子最小样本数后，训练分数下降，但结构更小、训练/验证差距也缩小。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>机器学习 · 4 / 8</strong></div>
  <div><span>前置</span><strong>逻辑回归与正则化</strong></div>
  <div><span>依赖</span><strong>NumPy 2.5.1 · pandas 2.3.3 · scikit-learn 1.9.0</strong></div>
  <div><span>完成后留下</span><strong>树结构、容量约束与过拟合证据</strong></div>
</div>

## 学习目标

- 理解树怎样按特征阈值递归划分样本。
- 用 Gini 不纯度解释候选切分的方向。
- 区分训练拟合能力与未见数据表现。
- 用 `max_depth` 和 `min_samples_leaf` 控制容量。
- 导出可读规则，同时避免把一棵小树误当业务规则真相。

<section id="concept-tree-split-impurity" data-learning-context="concept-tree-split-impurity" data-context-type="concept" markdown="1">
## 每个节点选择一个切分，让子节点标签更纯

分类树检查候选“特征 ≤ 阈值”条件，比较切分前后加权不纯度。Gini 为 0 表示节点内只有一个类别；数值更大表示类别混合。算法贪心选择当前下降最大的候选，并在子节点继续重复。

本课根节点先检查 `numeric__redundant_signal <= 0.773`。这是当前训练样本、预处理与随机种子下的结果；换数据、参数或特征后根切分可以变化。
</section>

<section id="concept-overfit-capacity" data-learning-context="concept-overfit-capacity" data-context-type="concept" markdown="1">
## 训练满分可能只是树记住了样本细节

不受约束的树深度 7、29 个节点、15 个叶子，在 90 行训练集上准确率 1.000，但验证准确率只有 0.567，训练/验证差距 0.433。训练分数高只能说明拟合能力，不自动说明泛化。

受约束树深度 3、9 个节点、5 个叶子，训练准确率降到 0.867，验证准确率为 0.600，差距缩到 0.267。单次小验证集仍不足以确定最佳模型，本课只确认容量确实减少。
</section>

<section id="example-tree-complexity" data-learning-context="example-tree-complexity" data-context-type="example" markdown="1">
## 深度限制路径长度，叶子最小样本数阻止碎片化

| 方案 | 深度 | 节点 / 叶子 | 训练准确率 | 验证准确率 | 正类召回 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 不受约束 | 7 | 29 / 15 | 1.000 | 0.567 | 见运行结果 |
| `depth=3, leaf=5` | 3 | 9 / 5 | 0.867 | 0.600 | 0.500 |

`max_depth` 限制一条路径可连续提问几次；`min_samples_leaf` 要求每个最终区域至少保留一定样本。二者改变可表达的规则数量，但不能保证验证指标一定提高。
</section>

<section id="reproduce-tree-v04" data-learning-context="reproduce-tree-v04" data-context-type="reproduce" markdown="1">
## 运行 v0.4 并导出树规则

```bash
cd site-src/examples/machine-learning/structured-data-ml-system-v04
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_decision_tree_lab.py
.venv/bin/python decision_tree_lab.py
```

8 项测试覆盖训练/验证边界、无约束拟合、容量减少、命名根特征、规则导出、固定结构、非法参数拒绝和固定报告。
</section>

<section id="modify-tree" data-learning-context="modify-tree" data-context-type="modify" markdown="1">
## 主动修改容量和信号

1. 枚举 `max_depth=1..7`，记录节点数、训练分数和验证分数。
2. 固定深度 3，比较 `min_samples_leaf=1 / 5 / 10 / 20`。
3. 删除 `redundant_signal`，检查根节点和规则是否变化。
4. 打乱训练标签，观察无约束树是否仍能提高训练分数以及验证表现。
</section>

<section id="troubleshoot-tree" data-learning-context="troubleshoot-tree" data-context-type="troubleshoot" markdown="1">
## 树模型异常先查容量、数据量、随机性和编码

| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 训练满分、验证很差 | 树过深且叶子过小 | 限制深度、叶子并交叉验证 |
| 每次规则略有变化 | 等价切分或随机状态未固定 | 固定种子并比较指标分布 |
| 类别列产生很多分支 | 高基数独热编码 | 重新审查特征语义和编码 |
| 根阈值看似不可解释 | 预处理后的列或缺失填补 | 同时输出字段名和预处理契约 |
| 小参数变化导致大波动 | 样本少、树不稳定 | 使用重复验证或集成方法 |
| 验证集被反复挑参数 | 把验证当训练反馈 | 下一课用交叉验证并冻结测试集 |
</section>

<section id="project-structured-data-ml-v04" data-learning-context="project-structured-data-ml-v04" data-context-type="project" markdown="1">
## 结构化数据机器学习系统 v0.4

- 复用相同数据、切分和缺失/类别预处理，确保模型比较边界一致。
- 新增不受约束树与 `max_depth=3, min_samples_leaf=5` 的受约束树。
- 输出深度、节点、叶子、训练/验证指标、根切分和规则行数。
- 固定随机状态并逐字比较规则，保证教学快照可回归。
- 下一版将候选模型与参数放进交叉验证，只在最后使用冻结测试集。
</section>

## 四类学习者入口

- 零基础兴趣：手画深度为 2 的树，沿两条路径解释最终类别。
- 有基础兴趣：画出深度与训练/验证差距的折线。
- 零基础求职：解释为什么训练准确率 100% 可能是坏信号。
- 有基础求职：设计树结构漂移、特征高基数、容量选择泄漏和规则稳定性的验收。

<section id="career-tree-contract" data-learning-context="career-tree-contract" data-context-type="career" markdown="1">
## 求职加练：训练集满分，是否应选择这棵树

原创追问：候选 A 训练 1.000、验证 0.567，候选 B 训练 0.867、验证 0.600。请解释容量、方差和小验证集不确定性；提出交叉验证、冻结测试集、错误成本和稳定性证据，而不是仅凭 B 的单次分数宣布胜出。
</section>

## 完成检查

- 8 项测试通过，不受约束树能拟合训练集但验证差距为 0.433。
- 受约束树深度 3、9 个节点、5 个叶子，容量确实下降。
- 根切分使用可追踪的变换后字段名和阈值。
- 同一固定种子导出的树规则逐字一致。
- 能说明树规则是模型产物，不是因果或永久业务规则。

## 来源与版本

- 核查日期 2026-07-23；运行依赖见同目录 `requirements.txt`。
- [scikit-learn DecisionTreeClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html)
- [scikit-learn decision trees guide](https://scikit-learn.org/stable/modules/tree.html)
- [scikit-learn export_text](https://scikit-learn.org/stable/modules/generated/sklearn.tree.export_text.html)

## 下一步

进入第 5 课《交叉验证、超参数选择与最终测试集》，把单次验证比较升级为明确的选择与最终评估协议。
