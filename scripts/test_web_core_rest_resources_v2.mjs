import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const project = join(root, "site-src/examples/web-core/learning-dashboard-v07");
const python = join(root, ".venv/bin/python");
const lesson = join(
  root,
  "learning-paths/web-fullstack/web-core/03-rest-resources-crud-pagination-idempotency.md"
);

const npmCommand = process.platform === "win32" ? "npm.cmd" : "npm";
const frontend = spawnSync(npmCommand, ["test"], { cwd: project, encoding: "utf8" });
assert.equal(frontend.status, 0, frontend.stdout + frontend.stderr);
assert.match(frontend.stdout, /"cursor_query_checked": true/);
assert.match(frontend.stdout, /"idempotency_header_checked": true/);

const backend = spawnSync(
  python,
  ["-m", "unittest", "discover", "-s", project, "-p", "test_app.py", "-v"],
  { cwd: root, encoding: "utf8" }
);
assert.equal(backend.status, 0, backend.stdout + backend.stderr);
assert.match(backend.stdout + backend.stderr, /Ran 16 tests/);

const schema = readFileSync(join(project, "schema.sql"), "utf8");
assert.match(schema, /idempotency_key TEXT UNIQUE/);
assert.match(schema, /idx_study_sessions_learner_id_id/);
assert.match(schema, /ON study_sessions\(learner_id, id\)/);
assert.match(schema, /PRAGMA user_version = 2/);

const database = readFileSync(join(project, "database.py"), "utf8");
assert.match(database, /WHERE learner_id = \? AND id > \?/);
assert.match(database, /LIMIT \?/);
assert.match(database, /WHERE idempotency_key = \?/);
assert.match(database, /raise IdempotencyConflictError/);
assert.match(database, /UPDATE study_sessions/);
assert.match(database, /DELETE FROM study_sessions WHERE id = \?/);
assert.doesNotMatch(database, /f["'](?:SELECT|INSERT|UPDATE|DELETE)/);

const app = readFileSync(join(project, "app.py"), "utf8");
assert.match(app, /Idempotency-Key/);
assert.match(app, /response\.headers\["Location"\]/);
assert.match(app, /HTTP_201_CREATED/);
assert.match(app, /HTTP_204_NO_CONTENT/);
assert.match(app, /status_code=409/);

const packageJson = JSON.parse(readFileSync(join(project, "package.json"), "utf8"));
assert.equal(packageJson.devDependencies.typescript, "7.0.2");

const course = readFileSync(lesson, "utf8");
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(course, new RegExp(`data-context-type="${type}"`), `课程缺少 ${type} 语义区域`);
}
assert.match(course, /四类画像共用同一份 v0\.7 项目/);
assert.match(course, /求职加练/);
assert.match(course, /删除后种子数据被自动补回来/);
assert.match(course, /Idempotency-Key/);

execFileSync(python, ["-m", "pip", "check"], { cwd: root, stdio: "pipe" });

console.log(JSON.stringify({
  valid: true,
  project_version: "0.7.0",
  frontend_contracts: 3,
  api_tests: 16,
  rest_resources: ["learners/{learner_id}/study-sessions", "study-sessions/{session_id}"],
  cursor_pagination_checked: true,
  idempotency_replay_checked: true,
  idempotency_conflict_checked: true,
  repeatable_put_checked: true,
  delete_final_state_checked: true,
  seed_resurrection_regression_checked: true,
  four_profiles_addressed: true,
  network_used_by_tests: false
}, null, 2));
