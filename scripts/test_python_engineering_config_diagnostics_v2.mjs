import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root=resolve(import.meta.dirname,"..");
const python=join(root,".venv/bin/python");
const project=join(root,"exercises/programming-languages/study-progress-reporters/python");
const env={...process.env,PYTHONPATH:join(project,"src")};
const run=(args,cwd=project)=>spawnSync(python,["-m","study_progress_reporter",...args],{cwd,encoding:"utf8",env});

const mypy=spawnSync(python,["-m","mypy","--strict","."],{cwd:project,encoding:"utf8"});
assert.equal(mypy.status,0,mypy.stdout+mypy.stderr);
const tests=spawnSync(python,["-m","unittest","discover","-s","tests","-v"],{cwd:project,encoding:"utf8",env});
assert.equal(tests.status,0,tests.stdout+tests.stderr);
assert.match(tests.stdout+tests.stderr,/Ran 30 tests/);

const workspace=mkdtempSync(join(tmpdir(),"be-config-diagnostics-"));
try {
  const defaultRun=run(["report"]);
  assert.equal(defaultRun.status,0);
  assert.match(defaultRun.stdout,/总体进度：87\.1%/);
  assert.equal(defaultRun.stderr,"");

  const config=join(workspace,"reporter.toml");
  writeFileSync(config,'[report]\ntag = "工程"\n[logging]\nlevel = "INFO"\n',"utf8");
  const configured=run(["--config",config,"report"]);
  assert.equal(configured.status,0);
  assert.match(configured.stdout,/工程复盘/);
  assert.doesNotMatch(configured.stdout,/Python 起步/);
  assert.match(configured.stderr,/INFO study_progress_reporter/);

  const overridden=run(["--config",config,"--log-level","WARNING","report","--tag","基础"]);
  assert.equal(overridden.status,0);
  assert.match(overridden.stdout,/Python 起步/);
  assert.doesNotMatch(overridden.stdout,/工程复盘/);
  assert.equal(overridden.stderr,"");

  for (const [name,contents] of [
    ["malformed.toml","[report\ntag = 1"],
    ["unknown.toml","[report]\ncolour = 'blue'\n"],
    ["wrong.toml","[report]\ntag = 3\n"],
    ["level.toml","[logging]\nlevel = 'TRACE'\n"],
  ]) {
    const path=join(workspace,name); writeFileSync(path,contents,"utf8");
    const result=run(["--config",path,"report"]);
    assert.equal(result.status,1,name+result.stdout+result.stderr);
    assert.equal(result.stdout,"");
    assert.match(result.stderr,/错误：/);
  }

  const noOutput=run(["audit"]);
  assert.equal(noOutput.status,1);
  assert.equal(noOutput.stdout,"");
  assert.match(noOutput.stderr,/需要 --output/);
  const badSyntax=run(["unknown"]);
  assert.equal(badSyntax.status,2);
  assert.equal(badSyntax.stdout,"");
  assert.match(badSyntax.stderr,/usage:/);

  const audit=join(workspace,"audit.txt");
  const auditOk=run(["--log-level","INFO","audit","--output",audit]);
  assert.equal(auditOk.status,0);
  assert.equal(auditOk.stdout,"");
  assert.match(auditOk.stderr,/审计文件已写入/);
  assert.match(readFileSync(audit,"utf8"),/^学习审计快照/);
  writeFileSync(audit,"旧内容\n","utf8");
  const badConfig=join(workspace,"bad-before-audit.toml");
  writeFileSync(badConfig,"[logging\n","utf8");
  const auditRejected=run(["--config",badConfig,"audit","--output",audit]);
  assert.equal(auditRejected.status,1);
  assert.equal(readFileSync(audit,"utf8"),"旧内容\n");

  const quietConfig=join(workspace,"config.example.toml");
  writeFileSync(quietConfig,'[report]\ntag = "工程"\n[logging]\nlevel = "INFO"\n',"utf8");
  const noAutoLoad=run(["report"],workspace);
  assert.equal(noAutoLoad.status,0);
  assert.match(noAutoLoad.stdout,/Python 起步/);
  assert.equal(noAutoLoad.stderr,"");

  const loggingProbe=spawnSync(python,["-c","from study_progress_reporter.logging_setup import configure_logging; a=configure_logging('INFO'); b=configure_logging('INFO'); b.info('once')"],{cwd:project,encoding:"utf8",env});
  assert.equal(loggingProbe.status,0);
  assert.equal((loggingProbe.stderr.match(/once/g)||[]).length,1);
} finally {
  rmSync(workspace,{recursive:true,force:true});
}

console.log(JSON.stringify({valid:true,mypy_strict_passed:true,project_tests:30,stdout_stderr_exit_codes:true,explicit_toml:true,validation_rejections:true,cli_precedence:true,named_logger_no_duplicates:true,no_auto_config:true,audit_preserved:true,network_used:false},null,2));
