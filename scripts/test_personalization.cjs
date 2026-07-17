#!/usr/bin/env node

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const personalization = require("../site-src/javascripts/personalization-core.js");

const root = path.resolve(__dirname, "..");
const config = JSON.parse(
  fs.readFileSync(path.join(root, "site-src/data/personalization/v1.json"), "utf8")
);

const validationErrors = personalization.validateConfig(config);
assert.deepEqual(validationErrors, [], validationErrors.join("\n"));

const builtSite = path.join(root, "site");
if (fs.existsSync(builtSite)) {
  for (const item of config.catalog.filter((candidate) => candidate.status === "ready")) {
    const output = path.join(builtSite, item.url, "index.html");
    assert.ok(fs.existsSync(output), `已开放目录项缺少构建页面: ${item.id} -> ${item.url}`);
  }
}

function answers(purpose, scores) {
  const result = { purpose };
  for (const question of config.assessment.questions) {
    const target = scores[question.dimension];
    const option = question.options.find((candidate) => candidate.score === target);
    assert.ok(option, `题目 ${question.id} 缺少分值 ${target} 的选项`);
    result[question.id] = option.id;
  }
  return result;
}

const beginnerInterest = personalization.scoreAssessment(
  config,
  answers("interest", {
    engineering_tools: 0,
    programming: 0,
    algorithms_cs: 0,
    project_engineering: 0
  })
);
assert.equal(beginnerInterest.profileKey, "beginner-interest");
assert.equal(beginnerInterest.startUrl, "learning-paths/engineering-foundation/stage-0/01-learning-method/");
assert.ok(!beginnerInterest.includedIds.includes("career-python-machine-test"));
assert.ok(beginnerInterest.hidden.some((item) => item.reason === "goal_mismatch"));
assert.ok(beginnerInterest.hidden.some((item) => item.reason === "locked"));

const experiencedInterest = personalization.scoreAssessment(
  config,
  answers("interest", {
    engineering_tools: 2,
    programming: 2,
    algorithms_cs: 1,
    project_engineering: 1
  })
);
assert.equal(experiencedInterest.profileKey, "experienced-interest");
assert.ok(!experiencedInterest.includedIds.includes("engineering-foundation-03"));
assert.ok(!experiencedInterest.includedIds.includes("python-basics-01"));
assert.ok(experiencedInterest.includedIds.includes("python-core-01"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-overview"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-01"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-02"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-03"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-04"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-05"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-06"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-07"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-08"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-09"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-10"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-11"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-12"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-13"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-14"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-15"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-16"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-17"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-18"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-19"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-20"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-21"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-22"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-23"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-24"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-25"));
assert.ok(experiencedInterest.includedIds.includes("cs-core-26"));

const beginnerCareer = personalization.scoreAssessment(
  config,
  answers("career", {
    engineering_tools: 0,
    programming: 0,
    algorithms_cs: 0,
    project_engineering: 0
  })
);
assert.equal(beginnerCareer.profileKey, "beginner-career");
assert.ok(beginnerCareer.includedIds.includes("career-python-machine-test"));
assert.ok(beginnerCareer.includedIds.includes("career-project-evidence"));

const experiencedCareer = personalization.scoreAssessment(
  config,
  answers("career", {
    engineering_tools: 2,
    programming: 2,
    algorithms_cs: 2,
    project_engineering: 2
  })
);
assert.equal(experiencedCareer.profileKey, "experienced-career");
assert.ok(experiencedCareer.includedIds.includes("career-python-machine-test"));
assert.ok(experiencedCareer.hidden.some((item) => item.reason === "mastered"));
assert.ok(experiencedCareer.hidden.some((item) => item.reason === "planned"));

const overrideRoute = personalization.buildRoute(config, experiencedInterest, ["engineering-foundation-03"]);
assert.ok(overrideRoute.includedIds.includes("engineering-foundation-03"));

const rawAnswerKeys = Object.keys(personalization.toStoredProfile(experiencedCareer));
assert.ok(!rawAnswerKeys.includes("answers"));
assert.deepEqual(rawAnswerKeys.sort(), [
  "confirmed",
  "dimensions",
  "includedOverrides",
  "profileKey",
  "purpose",
  "version",
  "view"
].sort());

console.log("个性化测评与四路线规则测试通过：4 类画像、补修、求职训练、未显示原因和最小存储均符合约定。");
