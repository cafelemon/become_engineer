<div class="be-tutor-mount" data-tutor-lesson="machine-learning-06" aria-hidden="true"></div>
<section id="overview-unsupervised-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-unsupervised-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">机器学习 · 第 6 / 8 课 · 结构化数据机器学习系统 v0.6</span>
# 聚类、PCA 与无监督评估
## 没有标签监督时，用结构指标和稳定性描述结果，不把簇叫作真相
```text
rows=120,features=4,target_used_for_fit=false
preprocess=median-impute,standard-scale,pca:2
explained_variance=pc1:0.508,pc2:0.254,total:0.762
kmeans=k:2,n_init:20,inertia:217.647,silhouette:0.337
cluster_sizes=57,63
candidate_silhouette=k2:0.337,k3:0.379,k4:0.384
seed_stability_adjusted_rand=1.000
raw_features_unchanged=true
interpretation=clusters-are-descriptive-not-ground-truth
invariants=no-target-fit,scaled-before-pca,fixed-random-state
```
本课从拟合输入中排除 `target`，先对四个数值特征填补、标准化并投影到两个主成分，再用 KMeans 形成描述性分组。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>机器学习 · 6 / 8</strong></div>
  <div><span>前置</span><strong>监督学习选择协议</strong></div>
  <div><span>依赖</span><strong>NumPy 2.5.1 · pandas 2.3.3 · scikit-learn 1.9.0</strong></div>
  <div><span>完成后留下</span><strong>PCA 投影、聚类结构与无监督结论边界</strong></div>
</div>

## 学习目标

- 区分监督任务的目标标签与无监督任务的输入结构。
- 在 PCA 前执行缺失填补和标准化。
- 解释主成分、解释方差比与二维投影的信息损失。
- 用惯性、轮廓系数、簇大小和跨种子一致性检查聚类。
- 拒绝把聚类标签直接命名为真实人群、因果机制或业务类别。

<section id="concept-pca-variance" data-learning-context="concept-pca-variance" data-context-type="concept" markdown="1">
## PCA 寻找方差最大的正交方向，不是在恢复真实概念

标准化后，PCA 找到第一主成分使投影方差最大，第二主成分与第一正交并解释剩余方差。本课前两维分别解释 0.508 和 0.254，总计 0.762；仍有约 23.8% 的标准化方差信息没有出现在二维投影中。

主成分是原特征的线性组合，符号可整体翻转，不能仅凭坐标方向命名成“质量”或“价值”。标准化很重要，否则量纲大的字段会在方差目标中占据不成比例的权重。
</section>

<section id="concept-kmeans-objective" data-learning-context="concept-kmeans-objective" data-context-type="concept" markdown="1">
## KMeans 最小化样本到簇中心的平方距离

KMeans 在给定 `k` 下交替分配样本和更新中心，目标是降低簇内平方距离和，也就是惯性。惯性随 `k` 增大通常不会上升，因此不能单独用最小惯性选择簇数。

本课使用 `n_init=20` 和固定随机状态，多次初始化后保留较好解。`k=2` 得到 57/63 两簇，轮廓系数 0.337；这些编号没有顺序含义，重新拟合后 0 与 1 可以交换。
</section>

<section id="example-unsupervised-evaluation" data-learning-context="example-unsupervised-evaluation" data-context-type="example" markdown="1">
## 无监督评估组合结构质量、稳定性与解释边界

| 证据 | 本课结果 | 能说明 | 不能说明 |
| --- | ---: | --- | --- |
| 前两主成分解释方差 | 0.762 | 二维保留的方差比例 | 业务信息保留比例 |
| `k=2` 轮廓系数 | 0.337 | 簇内紧密与簇间分离的相对结构 | 存在两个真实类别 |
| `k=2/3/4` 轮廓 | 0.337/0.379/0.384 | 当前候选间的结构比较 | `k=4` 必然有业务价值 |
| 跨种子调整兰德指数 | 1.000 | 两次划分在标签置换后一致 | 对新数据长期稳定 |

内部指标只能评估当前特征几何。是否有用还需领域解释、外部结果、时间稳定性和对下游行动的风险审查。
</section>

