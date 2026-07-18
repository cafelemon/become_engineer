import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root=resolve(import.meta.dirname,"..");
const python=join(root,".venv/bin/python");
const project=join(root,"exercises/programming-languages/study-progress-reporters/python");
const workspace=mkdtempSync(join(tmpdir(),"be-package-cli-"));
const dist=join(workspace,"dist");
const venv=join(workspace,"venv");
const bin=join(venv,"bin");

assert.match(execFileSync(python,["-m","mypy","--strict","."],{cwd:project,encoding:"utf8"}),/Success: no issues found/);
const tests=spawnSync(python,["-m","unittest","discover","-s","tests","-v"],{cwd:project,encoding:"utf8",env:{...process.env,PYTHONPATH:"src"}});
assert.equal(tests.status,0,tests.stdout+tests.stderr);
assert.match(tests.stdout+tests.stderr,/Ran 30 tests/);

try {
  execFileSync(python,["-m","build","--no-isolation","--outdir",dist],{cwd:project,encoding:"utf8"});
  const wheels=readdirSync(dist).filter(name=>name.endsWith(".whl"));
  assert.equal(wheels.length,1);
  execFileSync(python,["-m","venv",venv],{cwd:workspace});
  execFileSync(join(bin,"python"),["-m","pip","install","--no-deps",join(dist,wheels[0])],{cwd:workspace,encoding:"utf8"});

  const moduleRun=spawnSync(join(bin,"python"),["-m","study_progress_reporter","report"],{cwd:workspace,encoding:"utf8"});
  assert.equal(moduleRun.status,0,moduleRun.stdout+moduleRun.stderr);
  assert.match(moduleRun.stdout,/总体进度：87\.1%/);
  assert.equal(moduleRun.stderr,"");
  const commandRun=spawnSync(join(bin,"study-progress"),["report"],{cwd:workspace,encoding:"utf8"});
  assert.equal(commandRun.status,0,commandRun.stdout+commandRun.stderr);
  assert.equal(commandRun.stdout,moduleRun.stdout);
  assert.equal(commandRun.stderr,"");

  const filtered=spawnSync(join(bin,"study-progress"),["report","--tag","工程"],{cwd:workspace,encoding:"utf8"});
  assert.equal(filtered.status,0);
  assert.match(filtered.stdout,/工程复盘/);
  assert.doesNotMatch(filtered.stdout,/Python 起步/);
  const help=spawnSync(join(bin,"study-progress"),["--help"],{cwd:workspace,encoding:"utf8"});
  assert.equal(help.status,0);
  assert.match(help.stdout,/report/);
  assert.match(help.stdout,/audit/);
  const bad=spawnSync(join(bin,"study-progress"),["unknown"],{cwd:workspace,encoding:"utf8"});
  assert.equal(bad.status,2);
  assert.equal(bad.stdout,"");
  assert.match(bad.stderr,/usage:/);
  const quietImport=spawnSync(join(bin,"python"),["-c","import study_progress_reporter"],{cwd:workspace,encoding:"utf8"});
  assert.equal(quietImport.status,0);
  assert.equal(quietImport.stdout,"");
  assert.equal(quietImport.stderr,"");
} finally {
  rmSync(workspace,{recursive:true,force:true});
}

console.log(JSON.stringify({valid:true,mypy_strict_passed:true,project_tests:30,wheel_built:true,clean_venv_install:true,outside_project_run:true,module_and_console_equal:true,help_and_exit_codes:true,quiet_import:true,network_used:false},null,2));
