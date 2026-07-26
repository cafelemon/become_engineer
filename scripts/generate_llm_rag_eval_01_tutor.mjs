import{mkdirSync,writeFileSync}from"node:fs";import{resolve}from"node:path";const root=resolve(import.meta.dirname,".."),lessonId="llm-rag-eval-01",title="语料文档契约、来源身份与可复现索引",path="learning-paths/llm-agent/rag-eval/01-corpus-document-source-reproducible-index/";
const contexts=[["overview-reproducible-corpus","overview","可复现语料"],["concept-document-identity","concept","文档身份"],["concept-hash-trust-boundary","concept","哈希与信任边界"],["example-canonical-snapshot","example","规范索引快照"],["reproduce-corpus-v07","reproduce","运行语料实验"],["modify-corpus-schema","modify","修改语料Schema"],["troubleshoot-corpus-index","troubleshoot","语料索引排错"],["deepen-corpus-versioning","deepen","语料版本深化"],["project-learning-assistant-v07","project","智能学习助手v0.7"]].map(([id,type,title])=>({id,type,title,anchor:`#${id}`}));
const defs=[
["document-id","concept-document-identity","为什么文档不能用数组下标做身份？","第0篇文档不能当ID吗","导入顺序会变化；稳定document_id才能让索引、chunk和引用持续指向同一文档。","ID使用稳定slug。"],
["source-uri","concept-document-identity","source URI 为什么必须带锚点？","只有课程URL够吗","锚点把引用收窄到明确来源位置，后续才能回到原文核查。","course URI加anchor。"],
["content-hash","concept-hash-trust-boundary","content SHA-256 能证明什么？","哈希能证明内容是真的吗","只能发现保存前后内容是否一致，不能证明来源可信、事实正确或有授权。","hash不等于trust。"],
["corpus-fingerprint","example-canonical-snapshot","语料 fingerprint 覆盖哪些字段？","只hash正文够吗","覆盖Schema、corpus ID和每篇文档的ID、标题、来源、时间、正文与摘要。","任一身份字段变化都会改变。"],
["canonical-order","example-canonical-snapshot","为什么先按 document_id 排序？","输入重排不应该变版本吗","顺序不是语义变化；规范排序消除无意义差异，让同一语料得到同一指纹。","reordered fingerprint equal。"],
["duplicate-source","troubleshoot-corpus-index","两个文档ID能指向同一来源吗？","重复source URI怎么处理","本契约默认拒绝，避免同一来源被重复计权和引用身份分裂。","duplicate_source_uri。"],
["atomic-index","reproduce-corpus-v07","索引快照为什么原子替换？","直接write_text不行吗","中途崩溃可能留下半份JSON；同目录临时写、fsync再replace减少撕裂窗口。","测试确认无临时残留。"],
["schema-version","modify-corpus-schema","增加字段为何要升级 Schema？","loader忽略新字段可以吗","不能让读写双方对身份字段理解不同；新字段需显式版本和迁移策略。","额外字段默认拒绝。"],
["corpus-eval-link","deepen-corpus-versioning","评估报告为什么要记录 corpus fingerprint？","模型没变还需语料版本吗","语料变化也会改变检索和答案；没有语料身份就不能复现实验。","报告关联查询集和检索配置。"],
["assistant-v07","project-learning-assistant-v07","智能学习助手 v0.7 新增什么？","RAG第一课项目做什么","新增文档/来源契约、内容摘要、规范语料指纹、原子保存与加载校验。","下一版BM25。"],
];
const cards=defs.map(([id,c,q,a,answer,example],i)=>({id,lesson_id:lessonId,context_id:c,question:q,aliases:[a],keywords:[...new Set(`${q} ${a}`.replace(/[？?，、/]/g," ").split(/\s+/).filter(Boolean))],diagnostic:`先定位“${a}”属于文档身份、来源、摘要、快照还是持久化。`,hints:[`查看 #${c}。`,"运行 test_corpus_index.py 检查稳定错误码。"],example,answer,source:{label:contexts.find(x=>x.id===c).title,href:`#${c}`},updated_at:"2026-07-26",recommended:i<8}));
const cases=defs.flatMap(([id,,q,a])=>[{query:q.replace("？",""),expected_card:id},{query:a,expected_card:id}]);mkdirSync(resolve(root,"site-src/data/tutor"),{recursive:true});mkdirSync(resolve(root,"tests/tutor"),{recursive:true});writeFileSync(resolve(root,`site-src/data/tutor/${lessonId}.json`),`${JSON.stringify({version:2,lesson:{id:lessonId,title,path},contexts,cards},null,2)}\n`);writeFileSync(resolve(root,`tests/tutor/${lessonId}-search.json`),`${JSON.stringify({lesson_id:lessonId,cases,unknown:["怎么清洗羊毛大衣","月球为什么有环形山"]},null,2)}\n`);
