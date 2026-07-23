<div class="be-tutor-mount" data-tutor-lesson="machine-learning-08" aria-hidden="true"></div>
<section id="overview-delivery-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-delivery-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">机器学习 · 第 8 / 8 课 · 结构化数据机器学习系统 v0.8</span>
# 模型持久化、推理契约与交付验收
## 交付完整流水线、清单和拒绝路径，而不只是一个模型文件
```text
artifact_format=1,training_rows=120,features=5
manifest=model.pkl,sha256_length=64,threshold=0.35
dependencies=numpy:2.5.1,pandas:2.3.3,scikit-learn:1.9.0
roundtrip_probability_match=true
valid_inference=probability:0.479,decision:true
invalid_schema=rejected:missing-or-additional-feature
tampered_artifact=rejected:checksum-mismatch
unsafe_load=trusted-reviewed-artifacts-only
invariants=full-pipeline-persisted,schema-validated,manifest-verified
```
本课把缺失填补、缩放、类别编码、逻辑回归和 sigmoid 校准作为一个完整产物保存，同时交付字段 Schema、阈值、依赖版本与 SHA-256。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>机器学习 · 8 / 8</strong></div>
  <div><span>前置</span><strong>完整监督、无监督与误差分析</strong></div>
  <div><span>依赖</span><strong>NumPy 2.5.1 · pandas 2.3.3 · scikit-learn 1.9.0</strong></div>
  <div><span>完成后留下</span><strong>可验证模型产物与推理拒绝契约</strong></div>
</div>

## 学习目标

- 持久化完整训练流水线，而不是只保存分类器系数。
- 用 JSON 清单记录格式、Schema、阈值、版本和校验和。
- 在反序列化前验证文件完整性和依赖兼容。
- 对单条推理请求执行精确字段、类型、有限数和缺失策略校验。
- 区分离线教学交付与生产模型服务。

<section id="concept-artifact-boundary" data-learning-context="concept-artifact-boundary" data-context-type="concept" markdown="1">
## 模型产物包括所有已学习状态和决策契约

若只保存逻辑回归，推理端还需要“猜”中位数、尺度、独热类别顺序和校准状态。v0.8 保存完整 `CalibratedClassifierCV`，其中每个折模型都包含同一预处理 Pipeline；清单另行记录 0.35 阈值和五个输入字段。

训练后在全部 120 行版本化教学数据上重训交付模型，与第 5–7 课的一次最终评估角色分开。重训不会改变此前测试证据，也不能再声称有新的独立测试表现。
</section>

<section id="concept-serialization-trust" data-learning-context="concept-serialization-trust" data-context-type="concept" markdown="1">
## pickle 不是安全交换格式，只加载可信且已校验的本地产物

pickle 反序列化可以执行任意代码。SHA-256 能发现文件与清单不一致，却不能证明产物本身善意，也不能替代签名、来源控制、权限隔离或安全扫描。本课只加载刚在本机生成、经过审查的教学产物。

加载顺序固定为：解析清单 → 验证格式版本 → 定位文件 → 校验 SHA-256 → 比对依赖版本 → 才执行反序列化 → 验证 bundle 字段。校验失败立即拒绝。
</section>

<section id="example-inference-schema" data-learning-context="example-inference-schema" data-context-type="example" markdown="1">
## 推理入口先验证输入，再返回概率、阈值和决策

| 字段 | 类型 | 缺失 | 规则 |
| --- | --- | --- | --- |
| 4 个数值特征 | 有限整数/浮点数 | 可为 `null` | 拒绝布尔、字符串、NaN 与无穷 |
| `channel` | 非空字符串 | 可为 `null` | 未知字符串交给训练期编码器忽略 |
| 额外字段 | 不允许 | — | 精确字段集合 |
| `target` / ID | 不接收 | — | 不属于推理输入 |

合法示例得到正类概率 0.479，在阈值 0.35 下决策为真。返回概率与阈值能让调用方知道决策来源；不输出训练数据、内部对象或 pickle 内容。
</section>

<section id="reproduce-delivery-v08" data-learning-context="reproduce-delivery-v08" data-context-type="reproduce" markdown="1">
## 运行 v0.8 并验证往返、拒绝与篡改

