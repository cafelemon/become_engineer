import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="llm-use-04",title="错误分类、Deadline、退避与有界重试",path="learning-paths/llm-agent/model-use/04-error-taxonomy-deadline-backoff-bounded-retry/";
const contexts=[["overview-bounded-recovery","overview","有界失败恢复"],["concept-error-taxonomy","concept","错误分类"],["concept-three-budgets","concept","三层预算"],["example-recovery-state-machine","example","恢复状态机"],["reproduce-recovery-v04","reproduce","运行恢复实验"],["modify-retry-policy","modify","修改重试策略"],["troubleshoot-bounded-retry","troubleshoot","有界重试排错"],["deepen-backoff-jitter","deepen","退避与抖动"],["project-learning-assistant-v04","project","智能学习助手v0.4"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["retryable-errors","concept-error-taxonomy","哪些模型调用错误可以重试？","限流和认证失败都retry吗","默认只重试限流、暂时不可用和timeout；认证、坏请求、拒绝、坏输出与缺信息终止。","retryable集合只有三类。"],
["attempt-timeout","concept-three-budgets","单次 timeout 管什么？","attempt timeout和deadline区别","它限制一次provider调用等待时间，不包含整个操作的所有调用与退避。","每次call都有timeout。"],
["overall-deadline","concept-three-budgets","整体 deadline 管什么？","重试总共能等多久","它覆盖从操作开始到结束的全部调用与退避，后续timeout必须按剩余时间收窄。","200ms时第二次只剩60ms。"],
["attempt-budget","concept-three-budgets","为什么 deadline 外还要最大尝试次数？","调用很快会不会无限retry","会；次数硬上限保证即使每次立即失败也终止。","三次后attempt_budget_exhausted。"],
["terminal-error","concept-error-taxonomy","认证失败为什么不能靠重试恢复？","401多试几次可以吗","相同凭据和请求不会因重复调用自动正确，应停止并修复配置。","authentication只调用一次。"],
["backoff-deadline","example-recovery-state-machine","退避前为什么再检查 deadline？","先sleep再看时间行吗","等待本身消耗总预算；若等待会触及deadline，应立即停止。","80ms后20ms退避被拒绝。"],
["virtual-clock","reproduce-recovery-v04","虚拟时钟是否等于Mock provider？","不真实sleep算真实测试吗","它替换时间来源以确定性验证真实状态机；本课本就不声称连接provider。","8项测试零等待。"],
["retry-after","modify-retry-policy","如何处理 provider 的 Retry-After？","服务建议等待多久就盲从吗","先校验并设上限，再与本地退避和剩余deadline共同决策。","超过剩余预算就停止。"],
["jitter","deepen-backoff-jitter","生产重试为什么需要 jitter？","固定指数退避不够吗","大量客户端固定节奏会同步再冲击服务；有界抖动可分散重试。","测试注入固定随机源。"],
["assistant-v04","project-learning-assistant-v04","智能学习助手 v0.4 新增什么？","LLM第四课项目做什么","新增错误分类、timeout、deadline、退避、尝试预算和确定性恢复轨迹。","下一版处理流式事件。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先确认“${a}”属于错误分类、单次等待、整体预算还是退避决策。`,hints:[`查看 #${c}。`,"运行 test_recovery_policy.py 回放尝试记录。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎么修理自行车链条","冰箱冷藏室结霜怎么办"]},null,2)}\n`);
