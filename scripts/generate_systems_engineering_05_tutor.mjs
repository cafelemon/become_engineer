import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
const root=resolve(import.meta.dirname,".."), lessonId="systems-engineering-05";
const title="延迟分布、采样分析与性能预算";
const path="learning-paths/systems-engineering/05-latency-distribution-sampling-performance-budget/";
const contexts=[
["overview-performance-evidence","overview","性能证据目标"],["concept-latency-distribution","concept","延迟分布"],["example-sampling-clock","example","采样与时钟"],["reproduce-performance-v05","reproduce","运行性能实验"],["concept-performance-budget","concept","性能预算"],["modify-performance-budget","modify","修改预算"],["troubleshoot-performance-evidence","troubleshoot","性能排错"],["project-diagnostic-service-v05","project","可诊断系统服务 v0.5"],["career-tail-latency","career","尾延迟追问"]
].map(([id,type,contextTitle])=>({id,type,title:contextTitle,anchor:`#${id}`}));
const defs=[
["percentile-meaning","concept-latency-distribution","p95 延迟是什么意思？","p95 怎样解释","约 95% 样本不超过该值；必须同时说明样本集合与计算方法。","本课最近秩 p95_us=120。"],
["nearest-rank","concept-latency-distribution","最近秩怎样计算百分位？","百分位 rank 公式","先排序，rank=ceil(p*n/100)，再取 rank-1 下标。","20 个样本的 p95 取第 19 个。"],
["mean-tail","concept-latency-distribution","为什么平均值不能代替 p99？","均值为什么看不到尾延迟","均值压缩了分布，少量极慢请求可能仍影响超时与体验。","本课 p50=30、p99=200。"],
["steady-clock","example-sampling-clock","测持续时间为什么用 steady_clock？","系统时间能否测耗时","steady_clock 单调，不受墙钟校时倒退影响，适合计算时间间隔。","固定输出 measurement_clock=steady_clock。"],
["warmup-separation","example-sampling-clock","为什么预热不进入测量样本？","预热和采样怎样分开","预热用于稳定代码与运行状态；混入会改变所声明的热路径分布。","1000 次预热后采 2000 次。"],
["deterministic-replay","reproduce-performance-v05","为什么固定样本和真实测量要分开？","怎样让性能测试可重复","固定样本验证统计和预算逻辑；真实墙钟用于观察且受环境噪声影响。","elapsed=observed-not-asserted。"],
["budget-contract","concept-performance-budget","完整性能预算包含什么？","性能阈值还要写哪些条件","至少包含指标、统计方法、阈值、负载、环境和失败动作。","p95 150µs 只约束本课回放数据。"],
["ci-noise","troubleshoot-performance-evidence","共享 CI 的墙钟测试为何偶发失败？","性能门禁怎样减少环境噪声","共享负载、频率和后台进程会漂移，应在受控环境重复测量并保存基线。","功能 CI 不断言本机绝对耗时。"],
["compiler-elision","troubleshoot-performance-evidence","微基准快得异常应检查什么？","编译器会不会删掉工作","若结果未被消费，优化器可能消除工作；需消费输出并核对功能正确性。","示例累积 checksum 做健全性检查。"],
["diagnostic-v05","project-diagnostic-service-v05","可诊断系统服务 v0.5 新增什么？","第五课项目增量是什么","新增延迟回放、最近秩 p50/p95/p99、p95 预算、预热和单调时钟观测。","5 项测试不依赖机器绝对速度。"]
];
const cards=defs.map(([id,context,question,alias,answer,example],index)=>({id,lesson_id:lessonId,context_id:context,question,aliases:[alias],keywords:[...new Set(`${question} ${alias}`.replace(/[？?，、]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${alias}”涉及分布、采样还是预算边界。`,hints:[`查看 #${context} 的公式或测量阶段。`,`运行 test_performance_budget.py 核对“${question.replace("？","")}”。`],example,answer,source:{label:contexts.find(x=>x.id===context).title,href:`#${context}`},updated_at:"2026-07-23",recommended:index<6}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样给多肉植物换土","海豚为什么喜欢跃出水面"]},null,2)}\n`);
console.log(JSON.stringify({lesson_id:lessonId,cards:10,questions:20,unknown:2}));
