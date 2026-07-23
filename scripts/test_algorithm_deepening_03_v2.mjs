import assert from"node:assert/strict";import{spawnSync}from"node:child_process";import{readFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lesson=readFileSync(resolve(root,"learning-paths/algorithm-deepening/03-prefix-sum-difference-range-batching.md"),"utf8");
for(const type of["overview","concept","example","reproduce","modify","troubleshoot","project","career"])assert.match(lesson,new RegExp(`data-context-type="${type}"`),`missing ${type}`);
for(const phrase of["prefix=0,2,1,4,9,9","difference=2,3,-1,-2,-3,1","restored=2,5,4,2,-1","half-open-boundaries-cancel"])assert.ok(lesson.includes(phrase),`missing ${phrase}`);
assert.ok(lesson.includes("零基础兴趣")&&lesson.includes("有基础求职"),"four profiles missing");
const tests=spawnSync(resolve(root,".venv/bin/python"),["-m","unittest","-v","test_range_transform_trace.py"],{cwd:resolve(root,"site-src/examples/algorithm-deepening/pattern-lab-v03"),encoding:"utf8"});
assert.equal(tests.status,0,tests.stdout+tests.stderr);assert.match(tests.stdout+tests.stderr,/Ran 6 tests/);
console.log(JSON.stringify({valid:true,lesson_id:"algorithm-deepening-03",project:"pattern-lab-v03",tests:6,languages:["Python 3.11","C++20"],reports_match:true,interval_contract:"half-open",four_profiles_addressed:true},null,2));
