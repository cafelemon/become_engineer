import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonId = "deep-learning-02";
const title = "线性层、激活函数、参数与前向图";
const path = "learning-paths/ai-foundation/deep-learning/02-linear-layer-activation-parameters-forward-graph/";
const contexts = [
  ["overview-forward-network", "overview", "前向网络结果"],
  ["concept-module-parameters", "concept", "模块与参数"],
  ["concept-activation-nonlinearity", "concept", "激活与非线性"],
  ["example-forward-trace-logits", "example", "前向 trace 与 logits"],
  ["reproduce-forward-v02", "reproduce", "运行前向实验"],
  ["modify-forward-network", "modify", "修改前向网络"],
  ["troubleshoot-forward-network", "troubleshoot", "前向网络排错"],
  ["deepen-dynamic-forward-graph", "deepen", "动态前向图"],
  ["project-diagnosable-network-v02", "project", "可诊断网络 v0.2"],
].map(([id, type, contextTitle]) => ({ id, type, title: contextTitle, anchor: `#${id}` }));
const definitions = [
  ["module-registration", "concept-module-parameters", "nn.Module 为什么要注册子层？", "模型层为什么赋值给 self", "注册后参数、设备迁移、状态保存和优化器才能统一发现这些子层。", "fc1、activation、fc2 都是 Module 属性。"],
  ["parameter", "concept-module-parameters", "Parameter 和普通 tensor 有什么区别？", "哪些 tensor 会被模型训练", "Parameter 是被 Module 登记的可训练 tensor；普通 tensor 不会自动出现在 model.parameters()。", "v0.2 有四个 parameter tensor。"],
  ["linear-weight-shape", "concept-module-parameters", "nn.Linear 的 weight shape 怎样读？", "Linear 2 4 的权重为什么是 4x2", "存储 shape 是 [out_features,in_features]，接口把 [batch,in] 映射到 [batch,out]。", "fc1.weight 为 [4,2]。"],
  ["parameter-count", "concept-module-parameters", "两层网络的 22 个参数怎样计算？", "模型参数量怎么算", "把两层 weight 与 bias 元素相加：4×2+4+2×4+2=22。", "参数 tensor 数量为4，元素总数为22。"],
  ["activation", "concept-activation-nonlinearity", "激活函数为什么不能省略？", "两层 Linear 不加激活会怎样", "没有非线性时连续线性变换仍能合并为一次线性变换，表达能力没有因层数本质增加。", "v0.2 在两层之间使用 ReLU。"],
  ["relu", "concept-activation-nonlinearity", "ReLU 对数值和 shape 做了什么？", "relu 会改变维度吗", "ReLU 把负值变为0并保留非负值，不改变 tensor shape。", "[8,4] 经过 ReLU 仍是 [8,4]。"],
  ["logits", "example-forward-trace-logits", "logits 是概率吗？", "模型最后的分数为什么不相加为1", "不是；logits 是未归一化类别分数，可以为负，也不要求总和为1。", "交叉熵直接接收 logits。"],
  ["softmax-dim", "example-forward-trace-logits", "softmax 为什么使用类别维？", "dim 1 的概率是什么意思", "分类时在每个样本的类别维归一化，使每一行概率和为1。", "8行、2类 logits 使用 dim=1。"],
  ["grad-fn", "deepen-dynamic-forward-graph", "logits 有 grad_fn 表示什么？", "requires_grad true 是否已经训练", "它表示前向运算被自动微分图记录，不表示计算过 loss、梯度或更新参数。", "v0.2 明确 no-training-yet。"],
  ["forward-v02", "project-diagnosable-network-v02", "可诊断神经网络 v0.2 新增了什么？", "深度学习第二课项目做什么", "它新增两层 Module、ReLU、22 个参数、逐层 trace、概率检查和 8 项真实测试。", "下一版加入交叉熵与 backward。"],
];
const cards = definitions.map(([id, contextId, question, alias, answer, example], index) => ({
  id, lesson_id: lessonId, context_id: contextId, question, aliases: [alias],
  keywords: [...new Set(`${question} ${alias}`.replace(/[？?，、/]/g, " ").split(/\s+/).filter(Boolean))],
  diagnostic: `先判断“${alias}”涉及 Module 注册、参数 shape、激活、logits 还是前向图。`,
  hints: [`查看 #${contextId}。`, "运行 test_forward_lab.py 并读取 named_parameters 与 trace。"],
  example, answer,
  source: { label: contexts.find((item) => item.id === contextId).title, href: `#${contextId}` },
  updated_at: "2026-07-23", recommended: index < 8,
}));
const cases = definitions.flatMap(([id, , question, alias]) => [
  { query: question.replace("？", ""), expected_card: id },
  { query: alias, expected_card: id },
]);
mkdirSync(resolve(root, "site-src/data/tutor"), { recursive: true });
mkdirSync(resolve(root, "tests/tutor"), { recursive: true });
writeFileSync(resolve(root, `site-src/data/tutor/${lessonId}.json`), `${JSON.stringify({ version: 2, lesson: { id: lessonId, title, path }, contexts, cards }, null, 2)}\n`);
writeFileSync(resolve(root, `tests/tutor/${lessonId}-search.json`), `${JSON.stringify({ lesson_id: lessonId, cases, unknown: ["如何修理自行车链条", "候鸟为什么迁徙"] }, null, 2)}\n`);
