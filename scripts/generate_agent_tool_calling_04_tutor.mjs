import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="agent-tool-calling-04",title="受控副作用、人工确认与幂等保护",path="learning-paths/llm-agent/tool-calling-workflow/04-controlled-side-effects-confirmation-idempotency/";
const contexts=[["overview-controlled-side-effects","overview","受控副作用"],["concept-confirmation-binding","concept","确认绑定"],["concept-idempotent-write","concept","幂等写入"],["example-default-deny-write","example","默认拒绝写入"],["reproduce-controlled-write-v16","reproduce","运行受控写入"],["modify-confirmation-ttl","modify","修改确认时效"],["troubleshoot-write-gates","troubleshoot","写入门禁排错"],["deepen-atomic-idempotency-boundary","deepen","原子幂等边界"],["project-learning-assistant-v16","project","智能学习助手v0.16"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["confirmation-binding","concept-confirmation-binding","人工确认要绑定什么？","confirmed布尔值够吗","要绑定主体、call ID、工具、参数指纹和到期时间，并单次消费。","短期grant。"],
["model-not-confirm","concept-confirmation-binding","模型可以自己填写确认字段吗？","模型说用户同意能执行吗","不能；确认由应用的人类控制面签发，模型输出仍只是候选。","no model confirmation。"],
["idempotency-replay","concept-idempotent-write","同请求重试为什么不重复写？","网络重试会写两次吗","同主体、工具、key和payload命中已完成记录，返回replayed而不再次写入。","write_count=1。"],
["idempotency-conflict","concept-idempotent-write","同幂等键换参数怎么办？","key相同分钟数不同能覆盖吗","不能；参数指纹不同返回idempotency_conflict。","拒绝冲突。"],
["default-deny","example-default-deny-write","没有确认时发生什么？","缺grant能先写后补吗","返回confirmation_required且writes保持0。","默认拒绝。"],
["confirmation-expiry","modify-confirmation-ttl","确认为什么要过期？","一次同意永久有效吗","短期有效减少旧授权被挪用；过期不自动刷新。","TTL边界。"],
["write-count","troubleshoot-write-gates","怎样证明拒绝路径没有副作用？","只看403或错误码够吗","不够；还要断言store状态与write_count未变化。","零写入证据。"],
["exactly-once-boundary","deepen-atomic-idempotency-boundary","本课实现分布式 exactly-once 了吗？","内存幂等能外推生产吗","不能；生产还需事务、唯一约束、outbox或外部幂等协议。","边界声明。"],
["write-logs","troubleshoot-write-gates","写工具日志能记grant吗？","幂等键可打印吗","默认都不记录，只记call ID、工具名、状态和错误码。","敏感控制值脱敏。"],
["assistant-v16","project-learning-assistant-v16","智能学习助手 v0.16 新增什么？","第四课项目做什么","新增写风险、授权、绑定确认、单次短期grant与幂等replay/冲突。","下一版有界循环。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先定位“${a}”属于授权、确认、幂等、零写入证据还是生产原子性边界。`,hints:[`查看 #${c}。`,"运行 test_controlled_write.py 核对write_count。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["海水为什么是咸的","怎样练习毛笔字"]},null,2)}\n`);
