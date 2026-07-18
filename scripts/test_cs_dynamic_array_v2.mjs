#!/usr/bin/env node

import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const python = join(root, ".venv/bin/python");
const pythonProject = join(root, "exercises/cs-core/traceable-array-lab/python");
const cppProject = join(root, "exercises/cs-core/traceable-array-lab/cpp");
const micro = join(root, "site-src/examples/algorithm-foundation/dynamic_array_growth.py");
const temp = mkdtempSync(join(tmpdir(), "be-cs-dynamic-array-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}

function expectSuccess(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

try {
  const microRun = run(python, [micro]);
  expectSuccess(microRun, "动态数组微型例子运行失败");
  assert.equal(microRun.stdout, [
    "append | size | capacity | copies | steps",
    "7 | 1 | 1 | 0 | 1",
    "3 | 2 | 2 | 1 | 2",
    "9 | 3 | 4 | 2 | 3",
    "3 | 4 | 4 | 0 | 1",
    "5 | 5 | 8 | 4 | 5",
    "total_steps=12",
    "",
  ].join("\n"));

  const pythonEnv = { ...process.env, PYTHONPATH: join(pythonProject, "src") };
  expectSuccess(run(python, ["-m", "unittest", "discover", "-s", "tests", "-v"], { cwd: pythonProject, env: pythonEnv }), "Python 数组实验测试失败");
  expectSuccess(run(python, ["-m", "mypy", "--strict", "src", "tests"], { cwd: pythonProject, env: pythonEnv }), "Python 数组实验 mypy 失败");

  const build = join(temp, "cpp-build");
  expectSuccess(run("cmake", ["-S", cppProject, "-B", build, "-DCMAKE_BUILD_TYPE=Debug"]), "C++ 数组实验配置失败");
  expectSuccess(run("cmake", ["--build", build, "--config", "Debug", "--parallel"]), "C++ 数组实验构建失败");
  expectSuccess(run("ctest", ["--test-dir", build, "--build-config", "Debug", "--output-on-failure"]), "C++ 数组实验 CTest 失败");

  const cppApp = join(build, "traceable_array_lab");
  for (const mode of ["baseline", "text", "grid", "capacity"]) {
    const pythonReport = run(python, ["-m", "traceable_array_lab", mode], { cwd: pythonProject, env: pythonEnv });
    const cppReport = run(cppApp, [mode]);
    expectSuccess(pythonReport, `Python ${mode} 模式失败`);
    expectSuccess(cppReport, `C++ ${mode} 模式失败`);
    assert.equal(cppReport.stdout.trim(), pythonReport.stdout.trim(), `${mode} 模式双语言输出应逐字一致`);
  }

  console.log("动态数组容量、扩容成本与摊还分析验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}
