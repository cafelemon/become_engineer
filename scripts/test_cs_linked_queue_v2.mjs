#!/usr/bin/env node

import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const python = join(root, ".venv/bin/python");
const pythonProject = join(root, "exercises/cs-core/traceable-linear-structures-lab/python");
const cppProject = join(root, "exercises/cs-core/traceable-linear-structures-lab/cpp");
const micro = join(root, "site-src/examples/algorithm-foundation/linked_queue_trace.py");
const temp = mkdtempSync(join(tmpdir(), "be-cs-queue-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}

function expectSuccess(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

try {
  const microRun = run(python, [micro]);
  expectSuccess(microRun, "链式队列微型例子运行失败");
  assert.equal(microRun.stdout, [
    "empty        front=None back=None size=0",
    "enqueue 7    front=7 back=7 size=1",
    "enqueue 3    front=7 back=3 size=2",
    "dequeue -> 7",
    "after first  front=3 back=3 size=1",
    "dequeue -> 3",
    "empty again  front=None back=None size=0",
    "reuse 9      front=9 back=9 size=1",
    "",
  ].join("\n"));

  const pythonEnv = { ...process.env, PYTHONPATH: join(pythonProject, "src") };
  expectSuccess(run(python, ["-m", "unittest", "discover", "-s", "tests", "-v"], { cwd: pythonProject, env: pythonEnv }), "Python 线性结构测试失败");
  expectSuccess(run(python, ["-m", "mypy", "--strict", "src", "tests"], { cwd: pythonProject, env: pythonEnv }), "Python 线性结构 mypy 失败");

  const build = join(temp, "cpp-build");
  expectSuccess(run("cmake", ["-S", cppProject, "-B", build, "-DCMAKE_BUILD_TYPE=Debug"]), "C++ 线性结构配置失败");
  expectSuccess(run("cmake", ["--build", build, "--config", "Debug", "--parallel"]), "C++ 线性结构构建失败");
  expectSuccess(run("ctest", ["--test-dir", build, "--build-config", "Debug", "--output-on-failure"]), "C++ 线性结构 CTest 失败");

  const cppApp = join(build, "traceable_linear_structures_lab");
  for (const mode of ["linked", "stack", "queue"]) {
    const pythonReport = run(python, ["-m", "traceable_linear_structures_lab", mode], { cwd: pythonProject, env: pythonEnv });
    const cppReport = run(cppApp, [mode]);
    expectSuccess(pythonReport, `Python ${mode} 模式失败`);
    expectSuccess(cppReport, `C++ ${mode} 模式失败`);
    assert.equal(cppReport.stdout.trim(), pythonReport.stdout.trim(), `${mode} 模式双语言输出应逐字一致`);
  }

  console.log("队列、FIFO 与首尾不变量验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}
