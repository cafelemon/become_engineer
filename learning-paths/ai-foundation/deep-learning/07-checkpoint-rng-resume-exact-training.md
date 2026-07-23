<div class="be-tutor-mount" data-tutor-lesson="deep-learning-07" aria-hidden="true"></div>
<section id="overview-exact-resume" class="be-page-hero be-lesson-hero" data-learning-context="overview-exact-resume" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">深度学习 · 第 7 / 8 课 · 可诊断神经网络训练系统 v0.7</span>
# 检查点、随机状态与精确恢复训练
## 从第 3 epoch 中断，恢复到第 8 epoch 后逐值等于连续训练
```text
torch_version=2.13.0
model=2->12->2,dropout=0.2,optimizer=SGD(momentum:0.9)
schedule=total:8,interrupt:3,batch:8
checkpoint=model+optimizer+epoch+history+torch_rng_state
resume=epoch:8,rng_restored:true
equivalence=history:true,model:true,optimizer:true
loss=first:0.558763,final:0.098507
integrity=sha256:64-hex,verified-before-load
load=map_location:cpu,weights_only:true,schema:validated
corrupt_checkpoint=rejected
incompatible_checkpoint=rejected
invariants=atomic-write,trusted-local-artifact,exact-resume,no-test-data
```
只保存模型权重可以做推理，却不足以继续同一次训练。v0.7 同时保存优化器动量、完成 epoch、历史和 PyTorch RNG 状态，并用连续/中断两条路径的逐值相等证明恢复语义。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>深度学习 · 7 / 8</strong></div>
  <div><span>前置</span><strong>训练循环、Dropout、优化器与诊断</strong></div>
  <div><span>环境</span><strong>Python 3.12 · PyTorch 2.13.0 · CPU</strong></div>
  <div><span>完成后留下</span><strong>原子检查点、SHA-256 与 8 项恢复测试</strong></div>
</div>

## 学习目标

- 区分推理权重与可恢复训练检查点。
- 解释模型、优化器、进度、历史和随机状态各自的职责。
- 使用临时文件加原子替换，避免半写检查点成为“最新成功”。
- 在反序列化前核对摘要，再校验版本、架构和配置 Schema。
- 用 `map_location="cpu"` 与 `weights_only=True` 收窄加载面。
- 证明连续训练与中断恢复的 history、model、optimizer 逐值一致。

<section id="concept-checkpoint-state" data-learning-context="concept-checkpoint-state" data-context-type="concept" markdown="1">
## 恢复训练需要恢复一台状态机

| 状态 | 缺失后的后果 |
| --- | --- |
| `model_state_dict` | 参数回到初值，已学结果丢失 |
| `optimizer_state_dict` | SGD momentum 等内部状态丢失，后续轨迹改变 |
| `epoch` 与 history | 可能重复训练或错误追加指标 |
| `torch_rng_state` | shuffle 与 Dropout 从不同随机位置继续 |
| 固定 config / architecture | 可能把状态装进不同实验 |

本课训练含 Dropout、随机 `randperm` 和 SGD momentum，故意让“漏存优化器或 RNG”变成可观察错误。恢复目标不是“最终 loss 看起来差不多”，而是在限定的 CPU、版本、线程和算子条件下精确一致。
</section>

<section id="concept-rng-resume" data-learning-context="concept-rng-resume" data-context-type="concept" markdown="1">
## 随机种子只定义起点，RNG 状态才定义中断位置

重新调用 `manual_seed` 会回到序列起点，不能自动跳过前 3 个 epoch 已消费的随机数。检查点保存 `torch.get_rng_state()`；加载完模型和优化器后调用 `torch.set_rng_state()`，下一次 shuffle 与 Dropout 才接在同一位置。

这里的精确一致是本实验的受控证据，不承诺跨 PyTorch 版本、跨设备或不同并行策略逐位相同。生产复现还要记录依赖、设备、确定性设置与数据版本。
</section>

<section id="example-resume-transaction" data-learning-context="example-resume-transaction" data-context-type="example" markdown="1">
## 保存与加载都要有明确顺序

保存路径：

```python
payload = {
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "epoch": state.epoch,
    "history": list(state.history),
    "torch_rng_state": torch.get_rng_state(),
}
torch.save(payload, temporary_path)
temporary_path.replace(checkpoint_path)
digest = sha256(checkpoint_path)
```

加载路径：

```python
verify_sha256_before_deserialization(path, expected_digest)
payload = torch.load(path, map_location="cpu", weights_only=True)
validate_version_architecture_config(payload)
model.load_state_dict(payload["model_state_dict"], strict=True)
optimizer.load_state_dict(payload["optimizer_state_dict"])
torch.set_rng_state(payload["torch_rng_state"])
```

摘要只能发现字节变化，不能证明来源可信。课程只加载本机刚生成、调用方明确提供摘要的教学产物；未知来源文件即使“有 SHA-256”也不进入加载路径。
</section>

