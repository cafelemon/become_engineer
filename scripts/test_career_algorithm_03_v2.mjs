import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lesson = readFileSync(resolve(root, "learning-paths/career-algorithm/03-failure-categories-minimal-counterexamples-regression.md"), "utf8");
const project = resolve(root, "site-src/examples/career-algorithm/algorithm-rehearsal-v03");

for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project", "career"]) {
  assert.match(lesson, new RegExp(`data-context-type="${type}"`), `missing ${type} context`);
}
for (const phrase of ["contract", "boundary", "implementation", "complexity", "strategy", "counterexample-candidate-not-proof-of-global-minimality"]) {
  assert.ok(lesson.includes(phrase), `missing retrospective contract ${phrase}`);
}
assert.ok(lesson.includes("零基础兴趣") && lesson.includes("有基础求职"), "four profiles missing");
assert.ok(lesson.includes("不预测录用概率") && lesson.includes("不代表"), "scope boundary missing");

const tests = spawnSync(
  resolve(root, ".venv/bin/python"),
  ["-m", "unittest", "-v", "test_regression_cases.py", "test_retrospective.py"],
  { cwd: project, encoding: "utf8" },
);
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 12 tests/);

const run = spawnSync(resolve(root, ".venv/bin/python"), ["retrospective.py"], { cwd: project, encoding: "utf8" });
assert.equal(run.status, 0, run.stdout + run.stderr);
assert.ok(run.stdout.includes("coverage categories=boundary,complexity,contract,implementation,strategy"));
assert.ok(run.stdout.includes("gate=pass records=5"));
assert.ok(run.stdout.endsWith("claim=counterexample-candidate-not-proof-of-global-minimality\n"));

console.log(JSON.stringify({
  valid: true,
  lesson_id: "career-algorithm-03",
  project: "algorithm-rehearsal-v03",
  regression_tests: 5,
  retrospective_tests: 7,
  categories: 5,
  global_minimality_claimed: false,
  four_profiles_addressed: true,
}, null, 2));
