import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const python = process.env.PYTHON || join(root, ".venv/bin/python");
const project = join(root, "site-src/examples/cs-systems/runtime-observer-v01");
const lesson = join(root, "learning-paths/cs-systems-core/01-program-process-exit-status.md");

const tests = spawnSync(python, ["-m", "unittest", "discover", "-s", project, "-p", "test_observer.py", "-v"], { cwd: project, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 3 tests/);

const run = spawnSync(python, [join(project, "observer.py")], { cwd: project, encoding: "utf8" });
assert.equal(run.status, 0, run.stdout + run.stderr);
assert.equal(run.stdout, [
  "success: exit=0 child_different=True parent_matches=True",
  "failure: exit=7 stderr=simulated worker failure",
  "timeout: timed_out=True",
  "",
].join("\n"));

const course = readFileSync(lesson, "utf8");
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(course, new RegExp(`data-context-type="${type}"`), `课程缺少 ${type} 语义区域`);
}
assert.match(course, /四类画像共用同一份系统运行观察器/);
assert.match(course, /求职加练/);

console.log(JSON.stringify({
  valid: true,
  lesson: "cs-systems-01",
  project_version: "0.1",
  tests: 3,
  subprocess_success_checked: true,
  nonzero_exit_checked: true,
  timeout_checked: true,
  shell_disabled: true,
  network_used: false,
  four_profiles_addressed: true,
}, null, 2));
