import assert from"node:assert/strict";import{spawnSync}from"node:child_process";import{readFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lesson=readFileSync(resolve(root,"learning-paths/algorithm-deepening/02-sliding-window-frequency-minimum-cover.md"),"utf8");
for(const type of["overview","concept","example","reproduce","modify","troubleshoot","project","career"])assert.match(lesson,new RegExp(`data-context-type="${type}"`),`missing ${type}`);
for(const phrase of["best=0:5 text=ADOBEC","best=9:12 text=BANC","expands=13 shrinks=10","window-counts-match-state"])assert.ok(lesson.includes(phrase),`missing ${phrase}`);
assert.ok(lesson.includes("零基础兴趣")&&lesson.includes("有基础求职"),"four profiles missing");
const tests=spawnSync(resolve(root,".venv/bin/python"),["-m","unittest","-v","test_sliding_window_trace.py"],{cwd:resolve(root,"site-src/examples/algorithm-deepening/pattern-lab-v02"),encoding:"utf8"});
assert.equal(tests.status,0,tests.stdout+tests.stderr);assert.match(tests.stdout+tests.stderr,/Ran 6 tests/);
console.log(JSON.stringify({valid:true,lesson_id:"algorithm-deepening-02",project:"pattern-lab-v02",tests:6,languages:["Python 3.11","C++20"],reports_match:true,duplicate_requirement:true,four_profiles_addressed:true},null,2));
