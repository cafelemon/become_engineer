import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lessonId="algorithm-deepening-02",title="滑动窗口、频次状态与最短覆盖",path="learning-paths/algorithm-deepening/02-sliding-window-frequency-minimum-cover/";
const contexts=[["overview-sliding-window","overview","滑动窗口目标"],["concept-window-state","concept","窗口状态机"],["example-duplicate-frequency","example","重复需求"],["reproduce-window-v02","reproduce","运行窗口实验"],["concept-minimum-proof","concept","最短性证明"],["modify-window-contract","modify","修改窗口契约"],["troubleshoot-sliding-window","troubleshoot","窗口排错"],["project-pattern-lab-v02","project","约束模式实验 v0.2"],["career-window-state","career","窗口状态追问"]].map(([id,type,t])=>({id,type,title:t,anchor:`#${id}`}));
const defs=[
["expand-shrink","overview-sliding-window","滑动窗口的两个边界各负责什么？","右端和左端怎样分工","右端加入元素直到满足约束，满足后左端移除元素以寻找更短可行窗口。","BANC 是收缩得到的最终最短覆盖。"],
["window-invariant","concept-window-state","窗口频次不变量是什么？","current 必须对应什么","current 必须准确对应 text[left:right+1]，formed 必须准确反映满足需求频次的种类数。","固定输出 window-counts-match-state。"],
["duplicate-need","example-duplicate-frequency","需求 AAC 为什么不能用集合？","重复需求怎样表示","集合会丢掉两个 A 的数量要求，必须保存 required[A]=2。","AC 不满足 AAC，AAC 才满足。"],
["formed-increase","concept-window-state","formed 什么时候增加？","多余字符会增加 formed 吗","某需求字符的当前数量刚好达到要求时增加；超过要求不重复增加。","A 从 1 到 2 满足 A 类。"],
["formed-decrease","concept-window-state","formed 什么时候减少？","移除字符后何时失效","移除后当前数量跌到需求量以下时减少。","先减 current，再比较 required。"],
["minimum-proof","concept-minimum-proof","为什么持续收缩能找到该右端最短窗口？","固定 right 怎样找最优 left","依次移除左端直到刚刚失效，最后一个有效位置就是该 right 下最短窗口。","每次有效时先更新答案再移除。"],
["linear-window","concept-minimum-proof","嵌套 while 为什么仍是 O(n)？","窗口会不会 O(n平方)","右端每个位置加入一次，左端每个位置移除至多一次，总移动不超过 2n。","固定样例 expands=13 shrinks=10。"],
["no-cover","troubleshoot-sliding-window","没有覆盖窗口时返回什么？","空字符串是否会歧义","返回显式 None/not-found，避免与合法空窗口或真实空文本混淆。","ABC 无法覆盖 AA。"],
["tie-contract","modify-window-contract","并列最短窗口怎样处理？","最短答案顺序由什么决定","必须声明契约；本课只在严格变短时更新，因此保留最早发现的同长度答案。","改变平局规则要同步测试。"],
["pattern-v02","project-pattern-lab-v02","约束模式实验 v0.2 新增什么？","算法深化第二课项目是什么","新增需求频次、伸缩窗口、三次最佳改进、重复需求与双语言一致报告。","固定结果 9:12 BANC。"]
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”涉及窗口边界、频次阈值还是答案契约。`,hints:[`查看 #${c} 的状态变化。`,`运行 test_sliding_window_trace.py 核对“${q.replace("？","")}”。`],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-23",recommended:i<6}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样给陶土花瓶上釉","信天翁一生飞多远"]},null,2)}\n`);
console.log(JSON.stringify({lesson_id:lessonId,cards:10,questions:20,unknown:2}));
