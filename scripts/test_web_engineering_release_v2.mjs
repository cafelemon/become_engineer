import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { validateLesson } from "./lib/validate_web_engineering_lesson.mjs";

validateLesson("06");

const script = readFileSync(
  resolve(import.meta.dirname, "../site-src/examples/web-engineering/learning-dashboard-v14/backup_restore.sh"),
  "utf8",
);
for (const required of ["pg_dump --format=custom", "pg_restore --clean", "VERIFY_DATABASE_URL", "schema_present", "constraints_present"]) {
  assert.ok(script.includes(required), `backup restore script is missing ${required}`);
}
assert.match(script, /DATABASE_URL.*VERIFY_DATABASE_URL|VERIFY_DATABASE_URL.*DATABASE_URL/s);
