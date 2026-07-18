import assert from "node:assert/strict";

import { endpointFor, fetchSummary, loadingState, saveStudySession } from "./dist/api.js";
import { isLearningSummary, isStudySessionCreated, summaryToRecord } from "./dist/contracts.js";

const validSummary = {
  learner_id: "xiaoma",
  learner_name: "小码",
  description: "正在学习 Web 核心。",
  completed_lessons: 8,
  completed_hours: 7.5,
  status: "按计划推进",
  next_milestone: "保存到 SQLite"
};

const validSession = {
  session_id: 3,
  learner_id: "xiaoma",
  hours: 1,
  note: "SQLite 持久化练习"
};

assert.deepEqual(loadingState("xiaoma"), { kind: "loading", message: "正在从 SQLite 读取 xiaoma……" });
assert.equal(endpointFor("unavailable"), "/api/demo-unavailable");
assert.equal(isLearningSummary(validSummary), true);
assert.equal(isLearningSummary({ ...validSummary, completed_hours: "7.5" }), false);
assert.equal(isStudySessionCreated(validSession), true);
assert.equal(isStudySessionCreated({ ...validSession, session_id: 3.5 }), false);
assert.equal(summaryToRecord(validSummary).learnerId, "xiaoma");

const ok = await fetchSummary("xiaoma", async () => Response.json(validSummary));
assert.equal(ok.kind, "success");

const missing = await fetchSummary("nobody", async () => Response.json({ detail: "missing" }, { status: 404 }));
assert.equal(missing.kind, "empty");

const invalidId = await fetchSummary("AA", async () => Response.json({ detail: [] }, { status: 422 }));
assert.equal(invalidId.kind, "error");

const unavailable = await fetchSummary("unavailable", async () => Response.json({ detail: "later" }, { status: 503 }));
assert.equal(unavailable.kind, "error");

const drift = await fetchSummary("xiaoma", async () => Response.json({ ...validSummary, completed_hours: "七小时" }));
assert.equal(drift.kind, "contract-error");

const saved = await saveStudySession("xiaoma", 1, "SQLite 持久化练习", async (_input, init) => {
  assert.equal(init?.method, "POST");
  assert.match(String(init?.body), /"hours":1/);
  return Response.json(validSession, { status: 201 });
});
assert.equal(saved.kind, "saved");

const rejected = await saveStudySession("xiaoma", 0, "错误小时数", async () =>
  Response.json({ detail: [] }, { status: 422 })
);
assert.equal(rejected.kind, "error");

const rolledBack = await saveStudySession("xiaoma", 1, "失败事务", async () =>
  Response.json({ detail: "rollback" }, { status: 503 })
);
assert.equal(rolledBack.kind, "error");

const badSaveContract = await saveStudySession("xiaoma", 1, "错误响应", async () =>
  Response.json({ session_id: "three" }, { status: 201 })
);
assert.equal(badSaveContract.kind, "contract-error");

const offline = await saveStudySession("xiaoma", 1, "断线", async () => {
  throw new TypeError("offline");
});
assert.equal(offline.kind, "error");

console.log(JSON.stringify({
  valid: true,
  contract_guards: ["LearningSummary", "StudySessionCreated"],
  read_states: ["loading", "success", "empty", "error", "contract-error"],
  write_states: ["idle", "saving", "saved", "error", "contract-error"],
  http_statuses: [200, 201, 404, 422, 503],
  rollback_message: true,
  network_used: false
}, null, 2));
