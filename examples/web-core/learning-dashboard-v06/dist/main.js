import { fetchSummary, loadingState, saveStudySession } from "./api.js";
import { render, renderSave } from "./render.js";
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
    saveStatus: requiredElement("[data-save-status]")
};
const profileButtons = Array.from(document.querySelectorAll("[data-profile-id]"));
const saveButton = requiredElement("[data-save-one-hour]");
let activeLearnerId = "xiaoma";
async function loadProfile(profileId) {
    for (const button of profileButtons) {
        button.setAttribute("aria-pressed", String(button.dataset.profileId === profileId));
        button.disabled = true;
    }
    saveButton.disabled = true;
    render(loadingState(profileId), refs);
    const result = await fetchSummary(profileId);
    render(result, refs);
    if (result.kind === "success")
        activeLearnerId = result.record.learnerId;
    for (const button of profileButtons)
        button.disabled = false;
    saveButton.disabled = result.kind !== "success";
}
for (const button of profileButtons) {
    button.addEventListener("click", async () => {
        const profileId = button.dataset.profileId;
        if (profileId)
            await loadProfile(profileId);
    });
}
saveButton.addEventListener("click", async () => {
    saveButton.disabled = true;
    renderSave({ kind: "saving", message: "正在把 1 小时写入事务……" }, refs);
    const result = await saveStudySession(activeLearnerId, 1, "SQLite 持久化练习");
    renderSave(result, refs);
    if (result.kind === "saved")
        await loadProfile(activeLearnerId);
    saveButton.disabled = false;
});
