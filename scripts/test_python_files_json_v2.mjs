import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  copyFileSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const python = process.env.PYTHON || "python3";
const example = path.join(
  root,
  "site-src/examples/python-basics/v05/study_report_v05.py",
);
const fixture = path.join(
  root,
  "site-src/examples/python-basics/v05/data/study_records.json",
);

function createWorkspace() {
  const workspace = mkdtempSync(path.join(os.tmpdir(), "be-python-v05-"));
  mkdirSync(path.join(workspace, "data"));
  copyFileSync(fixture, path.join(workspace, "data/study_records.json"));
  return workspace;
}

function run(workspace) {
  return spawnSync(python, [example], {
    cwd: workspace,
    encoding: "utf8",
  });
}

const workspace = createWorkspace();
const inputPath = path.join(workspace, "data/study_records.json");
const inputBefore = readFileSync(inputPath);
const success = run(workspace);
assert.equal(success.status, 0, success.stderr);
assert.equal(
  success.stdout,
  [
    "发现 JSON：study_records.json",
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
assert.deepEqual(readFileSync(inputPath), inputBefore);
assert.match(
  readFileSync(path.join(workspace, "output/study_report.txt"), "utf8"),
  /总完成：8 小时/,
);

writeFileSync(path.join(workspace, "data/archive.json"), "{}\n", "utf8");
const scanned = run(workspace);
assert.equal(scanned.status, 0, scanned.stderr);
assert.match(scanned.stdout, /^发现 JSON：archive\.json, study_records\.json/m);

const brokenWorkspace = createWorkspace();
writeFileSync(
  path.join(brokenWorkspace, "data/study_records.json"),
  '{"records": [],}\n',
  "utf8",
);
const broken = run(brokenWorkspace);
assert.notEqual(broken.status, 0);
assert.match(broken.stderr, /JSONDecodeError/);

const missingWorkspace = mkdtempSync(path.join(os.tmpdir(), "be-python-v05-missing-"));
mkdirSync(path.join(missingWorkspace, "data"));
const missing = run(missingWorkspace);
assert.notEqual(missing.status, 0);
assert.match(missing.stderr, /FileNotFoundError/);

const micro = spawnSync(
  python,
  [path.join(root, "site-src/examples/python-basics/json_text_micro.py")],
  { cwd: root, encoding: "utf8" },
);
assert.equal(micro.status, 0, micro.stderr);
assert.match(micro.stdout, /^dict\nPython 起步\nTrue None\n/m);
assert.match(micro.stdout, /"active": true/);
assert.match(micro.stdout, /"note": null/);

console.log(JSON.stringify({
  valid: true,
  python,
  examples: 2,
  utf8_round_trip: true,
  input_read_only: true,
  bounded_glob: true,
  missing_file_failure: true,
  invalid_json_failure: true,
  network_used: false,
  third_party_packages: false,
}, null, 2));
