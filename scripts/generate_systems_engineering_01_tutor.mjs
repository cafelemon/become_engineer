import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonId = "systems-engineering-01";
const title = "文件描述符、部分 I/O 与所有权";
const path = "learning-paths/systems-engineering/01-file-descriptors-partial-io-ownership/";
const contexts = [
  ["overview-fd-partial-io", "overview", "部分 I/O 目标"],
  ["concept-fd-ownership-layers", "concept", "描述符所有权层次"],
  ["example-write-all-read-eof", "example", "完整读写循环"],
  ["reproduce-fd-pipeline-v01", "reproduce", "运行真实 pipe"],
  ["concept-eintr-eof-errors", "concept", "返回值状态"],
  ["modify-fd-failure-paths", "modify", "主动破坏 I/O"],
  ["troubleshoot-fd-pipeline", "troubleshoot", "描述符排错"],
  ["project-diagnostic-service-v01", "project", "可诊断系统服务 v0.1"],
  ["career-fd-ownership-review", "career", "描述符追问"],
].map(([id, type, contextTitle]) => ({ id, type, title: contextTitle, anchor: `#${id}` }));

const definitions = [
  ["partial-io", "overview-fd-partial-io", "为什么一次 write 不等于完整消息？", "短写后应该怎么处理", "write 返回的是本次实际写入字节数，可能小于请求量；循环必须按返回值推进到全部完成。", "11 字节按最多 3 字节请求，需要 4 次写。"],
  ["fd-layers", "concept-fd-ownership-layers", "描述符所有权有哪三层？", "int fd 内核对象和 C++ 对象是什么关系", "整数位于进程描述符表，指向内核打开对象；C++ UniqueFd 负责唯一关闭责任。", "移动 UniqueFd 改变所有者，不复制内核资源。"],
  ["unique-fd", "concept-fd-ownership-layers", "UniqueFd 为什么禁止复制？", "怎样避免两个对象重复 close", "复制会制造两个关闭责任人；删除复制并只允许移动，使关闭责任始终唯一。", "移动后源对象保存 -1。"],
  ["write-progress", "example-write-all-read-eof", "写循环为什么按 written 推进？", "offset 能不能加 request", "只有系统调用返回的 written 字节已经交付，按请求量推进会在短写时跳过数据。", "offset += static_cast<size_t>(written)。"],
  ["pipe-eof", "example-write-all-read-eof", "pipe 读端什么时候得到 EOF？", "为什么不关闭写端会一直等待", "所有写端描述符关闭且缓冲数据读尽后，read 才返回 0 表示 EOF。", "moved_write.reset() 先关闭最后写端。"],
  ["real-pipe", "reproduce-fd-pipeline-v01", "示例是否真的调用 POSIX pipe？", "fd pipeline 是不是 Mock", "是。测试编译并运行调用 pipe、read、write、close 和 fcntl 的 C++20 程序。", "编译产物放在临时目录。"],
  ["read-states", "concept-eintr-eof-errors", "read 的正数零和负一分别表示什么？", "怎样区分数据 EOF EINTR 和错误", "正数是收到字节，0 是 EOF，-1 且 EINTR 可重试，其他 -1 是错误。", "不能把暂时没数据当成 EOF。"],
  ["fd-reuse", "troubleshoot-fd-pipeline", "为什么关闭后不能长期依赖 fd 数值？", "描述符数字会不会被复用", "close 后该整数槽位可被新资源复用，数值相同不代表还是原内核对象。", "单一所有权并在关闭后立即置 -1。"],
  ["platform-boundary", "troubleshoot-fd-pipeline", "POSIX 描述符是不是标准 C++？", "这套代码能否直接用于 Windows", "不是。RAII 和移动属于 C++，pipe/read/write/close/fcntl 属于 POSIX；Windows 原生句柄需要另一套适配。", "本课目标平台是 macOS 与 Linux。"],
  ["diagnostic-v01", "project-diagnostic-service-v01", "可诊断系统服务 v0.1 交付什么？", "系统工程第一课项目产出是什么", "交付真实 pipe、完整读写循环、移动专属 UniqueFd、关闭证据和 4 项编译运行测试。", "固定输出包含 roundtrip=pass 与 all_descriptors=closed。"],
];

const cards = definitions.map(([id, context, question, alias, answer, example], index) => ({
  id, lesson_id: lessonId, context_id: context, question, aliases: [alias],
  keywords: [...new Set(`${question} ${alias}`.replace(/[？?，、]/g, " ").split(/\s+/).filter(Boolean))],
  diagnostic: `先判断“${alias}”属于进度、EOF、所有权还是平台边界。`,
  hints: [`查看 #${context} 的图或返回值表。`, `再运行 test_fd_pipeline.py 核对“${question.replace("？", "")}”。`],
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
writeFileSync(resolve(root, `tests/tutor/${lessonId}-search.json`), `${JSON.stringify({ lesson_id: lessonId, cases, unknown: ["怎样给彩虹分配文件描述符", "海豚短写后会不会变成树"], }, null, 2)}\n`);
console.log(JSON.stringify({ lesson_id: lessonId, cards: cards.length, questions: cases.length, unknown: 2 }));
