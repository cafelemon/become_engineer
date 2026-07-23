<div class="be-tutor-mount" data-tutor-lesson="deep-learning-06" aria-hidden="true"></div>
<section id="overview-training-diagnostics" class="be-page-hero be-lesson-hero" data-learning-context="overview-training-diagnostics" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">深度学习 · 第 6 / 8 课 · 可诊断神经网络训练系统 v0.6</span>
# 初始化、激活分布、梯度诊断与裁剪
## 梯度裁剪能把 1454.178728 限到 1，却不能解释为什么它爆炸
```text
torch_version=2.13.0
model=2->16->16->2,batch=32
initialization=normal,std:0.35,bias:zero,seed:20260723
activation=relu,nonzero_rates:0.504|0.369,max:2.728024
loss=1.076698,finite:true
gradient_norms=fc1.weight:0.750465,fc1.bias:0.507917,fc2.weight:0.700241,fc2.bias:0.368885,output.weight:0.802881,output.bias:0.149756
global_gradient_norm=1.454179
explosive_loss_scale=1000,clip_threshold=1.0,before:1454.178728,after:1.000000
zero_initialization=hidden_gradients_stalled:true
nonfinite_input=rejected
invalid_clip_threshold=rejected
invariants=activations-observed,layer-gradients-finite,clip-after-backward-before-step,root-cause-still-required
```
本课同时观察输入、激活、loss 和逐层 gradient。裁剪放在 backward 之后、step 之前，只限制本次更新；数据、学习率、loss 尺度或结构问题仍要定位。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>深度学习 · 6 / 8</strong></div>
  <div><span>前置</span><strong>训练、验证、正则化与梯度范数</strong></div>
  <div><span>环境</span><strong>Python 3.12 · PyTorch 2.13.0 · CPU</strong></div>
  <div><span>完成后留下</span><strong>逐层诊断快照与 8 项测试</strong></div>
</div>

## 学习目标

- 解释初始化为什么影响前向激活与反向梯度。
- 记录两层 ReLU 非零率和最大激活值。
- 检查每个 parameter gradient 的存在、有限性和范数。
- 区分梯度消失、梯度爆炸与非有限值。
- 正确使用 `clip_grad_norm_` 并核对裁剪前后全局范数。
- 说明裁剪是护栏，不是根因修复。

<section id="concept-initialization-symmetry" data-learning-context="concept-initialization-symmetry" data-context-type="concept" markdown="1">
## 初始化既要打破对称，也要控制信号尺度

若所有隐藏权重和 bias 都为 0，同层神经元得到相同输出和更新；本实验中 ReLU 隐藏激活全为0，三层 weight gradient 都停滞，只有最终 bias 能收到类别不平衡信号。

过大的随机尺度又会放大激活与梯度。v0.6 使用固定正态标准差0.35建立可观察基线，不把它称为通用最佳初始化。真实网络通常按激活和 fan-in/fan-out 选择 Xavier、Kaiming 等初始化。
</section>

<section id="concept-activation-gradient-signals" data-learning-context="concept-activation-gradient-signals" data-context-type="concept" markdown="1">
## 只看总 loss 会错过首个异常层

健康快照同时记录：

| 位置 | 观察量 | 本次结果 |
| --- | --- | --- |
| ReLU 1 | 非零率 | 0.504 |
| ReLU 2 | 非零率 | 0.369 |
| 全部激活 | 最大值 | 2.728024 |
| 六个参数 | gradient norm | 0.149756–0.802881 |
| 全模型 | global gradient norm | 1.454179 |

接近0的激活率可能提示大量 ReLU 关闭；层间梯度快速衰减或增长可能提示消失/爆炸。单个 batch 只是诊断切片，应结合多个 step、数据与曲线判断。
</section>

<section id="example-gradient-clipping" data-learning-context="example-gradient-clipping" data-context-type="example" markdown="1">
## 裁剪发生在 backward 之后、optimizer step 之前

实验把 loss 放大1000倍，因此 gradient norm 也精确放大约1000倍：

```python
loss.backward()
before = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
optimizer.step()
```

`clip_grad_norm_` 返回裁剪前总范数，并原地缩放 gradient。本课在 step 前停下，证明参数尚未改变；裁剪后范数为1.000000。

如果输入已经是 NaN，或 loss 公式错误，强行裁剪不能恢复可靠含义。v0.6 在前向入口拒绝非有限输入，并在每个 parameter gradient 上检查有限性。
</section>

<section id="reproduce-diagnostics-v06" data-learning-context="reproduce-diagnostics-v06" data-context-type="reproduce" markdown="1">
## 运行 v0.6 并核对诊断链

