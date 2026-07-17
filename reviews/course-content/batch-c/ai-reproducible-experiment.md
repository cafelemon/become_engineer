# AI：第一次训练与验证

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-ai-reproducible-experiment" aria-hidden="true"></div>

<section id="overview-ai-result" class="be-sample-hero" data-learning-context="overview-ai-result" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">AI 模型起步 · 结构化数据实验 v0.1</span>

## 同一份实验，应该能再跑一次

```text
数据：教学合成学习记录（不代表真实学习者）
记录数：240
多数类基线：...
逻辑回归：...
混淆矩阵：[[...], [...]]
验证集错例：...
```

机器学习不是“调用 `fit()` 就结束”。这页更关心数据从哪里来、拿什么比较、哪些记录被模型判断错，以及明天重跑时能不能得到同样的结果。

<p class="be-synthetic-note"><strong>先说清楚：</strong>这 240 条记录由程序生成，只用来练习实验流程。它不能说明真实学习者怎样学习，也不能用于评价任何人。</p>

<div class="be-sample-actions" markdown="1">
[看看一次实验怎么走](#concept-ai-pipeline){ .md-button .md-button--primary }
[在本地重跑](#reproduce-ai-experiment){ .md-button }
</div>

</section>

<section id="concept-ai-pipeline" class="be-sample-learning-unit" data-learning-context="concept-ai-pipeline" data-context-type="concept" markdown="1">

## 训练和验证要分开

<div class="be-model-flow" role="img" aria-label="数据经过划分、训练、验证和错例检查">
  <div><strong>240 条记录</strong><span>特征和标签</span></div>
  <div><strong>固定划分</strong><span>180 训练，60 验证</span></div>
  <div><strong>两种模型</strong><span>多数类基线与逻辑回归</span></div>
  <div><strong>验证与错例</strong><span>指标之外还要看判断错在哪里</span></div>
</div>

- **特征**是模型能看到的输入：计划小时、完成小时、练习次数、受阻分钟。
- **标签**是我们要预测的结果：这一阶段是否完成计划。
- **训练集**用来调整模型参数。
- **验证集**只用来检查训练后的表现，不能提前泄露给模型。

如果训练和验证混用，分数可能很好看，却不能告诉你模型面对新记录时会怎样。

</section>

<section id="example-ai-baseline" class="be-sample-learning-unit" data-learning-context="example-ai-baseline" data-context-type="example" markdown="1">

## 先找一个最简单的对手

`DummyClassifier(strategy="most_frequent")` 永远猜训练集里更多的那一类。它不聪明，但很重要：如果复杂模型连它都赢不了，就该先查数据和问题定义。

```python
baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(x_train, y_train)

model = make_pipeline(
    StandardScaler(),
    LogisticRegression(random_state=42),
)
model.fit(x_train, y_train)
```

逻辑回归前先缩放数值，是因为“受阻分钟”和“练习次数”的数值范围差很多。流水线保证训练和预测使用同一套处理。

</section>

<section id="reproduce-ai-experiment" class="be-sample-learning-unit" data-learning-context="reproduce-ai-experiment" data-context-type="reproduce" markdown="1">

## 跑一遍，再原样跑第二遍

```bash
.venv/bin/pip install -r reviews/course-content/batch-c/requirements.txt
.venv/bin/python reviews/course-content/batch-c/examples/ai-experiment/experiment.py
```

脚本会生成 `synthetic_study_sessions.csv`。再运行一次，输出应该相同，因为数据生成、划分和模型都使用固定随机种子 `42`。

<div class="be-metric-board" aria-label="实验读数说明">
  <div><b>240</b><span>教学合成记录</span></div>
  <div><b>180 / 60</b><span>训练与验证记录</span></div>
  <div><b>42</b><span>固定随机种子</span></div>
</div>

随机种子不是“让模型永远正确”，只是让这次随机过程可以重放。

</section>

<section id="modify-ai-data" class="be-sample-learning-unit" data-learning-context="modify-ai-data" data-context-type="modify" markdown="1">

## 改一个条件，先写下你的猜测

在 `generate_rows()` 中把练习次数的影响从 `0.38` 改成 `0.10`，然后重新运行。先猜两件事：

1. 验证分数会不会变化？
2. 错例数量会往哪个方向走？

修改的是数据生成规则，所以它改变了这个“教学世界”的规律。不要把变化解释成“现实中练习不重要”；你只是在检查实验是否会对数据变化作出反应。

</section>

<section id="troubleshoot-ai-leakage" class="be-sample-learning-unit" data-learning-context="troubleshoot-ai-leakage" data-context-type="troubleshoot" markdown="1">

## 分数突然接近满分，先怀疑泄漏

故意把 `goal_met` 放进特征列表，模型几乎等于提前看到了答案。这不是模型变强，而是题目被泄露。

再看混淆矩阵：

<div class="be-confusion-grid" role="img" aria-label="二分类混淆矩阵的四个位置">
  <span></span><span>预测未完成</span><span>预测完成</span>
  <span>实际未完成</span><span class="is-value">判断正确</span><span class="is-value">误报</span>
  <span>实际完成</span><span class="is-value">漏报</span><span class="is-value">判断正确</span>
</div>

同样的准确率，误报和漏报可能完全不同。真实项目里哪一种错误更贵，要由业务目标决定，不能只看一个总分。

</section>

<section id="project-ai-system" class="be-sample-project-panel" data-learning-context="project-ai-system" data-context-type="project" markdown="1">

## 结构化数据机器学习系统从这里起步

这次先把“能重跑”做好。未来替换为许可清楚的公开数据时，数据说明、划分、基线和错例检查仍然保留。

| 现在 | 后面会加 | 一直要守住 |
| --- | --- | --- |
| 合成 CSV | 真实公开数据与质量检查 | 数据来源清楚 |
| 两个模型 | 特征工程与模型比较 | 同一验证协议 |
| 终端指标 | 实验报告和推理入口 | 配置与结果可追溯 |

</section>

## 完成检查

- [ ] 能解释特征、标签、训练集和验证集。
- [ ] 能连续运行两次，并得到相同结果。
- [ ] 能说出为什么先做多数类基线。
- [ ] 能从混淆矩阵区分误报和漏报。
- [ ] 不会把合成数据结果说成真实学习规律。

下一页：[LLM：把一句话变成可靠数据](llm-structured-output.md)。

参考：[scikit-learn 模型评估](https://scikit-learn.org/stable/modules/model_evaluation.html) · [常见陷阱](https://scikit-learn.org/stable/common_pitfalls.html)
