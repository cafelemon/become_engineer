import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lessonId="algorithm-deepening-05",title="回溯、选择树与剪枝",path="learning-paths/algorithm-deepening/05-backtracking-choice-tree-pruning/";
const contexts=[["overview-backtracking","overview","回溯目标"],["concept-choice-tree","concept","选择树"],["example-choose-undo","example","选择与撤销"],["reproduce-backtracking-v05","reproduce","运行回溯实验"],["concept-pruning-proof","concept","剪枝证明"],["modify-backtracking","modify","修改回溯契约"],["troubleshoot-backtracking","troubleshoot","回溯排错"],["project-pattern-lab-v05","project","约束模式实验 v0.5"],["career-backtracking-pruning","career","回溯剪枝追问"]].map(([id,type,t])=>({id,type,title:t,anchor:`#${id}`}));
const defs=[
["backtrack-state","concept-choice-tree","回溯状态包含什么？","start total path 各自作用","start 限制后续位置，total 表示当前和，path 保存当前选择。","每层递归只处理自己的后续候选。"],
["choose-undo","example-choose-undo","为什么选择后必须撤销？","path pop 不能漏掉","path 被兄弟分支共享，返回后不撤销会污染下一分支。","固定输出 path_after_search=empty。"],
["position-once","concept-choice-tree","怎样保证每个位置最多用一次？","递归下一层 start 怎么传","选择 index 后递归 index+1，后续不再访问该位置。","允许复用时才传 index。"],
["same-level-duplicate","concept-pruning-proof","重复值为什么只在同层跳过？","index 大于 start 的判断","同层相同值产生相同分支；不同层相同值来自不同位置，可能构成合法组合。","[1,1,2] 只输出一次 [1,2]。"],
["suffix-prune","concept-pruning-proof","超过目标为什么能剪整个后缀？","break 需要什么前提","候选为正数且已排序，当前值已过大，右侧更大值也一定过大。","允许负数后该证明失效。"],
["zero-target","reproduce-backtracking-v05","目标为零返回什么？","空组合是不是解","空路径的和为零，因此返回一个空组合，而不是无解。","结果是 ((),)。"],
["no-solution","troubleshoot-backtracking","无解怎样表示？","回溯没有找到组合怎么办","返回空解集合，不混同包含一个空组合的零目标。","[2,4] target3 无解。"],
["node-count","overview-backtracking","节点计数说明什么？","剪枝数量能证明正确吗","计数展示搜索规模，但正确性仍由状态不变量与剪枝前提证明。","固定访问 14 节点、剪 11 候选。"],
["output-bound","modify-backtracking","解很多时怎样受控停止？","回溯输出爆炸怎么处理","定义最大解数或迭代接口，达到边界后显式报告截断。","不能静默丢掉剩余解。"],
["pattern-v05","project-pattern-lab-v05","约束模式实验 v0.5 新增什么？","算法深化第五课项目是什么","新增目标和选择树、同层去重、后缀剪枝、路径恢复和双语言报告。","固定不变量 choose-search-undo。"]
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”涉及递归状态、去重层级还是剪枝前提。`,hints:[`查看 #${c} 的选择树。`,`运行 test_backtracking_trace.py 核对“${q.replace("？","")}”。`],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-23",recommended:i<6}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样给木桌涂保护油","海豹如何在冰面休息"]},null,2)}\n`);
console.log(JSON.stringify({lesson_id:lessonId,cards:10,questions:20,unknown:2}));
