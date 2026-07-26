import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="agent-tool-calling-01",title="工具定义、注册表、候选调用与严格参数",path="learning-paths/llm-agent/tool-calling-workflow/01-tool-definition-registry-candidate-call-strict-arguments/";
const contexts=[["overview-tool-proposal","overview","工具候选协议"],["concept-tool-flow","concept","Tool Calling流程"],["concept-registry-manifest","concept","注册表与Manifest"],["example-strict-candidate","example","严格候选参数"],["reproduce-tool-v13","reproduce","运行工具协议"],["modify-tool-schema","modify","修改工具Schema"],["troubleshoot-tool-protocol","troubleshoot","工具协议排错"],["deepen-schema-security-boundary","deepen","Schema安全边界"],["project-learning-assistant-v13","project","智能学习助手v0.13"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["proposal-only","concept-tool-flow","为什么模型工具调用只是候选？","模型返回function call就执行吗","不执行；应用仍需验证、授权、确认、预算和受控handler。","executed:false。"],
["five-step-flow","concept-tool-flow","Tool Calling 有哪些阶段？","工具调用流程是什么","定义工具、接收候选、应用执行、按call_id回传结果、模型回答或继续。","本课停在执行前。"],
["allowlisted-registry","concept-registry-manifest","为什么需要工具允许列表？","按模型给的函数名反射不行吗","允许列表只暴露明确业务能力，拒绝run_shell或任意函数名。","ToolRegistry。"],
["manifest-fingerprint","concept-registry-manifest","工具 manifest 为什么做指纹？","schema版本怎么识别","规范排序后哈希识别模型看到的定义集合；指纹不证明定义安全。","e5c8836eb436。"],
["strict-json","example-strict-candidate","参数为什么不自动转换类型？","字符串true能转布尔吗","不转；隐式纠正会掩盖模型输出错误并把猜测送进执行器。","argument_type_invalid。"],
["extra-fields","example-strict-candidate","额外参数可以忽略吗？","多了admin字段怎么办","默认拒绝，避免模型扩张调用能力或业务层误用未知字段。","additionalProperties false。"],
["call-id","troubleshoot-tool-protocol","call_id 有什么作用？","工具结果怎么关联原调用","它是后续输出与候选调用的稳定关联键；本课先验证格式。","call_demo1。"],
["schema-not-auth","deepen-schema-security-boundary","strict Schema 等于授权吗？","参数合法就能访问别人的数据吗","不等于；Schema只管形状，主体权限、业务规则与副作用另行门禁。","下一课授权。"],
["tool-logs","troubleshoot-tool-protocol","工具候选日志保存参数吗？","排错要记录完整arguments吗","默认只记录call ID、工具名和错误码，不保存参数或用户原文。","允许字段日志。"],
["assistant-v13","project-learning-assistant-v13","智能学习助手 v0.13 新增什么？","Tool Calling第一课项目做什么","新增工具注册表、规范manifest、严格候选解析和不可变参数，不执行handler。","下一版只读执行。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先定位“${a}”属于候选流程、注册表、manifest、参数门禁还是授权边界。`,hints:[`查看 #${c}。`,"运行 test_tool_protocol.py 核对稳定错误码。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎么挑选露营帐篷","咖啡豆怎样烘焙"]},null,2)}\n`);
