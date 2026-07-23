import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lesson = readFileSync(resolve(root, "learning-paths/ai-foundation/deep-learning/02-linear-layer-activation-parameters-forward-graph.md"), "utf8");
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(lesson, new RegExp(`data-context-type="${type}"`));
}
for (const phrase of [
  "fc1=weight:4x2,bias:4",
  "forward=8x2->8x4->8x4->8x2",
  "parameters=trainable:22,tensors:4",
  "probability_rows_sum_one=true",
  "module-registered,parameter-shapes-explicit,forward-batch-preserved,no-training-yet",
]) assert.ok(lesson.includes(phrase), `missing fixed contract: ${phrase}`);
for (const phrase of ["nn.Module", "logits", "零基础兴趣", "有基础求职", "PyTorch 2.13.0"]) {
  assert.ok(lesson.includes(phrase), `missing lesson phrase: ${phrase}`);
}
const python = process.env.DL_PYTHON || resolve(root, ".venv/bin/python");
const tests = spawnSync(python, ["-m", "unittest", "-v", "test_forward_lab.py"], {
  cwd: resolve(root, "site-src/examples/deep-learning/diagnosable-neural-network-v02"),
  encoding: "utf8",
  env: process.env,
});
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 8 tests/);
console.log(JSON.stringify({ valid: true, lesson_id: "deep-learning-02", tests: 8, parameters: 22, forward_trace: true }, null, 2));