```bash
cd site-src/examples/machine-learning/structured-data-ml-system-v08
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_delivery_lab.py
.venv/bin/python delivery_lab.py
```

9 项测试覆盖完整五折校准模型、清单字段、往返概率、可空和未知类别、错误 Schema、篡改拒绝、版本漂移、训练输入和固定报告。
</section>

<section id="modify-delivery" data-learning-context="modify-delivery" data-context-type="modify" markdown="1">
## 主动修改格式版本、Schema 和交付门

1. 将 `format_version` 改为 2，先写兼容迁移规则，再允许加载。
2. 增加一个必填数值字段，确认旧请求和旧模型都被明确拒绝。
3. 修改模型文件一个字节，确认反序列化之前失败。
4. 设计不使用 pickle 的交换方案，比较可移植性、算子覆盖和安全边界。
</section>

<section id="troubleshoot-delivery" data-learning-context="troubleshoot-delivery" data-context-type="troubleshoot" markdown="1">
## 推理异常先查清单、版本、Schema 和训练/服务偏差

| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 加载时 checksum 不符 | 文件损坏或被替换 | 拒绝并从可信构建恢复 |
| 依赖版本不符 | 环境漂移 | 使用锁定环境或重新验证迁移 |
| 输入多一个字段 | 调用契约漂移 | 明确版本升级，不静默忽略 |
| 线上概率与离线不同 | 预处理或产物不一致 | 比较清单、哈希与样本快照 |
| 未知类别导致失败 | 推理未复用训练编码器 | 加载完整 Pipeline |
| pickle 来源不明 | 供应链风险 | 绝不加载，追溯可信来源 |
</section>

<section id="project-structured-data-ml-v08" data-learning-context="project-structured-data-ml-v08" data-context-type="project" markdown="1">
## 结构化数据机器学习系统 v0.8

- 全量重训五折 sigmoid 校准流水线，保留训练期全部预处理状态。
- 保存 `model.pkl` 与 `manifest.json`，清单包含 64 位十六进制 SHA-256、依赖版本、Schema 和阈值。
- 加载前验证格式、文件、校验和和依赖；加载后再验证 bundle 契约。
- 推理拒绝缺字段、额外字段、错误类型和非有限数，允许受控缺失和未知类别。
- 这是离线教学交付，不包含 HTTP 服务、模型注册中心、签名系统、监控或生产部署。
</section>

## 四类学习者入口

- 零基础兴趣：画出“请求 → Schema → 完整模型 → 概率 → 阈值 → 决策”链路。
- 有基础兴趣：制作一次模型文件篡改并观察校验在反序列化前失败。
- 零基础求职：解释为什么只交付一个 pickle 文件不是完整机器学习系统。
- 有基础求职：设计产物签名、灰度发布、输入漂移、回滚和在线监控的后续架构。

<section id="career-delivery-contract" data-learning-context="career-delivery-contract" data-context-type="career" markdown="1">
## 求职加练：离线模型文件已经能预测，为什么还不能上线

原创追问：要求训练/推理 Schema、完整预处理、版本与来源、校验和/签名、依赖镜像、性能预算、监控、回滚、隐私和人工处置边界。指出 pickle 任意代码风险，并设计一个篡改文件、未知类别、缺字段和版本不兼容都能安全拒绝的发布门。
</section>

## 完成检查

- 9 项测试通过，加载后概率与内存模型逐值一致。
- 清单记录格式、120 行训练数据、5 个字段、阈值和三项依赖版本。
- 模型篡改在 pickle 加载前因 SHA-256 不符被拒绝。
- 推理 Schema 精确拒绝缺失/额外字段与非法值。
- 能说明可信本地 pickle 与生产供应链安全之间的差距。

## 来源与版本

- 核查日期 2026-07-23；运行依赖见同目录 `requirements.txt`。
- [scikit-learn model persistence](https://scikit-learn.org/stable/model_persistence.html)
- [Python pickle security warning](https://docs.python.org/3/library/pickle.html)
- [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)

## 下一步

八课组级验收已经通过，机器学习模块现已开放；按课程地图进入深度学习。
