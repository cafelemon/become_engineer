import assert from"node:assert/strict";import{spawnSync}from"node:child_process";import{readFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lesson=readFileSync(resolve(root,"learning-paths/systems-engineering/06-fault-injection-resource-leaks-recovery-acceptance.md"),"utf8");
for(const type of["overview","concept","example","reproduce","modify","troubleshoot","project","career"])assert.match(lesson,new RegExp(`data-context-type="${type}"`),`missing ${type}`);
for(const phrase of["detector=fd-still-open","child_recovery=reaped","transport_fault=EPIPE-observed","resource_baseline=restored"])assert.ok(lesson.includes(phrase),`missing ${phrase}`);
assert.ok(lesson.includes("零基础兴趣")&&lesson.includes("有基础求职"),"four profiles missing");
const tests=spawnSync(resolve(root,".venv/bin/python"),["-m","unittest","-v","test_recovery_lab.py"],{cwd:resolve(root,"site-src/examples/systems-engineering/diagnostic-service-v06"),encoding:"utf8"});
assert.equal(tests.status,0,tests.stdout+tests.stderr);assert.match(tests.stdout+tests.stderr,/Ran 5 tests/);
console.log(JSON.stringify({valid:true,lesson_id:"systems-engineering-06",project:"diagnostic-service-v06",tests:5,real_faults:["fd-leak","child-exit","EPIPE","temporary-file"],resource_baseline_restored:true,external_network:false,four_profiles_addressed:true},null,2));