<section id="reproduce-unsupervised-v06" data-learning-context="reproduce-unsupervised-v06" data-context-type="reproduce" markdown="1">
## 运行 v0.6 并确认标签未参与拟合

```bash
cd site-src/examples/machine-learning/structured-data-ml-system-v06
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v test_unsupervised_lab.py
.venv/bin/python unsupervised_lab.py
```

8 项测试覆盖目标与 ID 排除、二维投影、解释方差、全量聚类、轮廓边界、固定种子、非法输入拒绝和原始特征不变。
</section>

<section id="modify-unsupervised" data-learning-context="modify-unsupervised" data-context-type="modify" markdown="1">
## 主动修改维度、簇数和特征

1. 比较保留 1、2、3 个主成分时的累计解释方差。
2. 将 `k` 扩展到 2–8，同时记录惯性、轮廓系数和最小簇大小。
3. 删除纯噪声特征，观察 PCA 与轮廓系数怎样变化。
4. 更换 10 个随机种子，汇总调整兰德指数分布，而不是只保留最好一次。
</section>

<section id="troubleshoot-unsupervised" data-learning-context="troubleshoot-unsupervised" data-context-type="troubleshoot" markdown="1">
## 无监督结果异常先查尺度、初始化、极小簇和解释越界

| 现象 | 可能原因 | 恢复 |
| --- | --- | --- |
| 一个特征支配主成分 | 未标准化或异常值 | 检查尺度与稳健处理 |
| 每次簇完全不同 | 初始化不稳定或结构弱 | 增加 `n_init` 并报告稳定性 |
| `k` 越大惯性越小 | 指标固有单调性 | 联合轮廓、稳定性和领域约束 |
| 出现极小簇 | 异常点或过大的 `k` | 检查簇大小和原始样本 |
| 二维图看似分开、指标很弱 | 视觉选择或投影失真 | 返回高维指标并固定图轴 |
| 簇被命名为真实人群 | 解释越过证据 | 改称描述性簇并做外部验证 |
</section>

<section id="project-structured-data-ml-v06" data-learning-context="project-structured-data-ml-v06" data-context-type="project" markdown="1">
## 结构化数据机器学习系统 v0.6

- 从拟合矩阵中显式排除 `sample_id` 和 `target`，只保留四个数值特征。
- 使用中位数填补、标准化和 PCA 两维投影，累计解释方差为 0.762。
- 对 `k=2/3/4` 计算轮廓系数，并记录 `k=2` 惯性、簇大小和跨种子一致性。
- 原始特征表保持不变，所有结论限制为当前合成特征空间的描述。
- 下一版回到监督模型，检查概率校准、阈值和分组错误。
</section>

## 四类学习者入口

- 零基础兴趣：画出二维点和两个中心，说明簇编号为什么可以互换。
- 有基础兴趣：绘制 `k=2..8` 的惯性、轮廓和最小簇大小。
- 零基础求职：解释为什么轮廓系数高也不能证明发现了真实用户类型。
- 有基础求职：设计跨时间、跨种子、外部变量和人工审查的聚类验收。

<section id="career-unsupervised-contract" data-learning-context="career-unsupervised-contract" data-context-type="career" markdown="1">
## 求职加练：轮廓系数显示四簇最好，能否立刻定义四类用户

原创追问：请检查特征是否含敏感代理、尺度和异常值，报告簇大小与多种子稳定性，并要求领域专家和独立时段验证。说明轮廓系数只评价当前几何，不证明四类人真实存在，也不能直接支持差别待遇。
</section>

## 完成检查

- 8 项测试通过，`target_used_for_fit=false`。
- 四个数值特征经填补、标准化和 PCA 得到 120×2 矩阵。
- 前两主成分累计解释方差 0.762。
- `k=2` 的簇大小、惯性、轮廓和跨种子一致性可复现。
- 能明确说出簇是描述性分组，不是标签、身份或因果。

## 来源与版本

- 核查日期 2026-07-23；运行依赖见同目录 `requirements.txt`。
- [scikit-learn PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)
- [scikit-learn KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
- [scikit-learn silhouette_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html)
- [scikit-learn adjusted_rand_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html)

## 下一步

进入第 7 课《概率校准、阈值、分组误差与模型比较》，把模型输出转换为可审计的决策证据。
