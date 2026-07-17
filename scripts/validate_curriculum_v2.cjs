#!/usr/bin/env node

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const registryPath = path.join(root, "site-src/data/curriculum/v2.json");
const registry = JSON.parse(fs.readFileSync(registryPath, "utf8"));

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

const mapSource = fs.readFileSync(path.join(root, registry.authority), "utf8");
for (const module of registry.modules) {
  assert.ok(mapSource.includes(`{ #${module.anchor} }`) || mapSource.includes(`id="${module.anchor}"`), `课程地图缺少模块锚点 #${module.anchor}`);
}
for (const lesson of registry.lessons) {
  const relative = lesson.url.replace(/^learning-paths\//, "");
  const linkPattern = new RegExp(`\\]\\(${relative.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\$&")}\\)`);
  assert.ok(linkPattern.test(mapSource), `课程地图未逐课链接 ${lesson.url}`);
}

console.log(JSON.stringify({
  valid: true,
  version: registry.version,
  modules: registry.modules.length,
  lessons: registry.lessons.length,
  statuses: Object.fromEntries(registry.content_statuses.map((status) => [status, registry.modules.filter((item) => item.content_status === status).length]))
}, null, 2));
