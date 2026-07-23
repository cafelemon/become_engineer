<div class="be-tutor-mount" data-tutor-lesson="deep-learning-01" aria-hidden="true"></div>
<section id="overview-tensor-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-tensor-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">深度学习 · 第 1 / 8 课 · 可诊断神经网络训练系统 v0.1</span>
# 张量、形状、数据类型与设备契约
## 同样是一组数字，形状或 dtype 错一处，后面的网络就没有可靠输入
```text
torch_version=2.13.0
device=cpu
rows=96,features=2,classes=0:48,1:48
inputs=shape:96x2,dtype:float32,device:cpu
targets=shape:96,dtype:int64,device:cpu
mini_batch=inputs:8x2,targets:8
linear_contract=8x2 @ 2x3 + 3 -> 8x3
broadcast_bias=3->8x3
seed_repeat=true
invalid_shape=rejected
invalid_dtype=rejected
invariants=feature-rank2,target-rank1,row-aligned,cpu-deterministic
```
这不是模型准确率报告。它先证明 96 行输入、类别索引、批次、矩阵乘法和广播遵守同一份张量契约，为下一课的神经网络前向计算准备可靠数据。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>深度学习 · 1 / 8</strong></div>
  <div><span>前置</span><strong>机器学习 8 / 8 · 向量与矩阵</strong></div>
  <div><span>环境</span><strong>Python 3.12 · PyTorch 2.13.0 · CPU</strong></div>
  <div><span>完成后留下</span><strong>张量数据契约与 8 项测试</strong></div>
</div>

## 学习目标

- 用 `shape`、`ndim`、`dtype` 和 `device` 描述张量，而不只看里面的数字。
- 为二分类任务区分浮点输入与整数类别索引。
- 读懂批次矩阵乘法 `8×2 @ 2×3 → 8×3`。
- 解释 bias 如何从 `[3]` 广播到 `[8, 3]`。
- 在进入网络前拒绝行数错位、错误类型、跨设备和非有限值。
- 知道固定种子、确定性算法与跨平台逐位复现不是同一承诺。

<section id="concept-tensor-metadata" data-learning-context="concept-tensor-metadata" data-context-type="concept" markdown="1">
## 张量由数值和元数据共同定义

张量可以看成带有规则形状的多维数组，但深度学习计算还同时依赖它的元数据。

| 属性 | v0.1 输入 | v0.1 目标 | 为什么重要 |
| --- | --- | --- | --- |
| `shape` | `[96, 2]` | `[96]` | 第一维必须逐行对齐 |
| `ndim` | 2 | 1 | 模型需要一批特征，损失需要一列类别索引 |
| `dtype` | `float32` | `int64` | 线性层计算浮点数，分类损失按整数找类别 |
| `device` | `cpu` | `cpu` | 同一次运算的张量必须位于兼容设备 |
| finite | 全为真 | 类别为 0/1 | `NaN` 或无穷会污染后续计算 |

`float64` 不等于“总是更好”，`float16` 也不等于“总是更快”。类型选择要和算子、设备、数值范围及精度目标一起判断；基础课先固定 `float32`。
</section>

<section id="concept-shape-linear-broadcast" data-learning-context="concept-shape-linear-broadcast" data-context-type="concept" markdown="1">
## 形状是线性层的接口

一个含 8 行、每行 2 个特征的批次记作 \(X\in\mathbb{R}^{8\times2}\)。若想得到 3 个隐藏表示，权重使用 \(W\in\mathbb{R}^{2\times3}\)，偏置使用 \(b\in\mathbb{R}^{3}\)：

\[
H = XW + b
\]

```text
X [8,2] ──矩阵乘法── W [2,3] ──> [8,3]
                                      +
                                  b [3]
                                      │ 广播到每一行
                                      ▼
                                   H [8,3]
```

