#!/usr/bin/env node

import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const python = join(root, ".venv/bin/python");
const pythonProject = join(root, "exercises/cs-core/traceable-hash-lab/python");
const cppProject = join(root, "exercises/cs-core/traceable-hash-lab/cpp");
const micro = join(root, "site-src/examples/algorithm-foundation/hash_table_growth.py");
const temp = mkdtempSync(join(tmpdir(), "be-cs-hash-table-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}
function expectSuccess(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

try {
  const microRun = run(python, [micro]);
  expectSuccess(microRun, "哈希表扩容小例子运行失败");
  assert.equal(microRun.stdout, [
    "put 1  bucket=1 comparisons=0 rehash=-",
    "put 5  bucket=1 comparisons=1 rehash=-",
    "put 9  bucket=1 comparisons=2 rehash=-",
    "put 2  bucket=2 comparisons=0 rehash=-",
    "put 13 bucket=5 comparisons=1 rehash=4->8 moved=4",
    "size=5 buckets=8 load=0.625",
    "",
  ].join("\n"));

  const pythonEnv = { ...process.env, PYTHONPATH: join(pythonProject, "src") };
  expectSuccess(run(python, ["-m", "unittest", "discover", "-s", "tests", "-v"], { cwd: pythonProject, env: pythonEnv }), "Python 哈希实验测试失败");
  expectSuccess(run(python, ["-m", "mypy", "--strict", "src", "tests"], { cwd: pythonProject, env: pythonEnv }), "Python 哈希实验 mypy 失败");

  const build = join(temp, "cpp-build");
  expectSuccess(run("cmake", ["-S", cppProject, "-B", build, "-DCMAKE_BUILD_TYPE=Debug"]), "C++ 哈希实验配置失败");
  expectSuccess(run("cmake", ["--build", build, "--config", "Debug", "--parallel"]), "C++ 哈希实验构建失败");
  expectSuccess(run("ctest", ["--test-dir", build, "--build-config", "Debug", "--output-on-failure"]), "C++ 哈希实验 CTest 失败");
  const cppApp = join(build, "traceable_hash_lab");
  for (const mode of ["hash", "table", "applications"]) {
    const py = run(python, ["-m", "traceable_hash_lab", mode], { cwd: pythonProject, env: pythonEnv });
    const cpp = run(cppApp, [mode]);
    expectSuccess(py, `Python ${mode} 模式失败`);
    expectSuccess(cpp, `C++ ${mode} 模式失败`);
    assert.equal(cpp.stdout.trim(), py.stdout.trim(), `${mode} 模式双语言输出应逐字一致`);
  }
  console.log("分离链接、负载因子与扩容验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}
