import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="llm-use-02",title="Prompt 角色、版本、参数与上下文预算",path="learning-paths/llm-agent/model-use/02-prompt-roles-version-parameters-context-budget/";
const contexts=[["overview-prompt-snapshot","overview","Prompt快照"],["concept-prompt-as-config","concept","Prompt配置"],["concept-role-budget","concept","角色与预算"],["example-canonical-fingerprint","example","规范指纹"],["reproduce-prompt-v02","reproduce","运行Prompt实验"],["modify-prompt-contract","modify","修改Prompt契约"],["troubleshoot-prompt-contract","troubleshoot","Prompt排错"],["deepen-prompt-limits","deepen","Prompt边界"],["project-learning-assistant-v02","project","智能学习助手v0.2"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["prompt-config","concept-prompt-as-config","为什么 Prompt 应当版本化？","Prompt不就是字符串吗","它与代码配置一样影响行为；ID和版本让变更可定位，测试再证明兼容性。","v0.2版本2.0.0。"],
["message-role","concept-role-budget","用户说忽略规则会变成 system 吗？","用户能否覆盖system role","不能；role由可信请求结构决定，用户文本始终留在user消息。","system_unchanged:true。"],
["input-budget","concept-role-budget","为什么在调用前检查上下文预算？","超长Prompt何时拒绝","可避免无效调用、费用和隐式截断；超限应明确失败或显式分段。","240字节教学预算。"],
["unit-boundary","concept-role-budget","UTF-8 字节能当 token 吗？","input_units是不是provider tokens","不能；它只是离线稳定估算，真实计费和上下文以对应模型计量为准。","固定输出明确not-provider-tokens。"],
["prompt-fingerprint","example-canonical-fingerprint","Prompt 指纹覆盖哪些字段？","hash只算用户问题够吗","应覆盖ID、版本、模型、角色内容、生成参数与输出上限。","规范JSON后SHA-256。"],
["canonical-json","example-canonical-fingerprint","为什么指纹前要规范序列化？","JSON key顺序影响hash吗","语义相同但字节顺序不同会改变哈希；固定排序和分隔符才能稳定比较。","sort_keys与固定separators。"],
["audit-redaction","troubleshoot-prompt-contract","Prompt 审计记录能保存什么？","是否记录完整Prompt","默认保存ID、版本、模型、角色、计量、参数和指纹，不保存原始内容。","audit_record排除messages。"],
["hash-secrecy","deepen-prompt-limits","Prompt 哈希能保证原文保密吗？","有SHA-256就无法猜原文吗","不能；短或可枚举文本可能被猜测，哈希是比较/完整性辅助而非保密方案。","课程明确不作保密承诺。"],
["temperature-zero","deepen-prompt-limits","temperature 0 能保证永远相同吗？","零温度是否绝对确定","不能保证跨模型更新、服务实现或时间绝对一致；快照只证明应用配置。","还需provider版本与结果证据。"],
["assistant-v02","project-learning-assistant-v02","智能学习助手 v0.2 新增什么？","LLM第二课项目做什么","新增PromptSpec、role、预算、指纹、脱敏审计和8项测试。","下一版进入严格JSON校验。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”涉及role、版本、参数、预算、指纹还是审计。`,hints:[`查看 #${c}。`,"运行 test_prompt_contract.py 比较请求快照。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样更换自行车内胎","燕子为什么春天回来"]},null,2)}\n`);