矩阵乘法要求中间维相同：`2` 必须对上 `2`。bias 没有真的预先复制 8 份；广播规则把 `[3]` 视为可作用于结果的每一行。能广播不代表语义一定正确，因此代码仍应明确注释 bias 对应最后一维。
</section>

<section id="example-dataset-batch-projection" data-learning-context="example-dataset-batch-projection" data-context-type="example" markdown="1">
## 从 96 行数据取 8 行，完成一次无模型的线性投影

`tensor_lab.py` 用本地 `torch.Generator` 生成两个类别各 48 行的二维数据。输入顺序由同一个生成器打乱，目标随相同索引移动，保证行对齐。

```python
negative = torch.randn((48, 2), generator=generator) * 0.35 - 1.0
positive = torch.randn((48, 2), generator=generator) * 0.35 + 1.0
inputs = torch.cat((negative, positive), dim=0).to(torch.float32)
targets = torch.cat((
    torch.zeros(48, dtype=torch.int64),
    torch.ones(48, dtype=torch.int64),
))
```

取前 8 行后，`inputs @ weights + bias` 得到 `[8, 3]`。这里没有训练，也没有声称这三个数是有用特征；例子只验证下一课需要的接口。
</section>

<section id="reproduce-tensor-v01" data-learning-context="reproduce-tensor-v01" data-context-type="reproduce" markdown="1">
## 运行 v0.1 并核对张量契约

从仓库根目录进入示例：

```bash
cd site-src/examples/deep-learning/diagnosable-neural-network-v01
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_tensor_lab.py
.venv/bin/python tensor_lab.py
```

8 项测试覆盖：

1. 输入与目标的 shape、dtype 和行对齐。
2. 同种子重复与不同种子变化。
3. 两类计数、有限值和同设备。
4. mini-batch 切片不打乱输入目标。
5. 矩阵乘法与 bias 广播后的形状。
6. 错误 rank、特征宽度和行数拒绝。
7. 错误 dtype 与 `NaN` 拒绝。
8. 批次边界和固定报告。

首次安装需要下载约百 MB 的 PyTorch wheel；测试与数据生成之后不联网。若安装命令找不到匹配 wheel，先确认 Python 为 3.9–3.12、操作系统受支持，再从 PyTorch 官方安装页选择当前稳定命令。
</section>

<section id="modify-tensor-contract" data-learning-context="modify-tensor-contract" data-context-type="modify" markdown="1">
## 主动修改特征宽度、隐藏宽度和错误输入

按顺序做三次修改，每次先预测结果再运行：

1. 把 `FEATURE_COUNT` 从 2 改为 4，同时修改生成数据和权重，写出新的矩阵形状。
2. 把 `HIDDEN_WIDTH` 从 3 改为 5，确认 bias 和输出最后一维一起变化。
3. 故意让 targets 少一行、改成 `float32`，或给输入写入 `NaN`，确认验证函数分别拒绝。

不要为了让测试变绿而删除校验。你需要保存修改后的 shape 推导、失败信息和恢复后的测试结果。
</section>

<section id="troubleshoot-tensor-contract" data-learning-context="troubleshoot-tensor-contract" data-context-type="troubleshoot" markdown="1">
## 报错先读形状、类型、设备和有限值

| 现象 | 先检查 | 常见原因 | 恢复 |
| --- | --- | --- | --- |
| `mat1 and mat2 shapes cannot be multiplied` | 两个 operand 的最后/倒数二维 | 特征宽度与权重输入宽度不同 | 写出 `B×F @ F×H` 再改权重 |
| 分类损失抱怨 target 类型 | `targets.dtype` | 类别索引被转成浮点 | 恢复 `torch.int64` |
| tensors on different devices | 输入、目标、参数的 `.device` | 只移动了部分对象 | 在同一入口统一 `.to(device)` |
| 输出形状意外扩大 | bias shape | 广播方向虽合法但语义错误 | 从最后一维向前对齐检查 |
| loss 变成 `nan` | `torch.isfinite` | 输入已有非有限值或后续数值爆炸 | 在数据入口拒绝，后续课再查梯度 |
| 同种子仍有差异 | 版本、硬件、算子和线程 | 只设置种子，不等于全链路确定 | 固定环境并审查确定性说明 |