<section id="reproduce-checkpoint-v07" data-learning-context="reproduce-checkpoint-v07" data-context-type="reproduce" markdown="1">
## 运行 v0.7 并核对恢复证据

```bash
cd site-src/examples/deep-learning/diagnosable-neural-network-v07
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_checkpoint_lab.py
.venv/bin/python checkpoint_lab.py
```

8 项测试覆盖训练进度、原子写入、完整状态恢复、history 等价、模型与优化器等价、篡改拒绝、版本拒绝和固定报告。测试使用临时目录，不在仓库残留模型文件。
</section>

<section id="modify-checkpoint" data-learning-context="modify-checkpoint" data-context-type="modify" markdown="1">
## 主动删掉一类状态，观察等价性在哪里断裂

1. 不保存 optimizer state，恢复时新建 SGD：history 与参数会从第 4 epoch 开始分叉。
2. 不恢复 RNG state：shuffle 或 Dropout 会消费另一段随机序列。
3. 把 `epoch` 写成 2 但保留 3 条 history：Schema 门禁应拒绝。
4. 把文件写到目标路径后只写一半：比较直接覆盖与临时文件原子替换。

记录第一个不一致的 epoch、状态种类与修复测试；不要用放宽浮点容差掩盖缺失状态。
</section>

<section id="troubleshoot-checkpoint" data-learning-context="troubleshoot-checkpoint" data-context-type="troubleshoot" markdown="1">
## 恢复失败按完整性 → 兼容性 → 状态 → 数据流排查

| 现象 | 先查什么 | 处理 |
| --- | --- | --- |
| 摘要不一致 | 文件是否截断或被替换 | 反序列化前拒绝，回退到已验证副本 |
| 版本或架构不匹配 | checkpoint Schema | 使用对应代码，不强行忽略字段 |
| optimizer 无 state | 是否在训练后保存、是否正确加载 | 先构造同型 optimizer 再加载 |
| 恢复后首个 batch 就分叉 | RNG 与数据顺序 | 保存/恢复所有实际使用的随机源 |
| history 长度不等于 epoch | 进度提交顺序 | 一次 epoch 完成后再共同提交 |
| CPU 无法读 GPU 产物 | 设备映射 | 显式 `map_location`，再验证 dtype/device |
</section>

<section id="deepen-checkpoint-boundary" data-learning-context="deepen-checkpoint-boundary" data-context-type="deepen" markdown="1">
## 精确恢复不是跨环境绝对可复现

本课在同一 PyTorch 2.13.0、CPU、单线程和同一实现内做逐值对照。GPU 非确定性算子、分布式 sampler、DataLoader worker、Python/NumPy 随机源和混合精度 scaler 都会增加必须保存的状态。

`weights_only=True` 减少任意 Python 对象反序列化能力，但不把未知文件变成可信输入。生产系统还需要产物来源、访问控制、签名或可信制品库、保留策略和回滚规则。
</section>

<section id="project-diagnosable-network-v07" data-learning-context="project-diagnosable-network-v07" data-context-type="project" markdown="1">
## 可诊断神经网络训练系统 v0.7

- 上一版：v0.6 能定位激活和梯度异常并设置裁剪护栏。
- 本课新增：原子检查点、SHA-256、版本/架构/config Schema、CPU 安全加载和精确恢复对照。
- 文件：`checkpoint_lab.py`、`test_checkpoint_lab.py` 与锁定依赖。
- 保存：一次中断恢复报告、8 项测试与一个“删状态导致分叉”的主动实验。
- 下一版：把训练态与离线推理产物分开，建立输入 Schema、类别语义、manifest、篡改拒绝和交付验收。
</section>

## 四类学习者入口

- 零基础兴趣：先画出“模型、优化器、进度、随机状态”四格状态机。
- 有基础兴趣：删掉 optimizer 或 RNG 状态，定位第一处轨迹分叉。
- 零基础求职：解释为什么“保存 `.pt` 文件”不等于可恢复训练。
- 有基础求职：用原子写、摘要前置、Schema、`weights_only` 与逐值对照陈述恢复边界。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 第 3 epoch 保存后恢复到第 8 epoch，history、model 与 optimizer 全部逐值相等。
- 加载时 RNG 与保存点一致；故意消耗随机数后仍能恢复。
- 摘要在 `torch.load` 之前核对，篡改和不兼容版本确定性拒绝。
- 目标文件通过同目录临时文件原子替换，不留下 `.tmp`。
- 能说明哈希、`weights_only=True` 与来源信任分别解决什么、不解决什么。

## 来源与版本

- 核查日期：2026-07-23。
- 运行环境：Python 3.12、PyTorch 2.13.0、CPU。
- [PyTorch saving and loading models](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html)
- [PyTorch reproducibility](https://docs.pytorch.org/docs/stable/notes/randomness.html)
- [torch.load](https://docs.pytorch.org/docs/stable/generated/torch.load.html)

## 下一步

进入第 8 课，冻结离线推理 Schema、manifest 和可信交付产物，完成深度学习八课组级验收。
