import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const python = join(root, ".venv/bin/python");
const example = join(root, "site-src/examples/python-core/dataclasses_contexts.py");
const project = join(root, "exercises/programming-languages/study-progress-reporters/python");

assert.match(
  execFileSync(python, ["-m", "mypy", "--strict", example], {
    cwd: root,
    encoding: "utf8",
  }),
  /Success: no issues found/,
);

const workspace = mkdtempSync(join(tmpdir(), "be-python-dataclasses-"));
const probe = join(workspace, "probe.py");
writeFileSync(
  probe,
  `import importlib.util\nimport sys\nfrom pathlib import Path\nfrom tempfile import TemporaryDirectory\npath=Path(${JSON.stringify(example)})\nspec=importlib.util.spec_from_file_location("dataclasses_contexts",path)\nassert spec and spec.loader\nmodule=importlib.util.module_from_spec(spec)\nsys.modules[spec.name]=module\nspec.loader.exec_module(module)\nfirst=module.StudyRecord("Python",10.0,7.5)\nsecond=module.StudyRecord("Python",10.0,7.5)\nassert first==second\nassert "StudyRecord" in repr(first)\nfirst.tags.append("基础")\nassert second.tags==[]\ncopy=first.clone()\ncopy.tags.append("重点")\nassert first.tags==["基础"]\nassert copy.tags==["基础","重点"]\nassert first.progress==0.75 and first.status=="进行中"\nfirst.add_completed_hours(2.5)\nassert first.progress==1.0 and first.status=="已完成"\ntry:\n    first.add_completed_hours(-1.0)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("negative hours accepted")\nwith TemporaryDirectory() as directory:\n    root=Path(directory)\n    ok,closed=module.write_audit_snapshot([first],root/"audit.txt")\n    assert ok and closed\n    assert (root/"audit.txt").read_text(encoding="utf-8")=="学习审计快照\\nPython\\t10\\t10\\n"\n    missing,missing_closed=module.write_audit_snapshot([first],root/"missing"/"audit.txt")\n    assert not missing and not missing_closed\nprint("probe-ok")\n`,
  "utf8",
);

try {
  assert.equal(execFileSync(python, [probe], { encoding: "utf8" }).trim(), "probe-ok");
  const output = execFileSync(python, [example], { encoding: "utf8" });
  assert.match(output, /before=75\.0% 进行中/);
  assert.match(output, /after=100\.0% 已完成/);
  assert.match(output, /original_tags=\['基础'\]/);
  assert.match(output, /copied_tags=\['基础', '重点'\]/);
  assert.match(output, /audit_ok=True/);
  assert.match(output, /audit_closed=True/);
  assert.match(output, /missing_parent=False/);
} finally {
  rmSync(workspace, { recursive: true, force: true });
}

assert.match(
  execFileSync(python, ["-m", "mypy", "--strict", "."], {
    cwd: project,
    encoding: "utf8",
  }),
  /Success: no issues found/,
);
const tests = spawnSync(
  python,
  ["-m", "unittest", "discover", "-s", "tests", "-v"],
  {
    cwd: project,
    encoding: "utf8",
    env: { ...process.env, PYTHONPATH: "src" },
  },
);
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 30 tests/);

console.log(
  JSON.stringify(
    {
      valid: true,
      mypy_strict_passed: true,
      generated_methods: true,
      mutable_defaults_isolated: true,
      clone_isolated: true,
      properties_and_methods: true,
      audit_success_and_closed: true,
      missing_parent_failure: true,
      project_tests: 30,
      network_used: false,
    },
    null,
    2,
  ),
);
