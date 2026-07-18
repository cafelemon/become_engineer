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
const micro = join(root, "site-src/examples/algorithm-core/stable_priority_queue_trace.py");
const temp = mkdtempSync(join(tmpdir(), "be-cs-priority-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}

function expectOk(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

try {
  const shortTrace = run(python, [micro]);
  expectOk(shortTrace, "稳定优先队列短轨迹失败");
  assert.match(shortTrace.stdout, /push test@1 key=\(1,1\)/);
  assert.match(shortTrace.stdout, /push lint@1 key=\(1,2\)/);
  assert.match(shortTrace.stdout, /heap_array=test@1, review@2, lint@1, deploy@3/);
  assert.match(shortTrace.stdout, /pop_order=test@1, lint@1, review@2, deploy@3/);
  assert.match(shortTrace.stdout, /tie_sequences=1, 2/);

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

  console.log("稳定优先队列、同优先级顺序与下溢验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}

