#!/usr/bin/env node

import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const cppProject = join(root, "exercises/programming-languages/study-progress-reporters/cpp");
const pythonProject = join(root, "exercises/programming-languages/study-progress-reporters/python");
const example = join(root, "site-src/examples/cpp-core/stl_algorithms.cpp");
const temp = mkdtempSync(join(tmpdir(), "be-cpp-stl-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}

function expectSuccess(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

try {
  const compiler = process.env.CXX || "c++";
  const micro = join(temp, "stl_algorithms");
  expectSuccess(run(compiler, ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wshadow", "-Werror", example, "-o", micro]), "STL 微型例子编译失败");
  const microRun = run(micro, []);
  expectSuccess(microRun, "STL 微型例子运行失败");
  assert.equal(microRun.stdout, [
    "first>=4=5",
    "even=2",
    "total=14",
    "doubled=4 10 6 8 ",
    "sorted=5 4 3 2 ",
    "original_first=2",
    "unique_tags=2",
    "",
  ].join("\n"));

  const build = join(temp, "cpp-build");
  expectSuccess(run("cmake", ["-S", cppProject, "-B", build, "-DCMAKE_BUILD_TYPE=Debug"]), "C++ 报告器配置失败");
  expectSuccess(run("cmake", ["--build", build, "--config", "Debug", "--parallel"]), "C++ 报告器构建失败");
  expectSuccess(run("ctest", ["--test-dir", build, "--build-config", "Debug", "--output-on-failure"]), "C++ 报告器 CTest 失败");

  const cppReport = run(join(build, "study_report_app"), []);
  expectSuccess(cppReport, "C++ 报告器运行失败");
  const python = join(root, ".venv/bin/python");
  const pythonReport = run(python, ["-m", "study_progress_reporter", "report"], {
    cwd: pythonProject,
    env: { ...process.env, PYTHONPATH: join(pythonProject, "src") },
  });
  expectSuccess(pythonReport, "Python 报告器运行失败");
  assert.equal(cppReport.stdout.trim(), pythonReport.stdout.trim(), "双语言主报告应逐字一致");
  console.log("C++ STL 容器、迭代器与算法验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}
