import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="agent-tool-calling-02",title="业务校验、主体授权与只读工具执行",path="learning-paths/llm-agent/tool-calling-workflow/02-business-validation-authorization-read-only-execution/";
const contexts=[["overview-read-only-execution","overview","只读工具执行"],["concept-validation-order","concept","验证授权顺序"],["concept-least-privilege-reader","concept","最小权限读取"],["example-owner-read","example","所有者读取"],["reproduce-read-only-v14","reproduce","运行只读工具"],["modify-result-bound","modify","修改结果上限"],["troubleshoot-read-only-tool","troubleshoot","只读工具排错"],["deepen-authorization-boundary","deepen","授权边界"],["project-learning-assistant-v14","project","智能学习助手v0.14"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["validation-order","concept-validation-order","为什么授权要在 handler 前？","先查询再判断权限可以吗","不可以；先访问可能泄露存在性、制造负载。handler计数证明拒绝未触达数据层。","validate then authorize。"],
["business-validation","concept-validation-order","Schema 通过后还检查什么？","字段类型对了就安全吗","还要ID格式、权限、资源所有权、风险和结果预算。","多层门禁。"],
["readonly-uri","concept-least-privilege-reader","怎样证明 SQLite 真只读？","代码只写SELECT够吗","用mode=ro连接并真实尝试INSERT，数据库返回写入失败。","两层只读。"],
["parameterized-sql","concept-least-privilege-reader","为什么 SQL 值要参数化？","字符串拼接learner_id行吗","参数化让值不改变SQL结构；工具也不接受模型生成SQL。","WHERE learner_id = ?。"],
["ownership","example-owner-read","有读取权限就能读所有学习者吗？","permission够不够","不够；参数learner_id还必须等于当前subject_id。","跨主体forbidden。"],
["bounded-result","modify-result-bound","工具结果为什么限制三条？","把全部记录交给模型不行吗","限制数据暴露和上下文成本；只返回完成数与最多三条课程ID。","LIMIT 3。"],
["error-envelope","troubleshoot-read-only-tool","工具失败要把异常堆栈给模型吗？","数据库路径能回传吗","不能；外部只返回稳定error_code，内部路径、SQL和异常不进入envelope。","tool_unavailable。"],
["parameterization-not-auth","deepen-authorization-boundary","参数化 SQL 等于授权吗？","防注入就不会越权吗","不等于；合法参数仍可能指向他人资源，必须重新按主体授权。","不同安全层。"],
["read-logs","troubleshoot-read-only-tool","只读工具日志记录结果全文吗？","排错需要保存query吗","默认只记call ID、工具名、状态和错误码，不保存参数、查询或结果。","允许字段。"],
["assistant-v14","project-learning-assistant-v14","智能学习助手 v0.14 新增什么？","Tool Calling第二课项目做什么","新增业务校验、主体授权、所有权、只读SQLite、参数化查询和结果envelope。","下一版多调用关联。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先定位“${a}”属于业务校验、权限、所有权、只读实现、结果上限还是错误脱敏。`,hints:[`查看 #${c}。`,"运行 test_read_only_tool.py 核对handler计数。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["如何学习水彩画","候鸟为什么迁徙"]},null,2)}\n`);
