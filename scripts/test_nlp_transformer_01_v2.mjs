import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createRequire } from "node:module";

const root = resolve(import.meta.dirname, "..");
const lessonId = "nlp-transformer-01";
const lesson = readFileSync(resolve(root, "site-src/learning-paths/ai-foundation/nlp-transformer/01-text-data-contract-splits-metrics.md"), "utf8");
const knowledge = JSON.parse(readFileSync(resolve(root, `site-src/data/tutor/${lessonId}.json`), "utf8"));
const fixture = JSON.parse(readFileSync(resolve(root, `tests/tutor/${lessonId}-search.json`), "utf8"));
const require = createRequire(import.meta.url);
const searchApi = require("../site-src/javascripts/tutor-search.js");

assert.ok(lesson.includes(`data-tutor-lesson="${lessonId}"`));
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(lesson, new RegExp(`data-context-type="${type}"`));
}
for (const context of knowledge.contexts) {
  assert.ok(lesson.includes(`id="${context.id}" data-learning-context="${context.id}"`) || lesson.includes(`id="${context.id}" class="be-page-hero be-lesson-hero" data-learning-context="${context.id}"`));
}
for (const phrase of ["train_rows=24", "validation_rows=8", "test_rows=8", "macro-F1", "8973927ed683f32cf92bb4a1483b960f3b8c09b0b8497bd0c5176891252b713c"]) {
  assert.ok(lesson.includes(phrase), `lesson missing ${phrase}`);
}
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
const cwd = resolve(root, "site-src/examples/nlp-transformer/text-classification-evolution-v01");
const python = process.env.NLP_PYTHON || "python3";
const tests = spawnSync(python, ["-m", "unittest", "-v", "test_experiment.py"], { cwd, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr);
assert.match(tests.stdout + tests.stderr, /Ran 10 tests/);
const run = spawnSync(python, ["experiment.py"], { cwd, encoding: "utf8" });
assert.equal(run.status, 0, run.stdout + run.stderr);
for (const phrase of ["rows=40,labels=code:20,plan:20", "train_rows=24,class_counts=code:12,plan:12", "validation_rows=8,class_counts=code:4,plan:4", "test_rows=8,class_counts=code:4,plan:4", "overlap=0", "test_policy=sealed_until_final_selection"]) {
  assert.ok(run.stdout.includes(phrase));
}
console.log(JSON.stringify({ valid: true, lesson_id: lessonId, python_tests: 10, tutor_cards: 8, search_cases: 16, top3_hits: topThreeHits, unknown_cases: fixture.unknown.length }, null, 2));
