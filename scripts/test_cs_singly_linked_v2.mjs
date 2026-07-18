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
const micro = join(root, "site-src/examples/algorithm-foundation/singly_linked_trace.py");
const temp = mkdtempSync(join(tmpdir(), "be-cs-linked-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}

function expectSuccess(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

try {
  const microRun = run(python, [micro]);
  expectSuccess(microRun, "单链表微型例子运行失败");
  assert.equal(microRun.stdout, [
    "linked=7 -> 3 -> 9",
    "find=3 index=1 visits=2",
    "pop_front=7",
    "remaining=3 -> 9",
    "size=2",
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

  console.log("单链表、节点链接与所有权验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}
