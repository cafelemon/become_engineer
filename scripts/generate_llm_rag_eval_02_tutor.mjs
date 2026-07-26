import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="llm-rag-eval-02",title="倒排索引、BM25、Top-k 与稳定排序",path="learning-paths/llm-agent/rag-eval/02-inverted-index-bm25-top-k-stable-ranking/";
const contexts=[["overview-bm25-baseline","overview","BM25关键词基线"],["concept-inverted-index","concept","倒排索引"],["concept-bm25-score","concept","BM25分数"],["example-tokenizer-contract","example","Tokenizer契约"],["reproduce-bm25-v08","reproduce","运行BM25实验"],["modify-bm25-tokenizer","modify","修改Tokenizer"],["troubleshoot-bm25-ranking","troubleshoot","BM25排错"],["deepen-lexical-baseline","deepen","关键词基线深化"],["project-learning-assistant-v08","project","智能学习助手v0.8"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["inverted-index","concept-inverted-index","倒排索引保存什么？","posting list是什么","保存term到文档ID集合的映射，同时每篇文档保存term frequency和长度。","查询无需扫描所有正文。"],
["idf","concept-bm25-score","IDF 为什么让稀有词权重更高？","df越小分越高吗","在其他条件相同时，出现文档更少的term更能区分结果，BM25的IDF更高。","rare高于common。"],
["tf-saturation","concept-bm25-score","BM25 为什么不让词频线性增长？","重复100次会得100倍吗","k1让term frequency收益逐渐饱和，避免堆词无限放大。","固定k1为1.2。"],
["length-normalization","concept-bm25-score","参数 b 控制什么？","长文档为什么要归一","b控制文档长度相对平均长度的归一强度；0不归一，1完全使用该项。","本课b等于0.75。"],
["han-tokenizer","example-tokenizer-contract","本课中文 tokenizer 有什么限制？","单字二元组算中文分词吗","只生成汉字单字和相邻二元组，能复现但不是通用分词，可能产生公共单字噪声。","general-segmentation:false。"],
["stable-tie","troubleshoot-bm25-ranking","BM25 同分如何稳定排序？","score一样每次顺序不同","先按score降序，再按稳定document_id升序。","alpha排在zeta前。"],
["empty-query","reproduce-bm25-v08","未知词查询应该返回什么？","没命中也返回零分文档吗","返回空结果；零分文档排除，不能用任意内容填满Top-k。","query-unknown=none。"],
["score-explain","troubleshoot-bm25-ranking","如何解释一篇文档的 BM25 分数？","总分从哪里来","展开每个去重query term的IDF、tf与长度归一贡献，求和必须等于总分。","explanation可核对。"],
["lexical-baseline","deepen-lexical-baseline","向量检索前为什么保留 BM25？","embedding更智能还要关键词吗","BM25无模型费用、词面精确且可解释，是判断向量或混合检索是否真正改进的基线。","同一查询集比较。"],
["assistant-v08","project-learning-assistant-v08","智能学习助手 v0.8 新增什么？","RAG第二课项目做什么","新增Tokenizer、倒排索引、BM25、Top-k、稳定并列和term贡献解释。","下一版分块引用。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先定位“${a}”属于token、posting、IDF、长度归一还是排序。`,hints:[`查看 #${c}。`,"运行 test_bm25_retriever.py 并查看explain。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎样给绿植换盆","为什么海水是咸的"]},null,2)}\n`);
