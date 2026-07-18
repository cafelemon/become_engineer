import {
  createStudySession,
  fetchSessionPage,
  fetchSummary,
  loadingState
} from "./api.js";
import { createSubmissionIntent, LatestRequestGate, validateSessionDraft } from "./form.js";
import {
  renderForm,
  renderSessions,
  renderSummary,
  showRefreshOnly,
  type DashboardRefs
} from "./render.js";
import type { FieldErrors, FormState } from "./contracts.js";

function requiredElement<T extends HTMLElement>(selector: string): T {
  const element = document.querySelector<T>(selector);
  if (!element) throw new Error(`页面缺少必要元素：${selector}`);
  return element;
}

const refs: DashboardRefs = {
  status: requiredElement("[data-view-status]"),
  content: requiredElement("[data-view-content]"),
  title: requiredElement('[data-field="title"]'),
  description: requiredElement('[data-field="description"]'),
  completedLessons: requiredElement('[data-field="completed-lessons"]'),
  hours: requiredElement('[data-field="hours"]'),
  currentStatus: requiredElement('[data-field="status"]'),
  nextMilestone: requiredElement('[data-field="next-milestone"]'),
  activeLearner: requiredElement("[data-active-learner]"),
  sessionStatus: requiredElement("[data-session-status]"),
  sessionList: requiredElement("[data-session-list]"),
  form: requiredElement<HTMLFormElement>("[data-session-form]"),
  submitButton: requiredElement<HTMLButtonElement>("[data-submit-session]"),
  refreshButton: requiredElement<HTMLButtonElement>("[data-refresh-dashboard]"),
  formStatus: requiredElement("[data-form-status]"),
  hoursError: requiredElement("[data-error-hours]"),
  noteError: requiredElement("[data-error-note]")
};

const hoursInput = requiredElement<HTMLInputElement>("[data-input-hours]");
const noteInput = requiredElement<HTMLTextAreaElement>("[data-input-note]");
const profileButtons = Array.from(document.querySelectorAll<HTMLButtonElement>("[data-profile-id]"));
const intent = createSubmissionIntent();
const refreshGate = new LatestRequestGate();
let activeLearnerId = "xiaoma";
let submitting = false;
let waitingForRefresh = false;

async function refreshProfile(profileId: string): Promise<boolean> {
  const token = refreshGate.start();
  for (const button of profileButtons) button.disabled = true;
  renderSummary(loadingState(profileId), refs);

  const [summary, sessions] = await Promise.all([
    fetchSummary(profileId),
    fetchSessionPage(profileId)
  ]);
  if (!refreshGate.isCurrent(token)) return false;

  renderSummary(summary, refs);
  renderSessions(sessions, refs);
  const ready = summary.kind === "success" &&
    (sessions.kind === "success" || sessions.kind === "empty");
  if (summary.kind === "success") activeLearnerId = summary.record.learnerId;
  for (const button of profileButtons) button.disabled = false;
  refs.submitButton.disabled = !ready || waitingForRefresh;
  return ready;
}

function nativeErrors(): FieldErrors {
  const errors: FieldErrors = {};
  if (!hoursInput.validity.valid) errors.hours = hoursInput.validationMessage;
  if (!noteInput.validity.valid) errors.note = noteInput.validationMessage;
  return errors;
}

for (const button of profileButtons) {
  button.addEventListener("click", async () => {
    const profileId = button.dataset.profileId;
    if (!profileId || submitting || waitingForRefresh) return;
    for (const item of profileButtons) {
      item.setAttribute("aria-pressed", String(item === button));
    }
    intent.complete();
    refs.form.reset();
    renderForm({ kind: "idle", message: "填写一条学习时段。" }, refs);
    await refreshProfile(profileId);
  });
}

for (const input of [hoursInput, noteInput]) {
  input.addEventListener("input", () => {
    if (!submitting && !waitingForRefresh) {
      renderForm({ kind: "editing", message: "内容还没有提交。" }, refs);
    }
  });
}

refs.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (submitting || waitingForRefresh) return;

  if (!refs.form.checkValidity()) {
    const errors = nativeErrors();
    renderForm({ kind: "invalid", message: "先改好标出的字段。", errors }, refs);
    refs.form.reportValidity();
    return;
  }

  const checked = validateSessionDraft(hoursInput.value, noteInput.value);
  if (!checked.ok) {
    renderForm({ kind: "invalid", message: "先改好标出的字段。", errors: checked.errors }, refs);
    return;
  }

  submitting = true;
  const key = intent.keyFor(checked.draft);
  renderForm({ kind: "submitting", message: "正在保存，请不要重复点击……" }, refs);
  const result = await createStudySession(activeLearnerId, checked.draft, key);
  submitting = false;

  if (result.kind !== "saved") {
    renderForm(result, refs);
    return;
  }

  intent.complete();
  waitingForRefresh = true;
  renderForm({ ...result, message: `${result.message} 正在重新读取服务器状态……` }, refs);
  const refreshed = await refreshProfile(activeLearnerId);
  waitingForRefresh = false;

  if (!refreshed) {
    showRefreshOnly(
      `记录 #${result.result.session.session_id} 已保存，但页面没有重新同步。请只点“重新同步”，不要再次提交。`,
      refs
    );
    return;
  }

  refs.form.reset();
  renderForm(
    {
      ...result,
      message: `记录 #${result.result.session.session_id} 已保存，汇总和列表已从服务器重新读取。`
    },
    refs
  );
});

refs.refreshButton.addEventListener("click", async () => {
  refs.refreshButton.disabled = true;
  const refreshed = await refreshProfile(activeLearnerId);
  refs.refreshButton.disabled = false;
  if (refreshed) {
    waitingForRefresh = false;
    refs.form.reset();
    renderForm({ kind: "idle", message: "页面已经同步，可以继续填写。" }, refs);
  }
});

renderForm({ kind: "idle", message: "填写一条学习时段。" }, refs);
await refreshProfile(activeLearnerId);
