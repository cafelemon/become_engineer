import {mkdirSync,writeFileSync} from "node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lessonId="systems-engineering-06",title="故障注入、资源泄漏与恢复验收",path="learning-paths/systems-engineering/06-fault-injection-resource-leaks-recovery-acceptance/";
const contexts=[["overview-recovery-acceptance","overview","恢复验收目标"],["concept-fault-plan","concept","故障计划"],["example-resource-baseline","example","资源基线"],["reproduce-recovery-v06","reproduce","运行恢复实验"],["concept-recovery-invariants","concept","恢复不变量"],["modify-recovery-plan","modify","破坏恢复"],["troubleshoot-recovery","troubleshoot","恢复排错"],["project-diagnostic-service-v06","project","可诊断系统服务 v0.6"],["career-recovery-review","career","泄漏恢复追问"]].map(([id,type,t])=>({id,type,title:t,anchor:`#${id}`}));
const defs=[
["recovery-proof","overview-recovery-acceptance","怎样证明服务真的恢复？","恢复日志够不够","不够；要同时验证业务重新取得进度和拥有的资源回到可接受基线。","新 socket 消息完整到达且旧 fd 已关闭。"],
["fault-plan","concept-fault-plan","故障注入计划要写什么？","故障实验四要素","写清故障点、预期错误、恢复动作和恢复后断言，并设置作用域与停止条件。","peer close 到 EPIPE，再重建连接。"],
["fd-detection","example-resource-baseline","怎样确认已知 fd 仍然打开？","fcntl 怎样查 fd","对本进程明确拥有的 fd 调用 fcntl F_GETFD；恢复后 EBADF 表示它已无效。","不扫描或关闭未知描述符。"],
["resource-scope","example-resource-baseline","为什么不能扫描后关闭所有陌生 fd？","资源清理怎样避免误伤","测试框架和其他线程也可能持有 fd；只能释放所有权明确属于当前组件的资源。","本课只检查自己创建的 pipe fd。"],
["child-reap","reproduce-recovery-v06","子进程失败后为什么还要 waitpid？","记录 exit 7 就够了吗","不够；waitpid 同时取得状态并回收子进程，避免僵尸进程占用表项。","child_fault=exit-7 且 child_recovery=reaped。"],
["epipe-recovery","reproduce-recovery-v06","EPIPE 后怎样恢复传输？","能否继续重试旧 socket","应停止写旧 fd、按策略关闭并有界重建连接，再用探针验证进度。","transport_recovery=reconnected。"],
["temporary-cleanup","concept-recovery-invariants","临时文件恢复验收检查什么？","unlink 之前还要做什么","完成写入后关闭 fd，再 unlink 路径，并确认路径不存在。","temporary_artifact=removed。"],
["retry-bound","troubleshoot-recovery","为什么恢复重试必须有上限？","无限重连有什么风险","永久故障时无限重试会消耗 CPU、连接和下游容量，放大原始故障。","达到边界后进入失败安全状态。"],
["service-resource","concept-recovery-invariants","恢复为什么分资源层和服务层？","资源关闭和业务恢复哪个重要","两者都重要：只恢复业务会累积泄漏，只清资源却无进度则服务仍不可用。","resource_baseline=restored 之外还验证消息。"],
["diagnostic-v06","project-diagnostic-service-v06","可诊断系统服务 v0.6 新增什么？","第六课项目增量是什么","新增 fd 泄漏、子进程失败、EPIPE、临时文件四组真实故障和恢复验收。","5 项测试构成六课项目收口。"]
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”处于注入、检测、恢复还是验收阶段。`,hints:[`查看 #${c} 的证据链。`,`运行 test_recovery_lab.py 核对“${q.replace("？","")}”。`],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-23",recommended:i<6}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样烤一块松软面包","长颈鹿睡觉时会做梦吗"]},null,2)}\n`);
console.log(JSON.stringify({lesson_id:lessonId,cards:10,questions:20,unknown:2}));
