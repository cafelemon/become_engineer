import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonId = "career-algorithm-01";
const title = "固定输入输出与本机判题契约";
const path = "learning-paths/career-algorithm/01-fixed-io-local-judge-contract/";
const contexts = [
  ["overview-fixed-io-judge", "overview", "本机判题目标"],
  ["concept-four-judge-boundaries", "concept", "判题链边界"],
  ["example-deduplicate-contract", "example", "去重排序契约"],
  ["reproduce-local-judge-v01", "reproduce", "运行真实判题"],
  ["concept-result-state-machine", "concept", "判定状态机"],
  ["modify-create-controlled-failures", "modify", "主动制造失败"],
  ["troubleshoot-local-judge", "troubleshoot", "判题排错"],
  ["project-algorithm-rehearsal-v01", "project", "算法演练运行器 v0.1"],
  ["career-judge-contract-review", "career", "机考契约追问"],
].map(([id, type, contextTitle]) => ({ id, type, title: contextTitle, anchor: `#${id}` }));

const definitions = [
  {
    id: "fixed-io-contract",
    context: "overview-fixed-io-judge",
    question: "固定输入输出判题到底检查什么？",
    alias: "为什么思路正确还可能判错",
    answer: "它同时检查输入格式、输出格式、进程退出和时间上限；算法思路只是完整契约中的一层。",
    example: "调试文本写进 stdout 会让正确算法得到 wrong-answer。",
  },
  {
    id: "judge-boundaries",
    context: "concept-four-judge-boundaries",
    question: "本机判题链有哪些边界？",
    alias: "cases judge solution 之间怎样通信",
    answer: "运行器读取用例，向解法子进程 stdin 写输入，再读取 stdout、stderr、退出码并处理超时。",
    example: "cases.json -> judge_runner.py -> solution.py -> 判定状态。",
  },
  {
    id: "deterministic-output",
    context: "example-deduplicate-contract",
    question: "集合去重后为什么还要排序？",
    alias: "怎样让算法输出稳定可重复",
    answer: "集合只负责唯一性，排序显式规定输出顺序，避免依赖未写进契约的遍历顺序。",
    example: "sorted(set(values)) 固定输出为 1 2 4 9。",
  },
  {
    id: "real-subprocess",
    context: "reproduce-local-judge-v01",
    question: "运行器是否真的启动了解法进程？",
    alias: "本机判题是不是 Mock",
    answer: "是。它用 subprocess.run 和参数列表启动当前 Python 解释器，传入 stdin 并捕获真实标准流与退出码。",
    example: "测试会实际运行错误退出和忙循环脚本。",
  },
  {
    id: "result-order",
    context: "concept-result-state-machine",
    question: "判题状态为什么要按顺序判断？",
    alias: "超时运行错误答案错误先判断哪个",
    answer: "先处理运行器错误和超时，再看非零退出，最后才比较正常进程的 stdout，避免把不同根因压成答案错误。",
    example: "exit 7 固定得到 runtime-error，不比较崩溃前输出。",
  },
  {
    id: "wrong-answer",
    context: "concept-result-state-machine",
    question: "wrong-answer 和 runtime-error 有什么区别？",
    alias: "答案错误和运行错误怎么区分",
    answer: "正常退出但 stdout 不符合期望是 wrong-answer；子进程非零退出是 runtime-error。",
    example: "打印错误文本后退出 0 是 stdout-mismatch，SystemExit(7) 是 exit-7。",
  },
  {
    id: "controlled-failure",
    context: "modify-create-controlled-failures",
    question: "怎样主动复现三类判题失败？",
    alias: "如何制造答案错误运行错误和超时",
    answer: "每次只改一个变量：加入多余输出、显式非零退出、加入忙循环，并记录预期、实际与恢复。",
    example: "使用 --timeout 0.05 让忙循环稳定进入 timeout。",
  },
  {
    id: "output-normalization",
    context: "troubleshoot-local-judge",
    question: "输出规范化会忽略哪些差异？",
    alias: "判题器如何处理空格和换行",
    answer: "本课统一换行并忽略行尾空白，但保留行内空格差异，避免宽松 strip 掩盖格式错误。",
    example: "行尾两个空格可忽略，1 双空格 2 与 1 空格 2 仍不同。",
  },
  {
    id: "workspace-boundary",
    context: "troubleshoot-local-judge",
    question: "为什么解法路径不能逃出工作区？",
    alias: "为什么拒绝绝对路径和上级目录",
    answer: "工作区边界让运行资产可移植，并避免运行器意外执行项目外的私人或系统文件。",
    example: "../outside.py 固定得到 solution escapes workspace。",
  },
  {
    id: "rehearsal-v01",
    context: "project-algorithm-rehearsal-v01",
    question: "算法演练运行器 v0.1 留下哪些证据？",
    alias: "第一课项目产出是什么",
    answer: "留下版本化用例、标准输入输出解法、真实子进程运行器、7 项测试和四类判题状态证据。",
    example: "固定快照记录状态与原因，不记录机器相关耗时。",
  },
];

const cards = definitions.map((item, index) => ({
  id: item.id,
  lesson_id: lessonId,
  context_id: item.context,
  question: item.question,
  aliases: [item.alias],
  keywords: [...new Set(`${item.question} ${item.alias}`.replace(/[？?，、]/g, " ").split(/\s+/).filter(Boolean))],
  diagnostic: `先定位“${item.alias}”属于输入、进程、输出还是时间边界。`,
  hints: [
    `查看 #${item.context} 的固定状态或表格。`,
    `再运行 test_judge_runner.py 核对“${item.question.replace("？", "")}”。`,
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
    unknown: ["怎样让鲸鱼参加字符串编译比赛", "云朵超时后应该返回哪种水果"],
  }, null, 2)}\n`,
);
console.log(JSON.stringify({ lesson_id: lessonId, cards: cards.length, questions: cases.length, unknown: 2 }));
