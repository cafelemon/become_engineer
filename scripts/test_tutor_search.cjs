#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");
const searchApi = require("../site-src/javascripts/tutor-search.js");

const root = path.resolve(__dirname, "..");
const registry = readRequiredJson("site-src/data/curriculum/v2.json");
const migrationRegistry = readRequiredJson("site-src/data/curriculum/migration-v2.json");
const sampleManifest = readRequiredJson("reviews/course-content/unified-review/sample-manifest.json");
const failures = [];
const genericCardPhrases = [
  "把这一步的命令、文件状态或输出写进学习记录。",
  "回到当前任务步骤，执行最小修改后重新运行或检查，再根据新反馈继续。",
  "参见本课“",
  "对应任务与代码"
];
const totals = {
  v1Lessons: 0,
  v2Lessons: 0,
  v2Samples: 0,
  cards: 0,
  cases: 0
};

function fail(message) {
  failures.push(message);
}

function readRequiredJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function readJson(relativePath, label) {
  try {
    return readRequiredJson(relativePath);
  } catch (error) {
    fail(label + " 无法读取：" + error.message);
    return null;
  }
}

function validateMarkdownScope(markdown, scopeId, schema, lessonId) {
  const escaped = scopeId.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const idPattern = new RegExp("id=[\\\"']" + escaped + "[\\\"']");
  const dataPattern = schema === "v1"
    ? new RegExp("data-step-id=[\\\"']" + escaped + "[\\\"']")
    : new RegExp("data-learning-context=[\\\"']" + escaped + "[\\\"']");
  if (!idPattern.test(markdown) || !dataPattern.test(markdown)) {
    fail(lessonId + "：正文缺少 " + scopeId + " 对应的" + (schema === "v1" ? "任务步骤" : "语义上下文"));
  }
}

function runLesson(entry) {
  const markdown = fs.readFileSync(path.join(root, entry.page), "utf8");
  const markerPattern = entry.formal
    ? /<div class="be-tutor-mount" data-tutor-lesson="([^"]+)" aria-hidden="true"><\/div>/
    : /<div class="be-sample-tutor-mount" data-tutor-context-lesson="([^"]+)" aria-hidden="true"><\/div>/;
  const marker = markdown.match(markerPattern);
  if (!marker) {
    fail(entry.page + " 缺少稳定的助教挂载点");
    return;
  }
  const lessonId = marker[1];
  if (entry.lessonId && entry.lessonId !== lessonId) fail(entry.page + "：登记标识与挂载标识不一致");
  const kb = readJson(entry.knowledge, lessonId + " 知识库");
  const fixture = readJson(entry.fixture, lessonId + " 测试集");
  if (!kb || !fixture) return;

  const schemaErrors = searchApi.validateKnowledgeBase(kb);
  for (const error of schemaErrors) fail(lessonId + "：" + error);
  const actualSchema = searchApi.detectSchema(kb);
  if (actualSchema !== entry.schema) fail(lessonId + "：知识库协议应为 " + entry.schema + "，实际为 " + actualSchema);
  if (!kb.lesson || kb.lesson.id !== lessonId) fail(lessonId + "：lesson.id 必须与课程挂载标识一致");

  const scopes = entry.schema === "v1" ? (kb.steps || []) : (kb.contexts || []);
  const scopeField = entry.schema === "v1" ? "step_id" : "context_id";
  if (entry.schema === "v1" && (scopes.length < 5 || scopes.length > 7)) {
    fail(lessonId + "：尚未迁移的 V1 课程必须保留 5 至 7 步");
  }
  if (!Array.isArray(kb.cards) || kb.cards.length < 8) fail(lessonId + "：知识卡不得少于 8 张");
  const scopeIds = new Set(scopes.map(function (scope) { return scope.id; }));
  const cardIds = new Set((kb.cards || []).map(function (card) { return card.id; }));
  for (const scopeId of scopeIds) validateMarkdownScope(markdown, scopeId, entry.schema, lessonId);

  for (const card of kb.cards || []) {
    const cardText = [card.diagnostic, ...(card.hints || []), card.example].join(" ");
    for (const phrase of genericCardPhrases) {
      if (cardText.includes(phrase)) {
        fail(lessonId + "：知识卡 " + card.id + " 包含通用占位提示");
        break;
      }
    }
  }

  const cases = Array.isArray(fixture) ? fixture : fixture.cases;
  if (!Array.isArray(cases) || cases.length < 16) {
    fail(lessonId + "：固定问法不得少于 16 条");
    return;
  }
  if (!Array.isArray(fixture) && fixture.lesson_id !== lessonId) fail(lessonId + "：测试 lesson_id 不一致");

  let topOneHits = 0;
  let topThreeHits = 0;
  for (const testCase of cases) {
    const expectedId = entry.schema === "v1" ? testCase.expected : testCase.expected_card;
    if (!cardIds.has(expectedId)) {
      fail(lessonId + "：测试引用了未知知识卡 " + expectedId);
      continue;
    }
    let scopeId = testCase[scopeField];
    if (entry.schema === "v2") {
      const expectedCard = kb.cards.find(function (card) { return card.id === expectedId; });
      scopeId = expectedCard && expectedCard.context_id;
    }
    if (!scopeIds.has(scopeId)) {
      fail(lessonId + "：测试引用了未知" + scopeField + " " + scopeId);
      continue;
    }
    const context = { lessonId: lessonId };
    if (entry.schema === "v1") context.stepId = scopeId;
    else context.contextId = scopeId;
    const results = searchApi.search(testCase.query, kb.cards, context, { limit: 3, threshold: 24 });
    const ids = results.map(function (candidate) { return candidate.card.id; });
    if (ids[0] === expectedId) topOneHits += 1;
    if (ids.includes(expectedId)) topThreeHits += 1;
    else fail(lessonId + "：未命中 “" + testCase.query + "”，期望 " + expectedId + "，实际 " + ids.join(", "));
  }

  const unknownQueries = Array.isArray(fixture)
    ? ["月球烘焙的彩虹配方是什么"]
    : (fixture.unknown || []);
  for (const unknown of unknownQueries) {
    const context = { lessonId: lessonId };
    if (entry.schema === "v1") context.stepId = scopes[0] && scopes[0].id;
    else context.contextId = scopes[0] && scopes[0].id;
    const results = searchApi.search(unknown, kb.cards, context, { limit: 3, threshold: 24 });
    if (results.length) fail(lessonId + "：未知问题未进入降级：" + unknown);
  }

  const hitRate = cases.length ? topThreeHits / cases.length : 0;
  if (hitRate < 0.8) fail(lessonId + "：Top 3 命中率低于 80%");
  totals.cards += kb.cards.length;
  totals.cases += cases.length;
  if (entry.formal && entry.schema === "v1") totals.v1Lessons += 1;
  else if (entry.formal) totals.v2Lessons += 1;
  else totals.v2Samples += 1;
  console.log(`${lessonId} [${entry.schema}]: ${kb.cards.length} 卡，${cases.length} 问，Top 1 ${topOneHits}/${cases.length}，Top 3 ${topThreeHits}/${cases.length} (${(hitRate * 100).toFixed(1)}%)，未知问题 ${unknownQueries.length} 条通过`);
}

