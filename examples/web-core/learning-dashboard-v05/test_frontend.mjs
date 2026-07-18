import assert from "node:assert/strict";

import { endpointFor, fetchSummary, loadingState } from "./dist/api.js";
import { isLearningSummary, summaryToRecord } from "./dist/contracts.js";

const validSummary = {
  learner_id: "xiaoma",
  learner_name: "小码",
  description: "正在学习 Web 核心。",
  completed_lessons: 8,
  completed_hours: 7.5,
  status: "按计划推进",
  next_milestone: "保持契约一致"
};

assert.deepEqual(loadingState("xiaoma"), { kind: "loading", message: "正在读取 xiaoma……" });
assert.equal(endpointFor("contract-drift"), "/api/demo-contract-drift");
assert.equal(isLearningSummary(validSummary), true);
assert.equal(isLearningSummary({ ...validSummary, completed_hours: "7.5" }), false);
assert.equal(isLearningSummary({ ...validSummary, status: "随便写一个状态" }), false);
assert.equal(isLearningSummary(null), false);
assert.equal(summaryToRecord(validSummary).completedLessons, 8);

const ok = await fetchSummary("xiaoma", async () => Response.json(validSummary));
assert.equal(ok.kind, "success");
assert.equal(ok.kind === "success" ? ok.record.name : "", "小码");

const missing = await fetchSummary("nobody", async () => Response.json({ detail: "missing" }, { status: 404 }));
assert.equal(missing.kind, "empty");

const invalidId = await fetchSummary("AA", async () => Response.json({ detail: [] }, { status: 422 }));
assert.equal(invalidId.kind, "error");

const unavailable = await fetchSummary("unavailable", async () => Response.json({ detail: "later" }, { status: 503 }));
assert.equal(unavailable.kind, "error");

const drift = await fetchSummary("contract-drift", async () => Response.json({ ...validSummary, completed_hours: "七小时" }));
assert.equal(drift.kind, "contract-error");

const badJson = await fetchSummary("xiaoma", async () => new Response("not json", {
  status: 200,
  headers: { "content-type": "application/json" }
}));
assert.equal(badJson.kind, "contract-error");

const offline = await fetchSummary("xiaoma", async () => {
  throw new TypeError("offline");
});
assert.equal(offline.kind, "error");

console.log(JSON.stringify({
  valid: true,
  contract_guard: true,
  states: ["loading", "success", "empty", "error", "contract-error"],
  http_statuses: [200, 404, 422, 503],
  invalid_json_rejected: true,
  offline_fallback: true,
  network_used: false
}, null, 2));
