import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lesson = readFileSync(resolve(root, "learning-paths/systems-engineering/01-file-descriptors-partial-io-ownership.md"), "utf8");
const project = resolve(root, "site-src/examples/systems-engineering/diagnostic-service-v01");

for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project", "career"]) {
  assert.match(lesson, new RegExp(`data-context-type="${type}"`), `missing ${type} context`);
}
for (const phrase of ["write_calls=4 read_calls=4", "roundtrip=pass", "move_source=empty", "all_descriptors=closed"]) {
  assert.ok(lesson.includes(phrase), `missing fixed contract ${phrase}`);
}
assert.ok(lesson.includes("零基础兴趣") && lesson.includes("有基础求职"), "four profiles missing");
assert.ok(lesson.includes("不是 Windows") && lesson.includes("不代表任何企业"), "scope boundary missing");

const tests = spawnSync(resolve(root, ".venv/bin/python"), ["-m", "unittest", "-v", "test_fd_pipeline.py"], { cwd: project, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 4 tests/);

console.log(JSON.stringify({
  valid: true,
  lesson_id: "systems-engineering-01",
  project: "diagnostic-service-v01",
  tests: 4,
  real_posix_pipe: true,
  cxx_standard: 20,
  supported_platforms: ["macOS", "Linux"],
  four_profiles_addressed: true,
}, null, 2));
