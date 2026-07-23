import assert from"node:assert/strict";import{spawnSync}from"node:child_process";import{readFileSync}from"node:fs";import{resolve}from"node:path";
const root=resolve(import.meta.dirname,".."),lesson=readFileSync(resolve(root,"learning-paths/ai-foundation/deep-learning/03-cross-entropy-autograd-backprop-gradient-check.md"),"utf8");
for(const type of["overview","concept","example","reproduce","modify","troubleshoot","project"])assert.match(lesson,new RegExp(`data-context-type="${type}"`));
for(const phrase of["loss=cross_entropy:0.902966,requires_grad:true","backward=parameter_gradients:4,finite:true","autograd:-0.525691,numerical:-0.525683,abs_error:0.000008","accumulation=second_backward:2.000x","loss-from-logits,backward-once-per-graph,gradients-checked,zero-before-next-step"])assert.ok(lesson.includes(phrase));
for(const phrase of["有限差分","set_to_none","零基础兴趣","有基础求职","PyTorch 2.13.0"])assert.ok(lesson.includes(phrase));
const python=process.env.DL_PYTHON||resolve(root,".venv/bin/python"),tests=spawnSync(python,["-m","unittest","-v","test_gradient_lab.py"],{cwd:resolve(root,"site-src/examples/deep-learning/diagnosable-neural-network-v03"),encoding:"utf8",env:process.env});
assert.equal(tests.status,0,tests.stdout+tests.stderr);assert.match(tests.stdout+tests.stderr,/Ran 8 tests/);
console.log(JSON.stringify({valid:true,lesson_id:"deep-learning-03",tests:8,finite_difference:true,gradient_accumulation:true},null,2));
