import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const example = join(root, "site-src/examples/cs-start/operation_growth.py");
const source = readFileSync(example, "utf8");
assert.match(source, /def linear_search/);
assert.match(source, /def growth_row/);
assert.match(source, /def count_adjacent_increases/);

const workspace = mkdtempSync(join(tmpdir(), "be-cs-growth-"));
const probe = join(workspace, "probe.py");
writeFileSync(
  probe,
  `import importlib.util\nimport sys\nfrom pathlib import Path\n\npath = Path(${JSON.stringify(example)})\nspec = importlib.util.spec_from_file_location("growth", path)\nassert spec and spec.loader\nmodule = importlib.util.module_from_spec(spec)\nsys.modules[spec.name] = module\nspec.loader.exec_module(module)\n\nassert module.growth_row(0) == module.GrowthRow(0, 0, 0, 0)\nassert module.growth_row(4) == module.GrowthRow(4, 1, 4, 6)\nassert module.growth_row(8) == module.GrowthRow(8, 1, 8, 28)\nassert module.growth_row(16) == module.GrowthRow(16, 1, 16, 120)\nassert module.growth_row(32) == module.GrowthRow(32, 1, 32, 496)\n\ntry:\n    module.growth_row(-1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("negative size must fail")\n\nassert module.linear_search([1, 4, 4, 7, 2], 1) == module.SearchTrace(0, 1)\nassert module.linear_search([1, 4, 4, 7, 2], 7) == module.SearchTrace(3, 4)\nassert module.linear_search([1, 4, 4, 7, 2], 9) == module.SearchTrace(None, 5)\nassert module.linear_search([], 9) == module.SearchTrace(None, 0)\n\nassert module.count_adjacent_increases([]) == (0, 0)\nassert module.count_adjacent_increases([4]) == (0, 0)\nassert module.count_adjacent_increases([1, 2, 3]) == (2, 2)\nassert module.count_adjacent_increases([3, 2, 1]) == (0, 2)\nassert module.count_adjacent_increases([1, 4, 4, 7, 2]) == (2, 4)\nvalues = [1, 4, 4, 7, 2]\nmodule.count_adjacent_increases(values)\nassert values == [1, 4, 4, 7, 2]\nprint("probe-ok")\n`,
  "utf8",
);

try {
  const probeOutput = execFileSync("python3", [probe], { encoding: "utf8" }).trim();
  assert.equal(probeOutput, "probe-ok");
  const output = execFileSync("python3", [example], { encoding: "utf8" });
  assert.match(output, /4 1 4 6/);
  assert.match(output, /8 1 8 28/);
  assert.match(output, /16 1 16 120/);
  assert.match(output, /32 1 32 496/);
  assert.match(output, /search 7: SearchTrace\(index=3, comparisons=4\)/);
  assert.match(output, /search 9: SearchTrace\(index=None, comparisons=5\)/);
  assert.match(output, /adjacent: \(2, 4\)/);
} finally {
  rmSync(workspace, { recursive: true, force: true });
}

console.log(JSON.stringify({
  valid: true,
  python: "python3",
  sizes: [4, 8, 16, 32],
  growth_rows_verified: true,
  empty_input_verified: true,
  search_best_and_worst_verified: true,
  adjacent_increases_verified: true,
  input_unchanged: true,
  network_used: false,
  third_party_packages: false,
}, null, 2));
