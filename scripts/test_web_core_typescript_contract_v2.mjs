import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const project = join(root, "site-src/examples/web-core/learning-dashboard-v05");
const python = join(root, ".venv/bin/python");
const lesson = join(root, "learning-paths/web-fullstack/web-core/01-typescript-openapi-runtime-contract.md");

const npmCommand = process.platform === "win32" ? "npm.cmd" : "npm";
const frontend = spawnSync(npmCommand, ["test"], { cwd: project, encoding: "utf8" });
assert.equal(frontend.status, 0, frontend.stdout + frontend.stderr);
assert.match(frontend.stdout, /"contract_guard": true/);
assert.match(frontend.stdout, /"invalid_json_rejected": true/);

const backend = spawnSync(
  python,
  ["-m", "unittest", "discover", "-s", project, "-p", "test_app.py", "-v"],
  { cwd: root, encoding: "utf8" }
);
assert.equal(backend.status, 0, backend.stdout + backend.stderr);
assert.match(backend.stdout + backend.stderr, /Ran 8 tests/);

const packageJson = JSON.parse(readFileSync(join(project, "package.json"), "utf8"));
assert.equal(packageJson.devDependencies.typescript, "7.0.2");

const tsconfig = JSON.parse(readFileSync(join(project, "tsconfig.json"), "utf8"));
assert.equal(tsconfig.compilerOptions.strict, true);
assert.equal(tsconfig.compilerOptions.noEmitOnError, true);

const apiSource = readFileSync(join(project, "src/api.ts"), "utf8");
assert.match(apiSource, /payload: unknown/);
assert.match(apiSource, /isLearningSummary\(payload\)/);
assert.doesNotMatch(apiSource, /as LearningSummary/);

const html = readFileSync(join(project, "index.html"), "utf8");
assert.match(html, /type="module" src="dist\/main\.js"/);
assert.match(html, /data-profile-id="contract-drift"/);

const course = readFileSync(lesson, "utf8");
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(course, new RegExp(`data-context-type="${type}"`), `课程缺少 ${type} 语义区域`);
}
assert.match(course, /四类画像共用学习进度报告器/);
assert.match(course, /focus_topic/);
assert.match(course, /求职加练/);

execFileSync(python, ["-m", "pip", "check"], { cwd: root, stdio: "pipe" });

console.log(JSON.stringify({
  valid: true,
  typescript: "7.0.2",
  strict_compile: true,
  runtime_unknown_guard: true,
  frontend_cases: 8,
  api_tests: 8,
  openapi_schema_checked: true,
  contract_drift_rejected: true,
  four_profiles_addressed: true,
  network_used_by_tests: false
}, null, 2));
