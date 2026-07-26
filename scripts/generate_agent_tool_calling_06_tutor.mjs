import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="agent-tool-calling-06",title="固定对抗评估、预算指标与回归交付",path="learning-paths/llm-agent/tool-calling-workflow/06-fixed-adversarial-evaluation-regression-delivery/";
const contexts=[["overview-tool-workflow-eval","overview","工作流评估"],["concept-frozen-eval-protocol","concept","冻结评估协议"],["concept-separated-metrics","concept","分组指标"],["example-adversarial-cases","example","对抗案例"],["reproduce-tool-eval-v18","reproduce","运行固定评估"],["modify-eval-case","modify","增加评估案例"],["troubleshoot-eval-gate","troubleshoot","评估门禁排错"],["deepen-eval-boundary","deepen","评估边界"],["project-learning-assistant-v18","project","智能学习助手v0.18"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["protocol-fingerprint","concept-frozen-eval-protocol","评估协议为什么要指纹？","案例顺序变化会影响吗","规范manifest冻结题目、期望和限制；排序不变，内容变化产生新指纹。","SHA-256。"],
["protocol-compatibility","concept-frozen-eval-protocol","两个报告什么时候可比较？","不同案例数能比较分数吗","只有协议指纹和案例数相同才可比较。","incompatible_protocol。"],
["separate-denominators","concept-separated-metrics","为什么指标要分组？","正常高分能抵消安全失败吗","不能；正常、安全和预算使用独立固定分母。","2/3/3。"],
["unsafe-zero","concept-separated-metrics","不安全执行允许几次？","平均分高能容忍一次危险handler吗","不能，unsafe executions必须为0，是硬门禁。","zero unsafe。"],
["adversarial-proof","example-adversarial-cases","怎样证明安全拒绝真的安全？","只看最终回复说拒绝够吗","不够；还要核对工具与handler计数，危险handler必须为0。","逐例证据。"],
["add-case","modify-eval-case","新增案例后还能用旧基线吗？","加确认过期例继续比旧3/3吗","不能；新manifest产生新指纹，要建立同协议baseline。","新协议。"],
["gate-failure","troubleshoot-eval-gate","incompatible_protocol 是退化吗？","指纹不同说明代码变差吗","不是；先说明不可比，不能解释为质量变化。","分开不可比与退化。"],
["eight-case-boundary","deepen-eval-boundary","8例满分代表生产质量吗？","scripted model满分能上线吗","不能；未覆盖真实provider、外部副作用、延迟成本和漂移。","诚实边界。"],
["eval-logs","troubleshoot-eval-gate","评估报告能保存prompt吗？","为了复盘打印全部参数行吗","公开报告只保存case ID、状态与计数；敏感正文不进入。","脱敏证据。"],
["assistant-v18","project-learning-assistant-v18","智能学习助手 v0.18 新增什么？","第六课项目做什么","新增冻结案例、协议指纹、分组指标、零危险执行和回归门禁。","整组48测试。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先定位“${a}”属于协议、分母、安全硬门禁、逐例证据还是外推边界。`,hints:[`查看 #${c}。`,"运行 test_tool_workflow_eval.py 查看门禁原因。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样种植番茄","古典音乐有哪些时期"]},null,2)}\n`);
