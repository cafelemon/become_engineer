import assert from "node:assert/strict";
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  realpathSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join, normalize } from "node:path";
import { spawnSync } from "node:child_process";

const workspace = mkdtempSync(join(tmpdir(), "be-stage-zero-validation-"));

function runGit(args) {
  const result = spawnSync("git", args, {
    cwd: workspace,
    encoding: "utf8",
    env: { ...process.env, GIT_CONFIG_NOSYSTEM: "1" },
  });

  if (result.status !== 0) {
    throw new Error([
      `git ${args.join(" ")} failed with status ${result.status}`,
      result.stdout,
      result.stderr,
    ].filter(Boolean).join("\n"));
  }

  return result.stdout.trim();
}

function classify({ ran, matched }) {
  if (!ran) return "unverified";
  return matched ? "success" : "failure";
}

try {
  mkdirSync(join(workspace, "notes"), { recursive: true });
  mkdirSync(join(workspace, "practice"), { recursive: true });
  mkdirSync(join(workspace, ".venv"), { recursive: true });

  writeFileSync(join(workspace, ".gitignore"), ".venv/\n*.log\n", "utf8");
  writeFileSync(join(workspace, "notes", "learning-log.md"), "# 学习记录\n\n工程基础开始。\n", "utf8");
  writeFileSync(join(workspace, "practice", "README.md"), "# 练习目录\n", "utf8");
  writeFileSync(join(workspace, ".venv", "pyvenv.cfg"), "home = <LOCAL>\n", "utf8");

  runGit(["init", "-b", "main"]);
  runGit(["config", "user.name", "Become Engineer Test"]);
  runGit(["config", "user.email", "test@example.invalid"]);
  runGit(["add", ".gitignore", "notes/learning-log.md", "practice/README.md"]);
  runGit(["commit", "-m", "create learning workspace"]);

  writeFileSync(join(workspace, "notes", "environment-check.md"), "# 开发环境检查\n", "utf8");
  runGit(["add", "notes/environment-check.md"]);
  runGit(["commit", "-m", "record development environment"]);

  writeFileSync(join(workspace, "notes", "docker-check.md"), "# Docker 检查\n\nEngine：未检查\n", "utf8");
  runGit(["add", "notes/docker-check.md"]);
  runGit(["commit", "-m", "record Docker basics"]);

  const reportedRoot = normalize(realpathSync(runGit(["rev-parse", "--show-toplevel"])));
  const expectedRoot = normalize(realpathSync(workspace));
  const commits = Number(runGit(["rev-list", "--count", "HEAD"]));
  const ignoredPath = runGit(["check-ignore", ".venv/pyvenv.cfg"]);
  const status = runGit(["status", "--porcelain=v1"]);

  let missingFileError = "";
  try {
    readFileSync(join(workspace, "notes", "does-not-exist.md"), "utf8");
  } catch (error) {
    missingFileError = error?.code ?? "UNKNOWN";
  }
  const recoveredContent = readFileSync(join(workspace, "notes", "learning-log.md"), "utf8");

  const checks = [
    { id: "project-root", ran: true, matched: reportedRoot === expectedRoot },
    { id: "git-history", ran: true, matched: commits === 3 },
    { id: "ignored-environment", ran: true, matched: ignoredPath === ".venv/pyvenv.cfg" },
    { id: "clean-worktree", ran: true, matched: status === "" },
    { id: "missing-file-reproduction", ran: true, matched: missingFileError === "ENOENT" && recoveredContent.includes("工程基础开始") },
    { id: "docker-engine", ran: false, matched: false },
  ].map((check) => ({ ...check, status: classify(check) }));

  assert.equal(checks.filter((check) => check.status === "success").length, 5);
  assert.equal(checks.filter((check) => check.status === "failure").length, 0);
  assert.equal(checks.filter((check) => check.status === "unverified").length, 1);
  assert.equal(checks.find((check) => check.id === "docker-engine")?.status, "unverified");

  assert.equal(classify({ ran: true, matched: false }), "failure");
  assert.equal(classify({ ran: false, matched: false }), "unverified");

  console.log(JSON.stringify({
    valid: true,
    project_root_confirmed: true,
    commits,
    ignored_environment: true,
    clean_worktree: true,
    safe_failure_reproduced: missingFileError,
    recovery_confirmed: true,
    docker_status: "unverified",
    network_used: false,
    docker_invoked: false,
  }, null, 2));
} finally {
  rmSync(workspace, { recursive: true, force: true });
}
