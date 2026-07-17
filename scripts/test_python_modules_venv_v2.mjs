import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  cpSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  writeFileSync,
} from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const python = process.env.PYTHON || "python3";
const source = path.join(root, "site-src/examples/python-basics/v06");

const workspace = mkdtempSync(path.join(os.tmpdir(), "be-python-v06-"));
cpSync(source, workspace, { recursive: true });

function run(executable, args, cwd = workspace) {
  return spawnSync(executable, args, { cwd, encoding: "utf8" });
}

const importOnly = run(python, [
  "-c",
  "import analysis, data_io, reporting, main",
]);
assert.equal(importOnly.status, 0, importOnly.stderr);
assert.equal(importOnly.stdout, "");
assert.equal(importOnly.stderr, "");
assert.equal(existsSync(path.join(workspace, "output")), false);

const normal = run(python, ["main.py"]);
assert.equal(normal.status, 0, normal.stderr);
assert.equal(
  normal.stdout,
  [
    "学习进度报告",
    "总计划：10 小时",
    "总完成：8 小时",
    "课程状态：",
    "- Python 起步: 60%，还需 2 小时",
    "- 复盘练习: 100%，已完成",
    "- Git 复习: 100%，已完成",
    "唯一标签：Python, 复盘, 工具, 起步",
    "报告文件：output/study_report.txt",
    "",
  ].join("\n"),
);

const outside = run(python, [path.join(workspace, "main.py")], os.tmpdir());
assert.equal(outside.status, 0, outside.stderr);
assert.equal(outside.stdout, normal.stdout);

const venv = run(python, ["-m", "venv", ".venv"]);
assert.equal(venv.status, 0, venv.stderr);
const venvPython = path.join(
  workspace,
  ".venv",
  process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
);
assert.equal(existsSync(venvPython), true);

const executableCheck = run(venvPython, [
  "-c",
  "import sys; print(sys.executable)",
]);
assert.equal(executableCheck.status, 0, executableCheck.stderr);
assert.match(executableCheck.stdout, /\.venv/);

const venvRun = run(venvPython, ["main.py"]);
assert.equal(venvRun.status, 0, venvRun.stderr);
assert.equal(venvRun.stdout, normal.stdout);

const shadowWorkspace = mkdtempSync(path.join(os.tmpdir(), "be-python-shadow-"));
mkdirSync(shadowWorkspace, { recursive: true });
writeFileSync(path.join(shadowWorkspace, "json.py"), "VALUE = 'local'\n", "utf8");
writeFileSync(
  path.join(shadowWorkspace, "check.py"),
  "import json\nprint(json.dumps({'ok': True}))\n",
  "utf8",
);
const shadow = run(python, ["check.py"], shadowWorkspace);
assert.notEqual(shadow.status, 0);
assert.match(shadow.stderr, /AttributeError/);

console.log(JSON.stringify({
  valid: true,
  python,
  modules: 4,
  import_side_effect_free: true,
  same_output_after_refactor: true,
  arbitrary_cwd_supported: true,
  venv_created: true,
  venv_interpreter_verified: true,
  standard_library_shadow_reproduced: true,
  network_used: false,
  third_party_packages: false,
}, null, 2));
