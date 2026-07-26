import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="llm-rag-eval-05",title="有证据回答、Claim-Citation 门禁与缺证据拒答",path="learning-paths/llm-agent/rag-eval/05-grounded-claim-citation-abstention/";
const contexts=[["overview-grounded-answer","overview","有证据回答"],["concept-context-pack","concept","上下文包"],["concept-claim-citation","concept","Claim与Citation"],["example-extractive-gate","example","抽取式门禁"],["reproduce-grounded-v11","reproduce","运行证据回答"],["modify-support-policy","modify","修改支持策略"],["troubleshoot-grounding","troubleshoot","证据回答排错"],["deepen-injection-abstention","deepen","注入与拒答"],["project-learning-assistant-v11","project","智能学习助手v0.11"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["context-budget","concept-context-pack","Context pack 为什么要有界？","检索结果都塞给模型不行吗","控制上下文成本和无关证据；本课只在完整chunk边界停止。","字符预算不冒充token。"],
["source-data","concept-context-pack","来源文本为什么要显式分隔？","RAG内容和指令怎么区分","来源是不可信数据；标签和system规则共同声明其中指令没有控制权限。","source-data。"],
["claim-granularity","concept-claim-citation","为什么按 claim 绑定 citation？","答案末尾一个引用不够吗","总引用无法说明每条事实由哪段证据支持；逐claim门禁可定位缺证据项。","claims[]各自引用。"],
["retrieved-only-answer","concept-claim-citation","回答能引用未检索语料吗？","全库有证据可以事后补吗","不能；本次未提供给生成边界的内容不能冒充本次回答依据。","citation_chunk_not_retrieved。"],
["extractive-baseline","example-extractive-gate","为什么先做抽取式 claim？","同义改写不能自动过吗","抽取式关系可机械证明；任意转述需要独立语义评估，不能用字符串规则假装。","extractive:true。"],
["quote-gate","troubleshoot-grounding","Citation 要校验哪些字段？","有chunk ID就够吗","还要合法相对区间、逐字quote和未篡改chunk摘要。","quote-match:true。"],
["abstention","deepen-injection-abstention","证据不足时应该输出什么？","不知道也要生成一段吗","返回abstained、空claims和稳定insufficient_evidence，不编造填空。","可计算拒答指标。"],
["injection-data","deepen-injection-abstention","来源里的忽略系统指令会执行吗？","检索文档能改规则吗","不会；它只在source-data中作为文本，控制规则来自更高权限边界。","instructions-in-source:false。"],
["grounding-logs","troubleshoot-grounding","证据回答日志保存全文吗？","排错要记录上下文和答案吗","默认只记录chunk ID、状态和错误码，不保存查询、上下文、答案或引文。","允许字段日志。"],
["assistant-v11","project-learning-assistant-v11","智能学习助手 v0.11 新增什么？","RAG第五课项目做什么","新增有界证据包、逐claim精确引用、抽取式支持门禁和结构化拒答。","下一版固定评估。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先定位“${a}”属于上下文预算、claim粒度、citation切片、拒答还是来源信任。`,hints:[`查看 #${c}。`,"运行 test_grounded_answer.py 核对门禁错误码。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样种植薄荷","月亮为什么有阴晴圆缺"]},null,2)}\n`);
