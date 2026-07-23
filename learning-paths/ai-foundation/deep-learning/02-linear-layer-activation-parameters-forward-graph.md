<div class="be-tutor-mount" data-tutor-lesson="deep-learning-02" aria-hidden="true"></div>
<section id="overview-forward-network" class="be-page-hero be-lesson-hero" data-learning-context="overview-forward-network" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">深度学习 · 第 2 / 8 课 · 可诊断神经网络训练系统 v0.2</span>
# 线性层、激活函数、参数与前向图
## 22 个待学习参数怎样把 8×2 的批次变成 8×2 的 logits
```text
torch_version=2.13.0
batch=8x2
module=TinyClassifier
fc1=weight:4x2,bias:4
relu=8x4
fc2=weight:2x4,bias:2
forward=8x2->8x4->8x4->8x2
parameters=trainable:22,tensors:4
logits=shape:8x2,requires_grad:true
probability_rows_sum_one=true
deterministic_initialization=true
invalid_feature_width=rejected
invariants=module-registered,parameter-shapes-explicit,forward-batch-preserved,no-training-yet
```
同样是“输入 2 个数、输出 2 个类别”，中间的 4 维 ReLU 让两层线性变换不再折叠成单个线性层。本课只观察前向计算和参数注册，不把随机初始化的输出误写成训练结果。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>深度学习 · 2 / 8</strong></div>
  <div><span>前置</span><strong>张量 shape、dtype、device 与广播</strong></div>
  <div><span>环境</span><strong>Python 3.12 · PyTorch 2.13.0 · CPU</strong></div>
  <div><span>完成后留下</span><strong>可追踪前向网络与 8 项测试</strong></div>
</div>

## 学习目标

- 用 `nn.Module` 注册子层和可训练参数。
- 从 `nn.Linear` 的输入输出宽度推导 weight 与 bias shape。
- 解释激活函数为什么使多层网络具有非线性表达能力。
- 区分 logits、概率和类别决策。
- 逐层记录前向 shape，并确认 batch 维保持不变。
- 知道 `requires_grad=True` 只表示会记录梯度图，不表示已经训练。

<section id="concept-module-parameters" data-learning-context="concept-module-parameters" data-context-type="concept" markdown="1">
## `nn.Module` 把计算结构和参数登记在一起

`TinyClassifier` 继承 `nn.Module`，并把两个线性层与一个 ReLU 赋给实例属性：

```python
class TinyClassifier(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.fc1 = nn.Linear(2, 4)
        self.activation = nn.ReLU()
        self.fc2 = nn.Linear(4, 2)
```

赋值给 Module 属性后，`fc1.weight`、`fc1.bias`、`fc2.weight` 和 `fc2.bias` 会被注册。`model.parameters()` 能遍历它们，优化器、设备迁移和状态保存才能统一处理。若把 tensor 随手放进普通列表而不使用 `Parameter`、`ModuleList` 或已注册子模块，框架可能看不到它。

本模型参数数目为：

| 参数 | shape | 元素数 |
| --- | --- | ---: |
| `fc1.weight` | `[4, 2]` | 8 |
| `fc1.bias` | `[4]` | 4 |
| `fc2.weight` | `[2, 4]` | 8 |
| `fc2.bias` | `[2]` | 2 |
| 合计 | 4 个 parameter tensor | 22 |

`nn.Linear(in_features, out_features)` 的 weight 存储形状是 `[out_features, in_features]`。前向接口仍可理解为输入 `[B, in]` 映射到 `[B, out]`。
</section>

<section id="concept-activation-nonlinearity" data-learning-context="concept-activation-nonlinearity" data-context-type="concept" markdown="1">
## 没有激活函数，多层线性仍只是一个线性变换

若两层之间没有 ReLU：

\[
(XW_1+b_1)W_2+b_2 = X(W_1W_2)+(b_1W_2+b_2)
\]

右侧仍能合并成一次线性变换。ReLU 对每个元素执行 \(\max(0,x)\)，把负值截为 0，引入不能被简单矩阵合并的分段非线性。

ReLU 不改变 `[8,4]` 的 shape，却改变数值和局部梯度。它并非所有任务的唯一选择：Sigmoid、Tanh、GELU 等激活有不同范围与梯度行为；这里选择 ReLU 是为了让前向结果和下一课反向路径容易观察。
</section>

<section id="example-forward-trace-logits" data-learning-context="example-forward-trace-logits" data-context-type="example" markdown="1">
## 逐层 trace，而不是只看最终输出

v0.2 的 `trace` 显式保留三处结果：

```python
hidden_linear = self.fc1(inputs)       # [8, 4]
hidden_active = self.activation(hidden_linear)  # [8, 4]
logits = self.fc2(hidden_active)       # [8, 2]
```

`logits` 是每个类别的未归一化分数，可以为负，也不要求两列相加为 1。只在需要解释为类别概率时使用：

```python
probabilities = torch.softmax(logits, dim=1)
```

`dim=1` 表示在每一行的两个类别之间归一化，因此每行概率和为 1。不要在模型末尾先加 softmax 再交给 `CrossEntropyLoss`；该损失直接接收 logits，并在内部以数值更稳定的方式组合 log-softmax 与负对数似然。
</section>

<section id="reproduce-forward-v02" data-learning-context="reproduce-forward-v02" data-context-type="reproduce" markdown="1">
## 运行 v0.2 并核对参数与前向路径

```bash
cd site-src/examples/deep-learning/diagnosable-neural-network-v02
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_forward_lab.py
.venv/bin/python forward_lab.py
```

8 项测试覆盖模块注册、参数名与 shape、逐层输出、ReLU、`model(inputs)` 与 trace 一致、softmax 行和、初始化与坏输入，以及固定报告。

