import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const python = join(root, ".venv/bin/python");
const example = join(root, "site-src/examples/python-core/type_contracts.py");
const source = readFileSync(example, "utf8");
assert.match(source, /class StudyRecord\(TypedDict\)/);
assert.match(source, /def validate_record\(value: object\) -> StudyRecord/);
assert.match(source, /Sequence\[StudyRecord\]/);
assert.doesNotMatch(source, /\bAny\b|#\s*type:\s*ignore|\bcast\(/);

assert.match(
  execFileSync(python, ["-m", "mypy", "--strict", example], {
    encoding: "utf8",
    cwd: root,
  }),
  /Success: no issues found/,
);

const workspace = mkdtempSync(join(tmpdir(), "be-python-types-"));
const probe = join(workspace, "probe.py");
const invalid = join(workspace, "invalid_types.py");
writeFileSync(
  probe,
  `import importlib.util\nimport sys\nfrom pathlib import Path\n\npath = Path(${JSON.stringify(example)})\nspec = importlib.util.spec_from_file_location("type_contracts", path)\nassert spec and spec.loader\nmodule = importlib.util.module_from_spec(spec)\nsys.modules[spec.name] = module\nspec.loader.exec_module(module)\n\nfirst = module.validate_record({"course_name": "Python", "target_hours": 10, "completed_hours": 4, "tags": ["类型"]})\nsecond = module.validate_record({"course_name": "CS", "target_hours": 8.0, "completed_hours": 6.0, "tags": []})\nassert module.calculate_progress(first) == 0.4\nassert module.total_completed([first, second]) == 10.0\nassert module.total_completed((second,)) == 6.0\nassert first["target_hours"] == 10.0\n\nbad_values = [\n    ({}, "missing course_name"),\n    ({"course_name": "", "target_hours": 1, "completed_hours": 0, "tags": []}, "non-empty"),\n    ({"course_name": "X", "target_hours": "ten", "completed_hours": 0, "tags": []}, "must be a number"),\n    ({"course_name": "X", "target_hours": True, "completed_hours": 0, "tags": []}, "must be a number"),\n    ({"course_name": "X", "target_hours": 0, "completed_hours": 0, "tags": []}, "greater than zero"),\n    ({"course_name": "X", "target_hours": 1, "completed_hours": -1, "tags": []}, "non-negative"),\n    ({"course_name": "X", "target_hours": 1, "completed_hours": 0, "tags": [1]}, "only strings"),\n]\nfor raw, message in bad_values:\n    try:\n        module.validate_record(raw)\n    except ValueError as error:\n        assert message in str(error), (raw, error)\n    else:\n        raise AssertionError(f"invalid record accepted: {raw}")\nprint("probe-ok")\n`,
  "utf8",
);
writeFileSync(
  invalid,
  "def progress_label(progress: float) -> str:\n    return progress\n",
  "utf8",
);

try {
  assert.equal(
    execFileSync(python, [probe], { encoding: "utf8" }).trim(),
    "probe-ok",
  );
  const invalidResult = spawnSync(
    python,
    ["-m", "mypy", "--strict", invalid],
    { encoding: "utf8", cwd: root },
  );
  assert.notEqual(invalidResult.status, 0);
  assert.match(invalidResult.stdout + invalidResult.stderr, /Incompatible return value type/);
  const output = execFileSync(python, [example], { encoding: "utf8" });
  assert.match(output, /course=Python 核心/);
  assert.match(output, /progress=40\.0%/);
  assert.match(output, /total_completed=10\.0/);
  assert.match(output, /tuple_input=6\.0/);
} finally {
  rmSync(workspace, { recursive: true, force: true });
}

console.log(JSON.stringify({
  valid: true,
  python: ".venv/bin/python",
  mypy_strict_passed: true,
  static_failure_nonzero: true,
  runtime_boundaries_verified: 7,
  list_and_tuple_inputs: true,
  dynamic_escape_hatches: false,
  network_used: false,
}, null, 2));
