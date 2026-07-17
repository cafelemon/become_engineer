import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  cpSync,
  existsSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const python = process.env.PYTHON || "python3";
const examples = path.join(root, "site-src/examples/python-basics");
const projectSource = path.join(
  root,
  "exercises/python-basics/study-progress-reporter",
);

function run(args, cwd = root) {
  return spawnSync(python, args, { cwd, encoding: "utf8" });
}

const kinds = run([path.join(examples, "failure_kinds.py")]);
assert.equal(kinds.status, 0, kinds.stderr);
assert.equal(
  kinds.stdout,
  [
    "错误结果：1.5（规则上限应为 1.0）",
    "已知输入错误：target_hours 必须大于 0",
    "",
  ].join("\n"),
);

const traceback = run([path.join(examples, "traceback_demo.py")]);
assert.notEqual(traceback.status, 0);
assert.match(traceback.stderr, /Traceback \(most recent call last\):/);
assert.match(traceback.stderr, /build_report/);
assert.match(traceback.stderr, /calculate_progress/);
assert.match(traceback.stderr, /ZeroDivisionError: division by zero/);

const microTests = run([
  "-m",
  "unittest",
  path.join(examples, "test_progress_micro.py"),
  "-v",
]);
assert.equal(microTests.status, 0, microTests.stderr);
assert.match(microTests.stderr, /Ran 2 tests/);
assert.match(microTests.stderr, /OK/);

const workspace = mkdtempSync(path.join(os.tmpdir(), "be-python-v10-"));
cpSync(projectSource, workspace, { recursive: true });
rmSync(path.join(workspace, "output"), { recursive: true, force: true });

const importOnly = run(
  ["-c", "import analysis, data_io, reporting, main"],
  workspace,
);
assert.equal(importOnly.status, 0, importOnly.stderr);
assert.equal(importOnly.stdout, "");
assert.equal(importOnly.stderr, "");
assert.equal(existsSync(path.join(workspace, "output")), false);

const projectTests = run(
  ["-m", "unittest", "discover", "-s", "tests", "-v"],
  workspace,
);
assert.equal(projectTests.status, 0, projectTests.stderr);
assert.match(projectTests.stderr, /Ran 14 tests/);
assert.match(projectTests.stderr, /OK/);

const inputPath = path.join(workspace, "data/study_records.json");
const before = readFileSync(inputPath);
const normal = run(["main.py"], workspace);
assert.equal(normal.status, 0, normal.stderr);
assert.match(normal.stdout, /学习进度报告/);
assert.equal(Buffer.compare(before, readFileSync(inputPath)), 0);
assert.equal(existsSync(path.join(workspace, "output/study_report.txt")), true);

writeFileSync(inputPath, '{"records": [}', "utf8");
const badJson = run(["main.py"], workspace);
assert.equal(badJson.status, 1);
assert.match(badJson.stderr, /JSON 格式无效/);
assert.match(badJson.stderr, /第 1 行/);

console.log(JSON.stringify({
  valid: true,
  python,
  micro_examples: 3,
  wrong_result_reproduced: true,
  traceback_chain_verified: true,
  micro_unittest_count: 2,
  project_unittest_count: 14,
  import_side_effect_free: true,
  success_exit_code: 0,
  invalid_input_exit_code: 1,
  input_read_only: true,
  network_used: false,
  third_party_packages: false,
}, null, 2));
