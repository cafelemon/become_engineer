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
const micro = join(root, "site-src/examples/algorithm-foundation/binary_tree_slots_trace.py");
const temp = mkdtempSync(join(tmpdir(), "be-cs-tree-shape-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}

function expectSuccess(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

try {
  const sample = run(python, [micro]);
  expectSuccess(sample, "树槽位轨迹失败");
  assert.equal(sample.stdout, [
    "slots=[7,3,9,null,5,8,11]",
    "index=0 value=7 path=root parent=none",
    "index=4 value=5 path=LR parent=1",
    "index=6 value=11 path=RR parent=2",
    "orphan=rejected reason=slot 3 has no parent",
    "empty_root=rejected reason=non-empty tree requires a root value",
    "empty_slot=3 rejected reason=slot is empty",
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

  console.log("二叉树形状、链接所有权与槽位表示验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}
