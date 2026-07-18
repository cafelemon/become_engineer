import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const python = join(root, ".venv/bin/python");
const example = join(root, "site-src/examples/python-core/interfaces_protocols.py");
const project = join(root, "exercises/programming-languages/study-progress-reporters/python");
const source = readFileSync(example, "utf8");
assert.match(source, /class ReportWriter\(Protocol\)/);
assert.match(source, /\*,\n    writer: ReportWriter/);
assert.match(source, /history: list\[str\] \| None = None/);
assert.doesNotMatch(source, /history: list\[str\] = \[\]/);

assert.match(
  execFileSync(python, ["-m", "mypy", "--strict", example], {
    cwd: root,
    encoding: "utf8",
  }),
  /Success: no issues found/,
);

const workspace = mkdtempSync(join(tmpdir(), "be-python-interfaces-"));
const probe = join(workspace, "probe.py");
const invalid = join(workspace, "invalid_writer.py");
writeFileSync(
  probe,
  `import importlib.util\nimport sys\nfrom pathlib import Path\n\npath = Path(${JSON.stringify(example)})\nspec = importlib.util.spec_from_file_location("interfaces_protocols", path)\nassert spec and spec.loader\nmodule = importlib.util.module_from_spec(spec)\nsys.modules[spec.name] = module\nspec.loader.exec_module(module)\n\nrecords = [{"course_name": "Python", "completed_hours": 4.0}]\nwritten = []\ndef remember(text: str, /) -> None:\n    written.append(text)\nreport = module.run_report(records, writer=remember, title="测试报告")\nassert written == [report]\nassert report == "测试报告\\n总完成：4.0 小时"\nassert records == [{"course_name": "Python", "completed_hours": 4.0}]\nassert module.remember_course("Python") == ["Python"]\nassert module.remember_course("CS") == ["CS"]\nhistory = []\nassert module.remember_course("Python", history) is history\nassert module.remember_course("CS", history) == ["Python", "CS"]\ntry:\n    module.run_report(records, remember)\nexcept TypeError:\n    pass\nelse:\n    raise AssertionError("keyword-only writer accepted positionally")\nprint("probe-ok")\n`,
  "utf8",
);
writeFileSync(
  invalid,
  `from typing import Protocol\nclass ReportWriter(Protocol):\n    def __call__(self, report: str, /) -> None: ...\ndef wrong_writer(report: bytes, /) -> int:\n    return len(report)\nwriter: ReportWriter = wrong_writer\n`,
  "utf8",
);

try {
  assert.equal(execFileSync(python, [probe], { encoding: "utf8" }).trim(), "probe-ok");
  const invalidResult = spawnSync(python, ["-m", "mypy", "--strict", invalid], {
    cwd: root,
    encoding: "utf8",
  });
  assert.notEqual(invalidResult.status, 0);
  assert.match(invalidResult.stdout + invalidResult.stderr, /Incompatible types in assignment/);
  const output = execFileSync(python, [example], { encoding: "utf8" });
  assert.match(output, /terminal:\n接口学习报告\n总完成：6\.0 小时/);
  assert.match(output, /memory_count=1/);
  assert.match(output, /memory_matches=True/);
  assert.match(output, /fresh_defaults=True/);
} finally {
  rmSync(workspace, { recursive: true, force: true });
}

const analysisSource = readFileSync(join(project, "src/study_progress_reporter/analysis.py"), "utf8");
const reportingSource = readFileSync(join(project, "src/study_progress_reporter/reporting.py"), "utf8");
assert.doesNotMatch(analysisSource, /from study_progress_reporter\.(cli|__main__)/);
assert.doesNotMatch(reportingSource, /from study_progress_reporter\.(cli|__main__)/);
assert.match(
  execFileSync(python, ["-m", "mypy", "--strict", "."], {
    cwd: project,
    encoding: "utf8",
  }),
  /Success: no issues found/,
);
const projectTests = spawnSync(
  python,
  ["-m", "unittest", "discover", "-s", "tests", "-v"],
  {
    cwd: project,
    encoding: "utf8",
    env: { ...process.env, PYTHONPATH: "src" },
  },
);
assert.equal(projectTests.status, 0, projectTests.stderr);
assert.match(projectTests.stdout + projectTests.stderr, /Ran 30 tests/);

console.log(JSON.stringify({
  valid: true,
  mypy_strict_passed: true,
  terminal_and_memory_writers: true,
  keyword_only_boundary: true,
  mutable_default_repaired: true,
  incompatible_protocol_rejected: true,
  dependency_direction_checked: true,
  project_mypy_passed: true,
  project_tests: 30,
  network_used: false,
}, null, 2));
