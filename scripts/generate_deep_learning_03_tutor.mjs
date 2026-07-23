import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
const root = resolve(import.meta.dirname, ".."), lessonId = "deep-learning-03";
const title = "交叉熵、自动微分、反向传播与梯度核查";
const path = "learning-paths/ai-foundation/deep-learning/03-cross-entropy-autograd-backprop-gradient-check/";
const contexts = [
  ["overview-gradient-contract","overview","梯度核查结果"],["concept-cross-entropy-loss","concept","交叉熵损失"],
  ["concept-backprop-chain-rule","concept","反向传播链式法则"],["example-finite-difference","example","有限差分核查"],
  ["reproduce-gradient-v03","reproduce","运行梯度实验"],["modify-gradient-check","modify","修改梯度实验"],
  ["troubleshoot-gradient-contract","troubleshoot","梯度排错"],["deepen-gradient-accumulation","deepen","梯度累加"],
  ["project-diagnosable-network-v03","project","可诊断网络 v0.3"],
].map(([id,type,t])=>({id,type,title:t,anchor:`#${id}`}));
const defs = [
  ["cross-entropy","concept-cross-entropy-loss","交叉熵为什么直接接收 logits？","softmax 后还能传 CrossEntropyLoss 吗","CrossEntropyLoss 内部稳定组合 log-softmax 与负对数似然，应直接接收未归一化 logits。","v0.3 输入 [8,2] logits。"],
  ["class-target","concept-cross-entropy-loss","分类目标为什么必须是 int64 索引？","交叉熵 target dtype 是什么","单标签分类目标指向每行 logits 的类别列，使用 int64 类别索引。","targets shape 为 [8]。"],
  ["backward","concept-backprop-chain-rule","loss.backward 做了什么？","backward 怎样得到参数梯度","它从标量 loss 出发，沿计算图反向应用局部导数与链式法则，把结果累加到叶子参数 grad。","四个参数都得到同 shape 梯度。"],
  ["grad-shape","concept-backprop-chain-rule","参数梯度的 shape 为什么相同？","weight grad 维度怎么看","每个梯度元素对应同位置参数的局部变化率，所以 gradient shape 与 parameter shape 对齐。","fc1.weight 与 grad 都是 [4,2]。"],
  ["finite-difference","example-finite-difference","有限差分怎样核查 autograd？","数值梯度怎么算","中心差分用 L(w+epsilon)-L(w-epsilon) 除以 2epsilon，近似当前点局部导数。","非零参数绝对误差为0.000008。"],
  ["epsilon","modify-gradient-check","有限差分 epsilon 越小越好吗？","数值梯度步长怎么选","不是；过大有截断误差，过小会被浮点舍入和相消放大。","比较1e-1、1e-3和1e-7。"],
  ["accumulation","deepen-gradient-accumulation","为什么两次 backward 梯度会翻倍？","grad 默认会累加吗","PyTorch 默认把新梯度加到现有 grad，而不是覆盖；相同前向两次会得到2倍。","v0.3 固定输出2.000x。"],
  ["zero-grad","deepen-gradient-accumulation","zero_grad set_to_none 有什么作用？","每轮为什么清梯度","它移除旧梯度缓冲，防止普通训练把不同 step 意外累加，并区分无梯度与零梯度。","下一轮 backward 前清除。"],
  ["graph-lifetime","troubleshoot-gradient-contract","为什么同一个 loss 不能默认 backward 两次？","Trying to backward through graph a second time","普通 backward 后中间图会释放；需要新梯度时重新 forward，除非确有理由保留图。","不要习惯性 retain_graph。"],
  ["gradient-v03","project-diagnosable-network-v03","可诊断神经网络 v0.3 新增了什么？","深度学习第三课项目做什么","它新增交叉熵、backward、梯度范数、有限差分、累加清零和8项真实测试。","尚未执行 optimizer step。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先判断“${a}”涉及 loss、计算图、数值梯度、累加还是清零。`,hints:[`查看 #${c}。`,"运行 test_gradient_lab.py 并读取梯度证据。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-23",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);
mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});
writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);
writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样给绿植换盆","为什么海水是咸的"]},null,2)}\n`);
