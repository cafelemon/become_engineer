import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const examples = path.join(root, "site-src", "examples", "python-basics");
const python = process.env.PYTHON || "python3";

function run(file) {
  return spawnSync(python, [path.join(examples, file)], {
    cwd: root,
    encoding: "utf8",
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" },
  });
}

const report = run("learning_profile_v03.py");
assert.equal(report.status, 0, report.stderr);
assert.equal(
  report.stdout,
  "学习档案\n昵称： 小码\n- Python 起步: 60%，还需 2 小时\n* 复盘练习: 100%，已完成\n",
);

const returnDemo = run("return_vs_print.py");
assert.equal(returnDemo.status, 0, returnDemo.stderr);
assert.equal(
  returnDemo.stdout,
  "进行中\nshow_status 的调用结果： None\nget_status 的调用结果： 进行中\n",
);

const scopeFailure = run("local_scope_name_error.py");
assert.notEqual(scopeFailure.status, 0);
assert.match(scopeFailure.stdout, /正在学习：Python 起步/);
assert.match(scopeFailure.stderr, /NameError/);
assert.match(scopeFailure.stderr, /name 'message' is not defined/);
assert.match(scopeFailure.stderr, /print\(message\)/);

console.log(JSON.stringify({
  valid: true,
  python,
  examples: 3,
  report_contract: true,
  default_keyword_argument: true,
  return_vs_print: true,
  local_scope_failure: true,
  network_used: false,
  third_party_packages: false,
}, null, 2));
