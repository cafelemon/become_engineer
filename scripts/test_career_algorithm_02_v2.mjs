import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lesson = readFileSync(resolve(root, "learning-paths/career-algorithm/02-timed-rehearsal-strategy-log.md"), "utf8");
const project = resolve(root, "site-src/examples/career-algorithm/algorithm-rehearsal-v02");

for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project", "career"]) {
  assert.match(lesson, new RegExp(`data-context-type="${type}"`), `missing ${type} context`);
}
for (const phrase of ["source=declared-logical-minutes", "wall_clock=excluded-from-fixed-output", "timeout", "switch"]) {
  assert.ok(lesson.includes(phrase), `missing stable contract ${phrase}`);
}
assert.ok(lesson.includes("零基础兴趣") && lesson.includes("有基础求职"), "four profiles missing");
assert.ok(lesson.includes("不评估打字速度") && lesson.includes("不代表"), "scope boundary missing");

const tests = spawnSync(resolve(root, ".venv/bin/python"), ["-m", "unittest", "-v", "test_timed_rehearsal.py"], { cwd: project, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 7 tests/);

const run = spawnSync(resolve(root, ".venv/bin/python"), ["timed_rehearsal.py"], { cwd: project, encoding: "utf8" });
assert.equal(run.status, 0, run.stdout + run.stderr);
assert.equal(run.stdout, [
  "session=rehearsal-001 budget=45 source=declared-logical-minutes",
  "checkpoints=10,25,40",
  "task=io-warmup status=completed minutes=8 evidence=passed-local-cases",
  "task=boundary-search status=switched minutes=15 evidence=no-progress-after-checkpoint",
  "task=graph-shortest status=completed minutes=18 evidence=passed-local-cases",
  "summary completed=2 switched=1 remaining=2",
  "wall_clock=excluded-from-fixed-output",
  "",
].join("\n"));

console.log(JSON.stringify({
  valid: true,
  lesson_id: "career-algorithm-02",
  project: "algorithm-rehearsal-v02",
  tests: 7,
  declared_logical_time: true,
  wall_clock_snapshot: false,
  four_profiles_addressed: true,
}, null, 2));