```bash
cd site-src/examples/deep-learning/diagnosable-neural-network-v06
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_diagnostics_lab.py
.venv/bin/python diagnostics_lab.py
```

8 项测试覆盖初始化复现、激活统计、六个 gradient、loss 缩放、裁剪、零初始化停滞、非有限拒绝和固定报告。
</section>

<section id="modify-diagnostics" data-learning-context="modify-diagnostics" data-context-type="modify" markdown="1">
## 主动改初始化、激活和裁剪阈值

1. 把初始化 std 改为0、0.05、0.35、2.0，比较激活与梯度。
2. 把 ReLU 换成 Tanh，增加饱和区间比例统计。
3. 比较 clip threshold 0.1、1、10 对同一 gradient 的影响。
4. 故意给一个输入写入 NaN，确认在计算 loss 前拒绝。

保存首个异常层、根因假设、修复动作和回归测试，不能只写“加了裁剪后能跑”。
</section>

<section id="troubleshoot-training-diagnostics" data-learning-context="troubleshoot-training-diagnostics" data-context-type="troubleshoot" markdown="1">
## 训练不稳定按数据 → 激活 → loss → gradient → update 排查

| 现象 | 先检查 | 恢复方向 |
| --- | --- | --- |
| 首层激活已非有限 | 输入与初始化 | 拒绝坏数据，缩放输入/权重 |
| 深层非零率接近0 | bias、学习率、ReLU | 调初始化或激活，不盲目加层 |
| 各层 gradient 越来越小 | 激活与深度 | 检查饱和、归一化或残差路径 |
| global norm 突增 | loss scale、异常 batch | 定位根因，再决定是否裁剪 |
| clip 每步都触发 | 阈值或系统性不稳定 | 不把长期饱和裁剪当正常 |
| gradient 有 NaN | 首个非有限节点 | 立即停止 step，保存诊断快照 |
</section>

<section id="deepen-clip-semantics" data-learning-context="deepen-clip-semantics" data-context-type="deepen" markdown="1">
## 全局范数裁剪保留方向近似，但改变步长

当总范数超过阈值时，所有 gradient 按同一比例缩放，因此联合方向不变、长度受限。按值裁剪则逐元素截断，方向可能显著改变。

混合精度训练还需先 unscale 再裁剪；分布式训练需要明确裁剪发生在梯度同步前后。它们超出本课 CPU 基础范围，但说明“调用一个裁剪函数”并不是完整稳定性方案。
</section>

<section id="project-diagnosable-network-v06" data-learning-context="project-diagnosable-network-v06" data-context-type="project" markdown="1">
## 可诊断神经网络训练系统 v0.6

- 上一版：v0.5 能用验证协议比较正则候选。
- 本课新增：初始化入口、逐层激活、六个梯度范数、全局范数、非有限门禁和裁剪。
- 文件：`diagnostics_lab.py`、`test_diagnostics_lab.py` 与锁定依赖。
- 保存：健康/爆炸/零初始化三份快照、8项测试和一次根因恢复记录。
- 下一版：保存 model、optimizer、epoch 与随机状态，证明中断恢复与连续训练逐值一致。
</section>

## 四类学习者入口

- 零基础兴趣：沿数据到更新画五个检查点，并标出首个可能异常位置。
- 有基础兴趣：比较四种初始化尺度的激活与 gradient profile。
- 零基础求职：解释一次“裁剪后能训练但问题仍未解决”的排错过程。
- 有基础求职：用逐层范数、非有限门禁和裁剪位置展示诊断证据，不只报 global norm。

## 完成检查

- 8项 unittest 与固定报告通过。
- 两层 ReLU 非零率、最大激活和六个 gradient norm 可复查。
- loss 放大1000倍时 gradient norm 同比例变化。
- 裁剪前范数1454.178728，裁剪后不超过1.00001，参数尚未 step。
- 零初始化隐藏 weight gradient 停滞。
- 非有限输入与非法阈值确定性拒绝。

## 来源与版本

- 核查日期：2026-07-23。
- 运行环境：Python 3.12、PyTorch 2.13.0、CPU。
- [PyTorch initialization](https://docs.pytorch.org/docs/stable/nn.init.html)
- [PyTorch clip_grad_norm_](https://docs.pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html)
- [PyTorch numerical accuracy](https://docs.pytorch.org/docs/stable/notes/numerical_accuracy.html)

## 下一步

进入第7课，保存并恢复模型、优化器、epoch与随机状态，验证连续训练和中断恢复一致。
