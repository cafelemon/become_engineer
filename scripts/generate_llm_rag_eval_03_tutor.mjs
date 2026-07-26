import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="llm-rag-eval-03",title="分块、重叠、来源坐标与精确引用",path="learning-paths/llm-agent/rag-eval/03-chunk-overlap-source-coordinates-citation/";
const contexts=[["overview-source-grounded-chunks","overview","可追溯分块"],["concept-chunk-boundary","concept","分块边界"],["concept-citation-coordinate","concept","引用坐标"],["example-exact-citation","example","精确引用"],["reproduce-chunk-v09","reproduce","运行分块实验"],["modify-chunk-policy","modify","修改分块策略"],["troubleshoot-chunk-citation","troubleshoot","分块引用排错"],["deepen-retrieved-data-boundary","deepen","检索数据边界"],["project-learning-assistant-v09","project","智能学习助手v0.9"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["chunk-bound","concept-chunk-boundary","为什么 chunk 要有最大字符数？","文档整篇放上下文不行吗","大chunk混入无关内容并消耗预算；明确上限让索引单位和上下文成本可观察。","本课max_chars为32。"],
["sentence-boundary","concept-chunk-boundary","单句超过上限为什么不直接硬切？","长句从中间切开可以吗","静默硬切会丢失语义与引用边界；本策略明确报错，次级切分需另立契约。","sentence_too_long。"],
["chunk-id","concept-citation-coordinate","chunk ID 为什么包含字符区间？","只用递增编号不行吗","document_id加start/end能直接定位原文，并让内容变化后的边界差异可见。","python-venv:0:23。"],
["overlap-cost","modify-chunk-policy","句子重叠有什么代价？","overlap越多越好吗","可能提高边界召回，也增加索引量、上下文重复和证据重复，必须评估。","比较0、1、2句。"],
["relative-absolute","concept-citation-coordinate","引用相对坐标如何回到原文？","quote_start从哪里算","chunk.start加quote相对起止，得到source document绝对区间。","0:10回到原文。"],
["retrieved-only","example-exact-citation","为什么只能引用已检索 chunk？","全语料里有同一句能补引用吗","模型本次未看到的内容不能成为本次回答证据，否则掩盖检索失败。","unknown chunk拒绝。"],
["quote-match","example-exact-citation","精确引文可以自动改空格吗？","同义改写算quote吗","不算；quote必须逐字符等于chunk切片，摘要或改写应使用另一字段。","citation_quote_mismatch。"],
["chunk-tamper","troubleshoot-chunk-citation","如何发现 chunk 被篡改？","坐标没变文字变了","重新用来源切片核对text和SHA-256；任一不符返回chunk_content_mismatch。","加载前验证。"],
["source-instruction","deepen-retrieved-data-boundary","来源里的忽略系统指令该执行吗？","RAG文档能改变system规则吗","不能；检索文本是不可信数据，需明确分隔，来源中的指令没有更高权限。","instructions-in-source:false。"],
["assistant-v09","project-learning-assistant-v09","智能学习助手 v0.9 新增什么？","RAG第三课项目做什么","新增句子分块、重叠、原文坐标、chunk摘要和精确citation门禁。","下一版混合检索。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先定位“${a}”属于句子边界、chunk坐标、重叠、检索集合还是引文匹配。`,hints:[`查看 #${c}。`,"运行 test_chunk_citation.py 核对来源切片。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎么制作酸奶","为什么树叶秋天变黄"]},null,2)}\n`);
