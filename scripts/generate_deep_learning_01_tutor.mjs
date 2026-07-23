import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonId = "deep-learning-01";
const title = "张量、形状、数据类型与设备契约";
const path = "learning-paths/ai-foundation/deep-learning/01-tensor-shape-dtype-device-contract/";

const contexts = [
  ["overview-tensor-contract", "overview", "张量契约结果"],
  ["concept-tensor-metadata", "concept", "张量元数据"],
  ["concept-shape-linear-broadcast", "concept", "形状与广播"],
  ["example-dataset-batch-projection", "example", "数据批次与投影"],
  ["reproduce-tensor-v01", "reproduce", "运行张量实验"],
  ["modify-tensor-contract", "modify", "修改张量契约"],
  ["troubleshoot-tensor-contract", "troubleshoot", "张量契约排错"],
  ["deepen-device-reproducibility", "deepen", "设备与复现"],
  ["project-diagnosable-network-v01", "project", "可诊断网络 v0.1"],
].map(([id, type, contextTitle]) => ({ id, type, title: contextTitle, anchor: `#${id}` }));

const definitions = [
  ["tensor-shape", "concept-tensor-metadata", "张量的 shape 表示什么？", "shape 里的每一维怎么读", "shape 记录每一维长度；本课输入的 [96,2] 表示 96 行样本、每行 2 个特征。", "先从 batch 或 rows 维开始逐维命名。"],
  ["tensor-rank", "concept-tensor-metadata", "ndim 和 shape 有什么关系？", "张量 rank 是什么", "ndim 是 shape 中维度的数量；[96,2] 的 ndim 为 2，[96] 的 ndim 为 1。", "输入 rank2，目标 rank1。"],
  ["input-dtype", "concept-tensor-metadata", "深度学习输入为什么使用 float32？", "特征 dtype 为什么不是 int", "线性计算需要浮点表示；float32 是本课精度、兼容性和成本之间的明确选择。", "v0.1 在入口拒绝 float64。"],
  ["target-dtype", "concept-tensor-metadata", "分类目标为什么使用 int64？", "类别标签为什么要 long", "类别目标是离散索引，PyTorch 分类损失通常要求 int64 类别索引而不是浮点数。", "0 和 1 是类别编号，不是概率。"],
  ["device", "deepen-device-reproducibility", "tensor 的 device 表示什么？", "cpu cuda mps 有什么关系", "device 表示张量所在计算后端；参与同一运算的输入、目标与参数必须在兼容设备上。", "本组固定 CPU 低成本路径。"],
  ["matmul-shape", "concept-shape-linear-broadcast", "怎样推导矩阵乘法后的 shape？", "8x2 乘 2x3 为什么是 8x3", "矩阵乘法要求中间维相等并保留外侧维，所以 [8,2]@[2,3] 得到 [8,3]。", "先写 B×F @ F×H。"],
  ["broadcast", "concept-shape-linear-broadcast", "bias 广播做了什么？", "3 怎么加到 8x3", "形状 [3] 从尾维与 [8,3] 对齐，等价于对 8 行分别加同一组偏置。", "可广播不代表业务语义必然正确。"],
  ["row-alignment", "example-dataset-batch-projection", "输入和目标为什么必须行对齐？", "X 和 y 少一行会怎样", "第 i 行输入的监督答案必须是第 i 个目标；数量或顺序错位会让训练关系失真。", "同一个 randperm 同时索引 inputs 和 targets。"],
  ["seed-reproducibility", "deepen-device-reproducibility", "固定随机种子就能完全复现吗？", "manual_seed 是否保证跨平台一致", "不能；种子只是条件之一，版本、硬件、算子和并行顺序也会影响结果。", "本课只承诺同环境 CPU 实验重复。"],
  ["tensor-contract-v01", "project-diagnosable-network-v01", "可诊断神经网络 v0.1 新增了什么？", "深度学习第一课项目做什么", "它新增版本化合成张量、批次、线性投影、入口校验、固定报告和 8 项真实测试。", "v0.1 尚未训练模型。"],
];

const cards = definitions.map(([id, contextId, question, alias, answer, example], index) => ({
  id,
  lesson_id: lessonId,
  context_id: contextId,
  question,
  aliases: [alias],
  keywords: [...new Set(`${question} ${alias}`.replace(/[？?，、/]/g, " ").split(/\s+/).filter(Boolean))],
  diagnostic: `先判断“${alias}”涉及 shape、dtype、device、广播还是行对齐。`,
  hints: [`查看 #${contextId}。`, "运行 test_tensor_lab.py 并读取实际 shape。"],
  example,
  answer,
  source: { label: contexts.find((item) => item.id === contextId).title, href: `#${contextId}` },
  updated_at: "2026-07-23",
  recommended: index < 8,
}));

const cases = definitions.flatMap(([id, , question, alias]) => [
  { query: question.replace("？", ""), expected_card: id },
  { query: alias, expected_card: id },
]);

mkdirSync(resolve(root, "site-src/data/tutor"), { recursive: true });
mkdirSync(resolve(root, "tests/tutor"), { recursive: true });
writeFileSync(
  resolve(root, `site-src/data/tutor/${lessonId}.json`),
  `${JSON.stringify({ version: 2, lesson: { id: lessonId, title, path }, contexts, cards }, null, 2)}\n`,
);
writeFileSync(
  resolve(root, `tests/tutor/${lessonId}-search.json`),
  `${JSON.stringify({ lesson_id: lessonId, cases, unknown: ["怎样挑选登山鞋", "鲸鱼一天睡多久"] }, null, 2)}\n`,
);
