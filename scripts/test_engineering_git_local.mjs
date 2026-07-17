import assert from "node:assert/strict";
import { appendFile, mkdir, mkdtemp, realpath, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFileSync } from "node:child_process";

const root = await mkdtemp(join(tmpdir(), "be-engineering-git-local-"));
const home = join(root, "home");
const workspace = join(root, "learning-workspace");

await mkdir(home, { recursive: true });
await mkdir(join(workspace, "notes"), { recursive: true });
await mkdir(join(workspace, "practice"), { recursive: true });
await mkdir(join(workspace, "assets"), { recursive: true });

const env = {
  ...process.env,
  HOME: home,
  XDG_CONFIG_HOME: join(home, ".config"),
  GIT_CONFIG_NOSYSTEM: "1",
  GIT_AUTHOR_DATE: "2026-07-17T08:00:00+08:00",
  GIT_COMMITTER_DATE: "2026-07-17T08:00:00+08:00",
};

function git(args) {
  return execFileSync("git", args, {
    cwd: workspace,
    env,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  }).trim();
}

try {
  await writeFile(
    join(workspace, "notes", "learning-log.md"),
    "# 工程学习记录\n\n## 本次结果\n\n- 已建立学习工作区。\n",
    "utf8",
  );
  await writeFile(
    join(workspace, "practice", "README.md"),
    "# Practice\n\n这里保存可复现练习。\n",
    "utf8",
  );
  await writeFile(
    join(workspace, ".gitignore"),
    "*.log\n.venv/\n__pycache__/\n.env\n.DS_Store\nThumbs.db\n",
    "utf8",
  );
  await writeFile(join(workspace, "debug.log"), "temporary debug output\n", "utf8");

  git(["init", "-b", "main"]);
  git(["config", "--local", "user.name", "Course Verifier"]);
  git(["config", "--local", "user.email", "course-verifier@example.invalid"]);

  assert.equal(git(["branch", "--show-current"]), "main");
  assert.equal(await realpath(git(["rev-parse", "--show-toplevel"])), await realpath(workspace));
  assert.match(git(["config", "--local", "--list", "--show-origin"]), /\.git\/config\s+user\.name=Course Verifier/);

  const ignoreMatch = git(["check-ignore", "-v", "debug.log"]);
  assert.match(ignoreMatch, /\.gitignore:1:\*\.log\s+debug\.log$/);
  assert.match(git(["status", "--short", "--ignored"]), /^!! debug\.log$/m);

  git(["add", ".gitignore", "notes/learning-log.md", "practice/README.md"]);
  assert.deepEqual(
    git(["diff", "--cached", "--name-only"]).split("\n"),
    [".gitignore", "notes/learning-log.md", "practice/README.md"],
  );
  assert.equal(git(["ls-files", "debug.log"]), "");
  git(["commit", "-m", "record learning workspace"]);

  await appendFile(
    join(workspace, "notes", "learning-log.md"),
    "\n## Git 本地记录\n\n- 当前分支：main\n- 忽略检查：debug.log 匹配 `*.log`\n",
    "utf8",
  );
  assert.match(git(["diff", "--", "notes/learning-log.md"]), /Git 本地记录/);
  git(["add", "notes/learning-log.md"]);
  git(["commit", "-m", "document Git setup"]);

  assert.deepEqual(
    git(["log", "-2", "--format=%s"]).split("\n"),
    ["document Git setup", "record learning workspace"],
  );
  assert.equal(git(["ls-files", "debug.log"]), "");
  assert.equal(git(["status", "--short", "--ignored"]), "!! debug.log");

  process.stdout.write(
    `${JSON.stringify({
      valid: true,
      branch: "main",
      commits: 2,
      ignored: ["debug.log"],
      tracked: [".gitignore", "notes/learning-log.md", "practice/README.md"],
    }, null, 2)}\n`,
  );
} finally {
  await rm(root, { recursive: true, force: true });
}
