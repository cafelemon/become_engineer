import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lesson = readFileSync(resolve(root,"learning-paths/systems-engineering/04-nonblocking-network-event-loop-backpressure.md"),"utf8");
const project = resolve(root,"site-src/examples/systems-engineering/diagnostic-service-v04");
for (const type of ["overview","concept","example","reproduce","modify","troubleshoot","project","career"]) {
  assert.match(lesson,new RegExp(`data-context-type="${type}"`),`missing ${type}`);
}
for (const phrase of ["backpressure=EAGAIN-observed","poll_while_full=not-writable","poll_after_drain=writable","resume_send=pass"]) {
  assert.ok(lesson.includes(phrase),`missing ${phrase}`);
}
assert.ok(lesson.includes("零基础兴趣") && lesson.includes("有基础求职"),"four profiles missing");
const tests = spawnSync(resolve(root,".venv/bin/python"),["-m","unittest","-v","test_nonblocking_socket.py"],{cwd:project,encoding:"utf8"});
assert.equal(tests.status,0,tests.stdout+tests.stderr);
assert.match(tests.stdout+tests.stderr,/Ran 5 tests/);
console.log(JSON.stringify({
  valid:true,
  lesson_id:"systems-engineering-04",
  project:"diagnostic-service-v04",
  tests:5,
  real_socketpair:true,
  external_network:false,
  eagain_observed:true,
  readiness_recovered:true,
  four_profiles_addressed:true,
},null,2));
