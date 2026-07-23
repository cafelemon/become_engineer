<div class="be-tutor-mount" data-tutor-lesson="deep-learning-05" aria-hidden="true"></div>
<section id="overview-validation-regularization" class="be-page-hero be-lesson-hero" data-learning-context="overview-validation-regularization" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">深度学习 · 第 5 / 8 课 · 可诊断神经网络训练系统 v0.5</span>
# 验证曲线、过拟合、权重衰减与 Dropout
## 无正则模型曾经更好，却在固定训练预算结束时退化
```text
torch_version=2.13.0
data=train:64,noisy_labels:16,validation:256,validation_labels:clean
budget=epochs:240,learning_rate:0.05,optimizer:SGD-momentum
candidate=unregularized,weight_decay:0.0,dropout:0.0,best_epoch:50,train_accuracy:0.828,final_validation_loss:0.571875,final_validation_accuracy:0.797,best_validation_loss:0.400381
candidate=regularized,weight_decay:0.02,dropout:0.25,best_epoch:204,train_accuracy:0.750,final_validation_loss:0.488543,final_validation_accuracy:0.871,best_validation_loss:0.487638
selected=regularized,rule=lowest-final-validation-loss
dropout=train_stochastic:true,eval_stable:true
validation_gradients=disabled
test_set=not-used
invalid_regularization=rejected
invariants=same-data-initialization-budget,validation-only-selection,best-state-retained,test-untouched
```
固定 240 epoch 比较会选择正则模型；若协议改成“每个候选取历史最佳验证损失”，无正则模型反而占优。结论不是“正则一定更好”，而是模型选择规则必须在看结果前写清。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>深度学习 · 5 / 8</strong></div>
  <div><span>前置</span><strong>训练循环、history 与验证隔离</strong></div>
  <div><span>环境</span><strong>Python 3.12 · PyTorch 2.13.0 · CPU</strong></div>
  <div><span>完成后留下</span><strong>正则化对照、选择协议与 8 项测试</strong></div>
</div>

## 学习目标

- 用训练/验证曲线识别拟合改善与泛化退化。
- 在同数据、初始化和预算下比较候选模型。
- 解释 weight decay 与 Dropout 的作用和限制。
- 正确切换 `model.train()`、`model.eval()` 与 `torch.no_grad()`。
- 区分固定预算选择、早停与最终测试。
- 保存被选候选的历史最佳 state，同时不触碰测试集。

<section id="concept-overfitting-curves" data-learning-context="concept-overfitting-curves" data-context-type="concept" markdown="1">
## 过拟合要看训练与验证轨迹的分叉

训练集只有 64 行，其中 16 个标签被确定性翻转；验证集 256 行保持生成规则的干净标签。无正则模型在第 50 轮达到验证损失 0.400381，继续拟合噪声后最终退到 0.571875。

训练准确率高并不自动意味着泛化好。这里无正则最终训练准确率 0.828，高于正则模型 0.750；正则模型却有更好的最终验证准确率 0.871。过拟合是“训练目标继续改善，但未参与训练的数据表现变差”的关系，不是一个固定 epoch 数。
</section>

<section id="concept-regularization-mechanisms" data-learning-context="concept-regularization-mechanisms" data-context-type="concept" markdown="1">
## 权重衰减和 Dropout 以不同方式限制拟合

SGD 的 `weight_decay=0.02` 在更新中惩罚较大的参数；Dropout 在训练模式随机把部分隐藏激活置零，并对保留值缩放，使网络不能一直依赖同一条局部路径。

| 机制 | 训练模式 | eval 模式 | 本课作用 |
| --- | --- | --- | --- |
| weight decay | 影响 optimizer 更新 | 参数已包含结果 | 抑制过大的权重 |
| Dropout | 随机 mask | 关闭随机丢弃 | 降低共适应 |
| validation | 不反向、不更新 | 稳定前向 | 比较候选 |

两者不是万能修复：正则过强会欠拟合，Dropout 比例也不是越高越好。数据、模型容量和选择协议仍决定结果。
</section>

<section id="example-selection-protocol" data-learning-context="example-selection-protocol" data-context-type="example" markdown="1">
## 同一实验可以支持两个不同但都诚实的选择协议

本课预先采用“训练 240 epoch 后，选最终验证损失最低者”，所以正则模型 0.488543 胜过无正则 0.571875。

若改为“每个候选都允许验证早停，再比较各自历史最佳”，无正则第 50 轮的 0.400381 会胜出。早停本身也是正则化和模型选择的一部分，不能在看到曲线后临时选择对自己有利的规则。

无论哪种规则，最终测试集都不参与候选比较。测试只应在方案冻结后使用一次；本课固定输出明确 `test_set=not-used`。
</section>

<section id="reproduce-validation-v05" data-learning-context="reproduce-validation-v05" data-context-type="reproduce" markdown="1">
## 运行 v0.5 并验证模式、曲线与选择

