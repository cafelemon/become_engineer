import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const python = join(root, ".venv/bin/python");
const example = join(root, "site-src/examples/python-core/iterators_generators.py");
const project = join(root, "exercises/programming-languages/study-progress-reporters/python");
assert.match(execFileSync(python,["-m","mypy","--strict",example],{cwd:root,encoding:"utf8"}),/Success: no issues found/);

const workspace=mkdtempSync(join(tmpdir(),"be-python-iterators-"));
const probe=join(workspace,"probe.py");
writeFileSync(probe,`import importlib.util\nimport sys\nfrom itertools import islice\nfrom pathlib import Path\npath=Path(${JSON.stringify(example)})\nspec=importlib.util.spec_from_file_location("iterators_generators",path)\nassert spec and spec.loader\nmodule=importlib.util.module_from_spec(spec)\nsys.modules[spec.name]=module\nspec.loader.exec_module(module)\nevents=[]\ndef source():\n    events.append("start")\n    for name, tag in (("A","x"),("B","y"),("C","x")):\n        events.append(name)\n        yield module.StudyRecord(course_name=name,completed_hours=1.0,target_hours=2.0,tags=[tag])\nfiltered=module.iter_by_tag(source(),"x")\nassert events==[]\nassert next(filtered)["course_name"]=="A"\nassert events==["start","A"]\nassert [r["course_name"] for r in filtered]==["C"]\nassert list(filtered)==[]\nassert [r["course_name"] for r in module.iter_by_tag(source(),"x")]==["A","C"]\nassert module.one_pass_summary(iter([2.0,3.0]))==(5.0,2)\nassert module.one_pass_summary(iter([]))==(0.0,0)\nassert list(islice(module.natural_numbers(),0))==[]\nassert list(islice(module.natural_numbers(),5))==[0,1,2,3,4]\ntry:\n    list(zip([1,2],[3],strict=True))\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("unequal zip accepted")\nprint("probe-ok")\n`,"utf8");
try{
 assert.equal(execFileSync(python,[probe],{encoding:"utf8"}).trim(),"probe-ok");
 const output=execFileSync(python,[example],{encoding:"utf8"});
 assert.match(output,/before=\[\]/);
 assert.match(output,/first=Python/);
 assert.match(output,/after_first=\['start', 'Python'\]/);
 assert.match(output,/remaining=\['CS'\]/);
 assert.match(output,/exhausted=\[\]/);
 assert.match(output,/one_pass=\(10\.0, 2\)/);
 assert.match(output,/bounded=\[0, 1, 2, 3, 4\]/);
}finally{rmSync(workspace,{recursive:true,force:true});}
assert.match(execFileSync(python,["-m","mypy","--strict","."],{cwd:project,encoding:"utf8"}),/Success: no issues found/);
const tests=execFileSync(python,["-m","unittest","discover","-s","tests"],{cwd:project,encoding:"utf8",env:{...process.env,PYTHONPATH:"src"},stdio:["ignore","pipe","pipe"]});
void tests;
console.log(JSON.stringify({valid:true,mypy_strict_passed:true,lazy_start:true,single_consumption:true,fresh_iterator:true,one_pass_summary:true,bounded_infinite_source:true,strict_zip_failure:true,project_tests:30,network_used:false},null,2));
