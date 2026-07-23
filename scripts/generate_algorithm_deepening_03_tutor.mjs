import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lessonId="algorithm-deepening-03",title="前缀和、差分与区间批处理",path="learning-paths/algorithm-deepening/03-prefix-sum-difference-range-batching/";
const contexts=[["overview-range-transform","overview","区间变换目标"],["concept-prefix-invariant","concept","前缀不变量"],["example-difference-boundaries","example","差分边界"],["reproduce-range-v03","reproduce","运行区间实验"],["concept-cost-choice","concept","操作成本选择"],["modify-range-transform","modify","扩展区间变换"],["troubleshoot-range-transform","troubleshoot","区间排错"],["project-pattern-lab-v03","project","约束模式实验 v0.3"],["career-range-choice","career","区间结构追问"]].map(([id,type,t])=>({id,type,title:t,anchor:`#${id}`}));
const defs=[
["prefix-meaning","concept-prefix-invariant","prefix i 表示什么？","前缀数组为什么长 n+1","prefix[i] 表示前 i 个元素之和，prefix[0]=0，因此数组长度为 n+1。","values 2,-1,3 得到 prefix 0,2,1,4。"],
["range-subtract","concept-prefix-invariant","半开区间和怎样计算？","为什么 prefix right 减 left","两份从 0 开始的累计相减，左侧公共部分抵消，只剩 [left,right)。","sum[1:5)=9-2=7。"],
["empty-range","concept-prefix-invariant","空区间为什么自然为零？","left 等于 right 怎么算","同一个前缀值减自身为零，无需访问数组元素或额外特判。","sum[3:3)=0。"],
["difference-start","example-difference-boundaries","区间加为什么在 left 加 delta？","差分从哪里生效","还原累计到 left 时把 delta 带入，因此从该位置开始生效。","[0:3)+2 在 difference[0] 加 2。"],
["difference-stop","example-difference-boundaries","区间加为什么在 right 减 delta？","差分怎样在右边界停止","还原累计到 right 时用相反标记抵消，使 right 不受更新影响。","difference[right]-=delta。"],
["overlap-add","example-difference-boundaries","重叠区间更新怎样组合？","差分标记能否覆盖","每个边界标记累加，最终前缀还原会自动叠加所有覆盖当前位置的增量。","三个更新还原 2,5,4,2,-1。"],
["prefix-cost","concept-cost-choice","前缀和的成本是什么？","多次静态查询为何适合前缀","O(n) 预处理后每次区间和 O(1)，适合数据不变且查询很多。","不用每次重新扫描区间。"],
["difference-cost","concept-cost-choice","差分更新的成本是什么？","离线区间加为何适合差分","每次边界标记 O(1)，全部更新后 O(n) 一次还原。","不适合每次更新后立即任意查询。"],
["half-open","troubleshoot-range-transform","为什么统一半开区间？","闭区间混用有什么风险","长度等于 right-left、空区间自然存在，相邻区间边界不重叠，前缀和与差分公式一致。","所有接口使用 [left,right)。"],
["pattern-v03","project-pattern-lab-v03","约束模式实验 v0.3 新增什么？","算法深化第三课项目是什么","新增 prefix 查询、difference 批量更新、重叠与空区间测试及双语言报告。","固定不变量 half-open-boundaries-cancel。"]
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”涉及累计定义、半开边界还是操作序列。`,hints:[`查看 #${c} 的公式。`,`运行 test_range_transform_trace.py 核对“${q.replace("？","")}”。`],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-23",recommended:i<6}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样修剪一棵盆景松","鲸鱼为什么会唱歌"]},null,2)}\n`);
console.log(JSON.stringify({lesson_id:lessonId,cards:10,questions:20,unknown:2}));
