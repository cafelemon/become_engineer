import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lessonId="algorithm-deepening-04",title="单调栈、单调队列与支配关系",path="learning-paths/algorithm-deepening/04-monotonic-stack-queue-dominance/";
const contexts=[["overview-monotonic-structures","overview","单调结构目标"],["concept-stack-resolution","concept","单调栈结算"],["example-deque-dominance","example","队列支配"],["reproduce-monotonic-v04","reproduce","运行单调实验"],["concept-amortized-linear","concept","摊还线性"],["modify-monotonic-contract","modify","修改单调契约"],["troubleshoot-monotonic","troubleshoot","单调结构排错"],["project-pattern-lab-v04","project","约束模式实验 v0.4"],["career-monotonic-dominance","career","单调结构追问"]].map(([id,type,t])=>({id,type,title:t,anchor:`#${id}`}));
const defs=[
["stack-purpose","concept-stack-resolution","单调栈保存什么候选？","栈里为什么是下标","保存尚未遇到右侧严格更大值的下标；下标同时保留位置、值和顺序。","扫描结束仍在栈内则答案 none。"],
["strict-compare","concept-stack-resolution","严格更大为什么不能弹出相等值？","比较符小于还是小于等于","相等不满足严格更大，因此只有栈顶值小于当前值时才能结算。","两个值 2 都由后续 4 结算。"],
["deque-front","example-deque-dominance","单调队列队首表示什么？","窗口最大值在哪里","清除过期下标后，值单调递减的队首就是当前窗口最大值下标。","宽度 3 输出 2,4,4。"],
["back-dominance","example-deque-dominance","为什么能从队尾删除不大于新值的候选？","旧候选为何永远回不来","新值更晚过期且不小，旧候选在未来任何共同窗口都不可能胜出。","固定样例尾部淘汰 3 次。"],
["front-expiry","example-deque-dominance","队首何时过期？","窗口左边界怎样判断","当下标 `<= index-width` 时已不属于当前窗口，必须从头部移除。","存值而不存下标无法判断过期。"],
["amortized","concept-amortized-linear","嵌套 while 为什么仍是线性？","单调结构怎样摊还分析","每个下标入结构一次、离开至多一次，全部弹出次数总计 O(n)。","不能把每轮 while 上限直接相乘。"],
["equal-max","modify-monotonic-contract","重复最大值保留早值还是新值？","尾部相等值怎样处理","由输出下标契约决定；用 <= 保留更新值，用 < 保留更早相等值。","只输出数值时两者都可正确。"],
["oversized-window","troubleshoot-monotonic","窗口宽度大于数组怎样处理？","没有完整窗口返回什么","本课返回空结果；宽度非正则明确拒绝。","边界契约必须写进测试。"],
["stack-none","troubleshoot-monotonic","没有右侧更大值怎样表示？","未结算栈元素怎么办","扫描结束留下的下标保持 None，不伪造哨兵值。","4 和末尾 3 的答案为 none。"],
["pattern-v04","project-pattern-lab-v04","约束模式实验 v0.4 新增什么？","算法深化第四课项目是什么","新增下一严格更大值、窗口最大值、支配/过期计数与双语言一致报告。","固定不变量 dominated-candidates-never-return。"]
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”涉及严格比较、支配淘汰还是窗口过期。`,hints:[`查看 #${c} 的候选规则。`,`运行 test_monotonic_structures_trace.py 核对“${q.replace("？","")}”。`],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-23",recommended:i<6}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样调一杯柠檬苏打","候鸟为什么排成人字形"]},null,2)}\n`);
console.log(JSON.stringify({lesson_id:lessonId,cards:10,questions:20,unknown:2}));
