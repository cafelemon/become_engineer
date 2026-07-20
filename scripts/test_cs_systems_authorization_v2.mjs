import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const python = process.env.PYTHON || join(root, ".venv/bin/python");
const project = join(root, "site-src/examples/cs-systems/runtime-observer-v06");
const lesson = join(root, "learning-paths/cs-systems-core/06-identity-authorization-least-privilege.md");

const tests = spawnSync(python, ["-m", "unittest", "discover", "-s", project, "-p", "test_authorization_lab.py", "-v"], { cwd: project, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 5 tests/);

const run = spawnSync(python, [join(project, "authorization_lab.py")], { cwd: project, encoding: "utf8" });
assert.equal(run.status, 0, run.stdout + run.stderr);
assert.equal(run.stdout, [
  "anonymous: status=401 challenge=Bearer",
  "viewer: action=status:read status=200",
  "denied: principal=viewer action=diagnostic:run status=403",
  "operator: action=diagnostic:run status=200",
  "audit: entries=4 raw_token_logged=False",
  "",
].join("\n"));

const source = readFileSync(join(project, "authorization_lab.py"), "utf8");
assert.doesNotMatch(source, /demo[-_]?(viewer|operator)[-_]?token/i, "示例不得硬编码演示令牌");

const course = readFileSync(lesson, "utf8");
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(course, new RegExp(`data-context-type="${type}"`), `课程缺少 ${type} 语义区域`);
}
assert.match(course, /四类画像共用系统运行观察器 v0\.6/);
assert.match(course, /求职加练/);
assert.match(course, /不自制 JWT/);

console.log(JSON.stringify({
  valid: true,
  lesson: "cs-systems-06",
  project_version: "0.6",
  tests: 5,
  authentication_checked: true,
  authorization_checked: true,
  least_privilege_checked: true,
  deny_by_default_checked: true,
  raw_token_storage_checked: true,
  audit_redaction_checked: true,
  external_service_used: false,
  four_profiles_addressed: true,
}, null, 2));
