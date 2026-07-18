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
const micro = join(root, "site-src/examples/algorithm-foundation/tree_frontier_trace.py");
const temp = mkdtempSync(join(tmpdir(), "be-cs-tree-frontier-"));

function run(command, args, options = {}) { return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options }); }
function expectSuccess(result, label) { assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`); }

try {
  const sample = run(python, [micro]);
  expectSuccess(sample, "树前沿轨迹失败");
  assert.equal(sample.stdout, [
    "dfs pop=7 frontier=[9,3]", "dfs pop=3 frontier=[9,5]", "dfs pop=5 frontier=[9]",
    "dfs pop=9 frontier=[11,8]", "dfs pop=8 frontier=[11]", "dfs pop=11 frontier=[]", "dfs max_frontier=2",
    "bfs pop=7 frontier=[3,9]", "bfs pop=3 frontier=[9,5]", "bfs pop=9 frontier=[5,8,11]",
    "bfs pop=5 frontier=[8,11]", "bfs pop=8 frontier=[11]", "bfs pop=11 frontier=[]", "bfs max_frontier=3", "",
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
    expectSuccess(pyResult, `Python ${mode} 失败`); expectSuccess(cppResult, `C++ ${mode} 失败`);
    assert.equal(cppResult.stdout.trim(), pyResult.stdout.trim());
  }
  console.log("迭代 DFS、BFS 与层级前沿验证通过");
} finally { rmSync(temp, { recursive: true, force: true }); }
