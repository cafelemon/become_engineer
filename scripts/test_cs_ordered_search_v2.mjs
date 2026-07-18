#!/usr/bin/env node
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root=resolve(import.meta.dirname,"..");
const python=join(root,".venv/bin/python");
const pyProject=join(root,"exercises/cs-core/traceable-search-sort-lab/python");
const cppProject=join(root,"exercises/cs-core/traceable-search-sort-lab/cpp");
const micro=join(root,"site-src/examples/algorithm-foundation/binary_bounds_trace.py");
const temp=mkdtempSync(join(tmpdir(),"be-cs-ordered-search-"));
function run(command,args,options={}){return spawnSync(command,args,{cwd:root,encoding:"utf8",...options});}
function ok(result,label){assert.equal(result.status,0,`${label}\n${result.stdout}\n${result.stderr}`);}
try{
  const sample=run(python,[micro]); ok(sample,"二分边界小例子运行失败");
  assert.equal(sample.stdout,[
    "lower round=1 range=[0,6) mid=3 value=3 next=[0,3)",
    "lower round=2 range=[0,3) mid=1 value=3 next=[0,1)",
    "lower round=3 range=[0,1) mid=0 value=1 next=[1,1)",
    "lower index=1 comparisons=3",
    "upper round=1 range=[0,6) mid=3 value=3 next=[4,6)",
    "upper round=2 range=[4,6) mid=5 value=9 next=[4,5)",
    "upper round=3 range=[4,5) mid=4 value=7 next=[4,4)",
    "upper index=4 comparisons=3",""
  ].join("\n"));
  const env={...process.env,PYTHONPATH:join(pyProject,"src")};
  ok(run(python,["-m","unittest","discover","-s","tests","-v"],{cwd:pyProject,env}),"Python 查找排序测试失败");
  ok(run(python,["-m","mypy","--strict","src","tests"],{cwd:pyProject,env}),"Python 查找排序 mypy 失败");
  const build=join(temp,"cpp-build");
  ok(run("cmake",["-S",cppProject,"-B",build,"-DCMAKE_BUILD_TYPE=Debug"]),"C++ 配置失败");
  ok(run("cmake",["--build",build,"--config","Debug","--parallel"]),"C++ 构建失败");
  ok(run("ctest",["--test-dir",build,"--build-config","Debug","--output-on-failure"]),"C++ CTest 失败");
  const cpp=join(build,"traceable_search_sort_lab");
  for(const mode of ["search","elementary","merge"]){
    const pyRun=run(python,["-m","traceable_search_sort_lab",mode],{cwd:pyProject,env});
    const cppRun=run(cpp,[mode]); ok(pyRun,`Python ${mode} 失败`); ok(cppRun,`C++ ${mode} 失败`);
    assert.equal(cppRun.stdout.trim(),pyRun.stdout.trim(),`${mode} 双语言输出应一致`);
  }
  console.log("有序查找、半开区间与左右边界验证通过");
}finally{rmSync(temp,{recursive:true,force:true});}
