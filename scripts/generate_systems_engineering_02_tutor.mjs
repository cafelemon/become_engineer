import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonId = "systems-engineering-02";
const title = "信号、进程监督与优雅停止";
const path = "learning-paths/systems-engineering/02-signals-process-supervision-graceful-shutdown/";
const contexts = [
  ["overview-signal-supervision", "overview", "信号监督目标"],
  ["concept-async-signal-boundary", "concept", "异步信号边界"],
  ["example-self-pipe-sequence", "example", "self-pipe 时序"],
  ["reproduce-signal-supervisor-v02", "reproduce", "运行真实信号"],
  ["concept-supervision-states", "concept", "监督状态"],
  ["modify-signal-failures", "modify", "制造监督失败"],
  ["troubleshoot-signal-supervisor", "troubleshoot", "停止排错"],
  ["project-diagnostic-service-v02", "project", "可诊断系统服务 v0.2"],
  ["career-graceful-shutdown-review", "career", "优雅停止追问"],
].map(([id, type, contextTitle]) => ({ id, type, title: contextTitle, anchor: `#${id}` }));

const definitions = [
  ["handler-boundary", "overview-signal-supervision", "信号处理器为什么只负责通知？", "能否在 handler 里直接清理业务", "信号可能打断任意代码，复杂库调用可能死锁；处理器应只做 signal-safe 通知，让主循环清理。", "固定输出 signal_handler=notification-only。"],
  ["self-pipe", "concept-async-signal-boundary", "self-pipe 解决什么问题？", "怎样把异步信号交给主循环", "处理器向 pipe 写标记，阻塞在普通 read 或事件循环中的代码被唤醒并在正常上下文处理状态。", "父子进程各使用自己的 self-pipe。"],
  ["errno-save", "concept-async-signal-boundary", "信号处理器为什么保存 errno？", "handler 会不会覆盖被打断代码的错误", "处理器调用 write 可能改变 errno，保存并恢复可避免污染被打断控制流的诊断状态。", "进入时 saved_errno，退出前恢复。"],
  ["ready-handshake", "example-self-pipe-sequence", "父进程为什么等待 ready marker？", "立即 kill worker 有什么竞态", "ready 证明子进程已安装处理器；否则 SIGTERM 可能按默认动作直接终止 worker。", "worker 安装 sigaction 后才写 ready。"],
  ["real-signal", "reproduce-signal-supervisor-v02", "测试是否使用真实 SIGTERM？", "监督器是不是 Mock", "是。程序调用 fork、kill、sigaction、pipe 和 waitpid，外层测试只负责编译、运行与超时。", "父进程向自身和 fork 返回的 worker PID 发 SIGTERM。"],
  ["reap", "concept-supervision-states", "为什么退出后还要 waitpid？", "worker 结束是不是自动回收", "父进程必须读取子进程退出状态才能回收资源并避免僵尸，同时保留失败证据。", "固定输出 worker_reaped=yes。"],
  ["exit-mapping", "concept-supervision-states", "监督器怎样区分三类结果？", "退出 0 1 2 分别代表什么", "0 表示正常停止，1 表示已回收但 worker 失败，2 表示参数或监督基础设施错误。", "--child-exit 7 让父进程返回 1。"],
  ["signal-safe", "troubleshoot-signal-supervisor", "哪些操作不该放进信号处理器？", "handler 里能否 iostream malloc waitpid", "本课不在处理器中使用 iostream、分配、锁、waitpid 或业务关闭，只写预建 pipe 和 sig_atomic_t。", "复杂清理回到主循环。"],
  ["notification-coalescing", "troubleshoot-signal-supervisor", "self-pipe 是否精确记录多次信号？", "连续 SIGTERM 会不会丢计数", "本课协议只表示有停止事件，不承诺精确计数或顺序；需要精确语义时必须另设队列协议。", "单个 sig_atomic_t 不能外推为信号日志。"],
  ["diagnostic-v02", "project-diagnostic-service-v02", "可诊断系统服务 v0.2 新增什么？", "系统工程第二课项目增量是什么", "新增父子 self-pipe、ready 握手、真实 SIGTERM、退出码传播、waitpid 回收和 5 项测试。", "尚未实现 TERM 到 KILL 的宽限期升级。"],
];

const cards = definitions.map(([id, context, question, alias, answer, example], index) => ({
  id, lesson_id: lessonId, context_id: context, question, aliases: [alias],
  keywords: [...new Set(`${question} ${alias}`.replace(/[？?，、]/g, " ").split(/\s+/).filter(Boolean))],
  diagnostic: `先判断“${alias}”位于信号边界、主循环还是回收阶段。`,
  hints: [`查看 #${context} 的时序或状态表。`, `再运行 test_signal_supervisor.py 核对“${question.replace("？", "")}”。`],
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
writeFileSync(resolve(root, `tests/tutor/${lessonId}-search.json`), `${JSON.stringify({ lesson_id: lessonId, cases, unknown: ["怎样向月亮发送优雅停止", "鲸鱼进程退出后会变成云吗"], }, null, 2)}\n`);
console.log(JSON.stringify({ lesson_id: lessonId, cards: cards.length, questions: cases.length, unknown: 2 }));
