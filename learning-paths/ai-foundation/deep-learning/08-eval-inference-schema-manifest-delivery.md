<div class="be-tutor-mount" data-tutor-lesson="deep-learning-08" aria-hidden="true"></div>
<section id="overview-offline-delivery" class="be-page-hero be-lesson-hero" data-learning-context="overview-offline-delivery" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">深度学习 · 第 8 / 8 课 · 可诊断神经网络训练系统 v0.8</span>
# Eval、推理 Schema、Manifest 与离线交付
## 交付的是可验证接口，不只是一个模型文件
```text
torch_version=2.13.0
artifact=diagnosable-neural-network-v08,version:1,files:model-state.pt|manifest.json
architecture=2->4->2,activation:relu,dropout:0.25
input_schema=signal_a:float32,signal_b:float32,extra:false,finite:true
output_schema=labels:negative|positive,probabilities:2,threshold:0.5
negative_case=label:negative,probabilities:0.750260|0.249740
positive_case=label:positive,probabilities:0.249740|0.750260
inference=eval:true,inference_mode:true,requires_grad:false,deterministic:true
integrity=sha256:64-hex,verified-before-load
load=map_location:cpu,weights_only:true,strict:true
invalid_input=missing|extra|type|nonfinite:rejected
tampered_model=rejected
invariants=state-dict-only,manifest-validated,trusted-local-artifact,no-network,no-personal-data
```
v0.8 把训练检查点与推理产物分开：只导出 `state_dict`，由 manifest 冻结架构、依赖、输入字段、类别顺序、阈值与摘要；推理入口先校验输入，再强制 `eval` 和 `inference_mode`。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>深度学习 · 8 / 8</strong></div>
  <div><span>前置</span><strong>训练、验证、诊断与检查点恢复</strong></div>
  <div><span>环境</span><strong>Python 3.12 · PyTorch 2.13.0 · CPU</strong></div>
  <div><span>完成后留下</span><strong>离线产物、Manifest 与 9 项交付测试</strong></div>
</div>

## 学习目标

- 区分训练检查点、推理权重和交付 manifest。
- 解释 `model.eval()` 与 `torch.inference_mode()` 的不同职责。
- 固定字段名、数值类型、有限性、额外字段策略与类别顺序。
- 在加载前检查摘要，并用版本、架构、依赖与 Schema 拒绝不兼容产物。
- 输出标签和完整概率向量，验证概率和与阈值语义。
- 说明本机离线交付不等于公网服务、生产安全或真实业务效果。

<section id="concept-inference-mode" data-learning-context="concept-inference-mode" data-context-type="concept" markdown="1">
## Eval 改模块行为，inference_mode 关闭自动微分开销

`model.eval()` 让 Dropout 停止随机丢弃，让 BatchNorm 使用已学习统计；它不会自动关闭 gradient。`torch.inference_mode()` 关闭推理图跟踪与版本计数等开销，却不会自动把模块切到 eval。

因此推理入口同时执行两者。测试先故意把模型设为 train，再调用两次 `predict`，结果逐值一致、模型回到 eval，所有 parameter 的 `.grad` 仍为 `None`。
</section>

<section id="concept-inference-contract" data-learning-context="concept-inference-contract" data-context-type="concept" markdown="1">
## Schema 让特征和类别不靠位置猜测

输入必须恰好包含：

| 字段 | 类型 | 约束 |
| --- | --- | --- |
| `signal_a` | float32 语义的数字 | 不能是 bool、字符串、NaN 或 Infinity |
| `signal_b` | float32 语义的数字 | 同上 |

缺字段、额外字段、错误类型与非有限值全部拒绝。输出固定 `negative | positive` 的类别顺序、两个概率与 0.5 正类阈值。若标签顺序被交换，即使 tensor shape 没变，业务语义也已经损坏。
</section>

<section id="example-artifact-manifest" data-learning-context="example-artifact-manifest" data-context-type="example" markdown="1">
## 两个文件承担不同职责

```text
artifact/
├── model-state.pt   # 仅 state_dict
└── manifest.json    # 身份、版本、架构、依赖、Schema、标签、阈值、SHA-256
```

加载顺序固定：

1. 读取并校验 manifest 的 artifact version、identity、architecture 和 PyTorch version。
2. 只允许固定 basename `model-state.pt`，拒绝 `../outside.pt` 等路径。
3. 在 `torch.load` 前核对模型文件 SHA-256。
4. 使用 CPU、`weights_only=True` 加载，再以 `strict=True` 装入已知模型类。
5. 切到 eval，由唯一 `predict` 入口验证输入并执行推理。

manifest 与摘要都不证明来源。若攻击者能同时替换权重与 manifest，哈希仍会“匹配”；本课只接受可信本机生成产物。
</section>

<section id="reproduce-delivery-v08" data-learning-context="reproduce-delivery-v08" data-context-type="reproduce" markdown="1">
## 运行 v0.8 并完成交付验收

