import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const example = join(root, "site-src/examples/cs-start/text_units.py");
const source = readFileSync(example, "utf8");
assert.match(source, /def analyze_text/);
assert.match(source, /def decode_strict/);
assert.match(source, /errors="strict"/);

const workspace = mkdtempSync(join(tmpdir(), "be-cs-text-"));
const probe = join(workspace, "probe.py");
writeFileSync(
  probe,
  `import importlib.util\nimport sys\nfrom pathlib import Path\n\npath = Path(${JSON.stringify(example)})\nspec = importlib.util.spec_from_file_location("text_units", path)\nassert spec and spec.loader\nmodule = importlib.util.module_from_spec(spec)\nsys.modules[spec.name] = module\nspec.loader.exec_module(module)\n\ncases = [\n    ("", 0, 0, 0, 0),\n    ("ABC", 3, 3, 3, 0),\n    ("工", 1, 3, 0, 1),\n    ("🧪", 1, 4, 0, 1),\n    ("A工🧪", 3, 8, 1, 2),\n    ("e\\u0301", 2, 3, 1, 1),\n]\nfor text, points, byte_count, ascii_count, multibyte_count in cases:\n    trace = module.analyze_text(text)\n    assert trace.code_points == points\n    assert trace.utf8_bytes == byte_count\n    assert trace.ascii_count == ascii_count\n    assert trace.multibyte_count == multibyte_count\n    assert trace.ascii_count + trace.multibyte_count == trace.code_points\n    assert module.decode_strict(text.encode("utf-8")) == text\n\nfor raw_hex in ("80", "e5 b7", "c0 af", "f4 90 80 80"):\n    try:\n        module.decode_strict(bytes.fromhex(raw_hex))\n    except UnicodeDecodeError:\n        pass\n    else:\n        raise AssertionError(f"invalid UTF-8 accepted: {raw_hex}")\nprint("probe-ok")\n`,
  "utf8",
);

try {
  assert.equal(
    execFileSync("python3", [probe], { encoding: "utf8" }).trim(),
    "probe-ok",
  );
  const output = execFileSync("python3", [example], { encoding: "utf8" });
  assert.match(output, /text='A工🧪'/);
  assert.match(output, /code_points=3, utf8_bytes=8/);
  assert.match(output, /ascii=1, multibyte=2/);
  assert.match(output, /hex=41 e5 b7 a5 f0 9f a7 aa/);
  assert.match(output, /round_trip=True/);
} finally {
  rmSync(workspace, { recursive: true, force: true });
}

console.log(JSON.stringify({
  valid: true,
  python: "python3",
  valid_cases: 6,
  invalid_utf8_cases: 4,
  code_point_and_byte_units: true,
  grapheme_boundary_demonstrated: true,
  strict_decode_verified: true,
  round_trip_verified: true,
  network_used: false,
  third_party_packages: false,
}, null, 2));
