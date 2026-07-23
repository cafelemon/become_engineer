<div class="be-tutor-mount" data-tutor-lesson="ai-math-data-01" aria-hidden="true"></div>
<section id="overview-vector-contract" class="be-page-hero be-lesson-hero" data-learning-context="overview-vector-contract" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">数学、数据与可复现实验 · 第 1 / 6 课 · 可复现实验与评估系统 v0.1</span>
# 向量、矩阵、形状与数值契约
## 数字能算之前，形状必须先对齐
```text
vector=1,2,3 weights=0.5,-1,2
dot=4.5
matrix_shape=2x3
matvec=4.5,3.0
distance_0_0_to_3_4=5.0
ragged=reject
invariants=same-length,rectangular-shape
```
本课不靠第三方数组 API 隐藏规则：向量长度、矩阵行列和乘法输入形状都成为显式契约。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>数学数据实验 · 1 / 6</strong></div>
  <div><span>前置</span><strong>Python 序列、循环、函数与异常</strong></div>
  <div><span>实现</span><strong>Python 3.11 标准库</strong></div>
  <div><span>完成后留下</span><strong>点积、矩阵向量积、距离与形状拒绝证据</strong></div>
</div>
## 学习目标
- 区分标量、向量、矩阵和它们的形状。
- 把点积写成同位置乘积之和。
- 把矩阵向量积拆成每行一次点积。
- 解释欧氏距离要求维度一致。
- 在进入计算前拒绝锯齿矩阵和形状错配。
<section id="concept-scalar-vector-matrix" data-learning-context="concept-scalar-vector-matrix" data-context-type="concept" markdown="1">
## 形状说明有多少轴、每个轴多长
标量是一个数；向量是一列有顺序的分量，形状可写作 `(3,)`；矩阵有行和列，样例两行三列写作 `2×3`。
```mermaid
flowchart LR
  S["标量 4.5"] --> V["向量 (1,2,3) · 长度 3"]
  V --> M["矩阵 2×3 · 两个长度 3 的行"]
```
Python 的嵌套列表允许不同行长度不同，但数学矩阵不允许。程序必须主动检查矩形形状，不能等到中途索引失败。
</section>
<section id="example-dot-matvec" data-learning-context="example-dot-matvec" data-context-type="example" markdown="1">
## 点积把两个等长向量压成一个标量
```text
(1,2,3) · (0.5,-1,2)
= 1×0.5 + 2×(-1) + 3×2
= 4.5
```
矩阵乘向量时，每一行与同一个向量点积。`[[1,2,3],[2,0,1]]` 乘权重后得到 `(4.5,3.0)`；矩阵列数必须等于向量长度。
</section>
<section id="concept-distance-dimension" data-learning-context="concept-distance-dimension" data-context-type="concept" markdown="1">
## 距离先逐维做差，再合成长度
二维点 `(0,0)` 到 `(3,4)` 的欧氏距离为 `sqrt(3²+4²)=5`。三维点不能直接与二维点比较，因为缺少的分量没有默认语义；补零、删除维度或拒绝输入必须由问题契约决定，本课选择拒绝。
</section>
<section id="reproduce-vector-v01" data-learning-context="reproduce-vector-v01" data-context-type="reproduce" markdown="1">
## 运行最小数值实验
```bash
cd site-src/examples/ai-math-data/reproducible-experiment-v01
../../../../.venv/bin/python -m unittest -v test_vector_shape_lab.py
```
6 项测试覆盖点积、空向量、矩阵形状、矩阵向量积、距离、形状错配与固定报告。运算时间与输入分量数线性相关；矩阵向量积为 `O(rows×columns)`。
</section>
<section id="modify-vector-contract" data-learning-context="modify-vector-contract" data-context-type="modify" markdown="1">
## 改变维度和输出
1. 增加第三行，预测输出长度与数值再运行。
2. 把一个三维权重删成二维，确认在计算前失败。
3. 实现曼哈顿距离，并对 `(0,0)` 与 `(3,4)` 比较 7 和 5。
4. 允许空矩阵时，说明 `(0,0)` 是教学约定而非所有数组库的唯一表示。
</section>
<section id="troubleshoot-vector-shape" data-learning-context="troubleshoot-vector-shape" data-context-type="troubleshoot" markdown="1">
## 数值错误先查形状，再查公式
| 现象 | 原因 | 恢复 |
| --- | --- | --- |
| zip 静默少算 | 两向量长度不同 | 先比较长度并使用 strict |
| 第二行索引失败 | 矩阵为锯齿结构 | 计算前验证每行列数 |
| matvec 输出个数错 | 混淆行数与列数 | 每行产生一个输出 |
| 距离能算但语义错误 | 不同维度被截断 | 拒绝或显式定义补齐 |
| 形状写成 3×2 | 行列顺序颠倒 | 固定 rows×columns |
| 小数显示漂移 | 输出未冻结格式 | 教学报告固定一位小数 |
</section>
<section id="project-reproducible-experiment-v01" data-learning-context="project-reproducible-experiment-v01" data-context-type="project" markdown="1">
## 可复现实验与评估系统 v0.1
- 第一版把数值输入形状、固定输出和失败状态变成可回归证据。
- 暂不引入 NumPy，确保学习者能解释数组库之后自动执行的规则。
- 下一版加入缩放和标准化，观察不同量纲怎样影响距离与点积。
</section>
## 四类学习者入口
- 零基础兴趣：用纸笔算点积和 2×3 矩阵向量积。
- 有基础兴趣：增加转置函数并写形状测试。
- 零基础求职：用一句话解释 matvec 为什么要求列数等于向量长度。
- 有基础求职：讨论空矩阵、稀疏矩阵与批量维度的契约差异。
<section id="career-vector-contract" data-learning-context="career-vector-contract" data-context-type="career" markdown="1">
## 求职加练：广播不是修复形状错误的万能答案
原创追问：一个特征向量有 4 列，权重只有 3 项，代码用普通 zip 得到了“正常”分数。请指出静默截断，设计形状校验和最小回归；再说明何时广播是明确模型，何时只是掩盖数据错误。
</section>
## 完成检查
- 6 项测试通过，固定报告不含机器相关值。
- 点积为 4.5，矩阵形状为 2×3，matvec 为 `4.5,3.0`。
- 欧氏距离为 5.0。
- 锯齿矩阵、长度与维度错配在计算前拒绝。
- 能解释 same-length 与 rectangular-shape 两个不变量。
## 来源与版本
- Python 3.11 标准库；核查日期 2026-07-23。
- [Python tutorial: Data Structures](https://docs.python.org/3.11/tutorial/datastructures.html)
- [NumPy: Array objects](https://numpy.org/doc/stable/reference/arrays.html)：用于确认后续数组形状术语，本课不依赖 NumPy 运行。
## 下一步
进入第 2 课《点积、距离、缩放与标准化》，处理量纲不同导致的比较偏差。

