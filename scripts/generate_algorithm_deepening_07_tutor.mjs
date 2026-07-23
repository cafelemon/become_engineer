import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lessonId="algorithm-deepening-07",title="线性动态规划、状态与转移",path="learning-paths/algorithm-deepening/07-linear-dynamic-programming-state-transition/";
const contexts=[["overview-linear-dp","overview","线性 DP 目标"],["concept-dp-state","concept","状态与转移"],["example-dp-table","example","状态表"],["concept-dp-reconstruction","concept","选择重建"],["reproduce-linear-dp-v07","reproduce","运行线性 DP"],["modify-linear-dp","modify","修改状态契约"],["troubleshoot-linear-dp","troubleshoot","动态规划排错"],["project-pattern-lab-v07","project","约束模式实验 v0.7"],["career-linear-dp","career","DP 状态追问"]].map(([id,type,t])=>({id,type,title:t,anchor:`#${id}`}));
const defs=[
["state-meaning","concept-dp-state","dp[i] 代表什么？","线性 DP 状态怎样定义","dp[i] 是前 i 个元素在不选相邻位置且允许空选择时的最大和。","dp[0] 对应空前缀。"],
["transition","concept-dp-state","状态转移怎样推导？","take 和 skip 是什么","跳过当前得到 dp[i-1]；选择当前得到 dp[i-2]+value[i-1]，取二者最大。","两类决策覆盖所有合法解。"],
["base-case","concept-dp-state","为什么需要 dp[0]=0？","空前缀基线有什么用","它给第一个元素和全负输入提供明确边界，并表达允许空选择。","表长度为 n+1。"],
["prefix-invariant","example-dp-table","状态表的不变量是什么？","怎样证明每个 dp 格子正确","dp[i] 始终是前 i 个元素的最优值；由更短前缀的最优值归纳得到。","固定不变量 dp-prefix-optimum。"],
["reconstruct","concept-dp-reconstruction","怎样重建一组最优下标？","从 dp 表尾如何回退","若 take>skip 就选当前并退两格，否则退一格，最后反转下标。","样例得到 0,2,4。"],
["tie-policy","concept-dp-reconstruction","take 和 skip 相等时怎么办？","DP 平局如何固定输出","本课固定跳过当前，使多组最优解的重建结果可重复。","[1,1] 选择下标 0。"],
["negative-empty","reproduce-linear-dp-v07","全负输入为什么返回零？","允许空选择怎样影响答案","空集合合法且和为零，比任何负数选择更优。","禁止空选择时必须重设基线。"],
["greedy-counterexample","overview-linear-dp","先取最大值为什么失败？","6 对 9 的反例","[4,5,4,1,1] 先取 5 后只得 6；DP 选择 4+4+1 得 9。","局部最大会阻塞两个可组合选择。"],
["space-compression","modify-linear-dp","什么时候能把空间压到 O(1)？","滚动变量会丢失什么","只求最优值时保留前两格即可；直接重建路径需要表或额外决策信息。","优化必须服从输出契约。"],
["pattern-v07","project-pattern-lab-v07","约束模式实验 v0.7 新增什么？","算法深化第七课项目是什么","新增线性 DP 状态表、选择重建、平局契约、错误贪心和小规模 oracle。","固定状态表 0,4,5,8,8,9。"]
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”涉及状态定义、基线、转移、计算顺序还是重建。`,hints:[`查看 #${c} 的状态证据。`,`运行 test_linear_dp_trace.py 核对“${q.replace("？","")}”。`],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-23",recommended:i<6}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样判断咖啡豆的新鲜度","月相变化需要多少天"]},null,2)}\n`);
console.log(JSON.stringify({lesson_id:lessonId,cards:10,questions:20,unknown:2}));

