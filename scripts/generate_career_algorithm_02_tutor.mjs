import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonId = "career-algorithm-02";
const title = "限时模拟、策略选择与过程记录";
const path = "learning-paths/career-algorithm/02-timed-rehearsal-strategy-log/";
const contexts = [
  ["overview-timed-rehearsal", "overview", "限时模拟目标"],
  ["concept-budget-checkpoints", "concept", "预算与检查点"],
  ["example-rehearsal-events", "example", "策略事件日志"],
  ["reproduce-timed-rehearsal-v02", "reproduce", "回放时间线"],
  ["concept-timeout-versus-switch", "concept", "超时与换题"],
  ["modify-own-timed-session", "modify", "个人限时模拟"],
  ["troubleshoot-rehearsal-log", "troubleshoot", "日志与策略排错"],
  ["project-algorithm-rehearsal-v02", "project", "算法演练运行器 v0.2"],
  ["career-timed-strategy-review", "career", "限时策略追问"],
].map(([id, type, contextTitle]) => ({ id, type, title: contextTitle, anchor: `#${id}` }));

const definitions = [
  ["timeboxed-goal", "overview-timed-rehearsal", "限时模拟真正要训练什么？", "限时训练是不是只看做完几题", "训练在固定预算内持续做出有证据的选择，并保留卡点、止损和复核记录，不只看最终完成数。", "示例完成两项、主动切换一项并保留 2 分钟。"],
  ["budget-first", "concept-budget-checkpoints", "为什么要先固定总预算？", "题目选择前为什么先写时间上限", "先固定预算才能比较任务选择和止损策略，避免结束后无限延长或改写标准。", "plan.json 在事件发生前固定 45 分钟。"],
  ["checkpoint", "concept-budget-checkpoints", "检查点应该检查什么？", "到检查点是否必须换题", "检查点要求核对题意、不变量、边界用例和继续投入依据，不要求机械换题。", "20 分钟记录 invariant-not-stable 后再决定止损。"],
  ["event-types", "example-rehearsal-events", "四种模拟事件分别是什么？", "start checkpoint submit switch 怎么用", "start 开始任务，checkpoint 保存证据，submit 完成本地提交，switch 记录止损并结束任务。", "活跃任务必须由 submit 或 switch 结束。"],
  ["logical-minutes", "reproduce-timed-rehearsal-v02", "逻辑分钟和墙钟耗时有什么区别？", "固定输出为什么不用 time time", "逻辑分钟是学习者声明并可回放的策略记录；墙钟受机器和环境影响，不进入固定快照。", "输出固定写 wall_clock=excluded-from-fixed-output。"],
  ["timeout-switch", "concept-timeout-versus-switch", "timeout 和 switch 有什么区别？", "运行超时与主动换题怎么区分", "timeout 是解法超过单例执行上限，switch 是学习者在总预算内基于证据主动结束当前任务。", "忙循环得到 timeout，不变量不稳后止损得到 switch。"],
  ["one-variable", "modify-own-timed-session", "两轮模拟为什么只改变一个变量？", "怎样做限时策略对照实验", "只改变一个检查点或选择规则，才能把结果差异与该策略关联，避免多项变化无法解释。", "保持题目和 45 分钟不变，只把首个检查点从 10 改到 8。"],
  ["honest-note", "troubleshoot-rehearsal-log", "换题说明怎样写才可复盘？", "为什么 note 不能只写太难", "说明要指出缺少的具体证据，如不变量、最小用例或复杂度判断，才能设计下一步实验。", "写 no-progress-after-checkpoint，不写 hard。"],
  ["timeline-state", "troubleshoot-rehearsal-log", "为什么任务事件不能重叠？", "一个任务没结束能否开始另一个", "单活跃任务让每段投入可归属；开始新任务前必须提交或明确切换旧任务。", "重叠 start 固定得到 cannot start while another task is active。"],
  ["rehearsal-v02", "project-algorithm-rehearsal-v02", "算法演练运行器 v0.2 新增了什么？", "第二课项目增量是什么", "v0.2 在判题状态之上新增预算、检查点、优先级、事件日志、固定汇总和 7 项时间线测试。", "它不采集屏幕、账号或跨设备速度排名。"],
];

const cards = definitions.map(([id, context, question, alias, answer, example], index) => ({
  id, lesson_id: lessonId, context_id: context, question, aliases: [alias],
  keywords: [...new Set(`${question} ${alias}`.replace(/[？?，、]/g, " ").split(/\s+/).filter(Boolean))],
  diagnostic: `先判断“${alias}”属于预算、事件还是证据边界。`,
  hints: [`查看 #${context} 的时间线或状态表。`, `再用 test_timed_rehearsal.py 核对“${question.replace("？", "")}”。`],
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
writeFileSync(resolve(root, `tests/tutor/${lessonId}-search.json`), `${JSON.stringify({ lesson_id: lessonId, cases, unknown: ["怎样给彗星安排限时午睡", "纸飞机的检查点应该种什么花"], }, null, 2)}\n`);
console.log(JSON.stringify({ lesson_id: lessonId, cards: cards.length, questions: cases.length, unknown: 2 }));
