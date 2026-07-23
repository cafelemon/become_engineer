import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="deep-learning-07",title="检查点、随机状态与精确恢复训练",path="learning-paths/ai-foundation/deep-learning/07-checkpoint-rng-resume-exact-training/";
const contexts=[["overview-exact-resume","overview","精确恢复结果"],["concept-checkpoint-state","concept","检查点状态"],["concept-rng-resume","concept","随机状态恢复"],["example-resume-transaction","example","保存加载顺序"],["reproduce-checkpoint-v07","reproduce","运行恢复实验"],["modify-checkpoint","modify","修改检查点"],["troubleshoot-checkpoint","troubleshoot","检查点排错"],["deepen-checkpoint-boundary","deepen","恢复边界"],["project-diagnosable-network-v07","project","可诊断网络 v0.7"]].map(([id,type,t])=>({id,type,title:t,anchor:`#${id}`}));
const defs=[
["checkpoint-state","concept-checkpoint-state","恢复训练要保存哪些状态？","checkpoint只存模型够吗","至少保存模型、优化器、进度、历史、实际随机源状态和兼容配置。","v0.7保存model+optimizer+epoch+history+RNG。"],
["optimizer-state","concept-checkpoint-state","为什么要保存 optimizer state？","momentum不保存会怎样","动量等内部状态决定后续更新；重新创建optimizer会让恢复轨迹分叉。","本课SGD momentum为0.9。"],
["rng-state","concept-rng-resume","随机种子和 RNG state 有什么区别？","恢复时重新seed够吗","种子定义序列起点，RNG state定义已消费到的位置；中断恢复需要后者。","恢复后shuffle和Dropout接续原序列。"],
["exact-resume","overview-exact-resume","怎样证明恢复训练正确？","恢复后loss差不多算成功吗","在受控环境比较连续与中断恢复的完整history、model和optimizer逐值一致。","第3轮中断、第8轮三类状态全相等。"],
["atomic-checkpoint","example-resume-transaction","为什么检查点要原子写入？","直接覆盖checkpoint有什么风险","进程中断可能留下半文件；先写同目录临时文件再原子替换目标。","测试确认没有残留tmp。"],
["digest-before-load","example-resume-transaction","为什么要在 torch.load 前验摘要？","checkpoint篡改何时检查","先检查字节完整性可在反序列化前拒绝截断或替换。","SHA-256在load前验证。"],
["weights-only","deepen-checkpoint-boundary","weights_only=True 解决了什么？","torch.load如何收窄风险","它限制可反序列化对象类型，但不能证明未知文件来源可信。","仅加载本机生成且已审查产物。"],
["schema-version","troubleshoot-checkpoint","checkpoint 版本不兼容怎么办？","模型结构不一样能强行load吗","应校验版本、架构和配置并确定性拒绝，不靠strict=False掩盖差异。","版本999被拒绝。"],
["map-location","troubleshoot-checkpoint","map_location=cpu 有什么用？","GPU checkpoint如何在CPU读取","它把存储映射到CPU，避免加载依赖原设备；仍需验证dtype与结构。","v0.7固定CPU恢复。"],
["checkpoint-v07","project-diagnosable-network-v07","可诊断神经网络 v0.7 新增什么？","深度学习第七课项目做什么","它新增完整训练态、原子保存、完整性和兼容门禁、精确恢复与8项测试。","下一版分离推理交付产物。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”缺的是状态完整性、写入原子性、加载信任还是恢复等价证据。`,hints:[`查看 #${c}。`,"运行 test_checkpoint_lab.py 并比较连续/恢复两条路径。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-23",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样制作陶瓷杯","候鸟为什么迁徙"]},null,2)}\n`);