```bash
cd site-src/examples/deep-learning/diagnosable-neural-network-v05
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_validation_lab.py
.venv/bin/python validation_lab.py
```

8 项测试覆盖标签噪声、候选公平性、无梯度验证、Dropout 模式、固定预算结果、选择与最佳 state、非法正则参数和固定报告。

验证函数先执行 `model.eval()`，再进入 `torch.no_grad()`。前者切换 Dropout/BatchNorm 行为，后者关闭梯度记录；两者职责不同，不能互相替代。
</section>

<section id="modify-validation-protocol" data-learning-context="modify-validation-protocol" data-context-type="modify" markdown="1">
## 主动改选择规则、噪声和正则强度

1. 把选择规则改成历史最佳验证损失，确认无正则候选被选中，并在报告中改名而不是偷换规则。
2. 把噪声标签从16改为0，观察正则化优势是否仍存在。
3. 分别只启用 weight decay、只启用 Dropout，再比较组合方案。
4. 在 eval 时故意遗漏 `model.eval()`，确认 Dropout 使重复输出不稳定。

每次比较固定种子、数据、初始化、epoch 和优化器；保存完整 history，不只截取有利点。
</section>

<section id="troubleshoot-validation-regularization" data-learning-context="troubleshoot-validation-regularization" data-context-type="troubleshoot" markdown="1">
## 验证结果异常先查模式、污染、规则和对照公平性

| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 同一验证输入两次不同 | eval 前仍是 train 模式 | `model.eval()` 后重跑 |
| validation 后出现 gradient | 未使用 no_grad 或错误 backward | 验证路径禁止 backward |
| 正则候选初始化不同 | 建模前随机状态漂移 | 每个候选用同 seed 初始化 |
| 某候选训练更久 | 预算不一致 | 固定 epoch、数据与 optimizer |
| 看完结果才换规则 | 选择偏差 | 预先写入 selection rule |
| validation 表现也越来越好 | 未出现过拟合或任务更简单 | 不强行宣称过拟合 |
| test 被反复查看 | 测试集变成调参集 | 冻结候选后只评一次 |
</section>

<section id="deepen-validation-reuse" data-learning-context="deepen-validation-reuse" data-context-type="deepen" markdown="1">
## 验证集也会因反复决策而被“过拟合”

即使验证样本从不参与梯度，只要持续根据其结果改架构、正则和训练预算，决策过程也会逐渐适应这份验证集。大量试验需要嵌套验证、多个种子、独立测试或更严格的实验登记。

本课只比较两个预声明候选和一个规则。它能解释机制，不能证明某组超参数在真实任务或其他随机种子上稳定优越。
</section>

<section id="project-diagnosable-network-v05" data-learning-context="project-diagnosable-network-v05" data-context-type="project" markdown="1">
## 可诊断神经网络训练系统 v0.5

- 上一版：v0.4 有可复现 SGD 训练循环和未触碰验证集。
- 本课新增：含噪训练/干净验证、两种候选、完整双曲线、weight decay、Dropout、选择规则和最佳 state。
- 文件：`validation_lab.py`、`test_validation_lab.py` 与锁定依赖。
- 保存：两候选 history、最终与历史最佳验证值、模式探针、8 项测试和一次协议切换记录。
- 下一版：观察初始化尺度、激活分布、逐层梯度范数、非有限值与梯度裁剪。

v0.5 没有使用测试集，也没有把正则模型称为普遍更好；它只在当前固定预算协议下被选择。
</section>

## 四类学习者入口

- 零基础兴趣：画两条训练/验证曲线，标出无正则模型第50轮最佳和第240轮退化。
- 有基础兴趣：把选择规则切换为早停，解释为什么结论变化仍然合理。
- 零基础求职：用 train/eval/no_grad 三者职责排查一次验证不稳定。
- 有基础求职：展示同初始化预算、选择规则、最佳 state 和 test 未使用证据，不只背“Dropout 防过拟合”。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 训练标签恰好 16 个噪声，验证标签保持干净。
- 两候选共享数据、初始化和训练预算。
- 固定预算规则选择正则候选；历史最佳规则可能选择无正则候选。
- train 模式 Dropout 随机，eval 模式重复输出一致。
- 验证不生成 gradient，测试集未使用。

## 来源与版本

- 核查日期：2026-07-23。
- 运行环境：Python 3.12、PyTorch 2.13.0、CPU。
- [PyTorch Dropout](https://docs.pytorch.org/docs/stable/generated/torch.nn.Dropout.html)
- [PyTorch SGD weight decay](https://docs.pytorch.org/docs/stable/generated/torch.optim.SGD.html)
- [PyTorch Module train/eval](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html)
- [PyTorch locally disabling gradient computation](https://docs.pytorch.org/docs/stable/notes/autograd.html#locally-disabling-gradient-computation)

## 下一步

进入第 6 课，用初始化、激活和梯度统计定位训练稳定性，并加入明确触发条件的梯度裁剪。
