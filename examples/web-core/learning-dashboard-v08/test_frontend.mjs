import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";

import {
  createStudySession,
  fetchSessionPage,
  serverFieldErrors
} from "./dist/api.js";
import {
  createSubmissionIntent,
  LatestRequestGate,
  validateSessionDraft
} from "./dist/form.js";

const validDraft = { hours: 1.25, note: "复盘表单状态" };
const session = {
  session_id: 5,
  learner_id: "xiaoma",
  hours: 1.25,
  note: "复盘表单状态",
  created_at: "2026-07-18 00:00:00"
};

assert.deepEqual(validateSessionDraft("1.25", " 复盘表单状态 "), {
  ok: true,
  draft: validDraft
});
assert.equal(validateSessionDraft("", "正常备注").ok, false);
assert.equal(validateSessionDraft("0.3", "正常备注").ok, false);
assert.equal(validateSessionDraft("25", "正常备注").ok, false);
assert.equal(validateSessionDraft("1", "   ").ok, false);
assert.equal(validateSessionDraft("1", "x".repeat(201)).ok, false);

let keyNumber = 0;
const intent = createSubmissionIntent(() => `fixed-${++keyNumber}`);
const firstKey = intent.keyFor(validDraft);
assert.equal(intent.keyFor(validDraft), firstKey);
const changedKey = intent.keyFor({ ...validDraft, hours: 1.5 });
assert.notEqual(changedKey, firstKey);
intent.complete();
assert.equal(intent.currentKey(), null);

const gate = new LatestRequestGate();
const oldToken = gate.start();
const latestToken = gate.start();
assert.equal(gate.isCurrent(oldToken), false);
assert.equal(gate.isCurrent(latestToken), true);

const validationPayload = {
  detail: [
    { loc: ["body", "hours"], msg: "Input should be a multiple of 0.25", type: "multiple_of" },
    { loc: ["body", "note"], msg: "Value error", type: "value_error" }
  ]
};
assert.deepEqual(serverFieldErrors(validationPayload), {
  hours: "小时数需要按 0.25 递增。",
  note: "备注不能只包含空格。"
});

let capturedBody = "";
let capturedKey = "";
const saved = await createStudySession(
  "xiaoma",
  validDraft,
  "lesson-v08-browser-test",
  async (_input, init) => {
    capturedBody = String(init?.body);
    capturedKey = new Headers(init?.headers).get("Idempotency-Key") ?? "";
    return new Response(JSON.stringify({ session, replayed: false }), {
      status: 201,
      headers: { "Content-Type": "application/json" }
    });
  }
);
assert.equal(saved.kind, "saved");
assert.equal(capturedKey, "lesson-v08-browser-test");
assert.deepEqual(JSON.parse(capturedBody), validDraft);

const rejected = await createStudySession(
  "xiaoma",
  validDraft,
  "lesson-v08-invalid-test",
  async () => new Response(JSON.stringify(validationPayload), {
    status: 422,
    headers: { "Content-Type": "application/json" }
  })
);
assert.equal(rejected.kind, "field-error");
assert.match(rejected.errors.hours ?? "", /0\.25/);

const networkFailure = await createStudySession(
  "xiaoma",
  validDraft,
  "lesson-v08-network-test",
  async () => { throw new TypeError("offline"); }
);
assert.equal(networkFailure.kind, "network-error");
assert.match(networkFailure.message, /同一个请求键/);

const serverFailure = await createStudySession(
  "xiaoma",
  validDraft,
  "lesson-v08-server-test",
  async () => new Response(JSON.stringify({ detail: "unavailable" }), {
    status: 503,
    headers: { "Content-Type": "application/json" }
  })
);
assert.equal(serverFailure.kind, "server-error");

let listUrl = "";
const page = await fetchSessionPage("xiaoma", 0, async (input) => {
  listUrl = String(input);
  return new Response(JSON.stringify({ items: [session], next_after_id: null }), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  });
});
assert.equal(page.kind, "success");
assert.match(listUrl, /limit=50/);

const root = import.meta.dirname;
const html = readFileSync(join(root, "index.html"), "utf8");
const css = readFileSync(join(root, "styles.css"), "utf8");
const main = readFileSync(join(root, "src/main.ts"), "utf8");
assert.match(html, /data-session-form/);
assert.match(html, /min="0\.25"/);
assert.match(html, /step="0\.25"/);
assert.match(html, /maxlength="200"/);
assert.match(html, /aria-live="polite"/);
assert.match(html, /<noscript>/);
assert.match(main, /checkValidity\(\)/);
assert.match(main, /reportValidity\(\)/);
assert.match(main, /Promise\.all/);
assert.match(main, /showRefreshOnly/);
assert.match(css, /max-width: 39rem/);
assert.match(css, /prefers-color-scheme: dark/);
assert.match(css, /prefers-reduced-motion: reduce/);

console.log(JSON.stringify({
  valid: true,
  client_validation_cases: 6,
  server_field_mapping_checked: true,
  idempotency_intent_reuse_checked: true,
  stale_refresh_guard_checked: true,
  network_retry_state_checked: true,
  server_resync_checked: true,
  mobile_dark_reduced_motion_noscript: true
}, null, 2));
