import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const example = join(root, "site-src/examples/cs-start/grid_coordinates.py");
const source = readFileSync(example, "utf8");
assert.match(source, /def validate_shape/);
assert.match(source, /def checked_grid_at/);
assert.match(source, /def sum_grid_row/);
assert.match(source, /row \* columns \+ column/);

const workspace = mkdtempSync(join(tmpdir(), "be-cs-grid-"));
const probe = join(workspace, "probe.py");
writeFileSync(
  probe,
  `import importlib.util\nimport sys\nfrom pathlib import Path\n\npath = Path(${JSON.stringify(example)})\nspec = importlib.util.spec_from_file_location("grid_coordinates", path)\nassert spec and spec.loader\nmodule = importlib.util.module_from_spec(spec)\nsys.modules[spec.name] = module\nspec.loader.exec_module(module)\n\nvalues = [2, 5, 3, 4, 1, 2]\noriginal = values.copy()\nassert module.checked_grid_at(values, 2, 3, 0, 0) == module.GridCell(0, 0, 0, 2)\nassert module.checked_grid_at(values, 2, 3, 1, 2) == module.GridCell(1, 2, 5, 2)\nassert module.checked_grid_at(values, 3, 2, 2, 1) == module.GridCell(2, 1, 5, 2)\ntrace = module.sum_grid_row(values, 2, 3, 1)\nassert trace == module.RowTrace(1, 7, 3)\nassert values == original\n\nmodule.validate_shape([], 0, 0)\nfor rows, columns in ((-1, 0), (0, -1)):\n    try:\n        module.validate_shape([], rows, columns)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError("negative shape accepted")\n\ntry:\n    module.validate_shape(values[:-1], 2, 3)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("shape mismatch accepted")\n\nfor row, column in ((-1, 0), (0, -1), (2, 0), (0, 3)):\n    try:\n        module.checked_grid_at(values, 2, 3, row, column)\n    except IndexError:\n        pass\n    else:\n        raise AssertionError(f"out-of-range coordinate accepted: {(row, column)}")\n\ntry:\n    module.checked_grid_at([], 0, 0, 0, 0)\nexcept IndexError:\n    pass\nelse:\n    raise AssertionError("empty-grid access accepted")\n\naliased = [[0] * 2] * 3\naliased[0][0] = 9\nassert aliased == [[9, 0], [9, 0], [9, 0]]\nsafe = [[0] * 2 for _ in range(3)]\nsafe[0][0] = 9\nassert safe == [[9, 0], [0, 0], [0, 0]]\nprint("probe-ok")\n`,
  "utf8",
);

try {
  assert.equal(
    execFileSync("python3", [probe], { encoding: "utf8" }).trim(),
    "probe-ok",
  );
  const output = execFileSync("python3", [example], { encoding: "utf8" });
  assert.match(output, /shape=2x3/);
  assert.match(output, /coordinate=\(1, 2\), flat_index=5, value=2/);
  assert.match(output, /row=1, total=7, visits=3/);
  assert.match(output, /coordinate=\(2, 1\), flat_index=5, value=2/);
} finally {
  rmSync(workspace, { recursive: true, force: true });
}

console.log(JSON.stringify({
  valid: true,
  python: "python3",
  shapes_verified: ["2x3", "3x2", "0x0"],
  coordinate_boundaries_verified: true,
  row_scan_visits_verified: true,
  source_values_unchanged: true,
  repeated_row_alias_demonstrated: true,
  independent_rows_verified: true,
  network_used: false,
  third_party_packages: false,
}, null, 2));
