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

const profile = run("learning_profile_v02.py");
assert.equal(profile.status, 0, profile.stderr);
assert.equal(
  profile.stdout,
  [
    "学习档案",
    "昵称： 小码",
    "课程： Python 起步",
    "本周计划： 5 小时",
    "本周完成： 3 小时",
    "状态： 进行中",
    "还需： 2 小时",
    "本周行动：",
    "1 继续学习",
    "2 运行代码",
    "3 记录结果",
    "可以复盘： False",
    "",
  ].join("\n"),
);

const cases = run("learning_profile_status_cases.py");
assert.equal(cases.status, 0, cases.stderr);
assert.equal(cases.stdout, "3 小时：进行中\n5 小时：已完成\n7 小时：已完成\n");

const earlySuccess = run("guess_word_three_times.py", "java\npython\n");
assert.equal(earlySuccess.status, 0, earlySuccess.stderr);
assert.match(earlySuccess.stdout, /第 1 次：不对，再想想/);
assert.match(earlySuccess.stdout, /第 2 次：答对了/);
assert.doesNotMatch(earlySuccess.stdout, /次数用完/);

const exhausted = run("guess_word_three_times.py", "java\nc\nrust\n");
assert.equal(exhausted.status, 0, exhausted.stderr);
assert.match(exhausted.stdout, /第 3 次：不对，再想想/);
assert.match(exhausted.stdout, /次数用完/);

console.log(JSON.stringify({
  valid: true,
  python,
  examples: 3,
  fixed_report: true,
  branch_cases: 3,
  early_break: true,
  bounded_failure: true,
  network_used: false,
  third_party_packages: false,
}, null, 2));
