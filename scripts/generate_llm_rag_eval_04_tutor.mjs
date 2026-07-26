import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="llm-rag-eval-04",title="Embedding 适配器、余弦相似度与 RRF 混合检索",path="learning-paths/llm-agent/rag-eval/04-embedding-cosine-rrf-hybrid-retrieval/";
const contexts=[["overview-hybrid-retrieval","overview","混合检索"],["concept-embedding-boundary","concept","Embedding边界"],["concept-cosine-ranking","concept","余弦排序"],["example-rrf-fusion","example","RRF融合"],["reproduce-hybrid-v10","reproduce","运行混合检索"],["modify-ranking-fusion","modify","修改排序融合"],["troubleshoot-vector-fusion","troubleshoot","向量融合排错"],["deepen-semantic-claim-boundary","deepen","语义声明边界"],["project-learning-assistant-v10","project","智能学习助手v0.10"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["adapter-boundary","concept-embedding-boundary","为什么要做 Embedding adapter？","向量接口为什么隔离","让检索核心依赖稳定批次契约，而非某个SDK、凭据或模型；provider可替换。","Protocol只声明embed。"],
["batch-shape","concept-embedding-boundary","返回向量数量错了怎么办？","embedding少返回一条","拒绝adapter_shape_mismatch，不能把后续向量错配到别的chunk。","输入输出一一对应。"],
["vector-validation","concept-cosine-ranking","向量进入索引前检查什么？","NaN零向量不同维怎么办","检查数字且非bool、有限、同维、非空和非零范数。","坏向量先拒绝。"],
["cosine","concept-cosine-ranking","余弦相似度比较什么？","向量长度会影响cosine吗","比较方向；点积除以两边范数，正比例向量相似度为1。","(1,1)与(2,2)。"],
["stable-vector-tie","concept-cosine-ranking","向量同分怎么稳定排序？","cosine一样谁先","先按score降序，再按稳定chunk ID升序。","chunk-a先于chunk-b。"],
["rrf-ranks","example-rrf-fusion","RRF 为什么不用原始分数？","BM25和cosine可以直接加吗","两种分数尺度不可直接比较；RRF按各自名次贡献1/(k+rank)。","固定k为60。"],
["rrf-duplicates","troubleshoot-vector-fusion","同一路排名重复 chunk 会怎样？","一个ID出现两次能多加分吗","不能；重复会虚增支持度，因此确定性拒绝duplicate_ranked_chunk。","每路ID唯一。"],
["fixture-honesty","deepen-semantic-claim-boundary","固定二维向量能证明语义检索吗？","fixture向量效果好算真实效果吗","不能；只证明接口、校验、cosine与排序，真实语义需真实模型和评估集。","semantic-claim:false。"],
["vector-logging","deepen-semantic-claim-boundary","向量和查询可以完整打日志吗？","排错记录embedding原值吗","本课允许chunk ID、分数、名次和错误码，不记录查询、正文或向量原值。","降低数据暴露。"],
["assistant-v10","project-learning-assistant-v10","智能学习助手 v0.10 新增什么？","RAG第四课项目做什么","新增embedding边界、严格向量索引、cosine Top-k与RRF混合排序。","下一版证据回答。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先定位“${a}”属于适配器、向量校验、cosine排序、RRF还是语义声明。`,hints:[`查看 #${c}。`,"运行 test_hybrid_retriever.py 核对固定排名。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎么烤制面包","猫为什么喜欢纸箱"]},null,2)}\n`);
