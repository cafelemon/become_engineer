import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="agent-tool-calling-03",title="多工具调用、call_id 关联与部分失败隔离",path="learning-paths/llm-agent/tool-calling-workflow/03-multiple-calls-call-id-correlation-partial-failure/";
const contexts=[["overview-multi-call-correlation","overview","多调用关联"],["concept-call-identity","concept","调用身份"],["concept-bounded-partial-failure","concept","有界部分失败"],["example-out-of-order-restore","example","乱序恢复"],["reproduce-multi-call-v15","reproduce","运行多调用"],["modify-batch-budget","modify","修改批次预算"],["troubleshoot-output-assembly","troubleshoot","结果组装排错"],["deepen-sequential-vs-parallel","deepen","顺序与并发边界"],["project-learning-assistant-v15","project","智能学习助手v0.15"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["call-id","concept-call-identity","call_id 有什么作用？","为什么不能按数组位置配对","它是调用身份；输出必须按唯一call_id回到原调用，不能猜位置或只看工具名。","call_status。"],
["exactly-once","concept-call-identity","怎样保证每次调用恰好一个输出？","结果数量一样就够吗","核对输入输出ID集合、输出ID唯一和工具名一致；长度相同仍可能错绑。","集合不变量。"],
["partial-failure","concept-bounded-partial-failure","一个工具失败要丢掉整批结果吗？","unknown_tool会让批次中止吗","已合法批次逐项生成envelope；局部错误保留，其他成功不丢失。","2成功1错误。"],
["batch-budget","concept-bounded-partial-failure","为什么限制单轮最多四个调用？","prompt里提醒少调用就够吗","预算必须由应用强制；超限在handler前整体拒绝。","MAX_CALLS=4。"],
["out-of-order","example-out-of-order-restore","结果乱序怎样恢复？","逆序outputs怎么办","先按call_id建表并校验，再按原calls顺序取回。","逆序恢复。"],
["missing-output","troubleshoot-output-assembly","missing_output 表示什么？","某个handler没返回怎么办","原调用ID在输出集合中缺失，不能伪造默认成功或猜测。","协议错误。"],
["name-mismatch","troubleshoot-output-assembly","为什么还要核对工具名？","call_id对了就行吗","不够；同ID绑定另一工具的结果同样是协议污染。","tool_name_mismatch。"],
["multi-not-parallel","deepen-sequential-vs-parallel","多调用等于并发吗？","支持乱序就是异步吗","不等于；本课顺序执行，乱序只测试关联独立于到达次序。","no parallel claim。"],
["safe-logs","troubleshoot-output-assembly","多调用日志记录什么？","能保存所有参数结果吗","只记call ID、工具名、状态和错误码，不保存参数或结果正文。","允许字段。"],
["assistant-v15","project-learning-assistant-v15","智能学习助手 v0.15 新增什么？","第三课项目做什么","新增批次预算、唯一call ID、结果assembler、稳定顺序和部分失败隔离。","下一版受控副作用。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”是批次、身份、集合、顺序、局部错误还是并发边界问题。`,hints:[`查看 #${c}。`,"运行 test_multi_call_batch.py 观察确定性错误。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样给月季修枝","地球为何有四季"]},null,2)}\n`);
