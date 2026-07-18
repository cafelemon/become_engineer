import type { PageState, SaveState } from "./contracts.js";

export interface DashboardRefs {
  status: HTMLElement;
  content: HTMLElement;
  title: HTMLElement;
  description: HTMLElement;
  completedLessons: HTMLElement;
  hours: HTMLElement;
  currentStatus: HTMLElement;
  nextMilestone: HTMLElement;
  activeLearner: HTMLElement;
  saveStatus: HTMLElement;
}

export function render(view: PageState, refs: DashboardRefs): void {
  refs.status.dataset.kind = view.kind;
  refs.status.textContent = view.message;
  refs.content.hidden = view.kind !== "success";

  if (view.kind !== "success") return;

  refs.title.textContent = `${view.record.name}的学习面板`;
  refs.description.textContent = view.record.description;
  refs.completedLessons.textContent = `${view.record.completedLessons} 节`;
  refs.hours.textContent = `${view.record.hours} 小时`;
  refs.currentStatus.textContent = view.record.status;
  refs.nextMilestone.textContent = view.record.nextMilestone;
  refs.activeLearner.textContent = view.record.learnerId;
}

export function renderSave(view: SaveState, refs: DashboardRefs): void {
  refs.saveStatus.dataset.kind = view.kind;
  refs.saveStatus.textContent = view.message;
}
