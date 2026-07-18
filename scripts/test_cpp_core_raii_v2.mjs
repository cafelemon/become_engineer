#!/usr/bin/env node

import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const cppProject = join(root, "exercises/programming-languages/study-progress-reporters/cpp");
const pythonProject = join(root, "exercises/programming-languages/study-progress-reporters/python");
const example = join(root, "site-src/examples/cpp-core/raii_scope.cpp");
const temp = mkdtempSync(join(tmpdir(), "be-cpp-raii-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}

function expectSuccess(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

try {
  const compiler = process.env.CXX || "c++";
  const micro = join(temp, "raii_scope");
  expectSuccess(run(compiler, ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wshadow", "-Werror", example, "-o", micro]), "RAII 微型例子编译失败");

  const audit = join(temp, "audit.txt");
  const success = run(micro, [audit]);
  expectSuccess(success, "RAII 成功路径运行失败");
  assert.equal(success.stdout, "进入：write_audit\n离开：write_audit\n写入：成功\n");
  assert.equal(readFileSync(audit, "utf8"), "学习审计快照\n课程：C++ 核心\n");

  const failure = run(micro, [join(temp, "missing", "audit.txt")]);
  assert.equal(failure.status, 1, `缺失目录应返回 1\n${failure.stdout}\n${failure.stderr}`);
  assert.equal(failure.stdout, "进入：write_audit\n离开：write_audit\n写入：失败\n");

  const dangling = join(temp, "dangling.cpp");
  writeFileSync(dangling, [
    "const int& bad_reference() {",
    "    const int local{42};",
    "    return local;",
    "}",
    "int main() { return 0; }",
    "",
  ].join("\n"));
  const danglingCompile = run(compiler, ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Werror", dangling, "-o", join(temp, "dangling")]);
  assert.notEqual(danglingCompile.status, 0, "返回局部对象引用的反例应被严格诊断拒绝");

  const build = join(temp, "cpp-build");
  expectSuccess(run("cmake", ["-S", cppProject, "-B", build, "-DCMAKE_BUILD_TYPE=Debug"]), "C++ 报告器配置失败");
  expectSuccess(run("cmake", ["--build", build, "--config", "Debug", "--parallel"]), "C++ 报告器构建失败");
  expectSuccess(run("ctest", ["--test-dir", build, "--build-config", "Debug", "--output-on-failure"]), "C++ 报告器 CTest 失败");

  const cppReport = run(join(build, "study_report_app"), []);
  expectSuccess(cppReport, "C++ 报告器运行失败");
  const pythonReport = run(join(root, ".venv/bin/python"), ["-m", "study_progress_reporter", "report"], {
    cwd: pythonProject,
    env: { ...process.env, PYTHONPATH: join(pythonProject, "src") },
  });
  expectSuccess(pythonReport, "Python 报告器运行失败");
  assert.equal(cppReport.stdout.trim(), pythonReport.stdout.trim(), "RAII 审计不能改变双语言主报告");

  console.log("C++ 对象、引用、指针、生命周期与 RAII 验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}
