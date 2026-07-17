import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../../..");
const batchRoot = path.join(root, "reviews/course-content/batch-a");
const search = require(path.join(batchRoot, "assets/tutor-v2-search.js"));

const samples = [
  { id: "sample-vscode-workspace", page: "vscode-workspace.md" },
  { id: "sample-python-variables", page: "python-variables.md" },
  { id: "sample-cs-data-representation", page: "cs-data-representation.md" },
  { id: "sample-study-progress-reporter", page: "study-progress-reporter.md" }
];
const requiredTypes = ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"];
const errors = [];

for (const sample of samples) {
  const pagePath = path.join(batchRoot, sample.page);
  const knowledgePath = path.join(batchRoot, "data/tutors", sample.id + ".json");
  const testsPath = path.join(batchRoot, "data/tests", sample.id + "-search.json");
  const markdown = fs.readFileSync(pagePath, "utf8");
  const knowledge = JSON.parse(fs.readFileSync(knowledgePath, "utf8"));
  const fixture = JSON.parse(fs.readFileSync(testsPath, "utf8"));

  if (/be-task-route|data-step-id|id=["']step-\d+/.test(markdown)) {
    errors.push(sample.id + ": 样板页出现旧任务步骤结构");
  }
  for (const required of ["be-sample-hero", "be-sample-project-panel", "完成检查"]) {
    if (!markdown.includes(required)) errors.push(sample.id + ": 页面缺少 " + required);
  }

  const pageContexts = new Map();
  const contextPattern = /id="([^"]+)"[^>]*data-learning-context="([^"]+)"[^>]*data-context-type="([^"]+)"/g;
  let match;
  while ((match = contextPattern.exec(markdown)) !== null) {
    if (match[1] !== match[2]) errors.push(sample.id + ": id 与 data-learning-context 不一致: " + match[1]);
    pageContexts.set(match[2], match[3]);
  }
  for (const type of requiredTypes) {
    if (![...pageContexts.values()].includes(type)) errors.push(sample.id + ": 缺少语义类型 " + type);
  }

  for (const error of search.validateKnowledgeBase(knowledge)) errors.push(sample.id + ": " + error);
  for (const context of knowledge.contexts || []) {
    if (!pageContexts.has(context.id)) errors.push(sample.id + ": 知识库上下文未出现在正文: " + context.id);
    else if (pageContexts.get(context.id) !== context.type) errors.push(sample.id + ": 上下文类型不一致: " + context.id);
  }
  if (fixture.lesson_id !== sample.id) errors.push(sample.id + ": 测试 lesson_id 不一致");
  if (!Array.isArray(fixture.cases) || fixture.cases.length < 16) errors.push(sample.id + ": 固定问法不足 16 条");

  let top1 = 0;
  let top3 = 0;
  for (const testCase of fixture.cases || []) {
    const expected = knowledge.cards.find((card) => card.id === testCase.expected_card);
    if (!expected) {
      errors.push(sample.id + ": 测试引用未知卡片 " + testCase.expected_card);
      continue;
    }
    const results = search.search(testCase.query, knowledge.cards, {
      lessonId: sample.id,
      contextId: expected.context_id
    }, { limit: 3, threshold: 24 });
    if (results[0]?.card.id === testCase.expected_card) top1 += 1;
    if (results.some((result) => result.card.id === testCase.expected_card)) top3 += 1;
  }
  const top3Rate = fixture.cases.length ? top3 / fixture.cases.length : 0;
  if (top3Rate < 0.8) errors.push(sample.id + ": Top 3 命中率低于 80%");
  for (const unknown of fixture.unknown || []) {
    const results = search.search(unknown, knowledge.cards, { lessonId: sample.id }, { limit: 3, threshold: 24 });
    if (results.length) errors.push(sample.id + ": 未知问题没有降级: " + unknown);
  }
  console.log(`${sample.id}: ${knowledge.cards.length} 卡，${fixture.cases.length} 问，Top 1 ${top1}/${fixture.cases.length}，Top 3 ${top3}/${fixture.cases.length}`);
}

if (errors.length) {
  console.error("\n批次 A 校验失败：");
  errors.forEach((error) => console.error("- " + error));
  process.exit(1);
}

console.log("批次 A 内容结构、语义知识库和检索降级全部通过。");