报错中的 shape 是接口证据，不要先用 `reshape(-1)` 随意压平。错误 reshape 可能让程序继续运行，却把样本维与特征维混在一起。
</section>

<section id="deepen-device-reproducibility" data-learning-context="deepen-device-reproducibility" data-context-type="deepen" markdown="1">
## `device` 是放置位置，固定种子只是复现条件之一

CPU、CUDA 和 Apple MPS 是不同计算后端。把 tensor 移到一个 device 不会自动移动模型参数，反之亦然。本组固定 CPU，是为了让低成本教学命令稳定，而不是断言 CPU 更适合所有训练。

`torch.manual_seed` 或本课的局部 `Generator` 能固定随机数序列，但复现还受 PyTorch 版本、底层库、硬件、算子实现和并行顺序影响。`torch.use_deterministic_algorithms(True)` 会让部分算子选择确定实现或在无确定实现时失败；官方也明确说明这个设置本身仍不足以保证所有场景复现。
</section>

<section id="project-diagnosable-network-v01" data-learning-context="project-diagnosable-network-v01" data-context-type="project" markdown="1">
## 可诊断神经网络训练系统 v0.1

- 上一版：机器学习系统已完成传统模型训练、验证、误差分析和离线交付；还没有神经网络张量接口。
- 本课新增：96 行二维数据、浮点输入、整数类别、8 行批次、线性投影和入口校验。
- 文件：`tensor_lab.py`、`test_tensor_lab.py` 与锁定依赖的 `requirements.txt`。
- 保存：固定报告、8 项测试、一次主动改宽度记录和一次错误恢复记录。
- 下一版：把手写权重换成 `nn.Module`，逐层观察线性层、激活、参数和前向图。

v0.1 不训练模型，也没有准确率。只有当张量接口先稳定，后面的损失下降和验证结果才有可解释基础。
</section>

## 四类学习者入口

- 零基础兴趣：先用纸画出 `[8,2] @ [2,3] + [3]`，再运行程序核对 `[8,3]`。
- 有基础兴趣：增加一个 rank 为 3 的序列批次，明确哪些算子仍可广播、哪些接口必须重写。
- 零基础求职：用 shape、dtype、device 和 row alignment 四个词解释一次真实失败，不背 API 清单。
- 有基础求职：把输入校验、固定配置、失败拒绝和测试组织成可复查项目证据；本课不声称任何招聘频率。

## 完成检查

- 8 项 unittest 全部通过，固定报告逐行一致。
- 能从矩阵维度推导 `8×2 @ 2×3 + 3 → 8×3`。
- 能说明输入为何用 `float32`，类别索引为何用 `int64`。
- 能制造并恢复一次 shape、dtype 或 `NaN` 错误。
- 能说明广播的便利与“合法但语义错误”的风险。
- 能区分固定种子、确定性算法与跨平台逐位复现。

## 来源与版本

- 核查日期：2026-07-23。
- 运行环境：Python 3.12、PyTorch 2.13.0、CPU。
- [PyTorch tensor API](https://docs.pytorch.org/docs/stable/torch.html)
- [PyTorch broadcasting semantics](https://docs.pytorch.org/docs/stable/notes/broadcasting.html)
- [PyTorch reproducibility](https://docs.pytorch.org/docs/stable/notes/randomness.html)
- [PyTorch deterministic algorithms](https://docs.pytorch.org/docs/stable/generated/torch.use_deterministic_algorithms.html)
- [PyTorch local installation](https://docs.pytorch.org/get-started/locally/)

## 下一步

进入第 2 课，把 v0.1 的张量数据接入 `nn.Module`，观察线性层、激活、参数和前向计算图。
