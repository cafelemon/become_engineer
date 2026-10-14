import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createRequire } from "node:module";

const root = resolve(import.meta.dirname, "..");
const id = "nlp-transformer-04";
const lesson = readFileSync(resolve(root, "site-src/learning-paths/ai-foundation/nlp-transformer/04-rnn-cnn-sequence-baselines.md"), "utf8");
const knowledge = JSON.parse(readFileSync(resolve(root, `site-src/data/tutor/${id}.json`), "utf8"));
const fixture = JSON.parse(readFileSync(resolve(root, `tests/tutor/${id}-search.json`), "utf8"));
const search = createRequire(import.meta.url)("../site-src/javascripts/tutor-search.js");
assert.ok(lesson.includes(`data-tutor-lesson="${id}"`));
for (const type of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
  assert.match(lesson, new RegExp(`data-context-type="${type}"`));
}
for (const context of knowledge.contexts) {
  assert.match(lesson, new RegExp(`<section[^>]*id="${context.id}"[^>]*data-learning-context="${context.id}"[^>]*data-context-type="${context.type}"`));
}
assert.deepEqual(search.validateKnowledgeBase(knowledge), []);
assert.equal(knowledge.lesson.id, id);
assert.ok(knowledge.cards.length >= 8);
assert.equal(fixture.lesson_id, id);
assert.ok(fixture.cases.length >= 16);
let top3 = 0;
for (const item of fixture.cases) {
  const card = knowledge.cards.find(candidate => candidate.id === item.expected_card);
  assert.ok(card, `missing ${item.expected_card}`);
  const hits = search.search(item.query, knowledge.cards, { lessonId: id, contextId: card.context_id }, { limit: 3, threshold: 24 });
  if (hits.some(candidate => candidate.card.id === card.id)) top3++;
}
assert.ok(top3 / fixture.cases.length >= 0.8, `Top3 ${top3}/${fixture.cases.length}`);
for (const query of fixture.unknown) {
  assert.equal(search.search(query, knowledge.cards, { lessonId: id, contextId: knowledge.contexts[0].id }, { limit: 3, threshold: 24 }).length, 0);
}
const cwd = resolve(root, "site-src/examples/nlp-transformer/text-classification-evolution-v04");
const python = process.env.NLP_PYTHON || process.env.PYTHON || "python3.12";
const tests = spawnSync(python, ["-m", "unittest", "-v", "test_sequence_lab.py"], { cwd, encoding: "utf8" });
assert.equal(tests.status, 0, tests.stdout + tests.stderr + (tests.error?.message ?? ""));
assert.match(tests.stdout + tests.stderr, /Ran 9 tests/);
const run = spawnSync(python, ["sequence_lab.py"], { cwd, encoding: "utf8" });
assert.equal(run.status, 0, run.stdout + run.stderr + (run.error?.message ?? ""));
const report = JSON.parse(run.stdout);
assert.equal(report.project_version, "0.4");
assert.equal(report.train_rows, 24);
assert.equal(report.validation_rows, 8);
assert.equal(report.test_status, "sealed");
assert.ok(!("test_metrics" in report));
for (const name of ["gru", "cnn"]) {
  assert.ok(report.results[name].parameter_count > 0);
  assert.ok(Number.isFinite(report.results[name].train_seconds));
  assert.ok(report.results[name].validation.accuracy >= 0 && report.results[name].validation.accuracy <= 1);
}
console.log(JSON.stringify({ valid: true, lesson_id: id, python_tests: 9, tutor_cards: knowledge.cards.length, search_cases: fixture.cases.length, top3_hits: top3, unknown_cases: fixture.unknown.length }, null, 2));