```bash
cd site-src/examples/deep-learning/diagnosable-neural-network-v08
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_delivery_lab.py
.venv/bin/python delivery_lab.py
```

9 项测试覆盖产物分离、manifest 加载、概率契约、eval/无梯度确定性、字段门禁、类型/有限性门禁、模型篡改、路径/Schema 不兼容和固定报告。全部产物写入临时目录，不提交二进制权重。
</section>

<section id="modify-delivery-contract" data-learning-context="modify-delivery-contract" data-context-type="modify" markdown="1">
## 主动演进一个字段，而不是偷偷改变位置

1. 给输入新增 `signal_c`，把 artifact version 和 architecture 一起升级。
2. 为旧 v1 保留显式适配器，用默认值填充并记录兼容边界。
3. 添加 batch 推理，明确输入是“记录列表”而不是把单条 shape 静默广播。
4. 修改阈值到 0.7，比较同一概率下的标签变化，但不得改写概率本身。

为旧、新 manifest 各保留接受/拒绝测试，并写清是否能安全回滚。
</section>

<section id="troubleshoot-delivery" data-learning-context="troubleshoot-delivery" data-context-type="troubleshoot" markdown="1">
## 推理异常按输入 → 产物 → 模式 → 输出语义排查

| 现象 | 先查什么 | 恢复 |
| --- | --- | --- |
| 相同输入结果抖动 | 模型是否仍在 train | 同时执行 eval 与 inference_mode |
| 字段都有但预测反向 | 特征顺序、缩放和标签顺序 | 以 manifest 为接口，不靠调用方记忆 |
| 概率和不为 1 | 是否对正确类别维 softmax | 检查 logits shape 与 `dim=1` |
| 权重摘要不一致 | 文件是否截断/替换 | 在 load 前拒绝并回退可信产物 |
| state_dict key 不匹配 | 架构或版本 | 不用 `strict=False` 静默吞掉差异 |
| manifest 指向目录外 | 路径穿越 | 只允许固定产物 basename |
| NaN 进入模型 | 输入门禁缺失 | 在 tensor 构造前拒绝非有限值 |
</section>

<section id="deepen-delivery-boundary" data-learning-context="deepen-delivery-boundary" data-context-type="deepen" markdown="1">
## 离线交付证据仍有边界

本课没有 HTTP、身份认证、并发、延迟 SLO、漂移监控、灰度发布或公网 TLS，也没有真实用户数据。两个合成样本只证明接口和确定性，不证明泛化质量、公平性或业务价值。

生产交付还需要签名或可信制品仓库、SBOM/漏洞管理、模型审批、数据与指标监控、回滚和访问控制。`state_dict`、`weights_only`、摘要与 Schema 是基础护栏，不是完整供应链安全。
</section>

<section id="project-diagnosable-network-v08" data-learning-context="project-diagnosable-network-v08" data-context-type="project" markdown="1">
## 可诊断神经网络训练系统 v0.8 完成

- v0.1–v0.3：建立 tensor、前向图、loss、autograd 与数值梯度证据。
- v0.4–v0.5：建立确定性训练循环、验证协议、过拟合与正则化判断。
- v0.6–v0.7：建立激活/梯度诊断、裁剪护栏与精确检查点恢复。
- v0.8：分离推理权重，冻结 manifest、输入/输出 Schema、可信加载与坏输入拒绝。
- 最终证据：65 项真实 PyTorch 测试、80 张小码卡、160 条问法、16 条未知问题和 8 课多模式页面验收。
</section>

## 四类学习者入口

- 零基础兴趣：按“输入 → tensor → logits → probability → label”画一条推理链。
- 有基础兴趣：为 batch 推理设计不歧义的 Schema 与 shape 测试。
- 零基础求职：解释为什么 eval、无梯度、输入校验缺一不可。
- 有基础求职：用 artifact identity、摘要前置、路径约束、strict state 与信任边界说明交付方案。

## 完成检查

- 9 项 unittest 与固定报告通过。
- manifest 冻结 artifact identity、version、架构、PyTorch 版本、输入输出 Schema 和 SHA-256。
- negative/positive 两个固定样本标签正确，概率均为 `0.750260 | 0.249740` 的镜像且和为 1。
- 同一输入重复推理逐值一致，Dropout 关闭且不创建 gradient。
- 缺失、额外、类型、bool、NaN 和 Infinity 输入确定性拒绝。
- 篡改权重、越界路径与不兼容 Schema 确定性拒绝。
- 能区分完整性、兼容性与来源信任三种边界。

## 来源与版本

- 核查日期：2026-07-23。
- 运行环境：Python 3.12、PyTorch 2.13.0、CPU。
- [PyTorch saving and loading models](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html)
- [torch.inference_mode](https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html)
- [Module.eval](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.eval)

## 下一步

八课已经通过组级浏览器、严格构建、站内链接和全量回归，深度学习模块已开放；随后按课程地图前置顺序进入下一课程组。
