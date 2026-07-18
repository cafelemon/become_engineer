#!/usr/bin/env node

import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const sample = join(root, "site-src/examples/cpp-core/cmake-minimal");
const formal = join(root, "exercises/programming-languages/study-progress-reporters/cpp");
const temp = mkdtempSync(join(tmpdir(), "be-cpp-cmake-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}

function expectSuccess(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

function buildAndTest(source, build, label) {
  expectSuccess(run("cmake", ["-S", source, "-B", build, "-DCMAKE_BUILD_TYPE=Debug"]), `${label} 配置失败`);
  expectSuccess(run("cmake", ["--build", build, "--config", "Debug", "--parallel"]), `${label} 构建失败`);
  const tests = run("ctest", ["--test-dir", build, "--build-config", "Debug", "--output-on-failure"]);
  expectSuccess(tests, `${label} CTest 失败`);
  assert.match(tests.stdout, /100% tests passed/);
}

try {
  const sampleBuild = join(temp, "sample-build");
  buildAndTest(sample, sampleBuild, "课程快照");

  const app = join(sampleBuild, "study_status_app");
  const appRun = run(app, [], { input: "Lin Yue\n10\n7.5\n" });
  expectSuccess(appRun, "课程应用运行失败");
  assert.match(appRun.stdout, /进度：75\.0%[\s\S]*状态：进行中/);

  const headerCheck = join(temp, "header_check.cpp");
  const headerObject = join(temp, "header_check.o");
  writeFileSync(headerCheck, '#include "study/study_status.hpp"\nint main() { return 0; }\n');
  const compiler = process.env.CXX || "c++";
  expectSuccess(run(compiler, ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Werror", `-I${join(sample, "include")}`, "-c", headerCheck, "-o", headerObject]), "自包含头文件检查失败");

  const badInclude = join(temp, "bad_include.cpp");
  writeFileSync(badInclude, '#include "study/missing.hpp"\nint main() { return 0; }\n');
  assert.notEqual(run(compiler, ["-std=c++20", `-I${join(sample, "include")}`, "-c", badInclude, "-o", join(temp, "bad.o")]).status, 0);

  const duplicateA = join(temp, "duplicate_a.cpp");
  const duplicateB = join(temp, "duplicate_b.cpp");
  writeFileSync(duplicateA, "int duplicated() { return 1; }\n");
  writeFileSync(duplicateB, "int duplicated() { return 2; }\nint main() { return duplicated(); }\n");
  assert.notEqual(run(compiler, [duplicateA, duplicateB, "-o", join(temp, "duplicate")]).status, 0);

  const formalBuild = join(temp, "formal-build");
  buildAndTest(formal, formalBuild, "正式 C++ 报告器");

  const cmakeText = readFileSync(join(sample, "CMakeLists.txt"), "utf8");
  assert.match(cmakeText, /add_library\(study_status_lib STATIC/);
  assert.match(cmakeText, /target_include_directories\([\s\S]*PUBLIC/);
  assert.match(cmakeText, /target_link_libraries\(study_status_tests PRIVATE study_status_lib\)/);
  assert.match(cmakeText, /add_test\(NAME study_status_tests/);
  console.log("C++ 头文件、源文件与 CMake 工程验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}
