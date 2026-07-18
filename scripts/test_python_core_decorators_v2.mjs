import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const python = join(root, ".venv/bin/python");
const example = join(root, "site-src/examples/python-core/decorators_contextmanagers.py");
const project = join(root, "exercises/programming-languages/study-progress-reporters/python");

assert.match(execFileSync(python,["-m","mypy","--strict",example],{cwd:root,encoding:"utf8"}),/Success: no issues found/);
const workspace=mkdtempSync(join(tmpdir(),"be-python-decorators-"));
const probe=join(workspace,"probe.py");
writeFileSync(probe,`import importlib.util\nimport sys\nfrom pathlib import Path\nfrom tempfile import TemporaryDirectory\npath=Path(${JSON.stringify(example)})\nspec=importlib.util.spec_from_file_location("decorators_contextmanagers",path)\nassert spec and spec.loader\nmodule=importlib.util.module_from_spec(spec)\nsys.modules[spec.name]=module\nspec.loader.exec_module(module)\nevents=[]\n@module.trace_calls(events.append)\ndef join(left: str, right: str="!") -> str:\n    """Join docs."""\n    return left+right\nassert join("A",right="B")=="AB"\nassert events==["开始:join","完成:join"]\nassert join.__name__=="join" and join.__doc__=="Join docs." and hasattr(join,"__wrapped__")\nfailure=[]\n@module.trace_calls(failure.append)\ndef fail() -> None:\n    raise ValueError("bad")\ntry:\n    fail()\nexcept ValueError as error:\n    assert str(error)=="bad"\nelse:\n    raise AssertionError("exception suppressed")\nassert failure==["开始:fail","失败:fail:ValueError"]\nwith TemporaryDirectory() as directory:\n    root=Path(directory)\n    output=root/"audit.txt"\n    with module.staged_output_path(output) as pending:\n        pending.write_text("new\\n",encoding="utf-8")\n    assert output.read_text(encoding="utf-8")=="new\\n"\n    output.write_text("old\\n",encoding="utf-8")\n    pending=output.with_name(f".{output.name}.tmp")\n    try:\n        with module.staged_output_path(output) as staged:\n            staged.write_text("broken\\n",encoding="utf-8")\n            raise RuntimeError("stop")\n    except RuntimeError:\n        pass\n    assert output.read_text(encoding="utf-8")=="old\\n"\n    assert not pending.exists()\nprint("probe-ok")\n`,"utf8");
try {
  assert.equal(execFileSync(python,[probe],{encoding:"utf8"}).trim(),"probe-ok");
  const output=execFileSync(python,[example],{encoding:"utf8"});
  assert.match(output,/result=完成。/);
  assert.match(output,/events=\['开始:join_text', '完成:join_text'\]/);
  assert.match(output,/name=join_text/);
  assert.match(output,/failure=ValueError/);
  assert.match(output,/preserved=旧审计内容/);
  assert.match(output,/pending_exists=False/);
} finally { rmSync(workspace,{recursive:true,force:true}); }

assert.match(execFileSync(python,["-m","mypy","--strict","."],{cwd:project,encoding:"utf8"}),/Success: no issues found/);
const tests=spawnSync(python,["-m","unittest","discover","-s","tests","-v"],{cwd:project,encoding:"utf8",env:{...process.env,PYTHONPATH:"src"}});
assert.equal(tests.status,0,tests.stdout+tests.stderr);
assert.match(tests.stdout+tests.stderr,/Ran 30 tests/);
console.log(JSON.stringify({valid:true,mypy_strict_passed:true,closure_isolated:true,signature_and_metadata:true,exception_propagated:true,staged_publish:true,old_file_preserved:true,pending_cleaned:true,project_tests:30,network_used:false},null,2));
