import assert from"node:assert/strict";import{spawnSync}from"node:child_process";import{readFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lesson=readFileSync(resolve(root,"learning-paths/algorithm-deepening/08-knapsack-interval-dp-space-compression.md"),"utf8");
for(const type of["overview","concept","example","reproduce","modify","troubleshoot","project","career"])assert.match(lesson,new RegExp(`data-context-type="${type}"`),`missing ${type}`);
for(const phrase of["knapsack_dp=0,0,3,4,5,8,8,11","forward_single_item=6 correct_single_item=3","matrix_cost=4500 order=((A1A2)A3)","item-used-at-most-once,subintervals-ready"])assert.ok(lesson.includes(phrase),`missing ${phrase}`);
assert.ok(lesson.includes("零基础兴趣")&&lesson.includes("有基础求职"),"four profiles missing");
const tests=spawnSync(resolve(root,".venv/bin/python"),["-m","unittest","-v","test_structured_dp_trace.py"],{cwd:resolve(root,"site-src/examples/algorithm-deepening/pattern-lab-v08"),encoding:"utf8"});
assert.equal(tests.status,0,tests.stdout+tests.stderr);assert.match(tests.stdout+tests.stderr,/Ran 6 tests/);
console.log(JSON.stringify({valid:true,lesson_id:"algorithm-deepening-08",project:"pattern-lab-v08",tests:6,languages:["Python 3.11","C++20"],reports_match:true,capacity_order:true,interval_order:true,four_profiles_addressed:true},null,2));
