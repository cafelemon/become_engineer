import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const python = process.env.PYTHON || join(root, ".venv/bin/python");
const project = join(root, "site-src/examples/cs-systems/runtime-observer-v03");
const lesson = join(root, "learning-paths/cs-systems-core/03-memory-file-resource-lifecycle.md");

const tests = spawnSync(python, ["-m", "unittest", "discover", "-s", project, "-p", "test_resource_lifecycle.py", "-v"], { cwd: project, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 4 tests/);

const run = spawnSync(python, [join(project, "resource_lifecycle.py")], { cwd: project, encoding: "utf8" });
assert.equal(run.status, 0, run.stdout + run.stderr);
assert.equal(run.stdout, [
  "memory: retained=True released=True traced_drop=True",
  "file: open_inside=True closed_outside=True",
  "failure: closed_after_error=True",
  "temporary: removed=True",
  "",
].join("\n"));

const course = readFileSync(lesson, "utf8");
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(course, new RegExp(`data-context-type="${type}"`), `课程缺少 ${type} 语义区域`);
}
assert.match(course, /四类画像共用系统运行观察器 v0\.3/);
assert.match(course, /求职加练/);
assert.match(course, /不等于操作系统 RSS/);

console.log(JSON.stringify({
  valid: true,
  lesson: "cs-systems-03",
  project_version: "0.3",
  tests: 4,
  reference_lifetime_checked: true,
  normal_close_checked: true,
  exceptional_close_checked: true,
  temporary_cleanup_checked: true,
  network_used: false,
  four_profiles_addressed: true,
}, null, 2));
