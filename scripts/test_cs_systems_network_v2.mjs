import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const python = process.env.PYTHON || join(root, ".venv/bin/python");
const project = join(root, "site-src/examples/cs-systems/runtime-observer-v04");
const lesson = join(root, "learning-paths/cs-systems-core/04-local-network-port-http.md");

const tests = spawnSync(python, ["-m", "unittest", "discover", "-s", project, "-p", "test_local_network_lab.py", "-v"], { cwd: project, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 4 tests/);

const run = spawnSync(python, [join(project, "local_network_lab.py")], { cwd: project, encoding: "utf8" });
assert.equal(run.status, 0, run.stdout + run.stderr);
assert.equal(run.stdout, [
  "tcp: connected=True loopback=True",
  'http: status=200 body={"status":"ok"}',
  "http error: status=404",
  "timeout: timed_out=True cleaned_up=True",
  "",
].join("\n"));

const course = readFileSync(lesson, "utf8");
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(course, new RegExp(`data-context-type="${type}"`), `课程缺少 ${type} 语义区域`);
}
assert.match(course, /四类画像共用系统运行观察器 v0\.4/);
assert.match(course, /求职加练/);
assert.match(course, /127\.0\.0\.1:0/);

console.log(JSON.stringify({
  valid: true,
  lesson: "cs-systems-04",
  project_version: "0.4",
  tests: 4,
  loopback_only: true,
  ephemeral_port_checked: true,
  http_status_checked: true,
  deterministic_timeout_checked: true,
  cleanup_checked: true,
  external_network_used: false,
  four_profiles_addressed: true,
}, null, 2));
