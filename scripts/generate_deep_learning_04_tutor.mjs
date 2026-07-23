import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="deep-learning-04",title="Mini-batch、SGD、学习率与训练循环",path="learning-paths/ai-foundation/deep-learning/04-mini-batch-sgd-learning-rate-training-loop/";
const contexts=[["overview-training-loop","overview","训练循环结果"],["concept-mini-batch-epoch","concept","batch step epoch"],["concept-sgd-learning-rate","concept","SGD 与学习率"],["example-zero-backward-step","example","更新状态机"],["reproduce-training-v04","reproduce","运行训练实验"],["modify-training-loop","modify","修改训练循环"],["troubleshoot-training-loop","troubleshoot","训练排错"],["deepen-optimizer-state","deepen","优化器状态"],["project-diagnosable-network-v04","project","可诊断网络 v0.4"]].map(([id,type,t])=>({id,type,title:t,anchor:`#${id}`}));
const defs=[
["mini-batch","concept-mini-batch-epoch","mini-batch 是什么？","为什么不一次用全部训练数据","mini-batch 是一次 forward/backward 使用的训练子集，在计算成本和梯度噪声之间形成选择。","本课每批12行。"],
["step","concept-mini-batch-epoch","训练 step 表示什么？","一次 step 做哪些事","一个 step 完成清零、前向、loss、反向和 optimizer 参数更新。","每个epoch有6 step。"],
["epoch","concept-mini-batch-epoch","一个 epoch 怎样算完整？","epoch 是否必须覆盖全部行","本课一个epoch要求每个训练行恰好访问一次，不漏行也不重复。","72行按12分成6批。"],
["sgd","concept-sgd-learning-rate","SGD 怎样更新参数？","梯度下降公式是什么","SGD 用参数减去学习率乘当前梯度，沿局部负梯度方向移动。","theta_next=theta-lr*grad。"],
["learning-rate","concept-sgd-learning-rate","学习率控制什么？","lr 越大训练越好吗","学习率缩放每次更新步长；过小慢，过大可能震荡或发散，不存在脱离任务的通用最优值。","v0.4固定0.1。"],
["training-order","example-zero-backward-step","为什么训练顺序是 zero backward step？","optimizer step 放在哪里","先清旧梯度，再前向与反向生成本批梯度，最后step更新；顺序错会累加或不更新。","zero_grad→forward→loss→backward→step。"],
["weighted-epoch-loss","example-zero-backward-step","epoch loss 为什么按 batch 行数加权？","batch loss 能直接平均吗","各batch长度可能不同，应累加mean_loss×rows再除以总行数。","最后一个短batch仍正确。"],
["seeded-batches","concept-mini-batch-epoch","怎样让每个 epoch 洗牌又可复现？","batch order 怎么固定","用配置种子加epoch建立局部Generator；同配置重现，不同epoch顺序变化。","排序后的索引必须为0到71。"],
["zero-learning-rate","concept-sgd-learning-rate","零学习率对照证明什么？","lr 0 为什么参数不变","它证明forward与backward可运行但step更新幅度为0，从而区分梯度计算与参数变化。","update norm精确为0。"],
["training-v04","project-diagnosable-network-v04","可诊断神经网络 v0.4 新增了什么？","深度学习第四课项目做什么","它新增分层数据、mini-batch、SGD、学习率、30 epoch历史、参数变化和8项测试。","验证集保持未参与训练。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”涉及 batch、step、epoch、学习率还是更新顺序。`,hints:[`查看 #${c}。`,"运行 test_training_lab.py 并读取history。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-23",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样烘焙酸面包","珊瑚为什么会白化"]},null,2)}\n`);
