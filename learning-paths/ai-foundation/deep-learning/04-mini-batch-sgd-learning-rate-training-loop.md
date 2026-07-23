<div class="be-tutor-mount" data-tutor-lesson="deep-learning-04" aria-hidden="true"></div>
<section id="overview-training-loop" class="be-page-hero be-lesson-hero" data-learning-context="overview-training-loop" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">深度学习 · 第 4 / 8 课 · 可诊断神经网络训练系统 v0.4</span>
# Mini-batch、SGD、学习率与训练循环
## 180 次参数更新怎样把训练损失从 0.841436 降到 0.016031
```text
torch_version=2.13.0
split=train:72,validation:24,classes=train:0:36,1:36;validation:0:12,1:12
optimizer=SGD,learning_rate=0.1,batch_size=12,epochs=30
initial_train=loss:0.841436,accuracy:0.069
final_train=loss:0.016031,accuracy:1.000
history=epochs:30,steps:180,rows_per_epoch:72
parameter_update_norm=2.637080
batch_order=seeded-per-epoch
learning_rate_zero=no_parameter_change:true
validation_untouched=true
invalid_hyperparameter=rejected
invariants=zero-backward-step,all-train-batches-once,history-recorded,validation-untouched
```
训练集准确率达到 1.000 只证明这个小网络拟合了当前 72 行教学数据。验证集仍保持未参与训练；下一课才用它判断泛化和正则化。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>深度学习 · 4 / 8</strong></div>
  <div><span>前置</span><strong>可信梯度、清零与交叉熵</strong></div>
  <div><span>环境</span><strong>Python 3.12 · PyTorch 2.13.0 · CPU</strong></div>
  <div><span>完成后留下</span><strong>确定性训练历史与 8 项测试</strong></div>
</div>

## 学习目标

- 让每个 epoch 恰好覆盖全部训练行一次。
- 按 `zero_grad → forward → loss → backward → step` 更新参数。
- 解释学习率如何缩放梯度更新，而不是“控制模型聪明程度”。
- 记录每个 epoch 的平均 loss、准确率和覆盖行数。
- 用零学习率对照证明 loss 计算不等于参数更新。
- 保持验证集不参与 batch、梯度和优化器。

<section id="concept-mini-batch-epoch" data-learning-context="concept-mini-batch-epoch" data-context-type="concept" markdown="1">
## batch、step 和 epoch 是三种不同尺度

训练集 72 行，batch size 为 12，所以每个 epoch 有 6 个 step。30 个 epoch 共 180 次 step。

| 名称 | 本课含义 | 数量 |
| --- | --- | ---: |
| mini-batch | 一次 forward/backward 使用的训练子集 | 12 行 |
| step | 一次 optimizer 参数更新 | 每 epoch 6 次 |
| epoch | 每一训练行恰好被访问一次 | 共 30 次 |

`epoch_batches` 用 `seed + epoch` 创建局部生成器：同一配置可重复，每个 epoch 顺序又不同。测试将所有 batch 索引拼接后排序，必须恰好等于 `0..71`，避免漏行或重复采样。
</section>

<section id="concept-sgd-learning-rate" data-learning-context="concept-sgd-learning-rate" data-context-type="concept" markdown="1">
## SGD 沿负梯度方向移动，学习率决定步长

最基本的 SGD 更新为：

\[
\theta_{t+1}=\theta_t-\eta\nabla_\theta L
\]

\(\eta\) 是学习率。过小会让下降很慢，过大可能越过稳定区域甚至发散；合适值依赖数据尺度、模型、batch、优化器与训练阶段。本课固定 0.1，不把它当通用最优值。

学习率为 0 时，forward、loss 和 backward 仍能运行，但 `step()` 不改变参数。v0.4 的对照确认 parameter update norm 精确为 0。
</section>

<section id="example-zero-backward-step" data-learning-context="example-zero-backward-step" data-context-type="example" markdown="1">
## 每个 step 的顺序是训练状态机

```python
optimizer.zero_grad(set_to_none=True)
logits = model(inputs)
loss = criterion(logits, targets)
loss.backward()
optimizer.step()
```

如果漏掉 zero，梯度跨 batch 意外累加；漏掉 backward，step 没有当前梯度；漏掉 step，参数永远不变。把 `model.train()` 放在 epoch 开始处，为后续 Dropout 和 BatchNorm 明确训练模式。

epoch loss 不能直接平均各 batch 的均值，除非 batch 等长。本课按 `loss × batch_rows` 累加再除以总行数，因此最后一个短 batch 也正确。
</section>

<section id="reproduce-training-v04" data-learning-context="reproduce-training-v04" data-context-type="reproduce" markdown="1">
## 运行 v0.4 并核对 180 个 step

```bash
cd site-src/examples/deep-learning/diagnosable-neural-network-v04
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_training_lab.py
.venv/bin/python training_lab.py
```

