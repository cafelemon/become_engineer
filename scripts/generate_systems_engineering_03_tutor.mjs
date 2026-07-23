import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonId = "systems-engineering-03";
const title = "条件变量、有界队列与关闭协议";
const path = "learning-paths/systems-engineering/03-condition-variables-bounded-queue-shutdown/";
const contexts = [
  ["overview-bounded-queue", "overview", "有界队列目标"],
  ["concept-queue-state", "concept", "队列状态机"],
  ["example-condition-predicates", "example", "条件变量谓词"],
  ["reproduce-bounded-queue-v03", "reproduce", "运行背压实验"],
  ["concept-close-invariant", "concept", "关闭不变量"],
  ["modify-queue-shutdown", "modify", "破坏关闭协议"],
  ["troubleshoot-bounded-queue", "troubleshoot", "队列排错"],
  ["project-diagnostic-service-v03", "project", "可诊断系统服务 v0.3"],
  ["career-queue-shutdown-review", "career", "队列关闭追问"],
].map(([id, type, contextTitle]) => ({ id, type, title: contextTitle, anchor: `#${id}` }));
const definitions = [
  ["bounded-purpose","overview-bounded-queue","有界队列为什么比无限队列安全？","容量上限解决什么过载问题","容量把持续过载变成可观察等待，避免任务无限占用内存。","容量 1 时第二次 push 确定性阻塞。"],
  ["drain-close","concept-queue-state","排空关闭是什么意思？","close 后是否立即清空任务","关闭先拒绝新任务，已接受任务继续被 pop；队列空后消费者才结束。","push_after_close=rejected 且 accepted=processed。"],
  ["wait-predicate","example-condition-predicates","条件变量为什么必须带谓词？","notify 一次是否等于条件成立","虚假唤醒和通知时序都可能发生，线程必须持锁重新检查共享事实。","生产者等待 space-or-closed，消费者等待 item-or-closed。"],
  ["notify-both","example-condition-predicates","close 为什么唤醒两组等待者？","只 notify 消费者够不够","满队列生产者需要醒来拒绝提交，空队列消费者需要醒来结束，因此两组都要通知。","close 对 not_empty 与 not_full 执行 notify_all。"],
  ["deterministic-pressure","reproduce-bounded-queue-v03","怎样不靠 sleep 证明生产者被阻塞？","背压测试如何避免调度运气","测试等待 waiting_producers 状态变为 1 后才启动消费者。","固定输出 backpressure=observed waiting_producers=1。"],
  ["accept-boundary","concept-close-invariant","任务何时算被服务接受？","push 返回 true 后谁负责","push 成功后服务承担处理或明确交接责任；内存队列关闭时必须排空。","accepted = processed + queued。"],
  ["close-reject","concept-close-invariant","关闭后 push 应该返回什么？","停止接收时能否继续入队","应返回 false，调用者据此停止提交或转交，不能静默接受后丢弃。","push_after_close=rejected。"],
  ["spurious-wakeup","troubleshoot-bounded-queue","虚假唤醒会造成什么问题？","if 加裸 wait 为什么危险","醒来时队列可能仍空或仍满，若不重查谓词可能越界访问或超过容量。","使用 condition_variable::wait(lock, predicate)。"],
  ["capacity-limit","troubleshoot-bounded-queue","增大容量能消除背压吗？","队列更大是否解决下游慢","不能；若下游长期更慢，大容量只延后填满并增加延迟与内存。","容量要结合等待和处理证据调整。"],
  ["diagnostic-v03","project-diagnostic-service-v03","可诊断系统服务 v0.3 新增什么？","第三课项目增量是什么","新增 C++20 有界队列、确定性生产者等待、FIFO 排空、关闭拒绝和 5 项测试。","固定输出 order=1,2,3 与 accepted-equals-processed。"],
];
const cards=definitions.map(([id,context,question,alias,answer,example],index)=>({id,lesson_id:lessonId,context_id:context,question,aliases:[alias],keywords:[...new Set(`${question} ${alias}`.replace(/[？?，、]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${alias}”涉及容量、等待谓词还是关闭状态。`,hints:[`查看 #${context} 的状态机或不变量。`,`再运行 test_bounded_queue.py 核对“${question.replace("？","")}”。`],example,answer,source:{label:contexts.find((item)=>item.id===context).title,href:`#${context}`},updated_at:"2026-07-23",recommended:index<6}));
const cases=definitions.flatMap(([id,,question,alias])=>[{query:question.replace("？",""),expected_card:id},{query:alias,expected_card:id}]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true}); mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样给星星设置队列容量","企鹅虚假唤醒后会唱歌吗"]},null,2)}\n`);
console.log(JSON.stringify({lesson_id:lessonId,cards:cards.length,questions:cases.length,unknown:2}));
