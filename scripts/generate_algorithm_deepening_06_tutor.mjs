import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lessonId="algorithm-deepening-06",title="贪心选择、交换论证与反例",path="learning-paths/algorithm-deepening/06-greedy-choice-exchange-counterexample/";
const contexts=[["overview-greedy","overview","贪心目标"],["concept-interval-contract","concept","区间契约"],["example-earliest-finish","example","最早结束选择"],["concept-exchange-proof","concept","交换论证"],["reproduce-greedy-v06","reproduce","运行贪心实验"],["modify-greedy","modify","修改目标与边界"],["troubleshoot-greedy","troubleshoot","贪心排错"],["project-pattern-lab-v06","project","约束模式实验 v0.6"],["career-greedy-proof","career","贪心证明追问"]].map(([id,type,t])=>({id,type,title:t,anchor:`#${id}`}));
const defs=[
["objective-count","concept-interval-contract","本课优化目标是什么？","区间调度最大化什么","在互不重叠前提下最大化选中区间数量，不是总时长或总价值。","目标改变后必须重新选择算法。"],
["half-open-touch","concept-interval-contract","两个端点相接的区间冲突吗？","半开区间怎样判断兼容","使用 [start,end)，下一段 start>=last_end 就兼容。","[1,4) 与 [4,7) 可同时选择。"],
["finish-rule","example-earliest-finish","正确的局部选择规则是什么？","区间按什么排序","按结束时间从早到晚扫描，选择第一个与已选结果兼容的区间。","样例选择 A,D,H,K。"],
["exchange-proof","concept-exchange-proof","交换论证怎样证明首选安全？","为什么最早结束不损失最优解","把任一最优解首段 o 换成结束不晚于它的 g，不减少后续空间或数量。","存在一个以 g 开头的最优解。"],
["earliest-start-counterexample","overview-greedy","最早开始为什么错误？","3 对 4 的贪心反例","它先选 C 占据较长前缀，只得到 C,G,K 三段；最早结束能得到四段。","样例给出可重复的反例。"],
["tie-determinism","example-earliest-finish","结束时间相同时怎样稳定输出？","贪心排序并列键","再按开始时间和标签排序；次级键用于确定性，不是正确性核心。","固定 order_by_finish 可逐字比较。"],
["bruteforce-oracle","reproduce-greedy-v06","穷举在实验中做什么？","为什么不能用穷举做生产算法","小 n 时枚举可行子集，作为独立 oracle 核对贪心最优值。","指数增长，因此只用于测试。"],
["weighted-failure","modify-greedy","加入区间价值后还能最早结束吗？","带权区间为什么需要 DP","交换后可能保留数量却损失更高价值，原目标保持步骤失效。","下一步用带权区间 DP。"],
["greedy-complexity","reproduce-greedy-v06","贪心区间调度复杂度是多少？","排序和扫描分别多快","排序 O(n log n)，扫描 O(n)，结果最多保存 n 个区间。","穷举 oracle 不计入生产复杂度。"],
["pattern-v06","project-pattern-lab-v06","约束模式实验 v0.6 新增什么？","算法深化第六课项目是什么","新增无权区间调度、错误规则反例、交换论证、小规模 oracle 与双语言固定报告。","固定不变量 selected-intervals-nonoverlap。"]
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”涉及目标、区间边界、局部规则还是证明义务。`,hints:[`查看 #${c} 的目标与证据。`,`运行 test_greedy_interval_trace.py 核对“${q.replace("？","")}”。`],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-23",recommended:i<6}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样修理漏水的花洒","候鸟为什么会排成人字形"]},null,2)}\n`);
console.log(JSON.stringify({lesson_id:lessonId,cards:10,questions:20,unknown:2}));

