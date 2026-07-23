<div class="be-tutor-mount" data-tutor-lesson="deep-learning-03" aria-hidden="true"></div>
<section id="overview-gradient-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-gradient-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">深度学习 · 第 3 / 8 课 · 可诊断神经网络训练系统 v0.3</span>
# 交叉熵、自动微分、反向传播与梯度核查
## `backward()` 给出的梯度，怎样证明不只是“有数字”
```text
torch_version=2.13.0
batch=8x2,targets=8
loss=cross_entropy:0.902966,requires_grad:true
backward=parameter_gradients:4,finite:true
gradient_norm=0.971790
finite_difference=parameter:fc2.weight[0,1],autograd:-0.525691,numerical:-0.525683,abs_error:0.000008
accumulation=second_backward:2.000x
zero_grad=set_to_none:true
invalid_target=rejected
invariants=loss-from-logits,backward-once-per-graph,gradients-checked,zero-before-next-step
```
自动微分梯度与有限差分只差 0.000008，说明这个参数在当前点的局部导数可信。两次 backward 若不清零会精确累加为 2 倍；这既可用于梯度累积，也可能悄悄破坏普通训练。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>深度学习 · 3 / 8</strong></div>
  <div><span>前置</span><strong>logits、Module 参数与前向图</strong></div>
  <div><span>环境</span><strong>Python 3.12 · PyTorch 2.13.0 · CPU</strong></div>
  <div><span>完成后留下</span><strong>可信梯度、有限差分与 8 项测试</strong></div>
</div>

## 学习目标

- 用交叉熵把一批 logits 与整数类别目标归约成标量 loss。
- 解释反向传播如何沿计算图应用链式法则。
- 检查每个参数的 `.grad` shape、有限性和全局范数。
- 用中心有限差分核查一个非零参数梯度。
- 观察梯度默认累加，并在下一轮前显式清零。
- 区分计算梯度、更新参数和完整训练循环。

<section id="concept-cross-entropy-loss" data-learning-context="concept-cross-entropy-loss" data-context-type="concept" markdown="1">
## 交叉熵直接接收 logits 和类别索引

二分类网络输出 `[8,2]` logits，targets 是 `[8]` 的 `int64` 类别索引。`nn.CrossEntropyLoss` 对每行执行稳定的 log-softmax，再取真实类别的负对数似然，最后对 batch 求平均。

```python
logits = model(batch.inputs)                 # [8, 2]
loss = nn.CrossEntropyLoss()(logits, targets)  # scalar
```

不要先对 logits 手工 softmax 再传给交叉熵；也不要把 0/1 类别索引随意改成 `float32`。若任务改成多标签分类，目标表示与损失会变化，不能继续套用同一契约。
</section>

<section id="concept-backprop-chain-rule" data-learning-context="concept-backprop-chain-rule" data-context-type="concept" markdown="1">
## backward 从标量 loss 沿图反向应用链式法则

前向计算建立：

```text
inputs → fc1 → ReLU → fc2 → logits → cross_entropy → loss
```

`loss.backward()` 从 \(\partial loss/\partial loss=1\) 开始，沿每个操作的局部导数反向组合，最终把梯度累加到叶子参数的 `.grad`。参数 `[4,2]` 的梯度也为 `[4,2]`：每个元素回答“在当前 batch 和当前参数点附近，轻微增大这个参数会怎样改变 loss”。

一次普通 backward 后，中间计算图通常会释放。若要再次计算同一批梯度，重新做 forward 更自然；不要习惯性开启 `retain_graph=True` 掩盖图生命周期或内存问题。
</section>

<section id="example-finite-difference" data-learning-context="example-finite-difference" data-context-type="example" markdown="1">
## 用中心差分核查 `fc2.weight[0,1]`

对参数 \(w\) 使用小扰动 \(\epsilon=10^{-3}\)：

\[
\frac{\partial L}{\partial w}\approx
\frac{L(w+\epsilon)-L(w-\epsilon)}{2\epsilon}
\]

实验先保存原值，在 `torch.no_grad()` 中分别写入加减 epsilon，计算两次 loss，再恢复原值。结果：

| 方法 | 梯度 |
| --- | ---: |
| autograd | -0.525691 |
| 中心差分 | -0.525683 |
| 绝对误差 | 0.000008 |

有限差分是局部近似，不替代 autograd，也不适合逐个检查大型网络。它特别适合验证自定义算子、手写损失或怀疑反向实现时的少量参数。
</section>

<section id="reproduce-gradient-v03" data-learning-context="reproduce-gradient-v03" data-context-type="reproduce" markdown="1">
## 运行 v0.3 并观察梯度生命周期

```bash
cd site-src/examples/deep-learning/diagnosable-neural-network-v03
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_gradient_lab.py
.venv/bin/python gradient_lab.py
```

8 项测试覆盖标量交叉熵、四个参数梯度、梯度 shape 和范数、有限差分、累加、`zero_grad(set_to_none=True)`、非法目标与固定报告。

固定输出中的 loss、梯度和差分只属于当前初始化与 batch，不代表训练质量。这里没有 `optimizer.step()`，所有参数在实验后仍是初始化值。
</section>

