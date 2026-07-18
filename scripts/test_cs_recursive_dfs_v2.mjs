#!/usr/bin/env node
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const python = join(root, ".venv/bin/python");
const pyProject = join(root, "exercises/cs-core/traceable-tree-traversal-lab/python");
const cppProject = join(root, "exercises/cs-core/traceable-tree-traversal-lab/cpp");
const micro = join(root, "site-src/examples/algorithm-foundation/recursive_dfs_frames_trace.py");
const temp = mkdtempSync(join(tmpdir(), "be-cs-recursive-dfs-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}

function expectSuccess(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

try {
  const sample = run(python, [micro]);
  expectSuccess(sample, "递归调用帧轨迹失败");
  assert.equal(sample.stdout, [
    "enter value=7 depth=0 stack=[7]",
    "record value=7 order=preorder",
    "enter value=3 depth=1 stack=[7, 3]",
    "record value=3 order=preorder",
    "enter value=5 depth=2 stack=[7, 3, 5]",
    "record value=5 order=preorder",
    "leave value=5 resume=3",
    "leave value=3 resume=7",
    "enter value=9 depth=1 stack=[7, 9]",
    "record value=9 order=preorder",
    "leave value=9 resume=7",
    "leave value=7 resume=done",
    "",
  ].join("\n"));

  const env = { ...process.env, PYTHONPATH: join(pyProject, "src") };
  expectSuccess(run(python, ["-m", "unittest", "discover", "-s", "tests", "-v"], { cwd: pyProject, env }), "Python 测试失败");
  expectSuccess(run(python, ["-m", "mypy", "--strict", "src", "tests"], { cwd: pyProject, env }), "mypy 失败");

  const build = join(temp, "cpp-build");
  expectSuccess(run("cmake", ["-S", cppProject, "-B", build, "-DCMAKE_BUILD_TYPE=Debug"]), "C++ 配置失败");
  expectSuccess(run("cmake", ["--build", build, "--config", "Debug", "--parallel"]), "C++ 构建失败");
  expectSuccess(run("ctest", ["--test-dir", build, "--build-config", "Debug", "--output-on-failure"]), "CTest 失败");

  const cpp = join(build, "traceable_tree_traversal_lab");
  for (const mode of ["shape", "recursive", "frontier"]) {
    const pyResult = run(python, ["-m", "traceable_tree_traversal_lab", mode], { cwd: pyProject, env });
    const cppResult = run(cpp, [mode]);
    expectSuccess(pyResult, `Python ${mode} 失败`);
    expectSuccess(cppResult, `C++ ${mode} 失败`);
    assert.equal(cppResult.stdout.trim(), pyResult.stdout.trim());
  }
  console.log("递归深度优先遍历、基线条件与调用深度验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}
