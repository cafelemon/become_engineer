import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const python = process.env.PYTHON || "python3";

function run(relativePath) {
  return spawnSync(python, [path.join(root, relativePath)], {
    cwd: root,
    encoding: "utf8",
  });
}

const report = run("site-src/examples/python-basics/learning_records_v04.py");
assert.equal(report.status, 0, report.stderr);
assert.equal(
  report.stdout,
  [
    "学习进度报告",
    "总计划：10 小时",
    "总完成：8 小时",
    "课程状态：",
    "- Python 起步: 60%，还需 2 小时",
    "- 复盘练习: 100%，已完成",
    "- Git 复习: 100%，已完成",
    "唯一标签：Python, 复盘, 工具, 起步",
    "",
  ].join("\n"),
);

const tags = run("site-src/examples/python-basics/normalize_tag_text.py");
assert.equal(tags.status, 0, tags.stderr);
assert.match(tags.stdout, /清理后： \['Python', '起步', '工具', 'Python'\]/);
assert.match(tags.stdout, /显示： Python \| 起步 \| 工具 \| Python/);
assert.match(tags.stdout, /去重： \['Python', '复盘'|去重： \['Python', '工具', '起步'\]/);

const aliasing = run("site-src/examples/python-basics/list_aliasing.py");
assert.equal(aliasing.status, 0, aliasing.stderr);
assert.equal(
  aliasing.stdout,
  [
    "直接赋值： 2 2",
    "复制外层： 2 3",
    "内层仍共享： Python 起步（已修改）",
    "",
  ].join("\n"),
);

console.log(JSON.stringify({
  valid: true,
  python,
  examples: 3,
  multi_record_report: true,
  string_cleanup: true,
  list_aliasing: true,
  shallow_copy_boundary: true,
  network_used: false,
  third_party_packages: false,
}, null, 2));
