import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../../..");
const batchRoot = path.join(root, "reviews/course-content/batch-c");
const search = require(path.join(root, "reviews/course-content/batch-a/assets/tutor-v2-search.js"));
const samples = [
  { id: "sample-web-local-api", page: "web-local-api.md" },
  { id: "sample-ai-reproducible-experiment", page: "ai-reproducible-experiment.md" },
  { id: "sample-llm-structured-output", page: "llm-structured-output.md" },
  { id: "sample-agent-read-only-tool", page: "agent-read-only-tool.md" }
];
const requiredTypes = ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"];
const bannedVisiblePhrases = [
  "可观察结果", "成功证据", "迁移验收", "受控失败实验", "心智模型", "本课增量", "当前任务"
];
const errors = [];

for (const sample of samples) {
  const markdown = fs.readFileSync(path.join(batchRoot, sample.page), "utf8");
  const knowledge = JSON.parse(fs.readFileSync(path.join(batchRoot, "data/tutors", sample.id + ".json"), "utf8"));
  const fixture = JSON.parse(fs.readFileSync(path.join(batchRoot, "data/tests", sample.id + "-search.json"), "utf8"));
  if (/be-task-route|data-step-id|id=["']step-\d+/.test(markdown)) errors.push(sample.id + ": 出现旧任务步骤结构");
  for (const phrase of bannedVisiblePhrases) if (markdown.includes(phrase)) errors.push(sample.id + ": 出现管理化表达 “ + phrase + ”");
  for (const required of ["be-sample-hero", "be-sample-project-panel", "完成检查"]) {
    if (!markdown.includes(required)) errors.push(sample.id + ": 页面缺少 " + required);
  }
  const pageContexts = new Map();
  const pattern = /id="([^"]+)"[^>]*data-learning-context="([^"]+)"[^>]*data-context-type="([^"]+)"/g;
  let match;
  while ((match = pattern.exec(markdown)) !== null) {
    if (match[1] !== match[2]) errors.push(sample.id + ": id 与上下文不一致: " + match[1]);
    pageContexts.set(match[2], match[3]);
  }
  for (const type of requiredTypes) if (![...pageContexts.values()].includes(type)) errors.push(sample.id + ": 缺少语义类型 " + type);
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
    if (!expected) { errors.push(sample.id + ": 测试引用未知卡片 " + testCase.expected_card); continue; }
    const results = search.search(testCase.query, knowledge.cards, { lessonId: sample.id, contextId: expected.context_id }, { limit: 3, threshold: 24 });
    if (results[0]?.card.id === testCase.expected_card) top1 += 1;
    if (results.some((result) => result.card.id === testCase.expected_card)) top3 += 1;
  }
  if (fixture.cases.length && top3 / fixture.cases.length < 0.8) errors.push(sample.id + ": Top 3 命中率低于 80%");
  for (const unknown of fixture.unknown || []) {
    if (search.search(unknown, knowledge.cards, { lessonId: sample.id }, { limit: 3, threshold: 24 }).length) {
      errors.push(sample.id + ": 未知问题没有降级: " + unknown);
    }
  }
  console.log(`${sample.id}: ${knowledge.cards.length} 卡，${fixture.cases.length} 问，Top 1 ${top1}/${fixture.cases.length}，Top 3 ${top3}/${fixture.cases.length}`);
}

function textFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(directory, entry.name);
    if (entry.isDirectory()) return textFiles(full);
    return /\.(?:md|py|js|json|yml|yaml|txt|example)$/.test(entry.name) ? [full] : [];
  });
}
const trackedTextFiles = textFiles(batchRoot);
for (const file of trackedTextFiles) {
  const text = fs.readFileSync(file, "utf8");
  if (/sk-[A-Za-z0-9_-]{16,}/.test(text)) errors.push(path.relative(root, file) + ": 疑似包含真实 API Key");
}

if (errors.length) {
  console.error("\n批次 C 校验失败：");
  errors.forEach((error) => console.error("- " + error));
  process.exit(1);
}
console.log("批次 C 内容结构、自然表达、语义知识库、检索降级和密钥边界全部通过。");
