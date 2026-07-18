import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";

import {
  createStudySession,
  fetchSessionPage,
  fetchSummary
} from "./dist/api.js";
import {
  isStudySessionPage,
  isStudySessionWriteResult
} from "./dist/contracts.js";

const summary = {
  learner_id: "xiaoma",
  learner_name: "小码",
  description: "正在学习 Web",
  completed_lessons: 8,
  completed_hours: 7.5,
  status: "按计划推进",
  next_milestone: "设计 REST 资源"
};

const session = {
  session_id: 4,
  learner_id: "xiaoma",
  hours: 1,
  note: "REST 与幂等练习",
  created_at: "2026-07-18 00:00:00"
};

const page = { items: [session], next_after_id: null };
const writeResult = { session, replayed: false };

assert.equal(isStudySessionPage(page), true);
assert.equal(isStudySessionPage({ items: [{}], next_after_id: null }), false);
assert.equal(isStudySessionWriteResult(writeResult), true);
assert.equal(isStudySessionWriteResult({ session, replayed: "no" }), false);

const summaryState = await fetchSummary("xiaoma", async () =>
  new Response(JSON.stringify(summary), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  })
);
assert.equal(summaryState.kind, "success");

let requestedUrl = "";
const pageState = await fetchSessionPage("xiaoma", 2, async (input) => {
  requestedUrl = String(input);
  return new Response(JSON.stringify(page), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  });
});
assert.equal(pageState.kind, "success");
assert.match(requestedUrl, /limit=2/);
assert.match(requestedUrl, /after_id=2/);

const emptyState = await fetchSessionPage("xiaoma", 4, async () =>
  new Response(JSON.stringify({ items: [], next_after_id: null }), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  })
);
assert.equal(emptyState.kind, "empty");

const badPage = await fetchSessionPage("xiaoma", 0, async () =>
  new Response(JSON.stringify({ items: "wrong", next_after_id: null }), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  })
);
assert.equal(badPage.kind, "contract-error");

let capturedKey = "";
const created = await createStudySession("xiaoma", "lesson-v07-test-key", async (_input, init) => {
  capturedKey = new Headers(init?.headers).get("Idempotency-Key") ?? "";
  return new Response(JSON.stringify(writeResult), {
    status: 201,
    headers: { "Content-Type": "application/json" }
  });
});
assert.equal(created.kind, "saved");
assert.equal(created.httpStatus, 201);
assert.equal(capturedKey, "lesson-v07-test-key");

const replayed = await createStudySession("xiaoma", "lesson-v07-test-key", async () =>
  new Response(JSON.stringify({ session, replayed: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  })
);
assert.equal(replayed.kind, "saved");
assert.match(replayed.message, /没有再插入/);

const conflict = await createStudySession("xiaoma", "lesson-v07-test-key", async () =>
  new Response(JSON.stringify({ detail: "conflict" }), {
    status: 409,
    headers: { "Content-Type": "application/json" }
  })
);
assert.equal(conflict.kind, "error");
assert.match(conflict.message, /另一份请求内容/);

const html = readFileSync(join(import.meta.dirname, "index.html"), "utf8");
const css = readFileSync(join(import.meta.dirname, "styles.css"), "utf8");
assert.match(html, /data-load-more/);
assert.match(html, /data-replay-write/);
assert.match(html, /<noscript>/);
assert.match(css, /max-width: 39rem/);
assert.match(css, /prefers-color-scheme: dark/);
assert.match(css, /prefers-reduced-motion: reduce/);

console.log(JSON.stringify({
  valid: true,
  runtime_contracts: 3,
  cursor_query_checked: true,
  idempotency_header_checked: true,
  conflict_state_checked: true,
  mobile_and_noscript_contracts: true
}, null, 2));
