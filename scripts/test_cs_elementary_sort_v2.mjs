#!/usr/bin/env node
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
const root=resolve(import.meta.dirname,".."); const python=join(root,".venv/bin/python");
const pyProject=join(root,"exercises/cs-core/traceable-search-sort-lab/python"); const cppProject=join(root,"exercises/cs-core/traceable-search-sort-lab/cpp");
const micro=join(root,"site-src/examples/algorithm-foundation/elementary_sort_trace.py"); const temp=mkdtempSync(join(tmpdir(),"be-cs-elementary-sort-"));
function run(c,a,o={}){return spawnSync(c,a,{cwd:root,encoding:"utf8",...o});} function ok(r,l){assert.equal(r.status,0,`${l}\n${r.stdout}\n${r.stderr}`);}
try{
 const sample=run(python,[micro]); ok(sample,"基础排序小例子失败"); assert.equal(sample.stdout,[
  "input=[3A,1B,3C,2D]",
  "insertion pass=1 items=[1B,3A,3C,2D] comparisons=1 shifts=1",
  "insertion pass=2 items=[1B,3A,3C,2D] comparisons=2 shifts=1",
  "insertion pass=3 items=[1B,2D,3A,3C] comparisons=5 shifts=3",
  "selection pass=1 items=[1B,3A,3C,2D] comparisons=3 swaps=1",
  "selection pass=2 items=[1B,2D,3C,3A] comparisons=5 swaps=2",
  "selection pass=3 items=[1B,2D,3C,3A] comparisons=6 swaps=2",""
 ].join("\n"));
 const env={...process.env,PYTHONPATH:join(pyProject,"src")}; ok(run(python,["-m","unittest","discover","-s","tests","-v"],{cwd:pyProject,env}),"Python 测试失败"); ok(run(python,["-m","mypy","--strict","src","tests"],{cwd:pyProject,env}),"Python mypy失败");
 const build=join(temp,"cpp-build"); ok(run("cmake",["-S",cppProject,"-B",build,"-DCMAKE_BUILD_TYPE=Debug"]),"C++配置失败"); ok(run("cmake",["--build",build,"--config","Debug","--parallel"]),"C++构建失败"); ok(run("ctest",["--test-dir",build,"--build-config","Debug","--output-on-failure"]),"CTest失败");
 const cpp=join(build,"traceable_search_sort_lab"); for(const mode of ["search","elementary","merge"]){const p=run(python,["-m","traceable_search_sort_lab",mode],{cwd:pyProject,env});const c=run(cpp,[mode]);ok(p,`Python ${mode}失败`);ok(c,`C++ ${mode}失败`);assert.equal(c.stdout.trim(),p.stdout.trim());}
 console.log("插入排序、选择排序与稳定性验证通过");
}finally{rmSync(temp,{recursive:true,force:true});}
