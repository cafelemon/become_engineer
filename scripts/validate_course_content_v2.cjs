#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const standardPath = "docs/08_content_standard.md";
const commonTemplatePath = "templates/course_lesson_template.md";
const skillRoot = ".agents/skills/become-engineer-course-authoring";
const skillTemplatePath = skillRoot + "/templates/course_lesson_template.md";
const courseTypes = [
  "tool-operation",
  "programming-start",
  "cs-concept",
  "algorithm-data-structure",
  "system-device",
  "ai-experiment",
  "web-llm-agent",
  "project-integration"
];
const requiredContexts = [
  "overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"
];
const bannedVisiblePhrases = [
  "可观察结果", "成功证据", "迁移验收", "受控失败实验", "心智模型", "本课增量", "当前任务"
];
const failures = [];

function read(relativePath) {
  const absolute = path.join(root, relativePath);
  if (!fs.existsSync(absolute)) {
    failures.push("缺少文件：" + relativePath);
    return "";
  }
  return fs.readFileSync(absolute, "utf8");
}

function stripCode(markdown) {
  return markdown.replace(/```[\s\S]*?```/g, "").replace(/`[^`]*`/g, "");
}

const standard = read(standardPath);
const commonTemplate = read(commonTemplatePath);
const skillTemplate = read(skillTemplatePath);
const skill = read(skillRoot + "/SKILL.md");
const contract = read(skillRoot + "/references/course-contract.md");

for (const context of requiredContexts) {
  if (!commonTemplate.includes(`data-context-type="${context}"`)) {
    failures.push(`共同模板缺少语义类型 ${context}`);
  }
  if (!standard.includes("`" + context + "`")) failures.push(`内容规范缺少语义类型 ${context}`);
}

for (const phrase of ["完成检查", "来源与版本", "适用版本", "核查日期", "下一步"]) {
  if (!commonTemplate.includes(phrase)) failures.push("共同模板缺少：" + phrase);
}
if (!commonTemplate.includes("be-tutor-mount")) failures.push("共同模板缺少正式助教挂载点");
if (/be-task-route|data-step-id|id=["']step-\d+/.test(commonTemplate)) failures.push("V2 共同模板仍包含旧任务步骤结构");

for (const courseType of courseTypes) {
  const relativePath = `${skillRoot}/templates/course-types/${courseType}.md`;
  const overlay = read(relativePath);
  for (const label of ["开场", "视觉", "复现", "常见失败", "项目连接"]) {
    if (!overlay.includes(label)) failures.push(`${courseType} 差异模板缺少 ${label}`);
  }
  if (/be-task-route|data-step-id|id=["']step-\d+/.test(overlay)) failures.push(`${courseType} 差异模板包含旧任务步骤结构`);
}

for (const relativePath of [commonTemplatePath, skillTemplatePath]) {
  const visible = stripCode(read(relativePath));
  for (const phrase of bannedVisiblePhrases) {
    if (visible.includes(phrase)) failures.push(`${relativePath} 出现管理化表达 “${phrase}”`);
  }
}

for (const mode of ["新建 V2 课程", "V1 迁移到 V2", "维护 V1"]) {
  if (!skill.includes(mode)) failures.push("Skill 缺少生产模式：" + mode);
}
for (const token of ["lesson + contexts + cards", "lesson + steps + cards", "be:tutor:v1:<lessonId>", "be:tutor:v2:<lessonId>"]) {
  if (!contract.includes(token)) failures.push("课程契约缺少兼容说明：" + token);
}
if (!standard.includes("十三个跨方向样板已于 2026-07-17 通过评审")) failures.push("内容规范未记录跨方向评审结论");
if (!standard.includes("现有 55 节正式课程")) failures.push("内容规范未说明 V1 正式课程迁移边界");

if (failures.length) {
  console.error("V2 课程生产契约校验失败：");
  failures.forEach(function (failure) { console.error("- " + failure); });
  process.exit(1);
}

console.log(JSON.stringify({
  valid: true,
  required_contexts: requiredContexts.length,
  course_types: courseTypes.length,
  modes: 3,
  formal_migration: false
}, null, 2));
