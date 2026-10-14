import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createRequire } from "node:module";

const root = resolve(import.meta.dirname, "..");
const lessonId = "nlp-transformer-06";
const lesson = readFileSync(resolve(root, "site-src/learning-paths/ai-foundation/nlp-transformer/06-transformer-encoder-classification-ablation.md"), "utf8");
const knowledge = JSON.parse(readFileSync(resolve(root, `site-src/data/tutor/${lessonId}.json`), "utf8"));
const fixture = JSON.parse(readFileSync(resolve(root, `tests/tutor/${lessonId}-search.json`), "utf8"));
const require = createRequire(import.meta.url);
const searchApi = require("../site-src/javascripts/tutor-search.js");

assert.ok(lesson.includes(`data-tutor-lesson="${lessonId}"`));
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(lesson, new RegExp(`data-context-type="${type}"`));
}
for (const context of knowledge.contexts) {
  assert.match(lesson, new RegExp(`<section[^>]*id="${context.id}"[^>]*data-learning-context="${context.id}"[^>]*data-context-type="${context.type}"`));
}
for (const phrase of ["src_key_padding_mask", "True", "8 条验证句", "四类学习者入口", "来源与版本", "test_status"]) {
  assert.ok(lesson.includes(phrase), `lesson missing ${phrase}`);
}
assert.deepEqual(searchApi.validateKnowledgeBase(knowledge), []);
assert.equal(knowledge.lesson.id, lessonId);
assert.ok(knowledge.cards.length >= 8);
assert.equal(fixture.lesson_id, lessonId);
assert.ok(fixture.cases.length >= 16);
let topThreeHits = 0;
for (const testCase of fixture.cases) {
  const card = knowledge.cards.find(item => item.id === testCase.expected_card);
  assert.ok(card, `unknown card: ${testCase.expected_card}`);
  const hits = searchApi.search(testCase.query, knowledge.cards, { lessonId, contextId: card.context_id }, { limit: 3, threshold: 24 });
  if (hits.some(item => item.card.id === card.id)) topThreeHits++;
}
assert.ok(topThreeHits / fixture.cases.length >= 0.8);
for (const unknown of fixture.unknown) {
  assert.equal(searchApi.search(unknown, knowledge.cards, { lessonId, contextId: knowledge.contexts[0].id }, { limit: 3, threshold: 24 }).length, 0);
}

const cwd = resolve(root, "site-src/examples/nlp-transformer/text-classification-evolution-v06");
const python = process.env.NLP_PYTHON || process.env.PYTHON || "python3.12";
const tests = spawnSync(python, ["-m", "unittest", "-v", "test_transformer_lab.py"], { cwd, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr + (tests.error?.message ?? ""));
assert.match(tests.stdout + tests.stderr, /Ran 9 tests/);
const run = spawnSync(python, ["transformer_lab.py"], { cwd, encoding: "utf8" });
assert.equal(run.status, 0, run.stdout + run.stderr + (run.error?.message ?? ""));
const report = JSON.parse(run.stdout);
assert.equal(report.project_version, "0.6");
assert.equal(report.corpus_sha256, "8973927ed683f32cf92bb4a1483b960f3b8c09b0b8497bd0c5176891252b713c");
assert.equal(report.train_rows, 24);
assert.equal(report.validation_rows, 8);
assert.equal(report.test_status, "sealed");
assert.deepEqual(Object.keys(report.variants).sort(), ["full", "no_key_padding_mask", "no_position"]);
assert.ok(!("test_metrics" in report));
for (const variant of Object.values(report.variants)) {
  assert.ok(variant.model_validation.accuracy >= 0 && variant.model_validation.accuracy <= 1);
  assert.ok(variant.model_validation.macro_f1 >= 0 && variant.model_validation.macro_f1 <= 1);
  assert.ok(variant.parameter_count > 0);
  assert.ok(variant.validation_batch_ms_median > 0);
  assert.ok(!("test_metrics" in variant));
}
console.log(JSON.stringify({ valid: true, lesson_id: lessonId, python_tests: 9, tutor_cards: knowledge.cards.length, search_cases: fixture.cases.length, top3_hits: topThreeHits, unknown_cases: fixture.unknown.length }, null, 2));
