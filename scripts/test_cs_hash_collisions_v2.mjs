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
const micro = join(root, "site-src/examples/algorithm-foundation/hash_bucket_trace.py");
const temp = mkdtempSync(join(tmpdir(), "be-cs-hash-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}

function expectSuccess(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

try {
  const microRun = run(python, [micro]);
  expectSuccess(microRun, "哈希桶微型例子运行失败");
  assert.equal(microRun.stdout, [
    "key bucket chain_before collision",
    "1   1      0            no",
    "5   1      1            yes",
    "9   1      2            yes",
    "2   2      0            no",
    "buckets=0:[] 1:[1, 5, 9] 2:[2] 3:[]",
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
    const pythonReport = run(python, ["-m", "traceable_hash_lab", mode], { cwd: pythonProject, env: pythonEnv });
    const cppReport = run(cppApp, [mode]);
    expectSuccess(pythonReport, `Python ${mode} 模式失败`);
    expectSuccess(cppReport, `C++ ${mode} 模式失败`);
    assert.equal(cppReport.stdout.trim(), pythonReport.stdout.trim(), `${mode} 模式双语言输出应逐字一致`);
  }

  console.log("哈希函数、键相等与冲突验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}
