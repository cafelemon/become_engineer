import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createRequire } from "node:module";

const root = resolve(import.meta.dirname, "..");
const lessonId = "nlp-transformer-02";
const lesson = readFileSync(resolve(root, "site-src/learning-paths/ai-foundation/nlp-transformer/02-tokenization-tfidf-linear-baseline.md"), "utf8");
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
for (const phrase of ["vocabulary_size=232", "accuracy=0.500,macro_f1=0.333", "accuracy=0.875,macro_f1=0.873", "validation_errors=P09", "test_policy=sealed", "训练集", "来源与版本"]) {
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

const cwd = resolve(root, "site-src/examples/nlp-transformer/text-classification-evolution-v02");
const python = process.env.NLP_PYTHON || "python3";
const tests = spawnSync(python, ["-m", "unittest", "-v", "test_experiment.py"], { cwd, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 6 tests/);
const run = spawnSync(python, ["experiment.py"], { cwd, encoding: "utf8" });
assert.equal(run.status, 0, run.stdout + run.stderr);
for (const phrase of ["vocabulary_size=232", "baseline_validation: accuracy=0.500,macro_f1=0.333", "model_validation: accuracy=0.875,macro_f1=0.873", "validation_errors=P09", "test_policy=sealed"]) {
  assert.ok(run.stdout.includes(phrase), `run missing ${phrase}`);
}
console.log(JSON.stringify({ valid: true, lesson_id: lessonId, python_tests: 6, tutor_cards: knowledge.cards.length, search_cases: fixture.cases.length, top3_hits: topThreeHits, unknown_cases: fixture.unknown.length }, null, 2));
