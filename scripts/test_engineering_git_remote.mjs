import assert from "node:assert/strict";
import { appendFile, mkdir, mkdtemp, realpath, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFileSync } from "node:child_process";

const root = await mkdtemp(join(tmpdir(), "be-engineering-git-remote-"));
const home = join(root, "home");
const source = join(root, "learning-workspace");
const remote = join(root, "learning-workspace.git");
const clone = join(root, "learning-workspace-clone");

await mkdir(home, { recursive: true });
await mkdir(join(source, "notes"), { recursive: true });
await mkdir(join(source, "practice"), { recursive: true });

const env = {
  ...process.env,
  HOME: home,
  XDG_CONFIG_HOME: join(home, ".config"),
  GIT_CONFIG_NOSYSTEM: "1",
  GIT_TERMINAL_PROMPT: "0",
  GIT_AUTHOR_DATE: "2026-07-17T09:00:00+08:00",
  GIT_COMMITTER_DATE: "2026-07-17T09:00:00+08:00",
};

function git(args, cwd = source) {
  return execFileSync("git", args, {
    cwd,
    env,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  }).trim();
}

try {
  await writeFile(join(source, ".gitignore"), "*.log\n.env\n", "utf8");
  await writeFile(join(source, "debug.log"), "temporary debug output\n", "utf8");
  await writeFile(join(source, "notes", "learning-log.md"), "# 工程学习记录\n", "utf8");
  await writeFile(join(source, "practice", "README.md"), "# Practice\n", "utf8");

  git(["init", "-b", "main"]);
  git(["config", "--local", "user.name", "Course Verifier"]);
  git(["config", "--local", "user.email", "course-verifier@example.invalid"]);
  git(["add", ".gitignore", "notes/learning-log.md", "practice/README.md"]);
  git(["commit", "-m", "record learning workspace"]);

  await appendFile(join(source, "notes", "learning-log.md"), "\n## Git 本地记录\n", "utf8");
  git(["add", "notes/learning-log.md"]);
  git(["commit", "-m", "document Git setup"]);

  git(["init", "--bare", "--initial-branch=main", remote], root);
  git(["remote", "add", "origin", remote]);
  assert.equal(await realpath(git(["remote", "get-url", "origin"])), await realpath(remote));

  git(["push", "-u", "origin", "main"]);
  assert.match(git(["branch", "-vv"]), /\[origin\/main\]/);
  assert.equal(git(["status", "-sb"]), "## main...origin/main");

  await appendFile(
    join(source, "notes", "learning-log.md"),
    "\n## GitHub 远程验证\n\n- 远程名称：origin\n- clone 检查：等待完成\n",
    "utf8",
  );
  git(["add", "notes/learning-log.md"]);
  git(["commit", "-m", "document remote verification"]);
  git(["push"]);

  git(["clone", remote, clone], root);
  const sourceHead = git(["rev-parse", "HEAD"]);
  const cloneHead = git(["rev-parse", "HEAD"], clone);
  const remoteHead = git(["--git-dir", remote, "rev-parse", "refs/heads/main"], root);

  assert.equal(sourceHead, cloneHead);
  assert.equal(sourceHead, remoteHead);
  assert.equal(await realpath(git(["remote", "get-url", "origin"], clone)), await realpath(remote));
  assert.equal(git(["log", "-1", "--format=%s"], clone), "document remote verification");
  assert.equal(git(["status", "--short"], clone), "");

  process.stdout.write(
    `${JSON.stringify({
      valid: true,
      local_commits: 3,
      upstream: "origin/main",
      remote_branch: "main",
      clone_head_matches: true,
      network_used: false,
      credentials_used: false,
    }, null, 2)}\n`,
  );
} finally {
  await rm(root, { recursive: true, force: true });
}
