#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");
const searchApi = require("../site-src/javascripts/tutor-search.js");

const root = path.resolve(__dirname, "..");
const kbPath = path.join(root, "site-src/data/tutor/python-basics-01.json");
const casesPath = path.join(root, "tests/tutor/python-basics-01-search.json");
const kb = JSON.parse(fs.readFileSync(kbPath, "utf8"));
const cases = JSON.parse(fs.readFileSync(casesPath, "utf8"));

const schemaErrors = searchApi.validateKnowledgeBase(kb);
if (schemaErrors.length) {
  console.error("知识库结构校验失败：");
  for (const error of schemaErrors) console.error("- " + error);
  process.exit(1);
}

let topThreeHits = 0;
let topOneHits = 0;
const misses = [];
for (const testCase of cases) {
  const results = searchApi.search(
    testCase.query,
    kb.cards,
    { lessonId: kb.lesson.id, stepId: testCase.step_id },
    { limit: 3, threshold: 24 }
  );
  const ids = results.map((candidate) => candidate.card.id);
  if (ids[0] === testCase.expected) topOneHits += 1;
  if (ids.includes(testCase.expected)) {
    topThreeHits += 1;
  } else {
    misses.push({ query: testCase.query, expected: testCase.expected, actual: ids });
  }
}

const hitRate = cases.length ? topThreeHits / cases.length : 0;
const unknownResults = searchApi.search(
  "量子编译器怎么安装",
  kb.cards,
  { lessonId: kb.lesson.id, stepId: "step-1" },
  { limit: 3, threshold: 24 }
);
console.log(`知识卡: ${kb.cards.length}`);
console.log(`固定问题: ${cases.length}`);
console.log(`Top 1 命中: ${topOneHits}/${cases.length}`);
console.log(`Top 3 命中: ${topThreeHits}/${cases.length} (${(hitRate * 100).toFixed(1)}%)`);
console.log(`未知问题降级: ${unknownResults.length === 0 ? "通过" : "失败"}`);

if (misses.length) {
  for (const miss of misses) console.error("未命中:", JSON.stringify(miss));
}
if (cases.length < 20 || hitRate < 0.8 || unknownResults.length !== 0) process.exit(1);
