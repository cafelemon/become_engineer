import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonId = "career-algorithm-03";
const title = "错因分类、最小反例与回归复盘";
const path = "learning-paths/career-algorithm/03-failure-categories-minimal-counterexamples-regression/";
const contexts = [
  ["overview-algorithm-retrospective", "overview", "复盘证据链"],
  ["concept-five-failure-categories", "concept", "五类错因"],
  ["example-counterexample-probe", "example", "反例候选与探针"],
  ["reproduce-retrospective-v03", "reproduce", "运行复盘检查"],
  ["concept-regression-evidence", "concept", "回归证据"],
  ["modify-own-retrospective", "modify", "个人失败复盘"],
  ["troubleshoot-retrospective", "troubleshoot", "复盘断链排错"],
  ["project-algorithm-rehearsal-v03", "project", "算法演练运行器 v0.3"],
  ["career-retrospective-review", "career", "失败解释追问"],
].map(([id, type, contextTitle]) => ({ id, type, title: contextTitle, anchor: `#${id}` }));

const definitions = [
  ["evidence-chain", "overview-algorithm-retrospective", "完整失败复盘需要哪些证据？", "失败后应该留下什么", "至少关联观察状态、反例候选、更小探针、原因、修复、唯一回归测试和时间线事件。", "修复后固定得到 after=regression-pass。"],
  ["five-categories", "concept-five-failure-categories", "算法错因分为哪五类？", "契约边界实现复杂度策略怎么区分", "本课使用 contract、boundary、implementation、complexity 和 strategy 五类当前假设。", "wrong-answer 可能来自边界或实现，状态不等于根因。"],
  ["category-hypothesis", "concept-five-failure-categories", "错因分类为什么不是永久结论？", "分类错了以后怎么办", "分类只是指导下一实验的当前假设；回归仍失败时应更新类别和原因。", "不能为了维护旧标签不断叠加补丁。"],
  ["counterexample-candidate", "example-counterexample-probe", "为什么只称反例候选？", "工具能否证明全局最小反例", "最小性依赖输入域、比较方式和搜索范围，结构检查器不能从一段文本证明全局最小。", "固定输出明确写 candidate-not-proof-of-global-minimality。"],
  ["smaller-probe", "example-counterexample-probe", "更小探针要记录什么？", "怎样说明反例已经缩小", "记录一次更小输入的结果，或说明在已声明输入域内为什么无法继续缩小。", "数量 0 的更小探针写 no smaller valid count exists。"],
  ["regression-gate", "reproduce-retrospective-v03", "复盘记录怎样通过门槛？", "after 为什么必须 regression-pass", "每条修复必须关联唯一测试并达到 regression-pass；未解决时应继续更新假设，不能强行过门。", "重复 regression_id 和 still-failing 都会被拒绝。"],
  ["operation-count", "concept-regression-evidence", "复杂度修复为什么用操作计数？", "为什么不用一次耗时证明更快", "操作计数直接对应实现工作量，避免机器负载干扰；它比一次墙钟稳定，但仍不替代完整证明。", "100 次查询固定执行 100 次集合成员检查。"],
  ["one-fix", "modify-own-retrospective", "为什么一次只做一个最小修复？", "同时重构和换算法有什么问题", "一次改动让回归变化能与具体原因关联；多项同时变化会让修复机制无法解释。", "先固定反例和失败测试，再改一个状态更新时机。"],
  ["technical-cause", "troubleshoot-retrospective", "原因为什么不能只写粗心？", "复盘中的 cause 应该怎么写", "原因要指出可观察的技术机制，例如访问时机、边界假设或复杂度增长，才能导出测试。", "写节点出队后才标记访问，不写我太粗心。"],
  ["rehearsal-v03", "project-algorithm-rehearsal-v03", "算法演练运行器 v0.3 交付什么？", "三课项目最终产出是什么", "它关联判题状态、限时事件、五类错因、反例探针、修复和回归，共有 26 项 Python 测试。", "项目不预测录用概率，也不保存企业题目或真实账号。"],
];

const cards = definitions.map(([id, context, question, alias, answer, example], index) => ({
  id, lesson_id: lessonId, context_id: context, question, aliases: [alias],
  keywords: [...new Set(`${question} ${alias}`.replace(/[？?，、]/g, " ").split(/\s+/).filter(Boolean))],
  diagnostic: `先判断“${alias}”的证据链断在观察、反例、修复还是回归。`,
  hints: [`查看 #${context} 的分类表或固定输出。`, `再用两组测试核对“${question.replace("？", "")}”。`],
  example, answer,
  source: { label: contexts.find((item) => item.id === context).title, href: `#${context}` },
  updated_at: "2026-07-23", recommended: index < 6,
}));
const cases = definitions.flatMap(([id, , question, alias]) => [
  { query: question.replace("？", ""), expected_card: id },
  { query: alias, expected_card: id },
]);

mkdirSync(resolve(root, "site-src/data/tutor"), { recursive: true });
mkdirSync(resolve(root, "tests/tutor"), { recursive: true });
writeFileSync(resolve(root, `site-src/data/tutor/${lessonId}.json`), `${JSON.stringify({ version: 2, lesson: { id: lessonId, title, path }, contexts, cards }, null, 2)}\n`);
writeFileSync(resolve(root, `tests/tutor/${lessonId}-search.json`), `${JSON.stringify({ lesson_id: lessonId, cases, unknown: ["怎样给极光制作最小饼干反例", "松鼠回归测试需要几把雨伞"], }, null, 2)}\n`);
console.log(JSON.stringify({ lesson_id: lessonId, cards: cards.length, questions: cases.length, unknown: 2 }));
