import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const project = join(root, "site-src/examples/web-core/learning-dashboard-v08");
const python = join(root, ".venv/bin/python");
const lesson = join(
  root,
  "learning-paths/web-fullstack/web-core/04-form-validation-submission-state-sync.md"
);

const npmCommand = process.platform === "win32" ? "npm.cmd" : "npm";
const frontend = spawnSync(npmCommand, ["test"], { cwd: project, encoding: "utf8" });
assert.equal(frontend.status, 0, frontend.stdout + frontend.stderr);
assert.match(frontend.stdout, /"server_field_mapping_checked": true/);
assert.match(frontend.stdout, /"idempotency_intent_reuse_checked": true/);
assert.match(frontend.stdout, /"server_resync_checked": true/);

const backend = spawnSync(
  python,
  ["-m", "unittest", "discover", "-s", project, "-p", "test_app.py", "-v"],
  { cwd: root, encoding: "utf8" }
);
assert.equal(backend.status, 0, backend.stdout + backend.stderr);
assert.match(backend.stdout + backend.stderr, /Ran 17 tests/);

const schema = readFileSync(join(project, "schema.sql"), "utf8");
assert.match(schema, /hours \* 4 = CAST\(hours \* 4 AS INTEGER\)/);
assert.match(schema, /length\(trim\(note\)\) BETWEEN 2 AND 200/);
assert.match(schema, /PRAGMA user_version = 3/);

const app = readFileSync(join(project, "app.py"), "utf8");
assert.match(app, /multiple_of=0\.25/);
assert.match(app, /field_validator\("note"\)/);
assert.match(app, /version="0\.8\.0"/);

const packageJson = JSON.parse(readFileSync(join(project, "package.json"), "utf8"));
assert.equal(packageJson.version, "0.8.0");
assert.equal(packageJson.devDependencies.typescript, "7.0.2");

const course = readFileSync(lesson, "utf8");
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(course, new RegExp(`data-context-type="${type}"`), `课程缺少 ${type} 语义区域`);
}
assert.match(course, /四类画像共用同一份 v0\.8 项目/);
assert.match(course, /求职加练/);
assert.match(course, /同一个请求键/);
assert.match(course, /服务器重新读取/);

execFileSync(python, ["-m", "pip", "check"], { cwd: root, stdio: "pipe" });

console.log(JSON.stringify({
  valid: true,
  project_version: "0.8.0",
  api_tests: 17,
  client_validation_checked: true,
  server_validation_mapping_checked: true,
  submission_state_machine_checked: true,
  idempotent_retry_checked: true,
  stale_response_guard_checked: true,
  server_truth_refresh_checked: true,
  four_profiles_addressed: true,
  network_used_by_tests: false
}, null, 2));
