#!/usr/bin/env node
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const python = join(root, ".venv/bin/python");
const pyProject = join(root, "exercises/cs-core/traceable-priority-shortest-path-lab/python");
const cppProject = join(root, "exercises/cs-core/traceable-priority-shortest-path-lab/cpp");
const micro = join(root, "site-src/examples/algorithm-core/dijkstra_relaxation_trace.py");
const temp = mkdtempSync(join(tmpdir(), "be-cs-dijkstra-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}

function expectOk(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

try {
  const trace = run(python, [micro]);
  expectOk(trace, "Dijkstra 松弛短轨迹失败");
  assert.match(trace.stdout, /relax 2->1: 4->3/);
  assert.match(trace.stdout, /relax 1->3: 6->4/);
  assert.match(trace.stdout, /stale vertex=1 queued=4 current=3/);
  assert.match(trace.stdout, /stale vertex=3 queued=6 current=4/);
  assert.match(trace.stdout, /stale vertex=4 queued=10 current=7/);
  assert.match(trace.stdout, /settled=0,2,1,3,4,5/);
  assert.match(trace.stdout, /distances=0,3,1,4,7,8,unreachable/);
  assert.match(trace.stdout, /stale_pops=3/);

  const env = { ...process.env, PYTHONPATH: join(pyProject, "src") };
  expectOk(run(python, ["-m", "unittest", "discover", "-s", "tests", "-v"], { cwd: pyProject, env }), "Python 测试失败");
  expectOk(run(python, ["-m", "mypy", "--strict", "src", "tests"], { cwd: pyProject, env }), "mypy 失败");

  const build = join(temp, "cpp-build");
  expectOk(run("cmake", ["-S", cppProject, "-B", build, "-DCMAKE_BUILD_TYPE=Debug"]), "C++ 配置失败");
  expectOk(run("cmake", ["--build", build, "--config", "Debug", "--parallel"]), "C++ 构建失败");
  expectOk(run("ctest", ["--test-dir", build, "--build-config", "Debug", "--output-on-failure"]), "CTest 失败");

  const cpp = join(build, "traceable_priority_shortest_path_lab");
  for (const mode of ["heap", "queue", "dijkstra"]) {
    const pyRun = run(python, ["-m", "traceable_priority_shortest_path_lab", mode], { cwd: pyProject, env });
    const cppRun = run(cpp, [mode]);
    expectOk(pyRun, `Python ${mode} 失败`);
    expectOk(cppRun, `C++ ${mode} 失败`);
    assert.equal(cppRun.stdout.trim(), pyRun.stdout.trim(), `${mode} 双语言输出不一致`);
  }

  console.log("带权图松弛、Dijkstra 与过期队列项验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}