8 项测试覆盖分层数据、每 epoch 全覆盖、顺序复现、loss 下降、history、零学习率、非法超参数和验证集不变。

固定输出记录训练前后 loss 与准确率，不记录耗时或设备性能。合成数据两类中心明显分离，因此高训练准确率是受控现象，不能外推真实任务。
</section>

<section id="modify-training-loop" data-learning-context="modify-training-loop" data-context-type="modify" markdown="1">
## 主动改学习率、batch 和 epoch

1. 比较学习率 `0`、`0.001`、`0.1`、`2.0` 的前 10 个 epoch loss，记录不更新、慢下降和潜在震荡。
2. 比较 batch size 1、12、72，保持其他配置一致，观察 step 数和 loss 曲线噪声。
3. 把训练行数改成不能整除 batch size，验证加权 epoch loss 与索引全覆盖仍正确。
4. 故意交换 `step` 与 `backward`，先预测失败或无效更新，再由测试恢复正确顺序。

比较时一次只改一个因素，并保存完整配置，不用最终准确率掩盖训练过程。
</section>

<section id="troubleshoot-training-loop" data-learning-context="troubleshoot-training-loop" data-context-type="troubleshoot" markdown="1">
## 训练不下降先查更新链、数据覆盖和尺度

| 现象 | 先查 | 常见原因 | 恢复 |
| --- | --- | --- | --- |
| loss 完全不变 | 参数 update norm | lr 为0、漏 step 或无 gradient | 检查 zero/backward/step |
| loss 快速变 NaN | loss、gradient norm、lr | 学习率过大或非有限输入 | 降 lr 并定位首个非有限值 |
| 每次结果不同 | 初始化与 batch 生成器 | 全局随机状态漂移 | 固定建模和 epoch seed |
| 训练行数不等于72 | batch indexes | 漏最后 batch 或重复采样 | 断言排序索引为完整范围 |
| accuracy 高但 loss 仍变化 | logits 置信度 | argmax 已对，概率仍在变化 | 同时记录 loss 与指标 |
| validation 被修改 | 误入 optimizer 数据流 | 划分边界不清 | 训练函数只接收 train split |
</section>

<section id="deepen-optimizer-state" data-learning-context="deepen-optimizer-state" data-context-type="deepen" markdown="1">
## 优化器不只是一个公式，也可能持有状态

本课使用无 momentum 的 SGD，便于直接观察梯度与更新。加入 momentum、Adam 或学习率调度器后，优化器会持有速度、矩估计或 step 计数；检查点恢复时必须连同 optimizer state 保存，否则“从同一步继续”并不成立。

优化器选择不是模型结构的一部分，却会显著改变训练轨迹。公平比较需要固定数据顺序、初始化、epoch、指标和预算，而不是只换一个类名。
</section>

<section id="project-diagnosable-network-v04" data-learning-context="project-diagnosable-network-v04" data-context-type="project" markdown="1">
## 可诊断神经网络训练系统 v0.4

- 上一版：v0.3 已能可信计算、核查和清除梯度。
- 本课新增：分层训练/验证数据、确定性 mini-batch、SGD、学习率、30 epoch 与结构化 history。
- 文件：`training_lab.py`、`test_training_lab.py` 与锁定依赖。
- 保存：180 step、参数变化范数、初末 loss、零学习率对照、8 项测试和一次超参数失败恢复。
- 下一版：同时记录 train/validation 曲线，对比无正则、权重衰减与 Dropout，并设置模型选择规则。

验证集虽然已经创建，但 v0.4 不用它调参或更新。训练准确率 1.000 不是开放模块或交付模型的门槛。
</section>

## 四类学习者入口

- 零基础兴趣：把 72 行卡片分成每组12行，手动数出 6 step 与 30 epoch 的180次更新。
- 有基础兴趣：控制初始化不变，比较三种 batch size 的历史曲线和 step 数。
- 零基础求职：用零学习率对照解释“有梯度但参数没变”的排查过程。
- 有基础求职：展示 batch 全覆盖、更新范数、history 与验证隔离证据，不只展示最终准确率。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 每个 epoch 的训练索引恰好覆盖 72 行一次。
- 30 epoch 记录 180 step，每个 history 行数为72。
- 训练 loss 明显下降，参数 update norm 大于0。
- 学习率为0时参数逐值不变。
- 验证 tensor 未参与训练且逐值不变。

## 来源与版本

- 核查日期：2026-07-23。
- 运行环境：Python 3.12、PyTorch 2.13.0、CPU。
- [PyTorch SGD](https://docs.pytorch.org/docs/stable/generated/torch.optim.SGD.html)
- [PyTorch optimizer zero_grad](https://docs.pytorch.org/docs/stable/generated/torch.optim.Optimizer.zero_grad.html)
- [PyTorch optimization tutorial](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html)
- [PyTorch Module train/eval](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html)

## 下一步

进入第 5 课，用验证曲线识别过拟合，并在固定选择协议下比较权重衰减与 Dropout。
