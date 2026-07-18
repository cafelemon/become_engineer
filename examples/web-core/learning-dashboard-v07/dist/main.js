import { createStudySession, fetchSessionPage, fetchSummary, loadingState } from "./api.js";
import { renderReplay, renderSessions, renderSummary } from "./render.js";
function requiredElement(selector) {
    const element = document.querySelector(selector);
    if (!element)
        throw new Error(`页面缺少必要元素：${selector}`);
    return element;
}
const refs = {
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
    replayStatus: requiredElement("[data-replay-status]")
};
const profileButtons = Array.from(document.querySelectorAll("[data-profile-id]"));
const loadMoreButton = requiredElement("[data-load-more]");
const replayButton = requiredElement("[data-replay-write]");
let activeLearnerId = "xiaoma";
let nextAfterId = null;
async function loadFirstPage(learnerId) {
    const page = await fetchSessionPage(learnerId);
    renderSessions(page, refs, false);
    nextAfterId = page.kind === "success" ? page.page.next_after_id : null;
    loadMoreButton.disabled = nextAfterId === null;
}
async function loadProfile(profileId) {
    for (const button of profileButtons) {
        button.setAttribute("aria-pressed", String(button.dataset.profileId === profileId));
        button.disabled = true;
    }
    replayButton.disabled = true;
    loadMoreButton.disabled = true;
    renderSummary(loadingState(profileId), refs);
    const result = await fetchSummary(profileId);
    renderSummary(result, refs);
    if (result.kind === "success") {
        activeLearnerId = result.record.learnerId;
        await loadFirstPage(activeLearnerId);
    }
    for (const button of profileButtons)
        button.disabled = false;
    replayButton.disabled = result.kind !== "success";
}
for (const button of profileButtons) {
    button.addEventListener("click", async () => {
        const profileId = button.dataset.profileId;
        if (profileId)
            await loadProfile(profileId);
    });
}
loadMoreButton.addEventListener("click", async () => {
    if (nextAfterId === null)
        return;
    loadMoreButton.disabled = true;
    const page = await fetchSessionPage(activeLearnerId, nextAfterId);
    renderSessions(page, refs, true);
    nextAfterId = page.kind === "success" ? page.page.next_after_id : null;
    loadMoreButton.disabled = nextAfterId === null;
});
replayButton.addEventListener("click", async () => {
    replayButton.disabled = true;
    const key = `lesson-v07-${crypto.randomUUID()}`;
    renderReplay({ kind: "saving", message: "正在连续发送两次相同请求……" }, refs);
    const first = await createStudySession(activeLearnerId, key);
    if (first.kind !== "saved") {
        renderReplay(first, refs);
        replayButton.disabled = false;
        return;
    }
    const second = await createStudySession(activeLearnerId, key);
    if (second.kind === "saved" && second.result.replayed) {
        renderReplay({
            ...second,
            message: `第一次 ${first.httpStatus}，第二次 ${second.httpStatus}；两次都是记录 #${second.result.session.session_id}。`
        }, refs);
        await loadProfile(activeLearnerId);
    }
    else {
        renderReplay(second, refs);
    }
    replayButton.disabled = false;
});
await loadProfile(activeLearnerId);
