import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="agent-tool-calling-05",title="有界工具循环、状态预算与显式终止",path="learning-paths/llm-agent/tool-calling-workflow/05-bounded-tool-loop-state-budgets-termination/";
const contexts=[["overview-bounded-tool-loop","overview","有界工具循环"],["concept-application-owned-loop","concept","应用拥有循环"],["concept-monotonic-budgets","concept","单调预算"],["example-cycle-detection","example","循环检测"],["reproduce-bounded-loop-v17","reproduce","运行有界循环"],["modify-loop-budgets","modify","修改循环预算"],["troubleshoot-loop-terminal","troubleshoot","终态排错"],["deepen-retry-vs-loop","deepen","重试与循环"],["project-learning-assistant-v17","project","智能学习助手v0.17"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["app-owned-loop","concept-application-owned-loop","谁拥有工具循环？","模型可以自己决定继续多久吗","应用拥有状态和while；模型只返回下一步事件，不能修改预算。","application-owned。"],
["protocol-terminal","concept-application-owned-loop","模型事件不合法时怎么办？","final还能带tool_calls吗","进入protocol_error，不能猜测或混合执行。","显式终态。"],
["round-budget","concept-monotonic-budgets","轮数预算限制什么？","每轮都没调用工具就不计数吗","限制每次模型往返；无论是否调用工具都消耗round。","max_rounds=3。"],
["call-budget","concept-monotonic-budgets","调用预算何时检查？","五个调用能先执行四个吗","整批执行前检查；将超限就零执行并终止。","max_tool_calls=4。"],
["deadline","concept-monotonic-budgets","deadline 与轮数有什么不同？","轮数少就不会超时吗","deadline限制累计耗时；事件跨界时其中工具也不执行。","100ms虚拟时钟。"],
["cycle-signature","example-cycle-detection","换 call ID 能绕过循环检测吗？","第二次用新ID就不是重复吗","不能；按工具名和规范参数生成语义签名。","第二次执行前停止。"],
["terminal-status","troubleshoot-loop-terminal","needs_input 是失败吗？","追问用户算错误吗","不是；它是主动、可恢复的显式终态，与tool_error区分。","九种终态。"],
["retry-budget","deepen-retry-vs-loop","工具重试要计入什么？","瞬时错误可以无限重试吗","重试也消耗工具调用预算和deadline，写工具还必须幂等。","无界重试禁止。"],
["safe-trace","troubleshoot-loop-terminal","状态机 trace 保存什么？","能打印prompt和工具结果吗","只保存轮次、事件种类、call ID、状态和错误码。","允许列表事件。"],
["assistant-v17","project-learning-assistant-v17","智能学习助手 v0.17 新增什么？","第五课项目做什么","新增应用状态机、轮数/调用/deadline预算、循环检测和显式终态。","下一版固定评估。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先定位“${a}”属于控制权、预算、协议、循环、终态还是日志边界。`,hints:[`查看 #${c}。`,"运行 test_bounded_tool_loop.py 观察零额外执行。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样辨认星座","烘焙面包要多少水"]},null,2)}\n`);
