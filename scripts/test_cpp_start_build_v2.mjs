#!/usr/bin/env node

import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const example = join(root, "site-src/examples/cpp-start/study_status.cpp");
const temp = mkdtempSync(join(tmpdir(), "be-cpp-start-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, {
    cwd: temp,
    encoding: "utf8",
    ...options,
  });
}

function findCompiler() {
  const candidates = [process.env.CXX, "clang++", "g++"].filter(Boolean);
  for (const candidate of candidates) {
    const result = run(candidate, ["--version"]);
    if (result.status === 0) return candidate;
  }
  throw new Error("找不到 clang++ 或 g++，无法验证 C++ 起步示例");
}

const compiler = findCompiler();
const flags = [
  "-std=c++20",
  "-Wall",
  "-Wextra",
  "-Wpedantic",
  "-Wconversion",
  "-Wshadow",
  "-Werror",
];

try {
  const executable = join(temp, "study_status");
  const compile = run(compiler, [...flags, example, "-o", executable]);
  assert.equal(compile.status, 0, compile.stderr);

  const success = run(executable, [], { input: "小林\n5\n" });
  assert.equal(success.status, 0, success.stderr);
  assert.match(success.stdout, /姓名：小林/);
  assert.match(success.stdout, /课程：C\+\+ 起步/);
  assert.match(success.stdout, /本周计划：5 小时/);
  assert.match(success.stdout, /是否完成：false/);

  const spacedName = run(executable, [], { input: "Lin Yue\n2.5\n" });
  assert.equal(spacedName.status, 0, spacedName.stderr);
  assert.match(spacedName.stdout, /姓名：Lin Yue/);
  assert.match(spacedName.stdout, /本周计划：2\.5 小时/);

  for (const [input, message] of [
    ["\n5\n", "姓名不能为空"],
    ["小林\nabc\n", "计划小时必须是数字"],
    ["小林\n0\n", "计划小时必须大于 0"],
    ["小林\n-1\n", "计划小时必须大于 0"],
  ]) {
    const failure = run(executable, [], { input });
    assert.equal(failure.status, 1);
    assert.match(failure.stderr, new RegExp(message));
  }

  const objectFile = join(temp, "study_status.o");
  const splitCompile = run(compiler, [...flags, "-c", example, "-o", objectFile]);
  assert.equal(splitCompile.status, 0, splitCompile.stderr);
  const splitExecutable = join(temp, "study_status_split");
  const splitLink = run(compiler, [objectFile, "-o", splitExecutable]);
  assert.equal(splitLink.status, 0, splitLink.stderr);

  const narrowingSource = join(temp, "narrowing.cpp");
  writeFileSync(narrowingSource, "int main() { const int hours{2.5}; return hours; }\n");
  const narrowing = run(compiler, [...flags, narrowingSource, "-o", join(temp, "narrowing")]);
  assert.notEqual(narrowing.status, 0, "窄化示例不应通过编译");

  const linkSource = join(temp, "link_error.cpp");
  writeFileSync(linkSource, "int build_plan();\nint main() { return build_plan(); }\n");
  const linkObject = join(temp, "link_error.o");
  const linkCompile = run(compiler, [...flags, "-c", linkSource, "-o", linkObject]);
  assert.equal(linkCompile.status, 0, linkCompile.stderr);
  const linkFailure = run(compiler, [linkObject, "-o", join(temp, "link_error")]);
  assert.notEqual(linkFailure.status, 0, "缺少定义的示例不应通过链接");

  assert.match(readFileSync(example, "utf8"), /std::getline/);
  console.log(`C++ 起步构建验证通过（${compiler}）`);
} finally {
  rmSync(temp, { recursive: true, force: true });
}