const migrationById = new Map(migrationRegistry.lessons.map(function (lesson) {
  return [lesson.id, lesson];
}));

for (const lesson of registry.lessons) {
  const markdown = fs.readFileSync(path.join(root, lesson.url), "utf8");
  const marker = markdown.match(/data-tutor-lesson="([^"]+)"/);
  const migration = migrationById.get(lesson.id);
  if (!migration) {
    fail(lesson.id + "：缺少课程迁移登记");
    continue;
  }
  runLesson({
    schema: migration.migration_status === "已迁移" ? "v2" : "v1",
    formal: true,
    lessonId: marker && marker[1],
    page: lesson.url,
    knowledge: "site-src/data/tutor/" + (marker && marker[1]) + ".json",
    fixture: "tests/tutor/" + (marker && marker[1]) + "-search.json"
  });
}

for (const sample of sampleManifest.samples) {
  runLesson({
    schema: "v2",
    formal: false,
    lessonId: sample.sample_id,
    page: sample.page,
    knowledge: `reviews/course-content/batch-${sample.batch}/data/tutors/${sample.sample_id}.json`,
    fixture: `reviews/course-content/batch-${sample.batch}/data/tests/${sample.sample_id}-search.json`
  });
}

if (totals.v1Lessons + totals.v2Lessons !== registry.course_count) {
  fail("正式课程数量与课程登记不一致：登记 " + registry.course_count + "，实际 " + (totals.v1Lessons + totals.v2Lessons));
}
if (totals.v2Samples !== sampleManifest.samples.length) {
  fail("V2 样板数量与样板登记不一致：登记 " + sampleManifest.samples.length + "，实际 " + totals.v2Samples);
}

console.log(`V1 正式课程: ${totals.v1Lessons}`);
console.log(`V2 正式课程: ${totals.v2Lessons}`);
console.log(`V2 冻结样板: ${totals.v2Samples}`);
console.log(`知识卡: ${totals.cards}`);
console.log(`固定问题: ${totals.cases}`);
if (failures.length) {
  console.error("助教知识库校验失败：");
  for (const message of failures) console.error("- " + message);
  process.exit(1);
}
