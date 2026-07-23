import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessonPath = resolve(
  root,
  "learning-paths/direction-choice/01-first-verifiable-project-direction-trials.md",
);
const project = resolve(
  root,
  "site-src/examples/direction-choice/verification-portfolio-v01",
);
const lesson = readFileSync(lessonPath, "utf8");

for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(lesson, new RegExp(`data-context-type="${type}"`));
}
for (const required of [
  "direction-choice-01",
  "## 四类学习者入口",
  "## 完成检查",
  "## 来源与版本",
  "## 下一步",
  "two-week-trial-not-career-conclusion",
]) {
  assert.ok(lesson.includes(required), `lesson is missing ${required}`);
}

const python = resolve(root, ".venv/bin/python");
const tests = spawnSync(
  python,
  ["-m", "unittest", "-v", "test_portfolio_check.py"],
  { cwd: project, encoding: "utf8" },
);
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stderr, /Ran 6 tests/);

const evidenceTests = spawnSync(
  python,
  ["-m", "unittest", "discover", "-s", "evidence", "-p", "test_study_summary.py", "-v"],
  { cwd: project, encoding: "utf8" },
);
assert.equal(evidenceTests.status, 0, evidenceTests.stdout + evidenceTests.stderr);
assert.match(evidenceTests.stderr, /Ran 3 tests/);

const run = spawnSync(
  python,
  ["portfolio_check.py", "--manifest", "portfolio.json", "--workspace", "."],
  { cwd: project, encoding: "utf8" },
);
assert.equal(run.status, 0, run.stdout + run.stderr);
for (const expected of [
  "evidence code=pass",
  "evidence tests=pass",
  "evidence readme=pass",
  "evidence reflection=pass",
  "gate=pass",
  "next_experiments=application-engineering,algorithm",
  "decision=two-week-trial-not-career-conclusion",
]) {
  assert.ok(run.stdout.includes(expected), `fixed output is missing ${expected}`);
}

const tutor = JSON.parse(readFileSync(resolve(root, "site-src/data/tutor/direction-choice-01.json"), "utf8"));
const fixture = JSON.parse(readFileSync(resolve(root, "tests/tutor/direction-choice-01-search.json"), "utf8"));
assert.equal(tutor.cards.length, 10);
assert.equal(fixture.cases.length, 20);
assert.equal(fixture.unknown.length, 2);

console.log(JSON.stringify({
  valid: true,
  lesson_id: "direction-choice-01",
  project: "verification-portfolio-v01",
  project_tests: 3,
  checker_tests: 6,
  evidence_kinds: 4,
  route_trials_are_reversible: true,
  external_network_used: false,
  four_profiles_addressed: true,
}, null, 2));
