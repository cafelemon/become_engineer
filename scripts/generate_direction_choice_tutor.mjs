import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonId = "direction-choice-01";
const title = "首个可验证项目：从代码证据到方向试学";
const path = "learning-paths/direction-choice/01-first-verifiable-project-direction-trials/";
const contexts = [
  ["overview-first-verifiable-project", "overview", "第一个项目门槛"],
  ["concept-four-evidence-kinds", "concept", "四类项目证据"],
  ["example-study-summary-evidence", "example", "小项目闭环示例"],
  ["reproduce-portfolio-checker", "reproduce", "运行证据检查器"],
  ["concept-direction-trials", "concept", "方向试学实验"],
  ["modify-own-portfolio", "modify", "替换成自己的项目"],
  ["troubleshoot-portfolio-evidence", "troubleshoot", "证据与复现排错"],
  ["project-verification-portfolio-v01", "project", "验证档案 v0.1"],
  ["career-project-evidence-review", "career", "项目证据追问"],
].map(([id, type, contextTitle]) => ({ id, type, title: contextTitle, anchor: `#${id}` }));

const definitions = [
  {
    id: "project-gate",
    context: "overview-first-verifiable-project",
    question: "第一个可验证项目要通过什么门槛？",
    alias: "项目做完的标准是什么",
    answer: "代码、测试、README 和复盘四类证据都真实存在并可复核，才通过本课项目门槛。",
    example: "检查器输出四条 evidence=pass 和 gate=pass。",
  },
  {
    id: "not-career-test",
    context: "overview-first-verifiable-project",
    question: "检查器能决定我适合什么职业吗？",
    alias: "方向排序是不是职业结论",
    answer: "不能。它只选择两个投入受限的试学实验，结果必须由真实完成记录继续修正。",
    example: "固定输出 decision=two-week-trial-not-career-conclusion。",
  },
  {
    id: "four-evidence",
    context: "concept-four-evidence-kinds",
    question: "项目为什么需要代码测试说明和复盘？",
    alias: "四类证据分别证明什么",
    answer: "代码证明行为，测试检查边界，README 提供复现路径，复盘记录错误假设、修改和剩余风险。",
    example: "只有代码能运行，仍无法知道怎样复现或失败路径是否处理。",
  },
  {
    id: "specific-claim",
    context: "concept-four-evidence-kinds",
    question: "artifact claim 应该怎么写？",
    alias: "证据声明为什么不能写学会了 Python",
    answer: "claim 要窄到能从对应文件核对具体行为或边界，不能写宽泛能力口号。",
    example: "写“覆盖正常、空输入和负数拒绝”，不要写“掌握测试”。",
  },
  {
    id: "small-project",
    context: "example-study-summary-evidence",
    question: "小项目也能作为项目证据吗？",
    alias: "项目是不是越大越好",
    answer: "可以。第一份项目优先形成实现、测试、说明和复盘闭环，不以代码量判断质量。",
    example: "学习时段汇总只有一个函数，但覆盖正常、空输入和负数失败。",
  },
  {
    id: "run-checker",
    context: "reproduce-portfolio-checker",
    question: "怎样运行方向选择证据检查器？",
    alias: "portfolio_check 命令是什么",
    answer: "进入 verification-portfolio-v01，运行 portfolio_check.py，并显式传入 manifest 和 workspace。",
    example: "../../../../.venv/bin/python portfolio_check.py --manifest portfolio.json --workspace .",
  },
  {
    id: "workspace-path",
    context: "reproduce-portfolio-checker",
    question: "为什么证据路径不能逃出工作区？",
    alias: "为什么拒绝绝对路径和上级目录",
    answer: "工作区边界让清单可移植，也避免检查器意外读取项目之外的私人或系统文件。",
    example: "../outside.py 会得到 artifact path escapes workspace。",
  },
  {
    id: "route-trial",
    context: "concept-direction-trials",
    question: "两周方向实验应该怎样设计？",
    alias: "方向试学要记录什么",
    answer: "每个实验写清具体产出、投入上限、停止条件和相同的比较记录，完成后再调整方向。",
    example: "6 小时内完成本机 API 和 5 项测试，并记录是否愿意再做一次。",
  },
  {
    id: "missing-evidence",
    context: "troubleshoot-portfolio-evidence",
    question: "missing evidence kinds 怎么修复？",
    alias: "检查器说缺少 reflection 怎么办",
    answer: "补上真实缺失的证据与具体内容，不复制同一文件冒充，也不能用空文件占位。",
    example: "删除 reflection 会固定返回 portfolio_error=missing evidence kinds: reflection。",
  },
  {
    id: "portfolio-v01",
    context: "project-verification-portfolio-v01",
    question: "验证档案 v0.1 最后保存什么？",
    alias: "方向选择课的项目产出有哪些",
    answer: "保存四类证据清单、成功输出、一次失败修复和两条有时间上限的方向实验。",
    example: "公开档案不包含真实姓名、账号、凭据或未授权项目内容。",
  },
];

const cards = definitions.map((item, index) => ({
  id: item.id,
  lesson_id: lessonId,
  context_id: item.context,
  question: item.question,
  aliases: [item.alias],
  keywords: [...new Set(`${item.question} ${item.alias}`.replace(/[？?，、]/g, " ").split(/\s+/).filter(Boolean))],
  diagnostic: `先定位“${item.alias}”对应的证据或试学边界。`,
  hints: [
    `先查看 #${item.context} 的表格或固定输出。`,
    `再用示例项目的测试核对“${item.question.replace("？", "")}”。`,
  ],
  example: item.example,
  answer: item.answer,
  source: { label: contexts.find((context) => context.id === item.context).title, href: `#${item.context}` },
  updated_at: "2026-07-23",
  recommended: index < 6,
}));

const cases = definitions.flatMap((item) => [
  { query: item.question.replace("？", ""), expected_card: item.id },
  { query: item.alias, expected_card: item.id },
]);

mkdirSync(resolve(root, "site-src/data/tutor"), { recursive: true });
mkdirSync(resolve(root, "tests/tutor"), { recursive: true });
writeFileSync(
  resolve(root, `site-src/data/tutor/${lessonId}.json`),
  `${JSON.stringify({ version: 2, lesson: { id: lessonId, title, path }, contexts, cards }, null, 2)}\n`,
);
writeFileSync(
  resolve(root, `tests/tutor/${lessonId}-search.json`),
  `${JSON.stringify({
    lesson_id: lessonId,
    cases,
    unknown: ["怎样把海浪编译成会发光的积木", "月球盆栽应该使用什么网络协议"],
  }, null, 2)}\n`,
);
console.log(JSON.stringify({ lesson_id: lessonId, cards: cards.length, questions: cases.length, unknown: 2 }));
