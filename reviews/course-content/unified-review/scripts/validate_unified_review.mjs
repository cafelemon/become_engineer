import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../../..");
const reviewRoot = path.join(root, "reviews/course-content/unified-review");
const manifest = JSON.parse(fs.readFileSync(path.join(reviewRoot, "sample-manifest.json"), "utf8"));
const search = require(path.join(root, "site-src/javascripts/tutor-search.js"));
const bannedVisiblePhrases = [
  "可观察结果", "成功证据", "迁移验收", "受控失败实验", "心智模型", "本课增量", "当前任务"
];
const errors = [];

if (manifest.samples.length !== 13) errors.push(`样板登记数量应为 13，实际为 ${manifest.samples.length}`);
if (manifest.course_types.length !== 8) errors.push(`课型数量应为 8，实际为 ${manifest.course_types.length}`);

const sampleIds = manifest.samples.map((sample) => sample.sample_id);
if (new Set(sampleIds).size !== sampleIds.length) errors.push("样板登记存在重复 sample_id");

const courseTypeIds = new Set(manifest.course_types.map((item) => item.id));
for (const type of courseTypeIds) {
  if (!manifest.samples.some((sample) => sample.course_type === type)) errors.push(`课型没有代表样板: ${type}`);
}
for (const sample of manifest.samples) {
  if (!courseTypeIds.has(sample.course_type)) errors.push(`${sample.sample_id}: 引用了未登记课型 ${sample.course_type}`);
}

let totalCards = 0;
let totalQuestions = 0;
let sourceGaps = 0;

for (const sample of manifest.samples) {
  const pagePath = path.join(root, sample.page);
  const batchRoot = path.join(root, `reviews/course-content/batch-${sample.batch}`);
  const knowledgePath = path.join(batchRoot, "data/tutors", `${sample.sample_id}.json`);
  const fixturePath = path.join(batchRoot, "data/tests", `${sample.sample_id}-search.json`);
  for (const file of [pagePath, knowledgePath, fixturePath]) {
    if (!fs.existsSync(file)) errors.push(`${sample.sample_id}: 缺少文件 ${path.relative(root, file)}`);
  }
  if (![pagePath, knowledgePath, fixturePath].every(fs.existsSync)) continue;

  const markdown = fs.readFileSync(pagePath, "utf8");
  const knowledge = JSON.parse(fs.readFileSync(knowledgePath, "utf8"));
  const fixture = JSON.parse(fs.readFileSync(fixturePath, "utf8"));

  if (/be-task-route|data-step-id|id=["']step-\d+/.test(markdown)) errors.push(`${sample.sample_id}: 出现旧任务步骤结构`);
  for (const phrase of bannedVisiblePhrases) {
    if (markdown.includes(phrase)) errors.push(`${sample.sample_id}: 出现管理化表达 “${phrase}”`);
  }
  for (const required of ["be-sample-hero", "be-sample-project-panel", "完成检查"]) {
    if (!markdown.includes(required)) errors.push(`${sample.sample_id}: 页面缺少 ${required}`);
  }
  if (!/下一页|下一课|下一步|下一阶段|回到/.test(markdown)) errors.push(`${sample.sample_id}: 缺少下一方向或返回入口`);

  const pageContexts = new Map();
  const pattern = /id="([^"]+)"[^>]*data-learning-context="([^"]+)"[^>]*data-context-type="([^"]+)"/g;
  let match;
  while ((match = pattern.exec(markdown)) !== null) {
    if (match[1] !== match[2]) errors.push(`${sample.sample_id}: id 与上下文不一致: ${match[1]}`);
    pageContexts.set(match[2], match[3]);
  }
  const allowedTypes = new Set([...manifest.common_contexts, ...manifest.optional_contexts]);
  for (const type of manifest.common_contexts) {
    if (![...pageContexts.values()].includes(type)) errors.push(`${sample.sample_id}: 缺少共同语义类型 ${type}`);
  }
  for (const type of pageContexts.values()) {
    if (!allowedTypes.has(type)) errors.push(`${sample.sample_id}: 使用未登记语义类型 ${type}`);
  }

  for (const error of search.validateKnowledgeBase(knowledge)) errors.push(`${sample.sample_id}: ${error}`);
  if (knowledge.lesson?.id !== sample.sample_id) errors.push(`${sample.sample_id}: 知识库 lesson.id 不一致`);
  for (const context of knowledge.contexts || []) {
    if (!pageContexts.has(context.id)) errors.push(`${sample.sample_id}: 知识库上下文未出现在正文: ${context.id}`);
    else if (pageContexts.get(context.id) !== context.type) errors.push(`${sample.sample_id}: 上下文类型不一致: ${context.id}`);
  }
  if ((knowledge.cards || []).length < 8) errors.push(`${sample.sample_id}: 知识卡不足 8 张`);
  if (fixture.lesson_id !== sample.sample_id) errors.push(`${sample.sample_id}: 测试 lesson_id 不一致`);
  if (!Array.isArray(fixture.cases) || fixture.cases.length < 16) errors.push(`${sample.sample_id}: 固定问法不足 16 条`);

  let top1 = 0;
  let top3 = 0;
  for (const testCase of fixture.cases || []) {
    const expected = knowledge.cards.find((card) => card.id === testCase.expected_card);
    if (!expected) {
      errors.push(`${sample.sample_id}: 测试引用未知卡片 ${testCase.expected_card}`);
      continue;
    }
    const results = search.search(testCase.query, knowledge.cards, { lessonId: sample.sample_id, contextId: expected.context_id }, { limit: 3, threshold: 24 });
    if (results[0]?.card.id === testCase.expected_card) top1 += 1;
    if (results.some((result) => result.card.id === testCase.expected_card)) top3 += 1;
  }
  if (fixture.cases.length && top3 / fixture.cases.length < 0.8) errors.push(`${sample.sample_id}: Top 3 命中率低于 80%`);
  for (const unknown of fixture.unknown || []) {
    if (search.search(unknown, knowledge.cards, { lessonId: sample.sample_id }, { limit: 3, threshold: 24 }).length) {
      errors.push(`${sample.sample_id}: 未知问题没有降级: ${unknown}`);
    }
  }

  totalCards += knowledge.cards.length;
  totalQuestions += fixture.cases.length;
  if (sample.source_status !== "visible-and-verified") sourceGaps += 1;
  console.log(`${sample.sample_id}: ${knowledge.cards.length} 卡，${fixture.cases.length} 问，Top 1 ${top1}/${fixture.cases.length}，Top 3 ${top3}/${fixture.cases.length}`);
}

function textFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(directory, entry.name);
    if (entry.isDirectory()) return textFiles(full);
    return /\.(?:md|js|json|yml|yaml|txt)$/.test(entry.name) ? [full] : [];
  });
}
for (const file of textFiles(reviewRoot)) {
  const text = fs.readFileSync(file, "utf8");
  if (/sk-[A-Za-z0-9_-]{16,}/.test(text)) errors.push(`${path.relative(root, file)}: 疑似包含真实 API Key`);
}

if (errors.length) {
  console.error("\n统一评审校验失败：");
  errors.forEach((error) => console.error(`- ${error}`));
  process.exit(1);
}

console.log(`\n统一评审通过：13 个样板、8 类课型、${totalCards} 张知识卡、${totalQuestions} 条固定问法。`);
console.log(`来源区块待正式固化：${sourceGaps} 页（作为下一阶段缺口记录，不改冻结正文）。`);
