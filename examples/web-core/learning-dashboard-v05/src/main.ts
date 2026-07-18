import { fetchSummary, loadingState } from "./api.js";
import { render, type DashboardRefs } from "./render.js";

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
  nextMilestone: requiredElement('[data-field="next-milestone"]')
};

const buttons = Array.from(document.querySelectorAll<HTMLButtonElement>("[data-profile-id]"));

for (const button of buttons) {
  button.addEventListener("click", async () => {
    const profileId = button.dataset.profileId;
    if (!profileId) return;

    for (const candidate of buttons) {
      candidate.setAttribute("aria-pressed", String(candidate === button));
      candidate.disabled = true;
    }

    render(loadingState(profileId), refs);
    render(await fetchSummary(profileId), refs);

    for (const candidate of buttons) candidate.disabled = false;
  });
}
