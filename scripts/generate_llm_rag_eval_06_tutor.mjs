import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="llm-rag-eval-06",title="固定评估集、检索指标、引用质量与回归门禁",path="learning-paths/llm-agent/rag-eval/06-fixed-eval-retrieval-citation-regression-gates/";
const contexts=[["overview-rag-evaluation","overview","RAG评估"],["concept-fixed-eval-set","concept","固定评估集"],["concept-rag-metrics","concept","RAG指标"],["example-regression-gate","example","回归门禁"],["reproduce-eval-v12","reproduce","运行固定评估"],["modify-eval-case","modify","修改评估案例"],["troubleshoot-evaluation","troubleshoot","评估排错"],["deepen-metric-limits","deepen","指标边界"],["project-learning-assistant-v12","project","智能学习助手v0.12"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["eval-fingerprint","concept-fixed-eval-set","评估集为什么要有 fingerprint？","案例重排算新版本吗","规范排序后哈希冻结问题和标注；重排不变，内容变化产生新协议。","同协议才可比较。"],
["recall-at-k","concept-rag-metrics","Recall@k 衡量什么？","前k召回怎么算","每个answerable案例命中的相关项比例，再对案例平均。","多相关项可部分命中。"],
["mrr","concept-rag-metrics","MRR 衡量什么？","第一个相关结果位置怎么计分","取首个相关结果名次倒数，再对answerable案例平均。","第4名贡献0.25。"],
["citation-validity","concept-rag-metrics","引用有效率的分母是什么？","没有引用能算满分吗","分母是所有已发出citation；没有citation时指标未定义并拒绝。","不是空集满分。"],
["abstention-accuracy","concept-rag-metrics","拒答准确率怎么计算？","只看未知问题吗","本课对全部案例检查abstained是否恰好等于不可回答，覆盖过度与不足拒答。","分母为全部案例。"],
["comparable-reports","example-regression-gate","哪些报告可以直接比较？","Top-k不同能比吗","必须同数据fingerprint、Top-k和案例数，否则返回incomparable_reports。","冻结协议。"],
["safety-gate","example-regression-gate","为什么检索变好仍可能阻止交付？","Recall升了引用错了能发吗","不能；引用有效率和拒答准确率必须为1，安全退化独立阻止。","多指标门禁。"],
["label-leakage","troubleshoot-evaluation","结果不好可以改相关标签吗？","候选出来后调整试卷吗","不能为候选改标签；标注变化形成新版本并独立复核。","避免评估污染。"],
["metric-limits","deepen-metric-limits","四个案例满分代表生产可用吗？","离线满分就能上线吗","不能；没覆盖真实分布、延迟成本、时效、完整性和对抗鲁棒性。","门禁是必要非充分。"],
["assistant-v12","project-learning-assistant-v12","智能学习助手 v0.12 新增什么？","RAG第六课项目做什么","新增固定评估集、四项指标、数据指纹、基线比较和可解释回归门禁。","RAG组级验收。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先定位“${a}”属于数据版本、指标分母、报告可比性、门禁还是指标盲区。`,hints:[`查看 #${c}。`,"运行 test_rag_evaluation.py 手算固定案例。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["如何修理自行车链条","海水为什么是咸的"]},null,2)}\n`);
