import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createRequire } from "node:module";

const root = resolve(import.meta.dirname, "..");
const lessonId = "nlp-transformer-07";
const lesson = readFileSync(resolve(root, "learning-paths/ai-foundation/nlp-transformer/07-pretrained-path-unified-evaluation-model-card.md"), "utf8");
const knowledge = JSON.parse(readFileSync(resolve(root, `site-src/data/tutor/${lessonId}.json`), "utf8"));
const fixture = JSON.parse(readFileSync(resolve(root, `tests/tutor/${lessonId}-search.json`), "utf8"));
const modelCard = readFileSync(resolve(root, "site-src/examples/nlp-transformer/text-classification-evolution-v07/MODEL_CARD.md"), "utf8");
const require = createRequire(import.meta.url);
const searchApi = require("../site-src/javascripts/tutor-search.js");

assert.ok(lesson.includes(`data-tutor-lesson="${lessonId}"`));
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(lesson, new RegExp(`data-context-type="${type}"`));
}
for (const context of knowledge.contexts) {
  assert.match(lesson, new RegExp(`id="${context.id}"[^>]*data-learning-context="${context.id}"`));
}
for (const phrase of ["validation: accuracy=1.000", "final_test: accuracy=0.500", "C03,C04,C15,P18", "pretrained_model_evidence=not_run", "v06 完整 Encoder", "消融", "四类学习者入口"]) {
  assert.ok(lesson.includes(phrase), `lesson missing ${phrase}`);
}
for (const phrase of ["最终测试：4/8", "预训练", "不得根据本次测试回头改选"]) assert.ok(modelCard.includes(phrase));
assert.deepEqual(searchApi.validateKnowledgeBase(knowledge), []);
assert.equal(knowledge.cards.length, 8);
assert.equal(fixture.cases.length, 16);
let topThreeHits = 0;
for (const testCase of fixture.cases) {
  const card = knowledge.cards.find(item => item.id === testCase.expected_card);
  assert.ok(card);
  const hits = searchApi.search(testCase.query, knowledge.cards, { lessonId, contextId: card.context_id }, { limit: 3, threshold: 24 });
  if (hits.some(item => item.card.id === card.id)) topThreeHits++;
}
assert.ok(topThreeHits / fixture.cases.length >= 0.8);
for (const unknown of fixture.unknown) {
  assert.equal(searchApi.search(unknown, knowledge.cards, { lessonId, contextId: knowledge.contexts[0].id }, { limit: 3, threshold: 24 }).length, 0);
}
const cwd = resolve(root, "site-src/examples/nlp-transformer/text-classification-evolution-v07");
const python = process.env.NLP_PYTHON || "python3.12";
const tests = spawnSync(python, ["-m", "unittest", "-v", "test_delivery_lab.py"], { cwd, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 10 tests/);
// Deliberately run only the pre-test plan here; never re-open final test in routine CI.
const run = spawnSync(python, ["delivery_lab.py"], { cwd, encoding: "utf8" });
assert.equal(run.status, 0, run.stdout + run.stderr);
const plan = JSON.parse(run.stdout);
assert.equal(plan.selected_before_test, "v06-encoder-full");
assert.equal(plan.test_status, "sealed_before_selection");
assert.equal(plan.candidates.length, 6);
assert.deepEqual(Object.keys(plan.ablations_not_candidates).sort(), ["no_key_padding_mask", "no_position"]);
console.log(JSON.stringify({ valid: true, lesson_id: lessonId, python_tests: 10, tutor_cards: 8, search_cases: 16, top3_hits: topThreeHits, unknown_cases: fixture.unknown.length, selected_before_test: plan.selected_before_test, routine_test_opened: false }, null, 2));
