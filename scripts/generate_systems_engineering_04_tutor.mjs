import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonId = "systems-engineering-04";
const title = "非阻塞网络、事件循环与背压";
const path = "learning-paths/systems-engineering/04-nonblocking-network-event-loop-backpressure/";
const contexts = [
  ["overview-nonblocking-io", "overview", "非阻塞网络目标"],
  ["concept-nonblocking-state", "concept", "非阻塞状态机"],
  ["example-poll-interest", "example", "poll 兴趣集合"],
  ["reproduce-nonblocking-v04", "reproduce", "运行 socket 实验"],
  ["concept-partial-io", "concept", "部分发送状态"],
  ["modify-event-loop", "modify", "修改事件循环"],
  ["troubleshoot-event-loop", "troubleshoot", "事件循环排错"],
  ["project-diagnostic-service-v04", "project", "可诊断系统服务 v0.4"],
  ["career-network-backpressure", "career", "网络背压追问"],
].map(([id, type, contextTitle]) => ({ id, type, title: contextTitle, anchor: `#${id}` }));
const definitions = [
  ["nonblocking-purpose","overview-nonblocking-io","非阻塞 socket 解决什么问题？","非阻塞是否消除等待","它把线程内的无限等待变成调用方可处理的返回状态，但不会消除缓冲区容量限制。","写满时 send 返回 EAGAIN。"],
  ["eagain-meaning","concept-nonblocking-state","EAGAIN 表示连接失败了吗？","EAGAIN 应该怎样处理","不是；它表示本次操作现在会阻塞，应保留未发送数据并等待写就绪。","固定输出 backpressure=EAGAIN-observed。"],
  ["pollout-interest","example-poll-interest","什么时候应该订阅 POLLOUT？","为什么不能一直监听可写","只有存在待发数据且发送暂时无法继续时订阅；否则可写 fd 会让循环频繁空转。","对端排空后 poll_after_drain=writable。"],
  ["pollin-meaning","example-poll-interest","POLLIN 保证读到完整消息吗？","读就绪是否等于整条消息到达","不保证；它只表示读取可能取得进度，字节流仍需累计并按协议找边界。","恢复消息触发 reader_event=readable。"],
  ["real-backpressure","reproduce-nonblocking-v04","怎样真实触发网络背压？","不用 Mock 怎样得到 EAGAIN","使用真实 socketpair，不读取对端，并以有界循环发送直到内核返回 EAGAIN。","测试不连接外网，也不固定缓冲区大小。"],
  ["partial-send","concept-partial-io","send 返回正数就代表整条消息完成吗？","部分发送怎样续传","只有返回值等于剩余长度才完成；否则增加 offset，下一次从未发送位置继续。","remaining = buffer.size - offset。"],
  ["stable-snapshot","reproduce-nonblocking-v04","网络实验为什么不记录写入次数？","怎样避免不同机器快照漂移","内核缓冲区大小和调度可变，固定输出只记录 EAGAIN、就绪恢复和消息完整性。","poll_while_full=not-writable。"],
  ["busy-loop","troubleshoot-event-loop","事件循环为什么会空转？","CPU 满载但没有业务流量","常见原因是没有待发数据时仍持续订阅 POLLOUT，fd 一直可写并反复唤醒。","清空待发缓冲后移除写兴趣。"],
  ["socket-close","troubleshoot-event-loop","对端关闭后怎样结束事件处理？","HUP 或 recv 等于 0 怎么办","处理 HUP、ERR 或 recv=0，停止订阅并按所有权释放描述符，不能反复轮询。","示例由 RAII 关闭 socketpair 两端。"],
  ["diagnostic-v04","project-diagnostic-service-v04","可诊断系统服务 v0.4 新增什么？","第四课项目增量是什么","新增真实非阻塞 socket、EAGAIN、poll 读写就绪、排空恢复和 5 项测试。","固定输出 resume_send=pass。"],
];
const cards = definitions.map(([id,context,question,alias,answer,example],index) => ({
  id, lesson_id: lessonId, context_id: context, question, aliases:[alias],
  keywords:[...new Set(`${question} ${alias}`.replace(/[？?，、]/g," ").split(/\s+/).filter(Boolean))],
  diagnostic:`先判断“${alias}”属于非阻塞状态、事件兴趣还是待发数据所有权。`,
  hints:[`查看 #${context} 的状态与固定证据。`,`运行 test_nonblocking_socket.py 核对“${question.replace("？","")}”。`],
  example, answer,
  source:{label:contexts.find((item)=>item.id===context).title,href:`#${context}`},
  updated_at:"2026-07-23", recommended:index<6,
}));
const cases = definitions.flatMap(([id,,question,alias]) => [
  {query:question.replace("？",""),expected_card:id},
  {query:alias,expected_card:id},
]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});
mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样给仙人掌挑花盆","企鹅在南极怎样跳探戈"]},null,2)}\n`);
console.log(JSON.stringify({lesson_id:lessonId,cards:cards.length,questions:cases.length,unknown:2}));
