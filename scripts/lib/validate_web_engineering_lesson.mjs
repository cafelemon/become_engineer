import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "../..");
const definitions = {
  "01": ["01-postgresql-alembic-data-migration.md","learning-dashboard-v09","test_postgres.py",4],
  "02": ["02-password-hashing-cookie-sessions-csrf.md","learning-dashboard-v10","test_auth_lab.py",9],
  "03": ["03-resource-ownership-authorization-audit.md","learning-dashboard-v11","test_authorization_lab.py",8],
  "04": ["04-session-frontend-e2e-ci.md","learning-dashboard-v12",null,7],
  "05": ["05-containers-config-health-graceful-shutdown.md","learning-dashboard-v13","test_app.py",4],
  "06": ["06-observability-backup-release-rollback.md","learning-dashboard-v14","test_observability.py",8]
};

export function validateLesson(number) {
  const [file, directory, testFile, checks] = definitions[number];
  const project = join(root,"site-src/examples/web-engineering",directory);
  const markdown = readFileSync(join(root,"learning-paths/web-fullstack/web-engineering",file),"utf8");
  for (const type of ["overview","concept","example","reproduce","modify","troubleshoot","project"]) assert.match(markdown,new RegExp(`data-context-type="${type}"`));
  assert.match(markdown,/data-learning-context=/); assert.match(markdown,/## 完成检查/); assert.match(markdown,/## 来源与版本/); assert.match(markdown,/## 下一步/);
  let result;
  if (number === "04") result=spawnSync("npm",["test"],{cwd:project,encoding:"utf8"});
  else result=spawnSync(join(root,".venv/bin/python"),["-m","unittest","discover","-s",project,"-p",testFile,"-v"],{cwd:root,encoding:"utf8",env:{...process.env,WEB_ENGINEERING_POSTGRES:number==="01"?"1":process.env.WEB_ENGINEERING_POSTGRES}});
  assert.equal(result.status,0,result.stdout+result.stderr);
  console.log(JSON.stringify({
    valid:true,
    lesson_id:`web-engineering-${number}`,
    project:directory,
    checks,
    real_postgresql:number==="01",
    database_backed_browser_e2e:number==="04"
  },null,2));
}
