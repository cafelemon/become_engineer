import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const args = process.argv.slice(2);

function option(name, fallback = null) {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : fallback;
}

const repoRoot = resolve(option("--repo", process.cwd()));
const defaultInput = resolve(repoRoot, "source-materials", "exports", "recruiting-reference-v2", "authoring-input.json");
const inputPath = resolve(option("--input", defaultInput));
const courseId = option("--course");
const stageId = option("--stage");
const ability = option("--ability");
const kind = option("--type");
const frequency = option("--frequency");
const priority = option("--priority");
const limit = Number(option("--limit", "12"));

if (!Number.isInteger(limit) || limit < 1 || limit > 100) throw new Error("--limit 必须是 1 到 100 的整数");
if (!courseId && !stageId && !ability) throw new Error("至少提供 --course、--stage 或 --ability 之一");

let library;
try {
  library = JSON.parse(await readFile(inputPath, "utf8"));
} catch (error) {
  throw new Error(`无法读取 V2 课程生产导出 ${inputPath}：${error.message}`);
}

const allowedTypes = new Set(["machine-test", "interview"]);
if (kind && !allowedTypes.has(kind)) throw new Error("--type 只能是 machine-test 或 interview");

const matches = library.signals
  .filter((signal) => !courseId || signal.course_ids.includes(courseId))
  .filter((signal) => !stageId || signal.planned_stage_ids.includes(stageId))
  .filter((signal) => !ability || signal.primary_ability_family === ability)
  .filter((signal) => !kind || signal.signal_kind === kind)
  .filter((signal) => !frequency || signal.roles.frequency === frequency)
  .filter((signal) => !priority || signal.roles.priority === priority)
  .sort((left, right) => {
    const priorityRank = { core: 0, "recommended-deepening": 1, "optional-observation": 2 };
    const frequencyRank = { "high-frequency-reference": 0, "repeated-signal": 1, "direction-signal": 2 };
    return (priorityRank[left.roles.priority] ?? 9) - (priorityRank[right.roles.priority] ?? 9)
      || (frequencyRank[left.roles.frequency] ?? 9) - (frequencyRank[right.roles.frequency] ?? 9)
      || left.topic_id.localeCompare(right.topic_id);
  })
  .slice(0, limit);

console.log(JSON.stringify({
  schema_version: library.schema_version,
  disclaimer: library.disclaimer,
  query: { course_id: courseId, stage_id: stageId, ability, signal_kind: kind, frequency, priority, limit },
  result_count: matches.length,
  signals: matches,
  authoring_rule: "只把能力、难度、证据等级和课程映射作为原创输入；禁止复述外部题面、标题叙事和答案结构。",
}, null, 2));