<section id="modify-gradient-check" data-learning-context="modify-gradient-check" data-context-type="modify" markdown="1">
## 主动改 epsilon、batch 和清零顺序

1. 将 epsilon 依次改为 `1e-1`、`1e-3`、`1e-7`，记录有限差分误差为何先减小后受浮点舍入影响。
2. 把 batch 从 8 改为 16，比较 loss 与梯度范数；不要期望按固定倍数变化。
3. 连续做三次 forward/backward 且不清零，验证选中梯度约为第一次的 3 倍。
4. 把清零放在 backward 之后、下一次 forward 之前，说明这和放在每轮开头的等价条件。

恢复时必须确认所有四个参数的 gradient 都有限，而不是只看一个被核查元素。
</section>

<section id="troubleshoot-gradient-contract" data-learning-context="troubleshoot-gradient-contract" data-context-type="troubleshoot" markdown="1">
## 梯度异常先查 loss 契约、图连接、累加和数值

| 现象 | 可能原因 | 检查 | 恢复 |
| --- | --- | --- | --- |
| target dtype 报错 | 类别索引变成 float | `targets.dtype` | 恢复 `int64` |
| `.grad is None` | 参数未参与图、被 detach 或尚未 backward | `grad_fn` 与 `named_parameters()` | 恢复图连接并计算标量 loss |
| 第二次同图 backward 失败 | 图已释放 | 是否复用旧 loss | 重新 forward，不滥用 retain graph |
| 梯度恰好翻倍 | 忘记清零 | 比较连续两次 `.grad` | 每轮显式 `zero_grad` |
| 梯度为 NaN/Inf | 输入、loss 或数值范围异常 | `isfinite` 和逐层 trace | 先定位首个非有限节点 |
| 差分误差很大 | epsilon 不合适、参数未恢复或随机层变化 | 固定模型状态和参数值 | 暂停随机层，中心差分后恢复 |

梯度为 0 不总是错误：ReLU 关闭、参数对当前 batch 无影响或局部最平坦都可能产生零梯度。先查结构和数据，再下结论。
</section>

<section id="deepen-gradient-accumulation" data-learning-context="deepen-gradient-accumulation" data-context-type="deepen" markdown="1">
## 梯度累加是机制，是否正确取决于训练协议

PyTorch 默认执行 `parameter.grad += new_gradient`。普通 mini-batch SGD 通常每个 step 前清零；显存不足时也可故意对多个 micro-batch 累加，再统一 step，但要决定 loss 是否除以累积步数，确保有效梯度尺度符合协议。

`set_to_none=True` 让 `.grad` 回到 `None`，可以减少写零开销，并让“本轮没有梯度”和“本轮梯度恰好为 0”更容易区分。使用前仍需确认优化器对 `None` gradient 的语义。
</section>

<section id="project-diagnosable-network-v03" data-learning-context="project-diagnosable-network-v03" data-context-type="project" markdown="1">
## 可诊断神经网络训练系统 v0.3

- 上一版：v0.2 有两层前向网络、ReLU、22 个参数与逐层 trace。
- 本课新增：交叉熵、一次 backward、四个参数梯度、全局范数、有限差分与累加/清零观察。
- 文件：`gradient_lab.py`、`test_gradient_lab.py` 与锁定依赖。
- 保存：固定 loss、非零差分核查、梯度范数、8 项测试和一次错误恢复。
- 下一版：加入 mini-batch 顺序、SGD、学习率和多 epoch 训练历史，证明参数更新与 loss 下降。

v0.3 仍没有优化器 step。算出正确梯度是训练必要条件，但不是训练完成。
</section>

## 四类学习者入口

- 零基础兴趣：沿“logits → loss → backward → grad”画箭头，手算一个一元函数的中心差分。
- 有基础兴趣：比较三个 epsilon 的差分误差，并解释截断误差与浮点舍入的权衡。
- 零基础求职：用一次梯度累加 bug 说明为什么训练循环必须有明确清零位置。
- 有基础求职：展示有限差分、全参数有限性和图生命周期证据；不把一次 `backward()` 包装成完整训练能力。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 能说明交叉熵为何接收 logits 与 int64 类别索引。
- 四个参数的 gradient 都存在、shape 对齐且为有限值。
- 非零参数的 autograd 与有限差分误差小于 `1e-4`。
- 能复现两次 backward 梯度为 2 倍，并用 `set_to_none=True` 清除。
- 能区分梯度计算、参数更新和训练循环。

## 来源与版本

- 核查日期：2026-07-23。
- 运行环境：Python 3.12、PyTorch 2.13.0、CPU。
- [PyTorch autograd mechanics](https://docs.pytorch.org/docs/stable/notes/autograd.html)
- [PyTorch automatic differentiation tutorial](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)
- [PyTorch CrossEntropyLoss](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)
- [PyTorch Module zero_grad](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.zero_grad)
- [PyTorch gradcheck](https://docs.pytorch.org/docs/stable/generated/torch.autograd.gradcheck.html)

## 下一步

进入第 4 课，把可信梯度接入 SGD 和学习率，建立可复现的 mini-batch 多 epoch 训练循环。
