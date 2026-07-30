import assert from"node:assert/strict";
import{spawnSync}from"node:child_process";
import{readFileSync}from"node:fs";
import{resolve}from"node:path";

const root=resolve(import.meta.dirname,"..");
const lesson=readFileSync(resolve(root,"learning-paths/llm-agent/agent-engineering/02-memory-provenance-consent-ttl-context-budget.md"),"utf8");
for(const type of["overview","concept","example","reproduce","modify","troubleshoot","project"])assert.match(lesson,new RegExp(`data-context-type="${type}"`));
for(const phrase of[
  "working:ephemeral,facts:persistent",
  "stored=4,eligible=1",
  "used-chars:29,limit-chars:29",
  "unconsented:true,expired:true,other-subject:true",
  "subject-scoped,budget-bounded",
  "零基础兴趣",
  "有基础求职",
  "本模块无招聘信号"
])assert.ok(lesson.includes(phrase),phrase);
const tests=spawnSync("python3",["-m","unittest","-v","test_memory_context.py"],{
  cwd:resolve(root,"site-src/examples/agent-engineering/intelligent-learning-assistant-v20"),
  encoding:"utf8"
});
assert.equal(tests.status,0,tests.stdout+tests.stderr);
assert.match(tests.stdout+tests.stderr,/Ran 8 tests/);
const report=spawnSync("python3",["memory_context.py"],{
  cwd:resolve(root,"site-src/examples/agent-engineering/intelligent-learning-assistant-v20"),
  encoding:"utf8"
});
assert.equal(report.status,0,report.stderr);
assert.match(report.stdout,/eligible=1/);
console.log(JSON.stringify({valid:true,lesson_id:"agent-engineering-02",tests:8,storage:"sqlite",context_budget:true},null,2));
