#!/usr/bin/env node

import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const example = join(root, "site-src/examples/cpp-start/function_status.cpp");
const temp = mkdtempSync(join(tmpdir(), "be-cpp-functions-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: temp, encoding: "utf8", ...options });
}

function findCompiler() {
  for (const candidate of [process.env.CXX, "clang++", "g++"].filter(Boolean)) {
    if (run(candidate, ["--version"]).status === 0) return candidate;
  }
  throw new Error("找不到 clang++ 或 g++，无法验证 C++ 函数示例");
}

const compiler = findCompiler();
const flags = ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wshadow", "-Werror"];

function expectRun(executable, input, status, stdoutPattern, stderrPattern) {
  const result = run(executable, [], { input });
  assert.equal(result.status, status, result.stderr);
  if (stdoutPattern) assert.match(result.stdout, stdoutPattern);
  if (stderrPattern) assert.match(result.stderr, stderrPattern);
}

try {
  const executable = join(temp, "function_status");
  const compile = run(compiler, [...flags, example, "-o", executable]);
  assert.equal(compile.status, 0, compile.stderr);

  expectRun(executable, "Lin Yue\n10\n7.5\n", 0, /进度：75\.0%[\s\S]*状态：进行中/, null);
  expectRun(executable, "Ada\n8\n8\n", 0, /进度：100\.0%[\s\S]*状态：已完成/, null);
  expectRun(executable, "Lin\n10\n12.5\n", 0, /进度：100\.0%[\s\S]*状态：已完成/, null);
  expectRun(executable, "\n10\n1\n", 1, null, /姓名不能为空/);
  expectRun(executable, "Lin\nten\n1\n", 1, null, /学习时间必须是数字/);
  expectRun(executable, "Lin\n0\n0\n", 1, null, /计划学习时间必须大于 0/);
  expectRun(executable, "Lin\n10\n-1\n", 1, null, /已完成时间不能小于 0/);

  const missing = join(temp, "missing_declaration.cpp");
  writeFileSync(missing, "int main() { return calculate_result(2); }\nint calculate_result(int value) { return value * 2; }\n");
  assert.notEqual(run(compiler, [...flags, missing, "-o", join(temp, "missing")]).status, 0);

  const mismatch = join(temp, "mismatched_definition.cpp");
  writeFileSync(mismatch, [
    "double calculate_progress(double, double);",
    "int main() { return calculate_progress(10.0, 5.0) > 0.0 ? 0 : 1; }",
    "double calculate_progress(int planned, int completed) { return static_cast<double>(completed) / static_cast<double>(planned); }",
    "",
  ].join("\n"));
  const mismatchObject = join(temp, "mismatch.o");
  assert.equal(run(compiler, [...flags, "-c", mismatch, "-o", mismatchObject]).status, 0);
  assert.notEqual(run(compiler, [mismatchObject, "-o", join(temp, "mismatch")]).status, 0);

  const constReference = join(temp, "const_reference.cpp");
  writeFileSync(constReference, "#include <string>\nvoid rename(const std::string& learner) { learner = \"changed\"; }\nint main() { return 0; }\n");
  assert.notEqual(run(compiler, [...flags, constReference, "-o", join(temp, "const_reference")]).status, 0);

  const ambiguous = join(temp, "ambiguous.cpp");
  writeFileSync(ambiguous, "void show(long) {}\nvoid show(double) {}\nint main() { show(1); return 0; }\n");
  assert.notEqual(run(compiler, [...flags, ambiguous, "-o", join(temp, "ambiguous")]).status, 0);

  const source = readFileSync(example, "utf8");
  assert.match(source, /namespace study/);
  assert.match(source, /double calculate_progress\(double planned_hours, double completed_hours\);/);
  assert.match(source, /const std::string& learner/);
  console.log(`C++ 函数与程序组织验证通过（${compiler}）`);
} finally {
  rmSync(temp, { recursive: true, force: true });
}
