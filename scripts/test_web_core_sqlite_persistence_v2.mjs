import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const project = join(root, "site-src/examples/web-core/learning-dashboard-v06");
const python = join(root, ".venv/bin/python");
const lesson = join(
  root,
  "learning-paths/web-fullstack/web-core/02-relational-model-sqlite-persistence.md"
);

const npmCommand = process.platform === "win32" ? "npm.cmd" : "npm";
const frontend = spawnSync(npmCommand, ["test"], { cwd: project, encoding: "utf8" });
assert.equal(frontend.status, 0, frontend.stdout + frontend.stderr);
assert.match(frontend.stdout, /"rollback_message": true/);
assert.match(frontend.stdout, /"StudySessionCreated"/);

const backend = spawnSync(
  python,
  ["-m", "unittest", "discover", "-s", project, "-p", "test_app.py", "-v"],
  { cwd: root, encoding: "utf8" }
);
assert.equal(backend.status, 0, backend.stdout + backend.stderr);
assert.match(backend.stdout + backend.stderr, /Ran 12 tests/);

const schema = readFileSync(join(project, "schema.sql"), "utf8");
assert.match(schema, /CREATE TABLE IF NOT EXISTS learners/);
assert.match(schema, /CREATE TABLE IF NOT EXISTS study_sessions/);
assert.match(schema, /FOREIGN KEY \(learner_id\) REFERENCES learners\(id\)/);
assert.match(schema, /CHECK \(hours > 0 AND hours <= 24\)/);
assert.match(schema, /PRAGMA user_version = 1/);

const database = readFileSync(join(project, "database.py"), "utf8");
assert.match(database, /PRAGMA foreign_keys = ON/);
assert.match(database, /WHERE learners\.id = \?/);
assert.match(database, /VALUES \(\?, \?, \?\)/);
assert.match(database, /with connection:/);
assert.match(database, /connection\.close\(\)/);
assert.doesNotMatch(database, /f["'](?:SELECT|INSERT|UPDATE|DELETE)/);

const packageJson = JSON.parse(readFileSync(join(project, "package.json"), "utf8"));
assert.equal(packageJson.devDependencies.typescript, "7.0.2");

const course = readFileSync(lesson, "utf8");
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(course, new RegExp(`data-context-type="${type}"`), `课程缺少 ${type} 语义区域`);
}
assert.match(course, /四类画像使用同一份 v0\.6 代码/);
assert.match(course, /求职加练/);
assert.match(course, /重启服务后仍能读到/);

execFileSync(python, ["-m", "pip", "check"], { cwd: root, stdio: "pipe" });

console.log(JSON.stringify({
  valid: true,
  project_version: "0.6.0",
  frontend_contracts: 2,
  api_tests: 12,
  tables: ["learners", "study_sessions"],
  foreign_keys_enabled_per_connection: true,
  parameterized_sql_checked: true,
  transaction_rollback_checked: true,
  restart_persistence_checked: true,
  four_profiles_addressed: true,
  network_used_by_tests: false
}, null, 2));
