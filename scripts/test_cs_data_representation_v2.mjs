import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const python = process.env.PYTHON || "python3";
const example = path.join(
  root,
  "site-src/examples/cs-start/data_representation.py",
);

const result = spawnSync(python, [example], {
  cwd: root,
  encoding: "utf8",
});
assert.equal(result.status, 0, result.stderr);
assert.equal(
  result.stdout,
  [
    "数据：[2, 5, 3, 4]",
    "下标 2：3",
    "查找 3：下标 2，比较 3 次",
    "查找 9：下标 None，比较 4 次",
    "边界：IndexError",
    "",
  ].join("\n"),
);

const importCheck = spawnSync(
  python,
  [
    "-c",
    [
      "import importlib.util",
      "spec=importlib.util.spec_from_file_location('data_representation', r'" +
        example.replaceAll("\\\\", "\\\\\\\\") + "')",
      "module=importlib.util.module_from_spec(spec)",
      "spec.loader.exec_module(module)",
      "assert module.find_first([1,4,4,7,2], 7) == (3, 4)",
      "assert module.find_first([1,4,4,7,2], 9) == (None, 5)",
      "print('ok')",
    ].join(";"),
  ],
  { cwd: root, encoding: "utf8" },
);
assert.equal(importCheck.status, 0, importCheck.stderr);
assert.equal(importCheck.stdout, "ok\n");

console.log(JSON.stringify({
  valid: true,
  python,
  fixed_data: [2, 5, 3, 4],
  indexed_access: true,
  first_match_scan: true,
  missing_value_scan: true,
  index_error_reproduced: true,
  alternate_data_verified: true,
  network_used: false,
  third_party_packages: false,
}, null, 2));
