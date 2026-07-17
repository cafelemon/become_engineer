import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const examples = path.join(root, "site-src", "examples", "python-basics");
const python = process.env.PYTHON || "python3";

function run(file, input = "") {
  return spawnSync(python, [path.join(examples, file)], {
    cwd: root,
    encoding: "utf8",
    input,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" },
  });
}

const profile = run("learning_profile_v01.py");
assert.equal(profile.status, 0, profile.stderr);
assert.equal(
  profile.stdout,
  "学习档案\n昵称： 小码\n课程： Python 起步\n本周计划： 5 小时\n",
);

const types = run("learning_profile_types.py");
assert.equal(types.status, 0, types.stderr);
assert.match(types.stdout, /小码 <class 'str'>/);
assert.match(types.stdout, /5 <class 'int'>/);
assert.match(types.stdout, /0\.2 <class 'float'>/);
assert.match(types.stdout, /True <class 'bool'>/);

const validInput = run("learning_profile_input.py", "小码\nPython 起步\n5\n");
assert.equal(validInput.status, 0, validInput.stderr);
assert.match(validInput.stdout, /本周计划： 5 小时/);
assert.match(validInput.stdout, /下周建议： 6 小时/);

const invalidInput = run("learning_profile_input.py", "小码\nPython 起步\nfive\n");
assert.notEqual(invalidInput.status, 0);
assert.match(invalidInput.stderr, /ValueError/);
assert.match(invalidInput.stderr, /int\(weekly_hours_text\)/);

console.log(JSON.stringify({
  valid: true,
  python,
  examples: 3,
  fixed_output: true,
  type_checks: 4,
  interactive_success: true,
  value_error_reproduced: true,
  network_used: false,
  third_party_packages: false,
}, null, 2));
