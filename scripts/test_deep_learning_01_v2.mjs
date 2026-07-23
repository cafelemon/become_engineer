import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonPath = resolve(root, "learning-paths/ai-foundation/deep-learning/01-tensor-shape-dtype-device-contract.md");
const lesson = readFileSync(lessonPath, "utf8");

for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(lesson, new RegExp(`data-context-type="${type}"`));
}
for (const phrase of [
  "rows=96,features=2,classes=0:48,1:48",
  "inputs=shape:96x2,dtype:float32,device:cpu",
  "targets=shape:96,dtype:int64,device:cpu",
  "linear_contract=8x2 @ 2x3 + 3 -> 8x3",
  "feature-rank2,target-rank1,row-aligned,cpu-deterministic",
]) {
  assert.ok(lesson.includes(phrase), `missing fixed contract: ${phrase}`);
}
for (const phrase of ["广播", "非有限值", "零基础兴趣", "有基础求职", "PyTorch 2.13.0"]) {
  assert.ok(lesson.includes(phrase), `missing lesson phrase: ${phrase}`);
}

const python = process.env.DL_PYTHON || resolve(root, ".venv/bin/python");
const tests = spawnSync(python, ["-m", "unittest", "-v", "test_tensor_lab.py"], {
  cwd: resolve(root, "site-src/examples/deep-learning/diagnosable-neural-network-v01"),
  encoding: "utf8",
  env: process.env,
});
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 8 tests/);

console.log(JSON.stringify({
  valid: true,
  lesson_id: "deep-learning-01",
  tests: 8,
  torch: "2.13.0",
  cpu_offline: true,
  tensor_contract: true,
}, null, 2));
