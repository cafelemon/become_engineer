import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="agent-engineering-01",title="SQLite 运行状态、事件日志与原子 checkpoint",path="learning-paths/llm-agent/agent-engineering/01-sqlite-run-state-event-log-atomic-checkpoint/";
const contexts=[["overview-durable-run-state","overview","持久运行状态"],["concept-snapshot-event-log","concept","快照与事件"],["concept-version-event-id","concept","版本与事件身份"],["example-atomic-checkpoint","example","原子checkpoint"],["reproduce-durable-state-v19","reproduce","运行持久状态"],["modify-transition-graph","modify","修改状态图"],["troubleshoot-run-state","troubleshoot","运行状态排错"],["deepen-state-not-reasoning","deepen","状态与思维边界"],["project-learning-assistant-v19","project","智能学习助手v0.19"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["snapshot-event","concept-snapshot-event-log","snapshot 和 event log 有什么区别？","为什么要保存两张表","snapshot回答当前状态，event按序解释状态怎样到来；同事务保持一致。","现在与历史。"],
["atomic-transition","concept-snapshot-event-log","事件和状态为何必须原子提交？","先写事件后崩溃怎么办","两条写入在同一事务中；注入失败后同时回滚。","BEGIN IMMEDIATE。"],
["expected-version","concept-version-event-id","expected version 解决什么？","两个worker同时写会覆盖吗","只有匹配当前version者更新，旧快照得到stale_version。","乐观并发。"],
["event-id","concept-version-event-id","event ID 解决什么？","超时重试会多一条事件吗","同ID同payload返回replay；同ID改payload冲突。","幂等身份。"],
["checkpoint-allowlist","example-atomic-checkpoint","checkpoint 能保存哪些字段？","可以保存完整prompt吗","只允许next step、工具状态和有界已完成step ID。","小型显式状态。"],
["transition-graph","modify-transition-graph","终态还能继续转移吗？","completed后能恢复running吗","不能；允许状态图明确拒绝终态后续写入。","状态机。"],
["storage-failure","troubleshoot-run-state","storage_failure 后怎样检查？","事件写了一半吗","重新读取snapshot与事件数；事务应保持原版本和原事件数。","回滚证据。"],
["no-reasoning","deepen-state-not-reasoning","为什么不保存 chain of thought？","恢复需要模型推理全文吗","不需要；只保存可验证业务状态，降低隐私、注入和访问风险。","显式checkpoint。"],
["state-logs","troubleshoot-run-state","事件日志能保存工具原文吗？","为了排错记录prompt行吗","默认只存事件类型、状态、序号和指纹，不存敏感正文。","最小事件。"],
["assistant-v19","project-learning-assistant-v19","智能学习助手 v0.19 新增什么？","Agent工程第一课做什么","新增SQLite run、事件日志、版本、幂等event和原子checkpoint。","下一版记忆上下文。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先定位“${a}”属于快照、事件、事务、并发、幂等、状态图还是数据最小化。`,hints:[`查看 #${c}。`,"运行 test_durable_run_state.py 观察版本和事件数。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样养护多肉植物","月亮为什么有圆缺"]},null,2)}\n`);
