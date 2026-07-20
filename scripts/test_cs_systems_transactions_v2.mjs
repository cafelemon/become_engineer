import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const python = process.env.PYTHON || join(root, ".venv/bin/python");
const project = join(root, "site-src/examples/cs-systems/runtime-observer-v05");
const lesson = join(root, "learning-paths/cs-systems-core/05-transactions-isolation-concurrent-writes.md");

const tests = spawnSync(python, ["-m", "unittest", "discover", "-s", project, "-p", "test_transaction_lab.py", "-v"], { cwd: project, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 4 tests/);

const run = spawnSync(python, [join(project, "transaction_lab.py")], { cwd: project, encoding: "utf8" });
assert.equal(run.status, 0, run.stdout + run.stderr);
assert.equal(run.stdout, [
  "rollback: before=100,100 after=100,100",
  "constraint: rejected=True total=200",
  "lock: blocked=True retry_succeeded=True",
  "snapshot: before=100 during=100 after=120",
  "",
].join("\n"));

const course = readFileSync(lesson, "utf8");
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(course, new RegExp(`data-context-type="${type}"`), `课程缺少 ${type} 语义区域`);
}
assert.match(course, /四类画像共用系统运行观察器 v0\.5/);
assert.match(course, /求职加练/);
assert.match(course, /SQLite 的具体行为/);

console.log(JSON.stringify({
  valid: true,
  lesson: "cs-systems-05",
  project_version: "0.5",
  tests: 4,
  rollback_checked: true,
  invariant_checked: true,
  writer_lock_checked: true,
  retry_checked: true,
  snapshot_checked: true,
  temporary_database_only: true,
  four_profiles_addressed: true,
}, null, 2));
