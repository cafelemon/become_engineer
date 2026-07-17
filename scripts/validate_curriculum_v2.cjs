#!/usr/bin/env node

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const registryPath = path.join(root, "site-src/data/curriculum/v2.json");
const registry = JSON.parse(fs.readFileSync(registryPath, "utf8"));
const migrationPath = path.join(root, "site-src/data/curriculum/migration-v2.json");
const migration = JSON.parse(fs.readFileSync(migrationPath, "utf8"));

const lessonRoots = [
  "learning-paths/engineering-foundation/stage-0",
  "learning-paths/programming-languages/python-basics",
  "learning-paths/programming-languages/cpp-core",
  "learning-paths/programming-languages/python-core",
  "learning-paths/cs-core"
];

function markdownLessons(directory) {
  return fs.readdirSync(path.join(root, directory))
    .filter((name) => name.endsWith(".md") && name !== "README.md")
    .map((name) => `${directory}/${name}`);
}

function unique(values, label) {
  assert.equal(new Set(values).size, values.length, `${label} 存在重复值`);
}

function alternatives(reference) {
  return reference.split("|");
}

function stripCode(markdown) {
  return markdown.replace(/```[\s\S]*?```/g, "").replace(/`[^`]*`/g, "");
}

assert.equal(registry.version, 2, "课程登记版本必须为 2");
assert.equal(registry.authority, "learning-paths/curriculum-map.md", "权威公开页面不一致");
assert.equal(registry.course_count, 55, "声明课程数必须为 55");
assert.equal(registry.lessons.length, registry.course_count, "逐课登记数量与声明不一致");

unique(registry.modules.map((item) => item.id), "模块 ID");
unique(registry.modules.map((item) => item.anchor), "模块锚点");
unique(registry.lessons.map((item) => item.id), "课程 ID");
unique(registry.lessons.map((item) => item.url), "课程 URL");

const moduleIds = new Set(registry.modules.map((item) => item.id));
const profileIds = new Set(Object.keys(registry.profile_rules));

for (const module of registry.modules) {
  assert.ok(registry.depths.includes(module.depth), `${module.id} 使用了未知深度：${module.depth}`);
  assert.ok(registry.roles.includes(module.role), `${module.id} 使用了未知角色：${module.role}`);
  assert.ok(registry.content_statuses.includes(module.content_status), `${module.id} 使用了未知内容状态`);
  assert.ok(registry.connection_statuses.includes(module.connection_status), `${module.id} 使用了未知衔接状态`);
  assert.match(module.anchor, /^module-[a-z0-9-]+$/, `${module.id} 的锚点格式无效`);
  for (const profile of module.profiles) assert.ok(profileIds.has(profile), `${module.id} 引用了未知画像 ${profile}`);
  for (const reference of [...module.prerequisites, ...module.unlocks]) {
    for (const candidate of alternatives(reference)) {
      assert.ok(moduleIds.has(candidate), `${module.id} 引用了未知模块 ${candidate}`);
    }
  }
  if (module.content_status === "已规划未建设") {
    assert.equal(registry.lessons.some((lesson) => lesson.module_id === module.id), false, `${module.id} 尚未建设却登记了正式课程`);
  }
}

const expectedUrls = lessonRoots.flatMap(markdownLessons).sort();
const registeredUrls = registry.lessons.map((item) => item.url).sort();
assert.deepEqual(registeredUrls, expectedUrls, "课程登记必须与五个已开放课程目录逐项一致");

for (const lesson of registry.lessons) {
  assert.ok(moduleIds.has(lesson.module_id), `${lesson.id} 引用了未知模块 ${lesson.module_id}`);
  assert.ok(["已开放", "已开放待重分层"].includes(lesson.content_status), `${lesson.id} 的开放状态无效`);
  const source = path.join(root, lesson.url);
  assert.ok(fs.existsSync(source), `${lesson.id} 的文件不存在：${lesson.url}`);
  const markdown = fs.readFileSync(source, "utf8");
  const heading = markdown.match(/^#\s+(.+)$/m);
  assert.ok(heading, `${lesson.id} 缺少一级标题`);
  assert.equal(heading[1].trim(), lesson.title, `${lesson.id} 的登记标题与正文不一致`);
}

assert.equal(migration.version, 1, "课程迁移台账版本必须为 1");
assert.equal(migration.registry, "site-src/data/curriculum/v2.json", "迁移台账引用了错误的课程登记");
assert.equal(migration.content_standard, "docs/08_content_standard.md", "迁移台账引用了错误的内容规范");
assert.equal(migration.current_schema, "mixed-v1-v2", "正式课程迁移期间必须声明 V1/V2 混合协议");
assert.equal(migration.target_schema, "v2", "正式课程目标协议声明必须为 V2");

unique(migration.batches.map((item) => item.id), "迁移批次 ID");
unique(migration.batches.map((item) => item.order), "迁移批次顺序");
unique(migration.lessons.map((item) => item.id), "迁移课程 ID");

const registeredLessonIds = registry.lessons.map((item) => item.id).sort();
const migrationLessonIds = migration.lessons.map((item) => item.id).sort();
assert.deepEqual(migrationLessonIds, registeredLessonIds, "迁移台账必须逐课覆盖全部正式课程");
assert.deepEqual(Object.keys(migration.tutor_lesson_ids).sort(), registeredLessonIds, "迁移台账必须冻结全部正式课程的 tutor lesson_id");

const lessonIds = new Set(registeredLessonIds);
const batchById = new Map(migration.batches.map((item) => [item.id, item]));
const projectLineIds = new Set(Object.keys(migration.project_lines));
const courseTypes = new Set(migration.course_types);
const migrationStatuses = new Set(migration.migration_statuses);
const migrationKinds = new Set(migration.migration_kinds);
const lessonIndex = new Map(migration.lessons.map((item, index) => [item.id, index]));

for (const batch of migration.batches) {
  assert.ok(Number.isInteger(batch.order) && batch.order > 0, `${batch.id} 的顺序无效`);
  assert.ok(batch.completion_gate.length >= 20, `${batch.id} 缺少清楚的完成门槛`);
  for (const moduleId of batch.prerequisite_modules) assert.ok(moduleIds.has(moduleId), `${batch.id} 引用了未知前置模块 ${moduleId}`);
  const actual = migration.lessons.filter((lesson) => lesson.batch_id === batch.id).length;
  assert.equal(actual, batch.lesson_count, `${batch.id} 的课程数量与逐课登记不一致`);
}

for (const item of migration.lessons) {
  const formal = registry.lessons.find((lesson) => lesson.id === item.id);
  const targetModule = registry.modules.find((module) => module.id === item.target_module_id);
  assert.ok(targetModule, `${item.id} 引用了未知目标模块 ${item.target_module_id}`);
  assert.equal(formal.module_id, item.target_module_id, `${item.id} 的课程登记尚未对齐目标模块`);
  assert.equal(item.target_depth, targetModule.depth, `${item.id} 的目标深度与模块不一致`);
  assert.equal(item.target_role, targetModule.role, `${item.id} 的目标角色与模块不一致`);
  assert.ok(courseTypes.has(item.course_type), `${item.id} 使用了未知课型 ${item.course_type}`);
  assert.ok(projectLineIds.has(item.project_line), `${item.id} 使用了未知项目线 ${item.project_line}`);
  assert.ok(batchById.has(item.batch_id), `${item.id} 使用了未知批次 ${item.batch_id}`);
  assert.ok(migrationStatuses.has(item.migration_status), `${item.id} 使用了未知迁移状态`);
  assert.ok(migrationKinds.has(item.migration_kind), `${item.id} 使用了未知迁移方式`);

  for (const prerequisite of item.prerequisite_lesson_ids) {
    assert.ok(lessonIds.has(prerequisite), `${item.id} 引用了未知前置课程 ${prerequisite}`);
    assert.ok(lessonIndex.get(prerequisite) < lessonIndex.get(item.id), `${item.id} 的前置课程 ${prerequisite} 没有排在它之前`);
  }

  const markdown = fs.readFileSync(path.join(root, formal.url), "utf8");
  const mounts = [...markdown.matchAll(/data-tutor-lesson="([^"]+)"/g)].map((match) => match[1]);
  assert.equal(mounts.length, 1, `${item.id} 必须且只能有一个小码挂载点`);
  assert.equal(mounts[0], migration.tutor_lesson_ids[item.id], `${item.id} 的稳定 tutor lesson_id 发生变化`);

  const knowledgePath = path.join(root, `site-src/data/tutor/${mounts[0]}.json`);
  assert.ok(fs.existsSync(knowledgePath), `${item.id} 缺少小码知识库 ${knowledgePath}`);
  const knowledge = JSON.parse(fs.readFileSync(knowledgePath, "utf8"));
  const hasSteps = Array.isArray(knowledge.steps);
  const hasContexts = Array.isArray(knowledge.contexts);
  assert.notEqual(hasSteps, hasContexts, `${item.id} 的知识库必须且只能使用一种协议`);
  if (item.migration_status === "已迁移") {
    assert.ok(hasContexts, `${item.id} 标记为已迁移但知识库仍不是 V2`);
    assert.doesNotMatch(markdown, /be-task-route|data-step-id|id=["']step-\d+/, `${item.id} 已迁移但仍包含 V1 任务步骤结构`);
    const contextTypes = new Set([...markdown.matchAll(/data-context-type="([^"]+)"/g)].map((match) => match[1]));
    for (const required of ["overview", "concept", "example", "reproduce", "modify", "troubleshoot", "project"]) {
      assert.ok(contextTypes.has(required), `${item.id} 已迁移但缺少 ${required} 语义区域`);
    }
    for (const heading of ["完成检查", "来源与版本", "下一步"]) {
      assert.ok(markdown.includes(`## ${heading}`), `${item.id} 已迁移但缺少“${heading}”`);
    }
    const visible = stripCode(markdown);
    for (const phrase of ["可观察结果", "成功证据", "迁移验收", "受控失败实验", "心智模型", "本课增量", "当前任务"]) {
      assert.ok(!visible.includes(phrase), `${item.id} 已迁移但仍出现管理化表达“${phrase}”`);
    }
  } else {
    assert.ok(hasSteps, `${item.id} 尚未迁移却提前切换了 V2 知识库`);
  }
}

