import assert from "node:assert/strict";
import { mkdtempSync, realpathSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, normalize, sep } from "node:path";
import { spawnSync } from "node:child_process";

const pythonCommand = process.env.PYTHON ?? (process.platform === "win32" ? "python" : "python3");
const workspace = mkdtempSync(join(tmpdir(), "be-development-environment-"));
const realWorkspace = realpathSync(workspace);
const venvDirectory = join(workspace, ".venv");
const venvPython = process.platform === "win32"
  ? join(venvDirectory, "Scripts", "python.exe")
  : join(venvDirectory, "bin", "python");

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: workspace,
    encoding: "utf8",
    ...options,
  });

  if (result.status !== 0) {
    throw new Error([
      `${command} ${args.join(" ")} failed with status ${result.status}`,
      result.stdout,
      result.stderr,
    ].filter(Boolean).join("\n"));
  }

  return result.stdout.trim();
}

try {
  const baseVersion = run(pythonCommand, ["--version"]);
  run(pythonCommand, ["-m", "venv", ".venv"]);

  const probe = JSON.parse(run(venvPython, [
    "-c",
    "import json, sys; print(json.dumps({'executable': sys.executable, 'prefix': sys.prefix, 'base_prefix': sys.base_prefix, 'isolated': sys.prefix != sys.base_prefix}))",
  ]));
  const pipVersion = run(venvPython, ["-m", "pip", "--version"]);

  assert.equal(probe.isolated, true, "the project interpreter must report an active virtual environment");
  assert.notEqual(probe.prefix, probe.base_prefix, "virtual and base prefixes must differ");
  assert.equal(
    normalize(realpathSync(probe.executable)),
    normalize(realpathSync(venvPython)),
    "sys.executable must point at the project virtual environment",
  );
  assert.match(pipVersion, /pip\s+\d+/i, "the virtual environment must provide pip");
  assert.ok(
    normalize(pipVersion).includes(`${sep}.venv${sep}`),
    "pip must be loaded from the project virtual environment",
  );

  console.log(JSON.stringify({
    valid: true,
    base_version: baseVersion,
    project_python: normalize(probe.executable).replace(normalize(realWorkspace), "<WORKSPACE>"),
    isolated: probe.isolated,
    pip_from_project_environment: true,
    network_used: false,
    packages_installed: false,
  }, null, 2));
} finally {
  rmSync(workspace, { recursive: true, force: true });
}
