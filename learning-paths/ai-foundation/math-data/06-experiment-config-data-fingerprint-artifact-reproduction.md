<div class="be-tutor-mount" data-tutor-lesson="ai-math-data-06" aria-hidden="true"></div>
<section id="overview-reproduction-manifest" class="be-page-hero be-lesson-hero" data-learning-context="overview-reproduction-manifest" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">数学、数据与可复现实验 · 第 6 / 6 课 · 可复现实验与评估系统 v0.6</span>
# 实验配置、数据指纹、产物清单与复现验收
## 一个指标必须能追溯到配置、数据、代码和产物
```text
manifest_version=1
code_revision=teaching-v06
config_sha256=89639c9f639c
data_sha256=d20a11731851
artifact_count=2
verify=pass
tampered=artifacts
invariants=canonical-config,stable-data-order,artifact-integrity
```
最终版用规范化序列化与 SHA-256 发现实验输入和产物变化，并明确哈希能证明什么、不能证明什么。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>数学数据实验 · 6 / 6</strong></div>
  <div><span>前置</span><strong>质量、划分、基线与指标契约</strong></div>
  <div><span>实现</span><strong>Python 3.11 标准库</strong></div>
  <div><span>完成后留下</span><strong>配置、数据、修订、指标与产物完整性清单</strong></div>
</div>
## 学习目标
- 把影响结果的种子、阈值、Schema 版本和划分策略写入配置。
- 用规范化 JSON 避免键顺序造成无意义指纹变化。
- 按稳定样本 ID 排序后计算数据指纹。
- 把代码修订、指标和每个产物摘要登记到版本化清单。
- 验证配置、数据和产物变化，并理解哈希不等于来源可信。
<section id="concept-reproduction-inputs" data-learning-context="concept-reproduction-inputs" data-context-type="concept" markdown="1">
## 复现需要回答“用什么产生了什么”
最小清单包含：清单版本、代码修订、完整配置、配置摘要、数据摘要、指标和产物摘要。只保存最终准确率无法知道种子、阈值或数据是否相同；只保存脚本也无法证明运行时用了哪份输入。

本课配置固定 `seed`、`threshold`、`schema_version` 和 `split_policy`。真实项目还要锁定依赖和运行环境，但不能把口令、令牌或个人数据写进公开清单。
</section>
<section id="concept-canonical-fingerprint" data-learning-context="concept-canonical-fingerprint" data-context-type="concept" markdown="1">
## 指纹先定义规范形式，再执行哈希
JSON 对象键顺序不应改变含义，所以序列化时排序键并移除无关空白；数据行先按唯一 `sample_id` 排序，因此来源行顺序变化不会改变数据指纹。

SHA-256 可以发现字节内容变化，却不能证明内容正确、来源可信或没有恶意替换；这些还依赖访问控制、签名、来源记录和审查。
</section>
<section id="example-manifest-verification" data-learning-context="example-manifest-verification" data-context-type="example" markdown="1">
## 验证结果要指出哪类边界变化
同一清单使用逆序数据行仍 `verify=pass`，因为规范化后内容一致。把 `metrics.json` 从 accuracy 1.0 改为 0.0 后得到 `tampered=artifacts`。

验证器分别返回 `config`、`data` 或 `artifacts`，让恢复动作定位到配置漂移、数据版本变化或文件内容变化，而不是只给一个模糊的“复现失败”。
</section>
<section id="reproduce-manifest-v06" data-learning-context="reproduce-manifest-v06" data-context-type="reproduce" markdown="1">
## 构建并验证实验清单
```bash
cd site-src/examples/ai-math-data/reproducible-experiment-v06
../../../../.venv/bin/python -m unittest -v test_reproducibility_lab.py
../../../../.venv/bin/python reproducibility_lab.py
```
6 项测试覆盖稳定行序、数据变化、清单字段、三类篡改检测、非法输入和固定报告。固定输出不含当前时间、绝对路径或机器标识。
</section>
<section id="modify-reproduction-manifest" data-learning-context="modify-reproduction-manifest" data-context-type="modify" markdown="1">
## 主动扩展环境和来源证据
1. 增加 Python 版本与依赖锁文件摘要。
2. 修改阈值，确认只有配置摘要变化。
3. 修改一行标签，确认数据摘要变化。
4. 设计签名清单，说明它相对普通哈希增加了哪种身份保证。
</section>
<section id="troubleshoot-reproduction" data-learning-context="troubleshoot-reproduction" data-context-type="troubleshoot" markdown="1">
## 复现失败时按边界定位
| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 相同数据行顺序变化就失败 | 未定义规范排序 | 按稳定唯一 ID 排序 |
| 同配置键顺序不同就失败 | 直接哈希原始文本 | 使用规范化序列化 |
| 指标相同却无法解释 | 没记录配置、数据或代码 | 补齐输入与修订 |
| 哈希通过但内容不可信 | 摘要只能证明一致 | 核对来源、权限或签名 |
| 清单泄露秘密 | 把环境值原样写入 | 只登记安全元数据和摘要 |
| 报告无法跨机器比较 | 包含绝对路径与时间 | 将机器相关观测另存 |
</section>
<section id="project-reproducible-experiment-v06" data-learning-context="project-reproducible-experiment-v06" data-context-type="project" markdown="1">
## 可复现实验与评估系统 v0.6
- v0.1–v0.2 建立数值形状与训练集标准化边界。
- v0.3–v0.4 建立数据质量、稳定身份和无泄漏划分。
- v0.5 固定基线、混淆矩阵、阈值与指标口径。
- v0.6 用复现清单把配置、数据、代码、指标和产物闭环。
</section>
## 四类学习者入口
- 零基础兴趣：画出配置、数据、代码到结果的四条箭头。
- 有基础兴趣：增加依赖锁文件与环境摘要。
- 零基础求职：解释为什么“有随机种子”仍不足以复现实验。
- 有基础求职：设计清单签名、秘密隔离和数据来源审计。
<section id="career-reproduction-evidence" data-learning-context="career-reproduction-evidence" data-context-type="career" markdown="1">
## 求职加练：同事跑出不同指标，如何排查
原创追问：双方代码看似相同但指标不同。请按配置、数据、代码修订、环境和产物五层列证据，设计能定位漂移的清单；再说明 SHA-256 完整性检查为何不能替代来源认证和访问控制。
</section>
## 完成检查
- 6 项测试通过，原始清单验证成功，修改产物被识别。
- 配置和数据使用规范化形式计算摘要。
- 数据行顺序变化不会改变指纹，内容变化会改变。
- 清单记录代码修订、指标和两个产物摘要。
- 能说出哈希不能证明来源可信。
## 来源与版本
- Python 3.11 标准库；核查日期 2026-07-23。
- [Python hashlib](https://docs.python.org/3.11/library/hashlib.html)
- [Python json](https://docs.python.org/3.11/library/json.html)
- [NIST Secure Hash Standard](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
## 下一步
完成本组六课组级验收后，可进入机器学习课程，把这些数据与复现契约应用到真实模型训练。