const mapSource = fs.readFileSync(path.join(root, registry.authority), "utf8");
for (const module of registry.modules) {
  assert.ok(mapSource.includes(`{ #${module.anchor} }`) || mapSource.includes(`id="${module.anchor}"`), `课程地图缺少模块锚点 #${module.anchor}`);
}
for (const lesson of registry.lessons) {
  const relative = lesson.url.replace(/^learning-paths\//, "");
  const linkPattern = new RegExp(`\\]\\(${relative.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\$&")}\\)`);
  assert.ok(linkPattern.test(mapSource), `课程地图未逐课链接 ${lesson.url}`);
}

const navSource = fs.readFileSync(path.join(root, "mkdocs.yml"), "utf8");
for (const lesson of registry.lessons) {
  const occurrences = navSource.split(lesson.url).length - 1;
  assert.equal(occurrences, 1, `正式导航必须且只能登记一次 ${lesson.url}`);
}
for (const label of ["CS 起步:", "C++ 起步:", "C++ 核心:", "Python 核心:", "Python 工程化:", "共同算法与数据结构基础:", "算法核心:"]) {
  assert.ok(navSource.includes(label), `正式导航缺少 V2 分层：${label}`);
}
const commonNavOrder = ["- 工程基础入门:", "- Python 起步:", "- CS 起步:"].map((label) => navSource.indexOf(label));
assert.ok(commonNavOrder.every((index) => index >= 0), "正式导航缺少共同基座分组");
assert.deepEqual([...commonNavOrder].sort((a, b) => a - b), commonNavOrder, "正式导航共同基座顺序必须是工程基础 → Python 起步 → CS 起步");

console.log(JSON.stringify({
  valid: true,
  version: registry.version,
  modules: registry.modules.length,
  lessons: registry.lessons.length,
  statuses: Object.fromEntries(registry.content_statuses.map((status) => [status, registry.modules.filter((item) => item.content_status === status).length])),
  migration: {
    batches: migration.batches.length,
    lesson_statuses: Object.fromEntries(migration.migration_statuses.map((status) => [status, migration.lessons.filter((item) => item.migration_status === status).length])),
    target_modules: Object.fromEntries([...new Set(migration.lessons.map((item) => item.target_module_id))].map((moduleId) => [moduleId, migration.lessons.filter((item) => item.target_module_id === moduleId).length]))
  }
}, null, 2));
