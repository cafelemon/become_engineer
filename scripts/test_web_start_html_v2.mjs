import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const v01Root = join(root, "site-src/examples/web-start/learning-dashboard-v01");
const html = readFileSync(join(v01Root, "index.html"), "utf8");
const css = readFileSync(join(v01Root, "styles.css"), "utf8");

for (const pattern of [
  /<!doctype html>/i,
  /<html lang="zh-CN">/,
  /<meta charset="utf-8">/,
  /<meta name="viewport" content="width=device-width, initial-scale=1">/,
  /<main>/,
  /<article class="study-card" aria-labelledby="profile-title">/,
  /<h1 id="profile-title">小码的学习卡片<\/h1>/,
  /<dl>/,
  /<dt>已完成课程<\/dt>/,
  /<dd>7 节<\/dd>/,
]) {
  assert.match(html, pattern);
}

assert.doesNotMatch(html, /style="|onclick="|<script/i);
assert.match(css, /grid-template-columns:\s*repeat\(auto-fit,\s*minmax\(9rem,\s*1fr\)\)/);
assert.match(css, /@media \(prefers-color-scheme: dark\)/);

const v02Root = join(root, "site-src/examples/web-start/learning-dashboard-v02");
const responsiveHtml = readFileSync(join(v02Root, "index.html"), "utf8");
const responsiveCss = readFileSync(join(v02Root, "styles.css"), "utf8");

for (const pattern of [
  /<article class="study-card" aria-labelledby="profile-title">/,
  /<dl class="metrics">/,
  /<dt>下一个里程碑<\/dt>/,
  /<dd>让页面响应一次用户操作<\/dd>/,
]) {
  assert.match(responsiveHtml, pattern);
}

assert.doesNotMatch(responsiveHtml, /style="|onclick="|<script/i);
assert.match(responsiveCss, /\*\s*{\s*box-sizing:\s*border-box;/s);
assert.match(responsiveCss, /grid-template-columns:\s*repeat\(3,\s*minmax\(0,\s*1fr\)\)/);
assert.match(responsiveCss, /@media \(max-width:\s*40rem\)[\s\S]*grid-template-columns:\s*1fr/);
assert.match(responsiveCss, /overflow-wrap:\s*anywhere/);
assert.match(responsiveCss, /@media \(prefers-color-scheme: dark\)/);

const v03Root = join(root, "site-src/examples/web-start/learning-dashboard-v03");
const stateHtml = readFileSync(join(v03Root, "index.html"), "utf8");
const stateCss = readFileSync(join(v03Root, "styles.css"), "utf8");
const stateScriptPath = join(v03Root, "app.js");

for (const pattern of [
  /<script src="app\.js" defer><\/script>/,
  /data-profile-id="xiaoma" aria-pressed="true"/,
  /data-profile-id="broken" aria-pressed="false"/,
  /role="status" data-view-status data-kind="success"/,
  /<noscript>/,
]) {
  assert.match(stateHtml, pattern);
}

assert.doesNotMatch(stateHtml, /onclick=|style=/i);
assert.match(stateCss, /button:focus-visible/);
assert.match(stateCss, /@media \(max-width:\s*40rem\)/);
assert.match(stateCss, /@media \(prefers-reduced-motion:\s*reduce\)/);

const require = createRequire(import.meta.url);
const dashboard = require(stateScriptPath);
assert.deepEqual(dashboard.getView("nobody"), {
  kind: "empty",
  message: "没有找到这位学习者。",
});
assert.equal(dashboard.getView("broken").kind, "error");
assert.equal(dashboard.getView("xiaoma").record.completedLessons, 7);
assert.equal(dashboard.loadingView("afei").kind, "loading");

function textRef() {
  return { textContent: "", hidden: false, dataset: {} };
}
const fakeRefs = {
  status: textRef(),
  content: textRef(),
  title: textRef(),
  description: textRef(),
  completedLessons: textRef(),
  hours: textRef(),
  currentStatus: textRef(),
  nextMilestone: textRef(),
};
dashboard.render(dashboard.getView("afei"), fakeRefs);
assert.equal(fakeRefs.status.dataset.kind, "success");
assert.equal(fakeRefs.title.textContent, "阿飞的学习面板");
assert.equal(fakeRefs.hours.textContent, "9 小时");
assert.equal(fakeRefs.content.hidden, false);
dashboard.render(dashboard.getView("nobody"), fakeRefs);
assert.equal(fakeRefs.content.hidden, true);
assert.equal(fakeRefs.status.textContent, "没有找到这位学习者。");

const v04Root = join(root, "site-src/examples/web-start/learning-dashboard-v04");
const apiHtml = readFileSync(join(v04Root, "index.html"), "utf8");
const apiCss = readFileSync(join(v04Root, "styles.css"), "utf8");
const apiScript = require(join(v04Root, "app.js"));

for (const pattern of [
  /学习进度报告器 Web v0\.4/,
  /data-profile-id="xiaoma" aria-pressed="true"/,
  /data-profile-id="AA" aria-pressed="false"/,
  /data-profile-id="unavailable" aria-pressed="false"/,
  /role="status" data-view-status/,
  /<noscript>/,
]) {
  assert.match(apiHtml, pattern);
}
assert.doesNotMatch(apiHtml, /onclick=|style=/i);
assert.match(apiCss, /@media \(max-width:\s*40rem\)/);
assert.match(apiCss, /@media \(prefers-reduced-motion:\s*reduce\)/);

const knownSummary = {
  learner_id: "xiaoma",
  learner_name: "小码",
  description: "从 API 读取。",
  completed_lessons: 7,
  completed_hours: 6.5,
  status: "按计划推进",
  next_milestone: "进入 Web 核心",
};
const knownView = await apiScript.fetchSummary("xiaoma", async () => ({
  status: 200,
  ok: true,
  json: async () => knownSummary,
}));
assert.equal(knownView.kind, "success");
assert.equal(knownView.record.name, "小码");
assert.equal(knownView.record.completedLessons, 7);

for (const [status, expectedKind] of [[404, "empty"], [422, "error"], [503, "error"]]) {
  const view = await apiScript.fetchSummary("nobody", async () => ({
    status,
    ok: false,
    json: async () => ({ detail: "demo" }),
  }));
  assert.equal(view.kind, expectedKind);
}
const offlineView = await apiScript.fetchSummary("xiaoma", async () => {
  throw new TypeError("fetch failed");
});
assert.equal(offlineView.kind, "error");
assert.match(offlineView.message, /Uvicorn/);

const invalidContractView = await apiScript.fetchSummary("xiaoma", async () => ({
  status: 200,
  ok: true,
  json: async () => ({ learner_name: "缺字段" }),
}));
assert.equal(invalidContractView.kind, "error");
assert.match(invalidContractView.message, /JSON/);

const python = join(root, ".venv/bin/python");
const apiTests = spawnSync(
  python,
  ["-m", "unittest", "discover", "-s", v04Root, "-p", "test_app.py", "-v"],
  { cwd: v04Root, encoding: "utf8" },
);
assert.equal(apiTests.status, 0, `${apiTests.stdout}\n${apiTests.stderr}`);

console.log(JSON.stringify({
  valid: true,
  html_language: "zh-CN",
  semantic_regions: ["main", "article", "h1", "dl", "dt", "dd"],
  responsive_layout: true,
  dark_mode: true,
  inline_behavior: false,
  versions: ["v0.1", "v0.2", "v0.3", "v0.4"],
  page_states: ["loading", "success", "empty", "error"],
  api_statuses: [200, 404, 422, 503, "offline"],
  api_tests: 6,
}, null, 2));