调用模型时使用 `model(inputs)`，不要直接调用 `model.forward(inputs)`。`nn.Module.__call__` 会正确进入 `forward`，并保留 hooks 等框架行为。此时 logits 有 `grad_fn`，说明 PyTorch 已记录本次计算图；直到下一课计算 loss 并调用 `backward()`，参数的 `.grad` 才会得到梯度。
</section>

<section id="modify-forward-network" data-learning-context="modify-forward-network" data-context-type="modify" markdown="1">
## 主动改宽度、激活和输出类别

1. 把隐藏宽度从 4 改为 6，先计算四个 parameter tensor 的新 shape 与总元素数。
2. 把 ReLU 换成 Tanh，比较输出范围，但不要用一次随机输出判断模型优劣。
3. 把类别数从 2 改为 3，同时修改第二层输出、目标契约和 softmax 断言。
4. 暂时删除激活层，用代数说明两层为什么仍可合并，再恢复 ReLU。

保存参数计数、前向 shape、测试结果和一次错误恢复。只有“程序能跑”不足以证明新结构正确。
</section>

<section id="troubleshoot-forward-network" data-learning-context="troubleshoot-forward-network" data-context-type="troubleshoot" markdown="1">
## 前向失败先查注册、shape、激活位置与 logits 语义

| 现象 | 可能原因 | 检查 | 恢复 |
| --- | --- | --- | --- |
| `state_dict` 缺少层 | 子层未注册 | `named_modules()` / `named_parameters()` | 赋给 Module 属性或使用容器模块 |
| 矩阵 shape 不匹配 | 上层输出宽度不等于下层输入宽度 | 逐层打印 `[B,F]` | 同步 `out_features` 与下一层 `in_features` |
| 只有 0/1 输出 | 过早执行 argmax 或阈值 | 查看最终一层 | 保留 logits 给损失 |
| softmax 全站求和为 1 | `dim` 用错 | 逐行检查概率和 | 分类任务在类别维归一化 |
| 参数 `.grad` 为 `None` | 尚未 backward，或参数未参与图 | 查看 loss 与 `grad_fn` | 下一课按 loss → backward 验证 |
| 两次初始化不同 | 未在建模前固定种子 | 比较 `state_dict` | 统一 `build_model(seed)` 入口 |

若只打印最终类别，就看不到错误来自第一层、激活还是第二层。训练初期保留小批次 trace，比盲目调学习率更有效。
</section>

<section id="deepen-dynamic-forward-graph" data-learning-context="deepen-dynamic-forward-graph" data-context-type="deepen" markdown="1">
## 前向运行同时构建本次自动微分图

PyTorch eager 模式在执行 tensor 运算时动态记录产生结果的操作。`trace.logits.grad_fn` 是这次图的一个入口；图在下一次 forward 会重新建立，所以 Python 控制流可以参与模型定义。

动态不等于接口可以随意变化。数据和模块仍应明确 batch、feature、class 维度，否则控制流只会把 shape 错误推迟到运行时。本组先用固定结构建立可诊断链，再讨论编译、性能或动态图高级用法。
</section>

<section id="project-diagnosable-network-v02" data-learning-context="project-diagnosable-network-v02" data-context-type="project" markdown="1">
## 可诊断神经网络训练系统 v0.2

- 上一版：v0.1 已有 96 行二维张量、8 行批次、dtype/device 和入口拒绝。
- 本课新增：`TinyClassifier`、两个线性层、ReLU、四个已注册 parameter tensor 和逐层 trace。
- 文件：`forward_lab.py`、`test_forward_lab.py` 与锁定依赖。
- 保存：22 个参数的计算、前向 shape、概率行和、8 项测试和一次改宽度记录。
- 下一版：对 logits 计算交叉熵，用 autograd 反向传播，并用有限差分核查一个参数梯度。

v0.2 仍没有优化器，也没有更新参数。随机初始化输出只能证明接口通，不证明模型已经学会分类。
</section>

## 四类学习者入口

- 零基础兴趣：逐行写出 22 个参数来自哪里，再沿着 `8×2 → 8×4 → 8×2` 画箭头。
- 有基础兴趣：比较 ReLU 与 Tanh 的输出分布，并解释为什么不能只凭一次前向决定激活优劣。
- 零基础求职：用注册参数、logits、激活和 batch 保持解释模型结构，而不是只说“用了两层网络”。
- 有基础求职：展示 `named_parameters()`、逐层 trace、坏输入拒绝和测试，形成可审查的结构证据；不宣称招聘频率。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 能推导两层 weight、bias 的 shape 和 22 个参数总数。
- 能解释没有激活时多层线性为何仍可合并。
- 能区分 logits、softmax 概率和 argmax 决策。
- 能说明 `requires_grad`、`grad_fn` 与“已经训练”的区别。
- 能制造并恢复一次层宽度、类别维或 softmax 维度错误。

## 来源与版本

- 核查日期：2026-07-23。
- 运行环境：Python 3.12、PyTorch 2.13.0、CPU。
- [PyTorch `nn.Module`](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html)
- [PyTorch `nn.Linear`](https://docs.pytorch.org/docs/stable/generated/torch.nn.Linear.html)
- [PyTorch `nn.ReLU`](https://docs.pytorch.org/docs/stable/generated/torch.nn.ReLU.html)
- [PyTorch softmax](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.softmax.html)
- [PyTorch autograd mechanics](https://docs.pytorch.org/docs/stable/notes/autograd.html)

## 下一步

进入第 3 课，为 v0.2 加入交叉熵、`backward()`、梯度清零和有限差分梯度核查。
