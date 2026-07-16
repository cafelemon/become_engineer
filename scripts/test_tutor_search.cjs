#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");
const searchApi = require("../site-src/javascripts/tutor-search.js");

const root = path.resolve(__dirname, "..");
const lessonRoots = [
  "learning-paths/engineering-foundation/stage-0",
  "learning-paths/programming-languages/python-basics",
  "learning-paths/programming-languages/cpp-core",
  "learning-paths/programming-languages/python-core",
  "learning-paths/cs-core"
];
const failures = [];
const genericCardPhrases = [
  "把这一步的命令、文件状态或输出写进学习记录。",
  "回到当前任务步骤，执行最小修改后重新运行或检查，再根据新反馈继续。",
  "参见本课“",
  "对应任务与代码"
];
let lessonCount = 0;
let totalCards = 0;
let totalCases = 0;

function fail(message) {
  failures.push(message);
}

function courseFiles() {
  return lessonRoots.flatMap(function (relativeRoot) {
    const absoluteRoot = path.join(root, relativeRoot);
    return fs.readdirSync(absoluteRoot)
      .filter(function (name) { return /^\d{2}-.+\.md$/.test(name); })
      .sort()
      .map(function (name) { return path.join(relativeRoot, name); });
  });
}

function readJson(relativePath, label) {
  try {
    return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
  } catch (error) {
    fail(label + " 无法读取：" + error.message);
    return null;
  }
}

for (const lessonFile of courseFiles()) {
  lessonCount += 1;
  const markdown = fs.readFileSync(path.join(root, lessonFile), "utf8");
  const marker = markdown.match(/<div class="be-tutor-mount" data-tutor-lesson="([^"]+)" aria-hidden="true"><\/div>/);
  if (!marker) {
    fail(lessonFile + " 缺少稳定的助教挂载点");
    continue;
  }
  const lessonId = marker[1];
  const kbRelativePath = "site-src/data/tutor/" + lessonId + ".json";
  const casesRelativePath = "tests/tutor/" + lessonId + "-search.json";
  const kb = readJson(kbRelativePath, lessonId + " 知识库");
  const cases = readJson(casesRelativePath, lessonId + " 测试集");
  if (!kb || !cases) continue;

  const schemaErrors = searchApi.validateKnowledgeBase(kb);
  for (const error of schemaErrors) fail(lessonId + "：" + error);
  if (!kb.lesson || kb.lesson.id !== lessonId) fail(lessonId + "：lesson.id 必须与课程挂载标识一致");
  if (!Array.isArray(kb.steps) || kb.steps.length < 5 || kb.steps.length > 7) {
    fail(lessonId + "：任务步骤必须为 5 至 7 步");
  }
  if (!Array.isArray(kb.cards) || kb.cards.length < 8) fail(lessonId + "：知识卡不得少于 8 张");
  if (!Array.isArray(cases) || cases.length < 16) fail(lessonId + "：固定问法不得少于 16 条");

  const stepIds = new Set((kb.steps || []).map(function (step) { return step.id; }));
  const cardIds = new Set((kb.cards || []).map(function (card) { return card.id; }));
  for (const card of kb.cards || []) {
    const cardText = [card.diagnostic, ...(card.hints || []), card.example].join(" ");
    for (const phrase of genericCardPhrases) {
      if (cardText.includes(phrase)) {
        fail(lessonId + "：知识卡 " + card.id + " 包含通用占位提示，需改为任务专属内容");
        break;
      }
    }
  }
  for (const stepId of stepIds) {
    const escaped = stepId.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const stepPattern = new RegExp("id=\\\"" + escaped + "\\\"[^>]*class=\\\"be-task-step\\\"[^>]*data-step-id=\\\"" + escaped + "\\\"");
    if (!stepPattern.test(markdown)) fail(lessonId + "：正文缺少 " + stepId + " 对应的任务卡与 data-step-id");
  }

  let topOneHits = 0;
  let topThreeHits = 0;
  for (const testCase of cases || []) {
    if (!stepIds.has(testCase.step_id)) {
      fail(lessonId + "：测试引用了未知步骤 " + testCase.step_id);
      continue;
    }
    if (!cardIds.has(testCase.expected)) {
      fail(lessonId + "：测试引用了未知知识卡 " + testCase.expected);
      continue;
    }
    const results = searchApi.search(
      testCase.query,
      kb.cards,
      { lessonId: lessonId, stepId: testCase.step_id },
      { limit: 3, threshold: 24 }
    );
    const ids = results.map(function (candidate) { return candidate.card.id; });
    if (ids[0] === testCase.expected) topOneHits += 1;
    if (ids.includes(testCase.expected)) topThreeHits += 1;
    else fail(lessonId + "：未命中 “" + testCase.query + "”，期望 " + testCase.expected + "，实际 " + ids.join(", "));
  }
  const hitRate = cases.length ? topThreeHits / cases.length : 0;
  if (hitRate < 0.8) fail(lessonId + "：Top 3 命中率低于 80%");
  const unknownResults = searchApi.search(
    "月球烘焙的彩虹配方是什么",
    kb.cards,
    { lessonId: lessonId, stepId: (kb.steps[0] || {}).id },
    { limit: 3, threshold: 24 }
  );
  if (unknownResults.length !== 0) fail(lessonId + "：未知问题未进入降级");

  totalCards += Array.isArray(kb.cards) ? kb.cards.length : 0;
  totalCases += Array.isArray(cases) ? cases.length : 0;
  console.log(`${lessonId}: ${kb.cards.length} 卡，${cases.length} 问，Top 1 ${topOneHits}/${cases.length}，Top 3 ${topThreeHits}/${cases.length} (${(hitRate * 100).toFixed(1)}%)，未知问题 ${unknownResults.length === 0 ? "通过" : "失败"}`);
}

console.log(`课程: ${lessonCount}`);
console.log(`知识卡: ${totalCards}`);
console.log(`固定问题: ${totalCases}`);
if (lessonCount !== 52) fail("正式课程数量应为 52，实际为 " + lessonCount);
if (failures.length) {
  console.error("助教知识库校验失败：");
  for (const message of failures) console.error("- " + message);
  process.exit(1);
}
