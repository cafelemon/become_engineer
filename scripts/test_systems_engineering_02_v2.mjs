import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lesson = readFileSync(resolve(root, "learning-paths/systems-engineering/02-signals-process-supervision-graceful-shutdown.md"), "utf8");
const project = resolve(root, "site-src/examples/systems-engineering/diagnostic-service-v02");
const source = readFileSync(resolve(project, "signal_supervisor.cpp"), "utf8");

for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project", "career"]) {
  assert.match(lesson, new RegExp(`data-context-type="${type}"`), `missing ${type} context`);
}
for (const phrase of ["signal_handler=notification-only", "worker_reaped=yes", "supervision_result=pass"]) {
  assert.ok(lesson.includes(phrase), `missing fixed contract ${phrase}`);
}
assert.match(source, /extern "C" void notify_signal[\s\S]*::write/);
assert.doesNotMatch(source.match(/extern "C" void notify_signal[\s\S]*?\n\}/)?.[0] ?? "", /std::|waitpid|malloc|new /);
assert.ok(lesson.includes("零基础兴趣") && lesson.includes("有基础求职"), "four profiles missing");

const tests = spawnSync(resolve(root, ".venv/bin/python"), ["-m", "unittest", "-v", "test_signal_supervisor.py"], { cwd: project, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 5 tests/);

console.log(JSON.stringify({
  valid: true,
  lesson_id: "systems-engineering-02",
  project: "diagnostic-service-v02",
  tests: 5,
  real_sigterm: true,
  child_reaped: true,
  handler_notification_only: true,
  four_profiles_addressed: true,
}, null, 2));
