import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lessonId="algorithm-deepening-01",title="有序双指针、候选消除与不变量",path="learning-paths/algorithm-deepening/01-sorted-two-pointers-candidate-elimination-invariant/";
const contexts=[["overview-two-pointers","overview","双指针目标"],["concept-candidate-grid","concept","候选网格"],["example-elimination-proof","example","排除证明"],["reproduce-two-pointer-v01","reproduce","运行双语言轨迹"],["concept-contract-boundaries","concept","答案契约"],["modify-two-pointer","modify","修改双指针"],["troubleshoot-two-pointer","troubleshoot","双指针排错"],["project-pattern-lab-v01","project","约束模式实验 v0.1"],["career-two-pointer-proof","career","双指针追问"]].map(([id,type,t])=>({id,type,title:t,anchor:`#${id}`}));
const defs=[
["sorted-precondition","overview-two-pointers","双指针求两数和为什么要求有序？","乱序时为什么会漏解","只有有序关系才能从当前和推出整行或整列候选都不可能。","示例明确拒绝乱序输入。"],
["move-right","example-elimination-proof","当前和过大为什么移动右指针？","sum 大于 target 排除什么","当前右值与最小候选相加都过大，包含该右值的其余候选只会更大。","1+8=9>8，因此排除右端 8。"],
["move-left","example-elimination-proof","当前和过小为什么移动左指针？","sum 小于 target 排除什么","当前左值与最大候选相加仍过小，包含该左值的其余候选只会更小。","1+6=7<8，因此排除左端 1。"],
["loop-invariant","concept-candidate-grid","双指针循环不变量是什么？","指针外候选怎样证明","若尚有解，它必在当前闭区间的不同下标对中；指针外候选已经被比较证明不可能。","固定输出 outside-pairs-eliminated。"],
["distinct-indices","concept-contract-boundaries","为什么循环条件是 left 小于 right？","能否用同一元素两次","严格小于保证两个不同位置；相等时只剩一个元素，不能组成下标对。","重复值 2,2 合法，但位置不同。"],
["first-match","concept-contract-boundaries","本课返回哪一组多解答案？","是否保证字典序最小","返回指针扫描首先遇到的一对，不承诺下标和或字典序最小。","改变答案顺序必须重写契约和测试。"],
["linear-cost","concept-candidate-grid","双指针为什么是 O(n)？","最多比较多少次","每次比较让左右距离减少 1，因此长度 n 最多比较 n-1 次。","没有嵌套候选扫描。"],
["all-pairs","modify-two-pointer","怎样返回全部不重复值对？","匹配后怎样跳过重复值","记录匹配后同时移动两端，并跨过与已匹配值相同的连续元素。","补全重复值和多个解测试。"],
["original-indices","career-two-pointer-proof","乱序数组要原下标怎么办？","排序后如何保留位置","排序值与原下标对，扫描后映射回原位置；或用哈希换取 O(n) 时间和 O(n) 空间。","两种方案的输出顺序契约不同。"],
["pattern-v01","project-pattern-lab-v01","约束模式实验 v0.1 新增什么？","算法深化第一课项目是什么","新增双语言有序双指针、逐步移动轨迹、6 项边界测试与输出对照。","固定结果 indices 1,4 values 2,6。"]
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”涉及有序前提、循环不变量还是输出契约。`,hints:[`查看 #${c} 的候选排除证据。`,`运行 test_two_pointer_trace.py 核对“${q.replace("？","")}”。`],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-23",recommended:i<6}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样给咖啡豆选择烘焙度","海星会不会在沙滩散步"]},null,2)}\n`);
console.log(JSON.stringify({lesson_id:lessonId,cards:10,questions:20,unknown:2}));
