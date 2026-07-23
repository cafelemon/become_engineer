import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonPath = resolve(root, "learning-paths/career-algorithm/01-fixed-io-local-judge-contract.md");
const project = resolve(root, "site-src/examples/career-algorithm/algorithm-rehearsal-v01");
const lesson = readFileSync(lessonPath, "utf8");

for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project", "career"]) {
  assert.match(lesson, new RegExp(`data-context-type="${type}"`), `missing ${type} context`);
}
for (const phrase of ["wrong-answer", "runtime-error", "timeout", "timing=excluded-from-fixed-output"]) {
  assert.ok(lesson.includes(phrase), `missing fixed contract ${phrase}`);
}
assert.ok(lesson.includes("零基础兴趣") && lesson.includes("有基础求职"), "four learner entrances missing");
assert.ok(lesson.includes("不访问外网") && lesson.includes("不代表任何企业"), "scope boundary missing");

const tests = spawnSync(
  resolve(root, ".venv/bin/python"),
  ["-m", "unittest", "-v", "test_judge_runner.py"],
  { cwd: project, encoding: "utf8" },
);
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
const testCount = (tests.stdout + tests.stderr).match(/Ran (\d+) tests?/);
assert.equal(Number(testCount?.[1]), 7, "expected seven judge tests");

const run = spawnSync(
  resolve(root, ".venv/bin/python"),
  ["judge_runner.py"],
  { cwd: project, encoding: "utf8" },
);
assert.equal(run.status, 0, run.stdout + run.stderr);
assert.equal(
  run.stdout,
  [
    "case=ordered-duplicates status=pass reason=output-matched",
    "case=negative-and-single status=pass reason=output-matched",
    "case=empty-sequence status=pass reason=output-matched",
    "summary passed=3 total=3",
    "timing=excluded-from-fixed-output",
    "",
  ].join("\n"),
);

console.log(JSON.stringify({
  valid: true,
  lesson_id: "career-algorithm-01",
  project: "algorithm-rehearsal-v01",
  tests: 7,
  real_subprocess: true,
  external_network_used: false,
  statuses: ["pass", "wrong-answer", "runtime-error", "timeout"],
  four_profiles_addressed: true,
}, null, 2));
