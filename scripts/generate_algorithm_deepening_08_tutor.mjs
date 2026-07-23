import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lessonId="algorithm-deepening-08",title="背包、区间动态规划与空间压缩",path="learning-paths/algorithm-deepening/08-knapsack-interval-dp-space-compression/";
const contexts=[["overview-structured-dp","overview","结构化 DP 目标"],["concept-knapsack-state","concept","背包状态"],["example-capacity-order","example","容量迭代顺序"],["concept-interval-order","concept","区间 DP 顺序"],["reproduce-structured-dp-v08","reproduce","运行结构化 DP"],["modify-structured-dp","modify","修改 DP 模型"],["troubleshoot-structured-dp","troubleshoot","结构化 DP 排错"],["project-pattern-lab-v08","project","约束模式实验 v0.8"],["career-structured-dp","career","空间压缩追问"]].map(([id,type,t])=>({id,type,title:t,anchor:`#${id}`}));
const defs=[
["knapsack-state","concept-knapsack-state","0/1 背包状态代表什么？","背包 dp 容量语义","处理若干物品后，dp[c] 是容量不超过 c 时的最大价值。","压缩前还显式包含物品维度。"],
["descending-capacity","example-capacity-order","0/1 背包为什么容量倒序？","怎样防止同一物品重复使用","倒序保证 dp[c-w] 仍是处理当前物品前的旧层状态。","每件物品在本轮至多使用一次。"],
["forward-counterexample","example-capacity-order","容量正序会出现什么错误？","单件物品 6 对 3 反例","重量 2 价值 3 容量 4 时，正序用刚写的 dp[2] 再写 dp[4]=6。","0/1 正确答案只能是 3。"],
["complete-knapsack","modify-structured-dp","什么时候容量可以正序？","完全背包怎样迭代","只有模型明确允许每件物品重复使用时，正序复用本轮状态才正确。","循环顺序表达模型。"],
["space-contract","concept-knapsack-state","空间压缩会丢失什么？","一维背包为什么难重建","一维表保留最优值，却覆盖物品层和部分决策来源。","要重建需二维表、父指针或额外记录。"],
["interval-state","concept-interval-order","矩阵链区间状态是什么？","cost left right 代表什么","cost[l][r] 是连续矩阵 l 到 r 的最少标量乘法次数。","单矩阵区间成本为零。"],
["length-order","concept-interval-order","区间 DP 为什么按长度递增？","子区间何时就绪","长度为 L 的转移只读取更短区间，先完成短区间才能安全合并。","固定不变量 subintervals-ready。"],
["matrix-result","concept-interval-order","样例矩阵链最优结果是什么？","4500 怎样得到","先算 A1A2 花 1500，再乘 A3 花 3000，总计 4500。","括号化 ((A1A2)A3)。"],
["complexities","reproduce-structured-dp-v08","两种 DP 的复杂度是多少？","背包和矩阵链分别多快","一维背包 O(items×capacity) 时间、O(capacity) 空间；矩阵链 O(n³) 时间、O(n²) 空间。","区间数平方，每区间枚举切分点。"],
["pattern-v08","project-pattern-lab-v08","约束模式实验 v0.8 新增什么？","算法深化第八课项目是什么","新增 0/1 背包压缩、错误复用反例、矩阵链区间 DP、括号化与双语言报告。","固定两个计算顺序不变量。"]
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”涉及模型、状态维度、压缩方向还是依赖就绪顺序。`,hints:[`查看 #${c} 的循环与状态。`,`运行 test_structured_dp_trace.py 核对“${q.replace("？","")}”。`],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-23",recommended:i<6}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["室内绿植多久浇一次水","怎样挑选合适的羽毛球拍"]},null,2)}\n`);
console.log(JSON.stringify({lesson_id:lessonId,cards:10,questions:20,unknown:2}));

