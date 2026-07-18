#!/usr/bin/env node
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const python = join(root, ".venv/bin/python");
const pyProject = join(root, "exercises/cs-core/traceable-spanning-forest-lab/python");
const cppProject = join(root, "exercises/cs-core/traceable-spanning-forest-lab/cpp");
const micro = join(root, "site-src/examples/algorithm-core/dsu_compression_trace.py");
const temp = mkdtempSync(join(tmpdir(), "be-cs-dsu-"));

function run(command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", ...options });
}

function expectOk(result, label) {
  assert.equal(result.status, 0, `${label}\n${result.stdout}\n${result.stderr}`);
}

try {
  const trace = run(python, [micro]);
  expectOk(trace, "并查集压缩短轨迹失败");
  assert.match(trace.stdout, /parents_before=0,0,0,0,0,4,4/);
  assert.match(trace.stdout, /path=5->4->0/);
  assert.match(trace.stdout, /root=0 visits=3 compressions=1/);
  assert.match(trace.stdout, /parents_after=0,0,0,0,0,0,4/);
  assert.match(trace.stdout, /root_size=7/);

  const env = { ...process.env, PYTHONPATH: join(pyProject, "src") };
  expectOk(run(python, ["-m", "unittest", "discover", "-s", "tests", "-v"], { cwd: pyProject, env }), "Python 测试失败");
  expectOk(run(python, ["-m", "mypy", "--strict", "src", "tests"], { cwd: pyProject, env }), "mypy 失败");

  const build = join(temp, "cpp-build");
  expectOk(run("cmake", ["-S", cppProject, "-B", build, "-DCMAKE_BUILD_TYPE=Debug"]), "C++ 配置失败");
  expectOk(run("cmake", ["--build", build, "--config", "Debug", "--parallel"]), "C++ 构建失败");
  expectOk(run("ctest", ["--test-dir", build, "--build-config", "Debug", "--output-on-failure"]), "CTest 失败");

  const cpp = join(build, "traceable_spanning_forest_lab");
  for (const mode of ["dsu", "kruskal", "prim"]) {
    const pyRun = run(python, ["-m", "traceable_spanning_forest_lab", mode], { cwd: pyProject, env });
    const cppRun = run(cpp, [mode]);
    expectOk(pyRun, `Python ${mode} 失败`);
    expectOk(cppRun, `C++ ${mode} 失败`);
    assert.equal(cppRun.stdout.trim(), pyRun.stdout.trim(), `${mode} 双语言输出不一致`);
  }

  console.log("并查集、按大小合并与路径压缩验证通过");
} finally {
  rmSync(temp, { recursive: true, force: true });
}

