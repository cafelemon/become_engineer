import type { PageState, SessionListState, StudySession, WriteState } from "./contracts.js";

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
  sessionStatus: HTMLElement;
  sessionList: HTMLElement;
  replayStatus: HTMLElement;
}

export function renderSummary(view: PageState, refs: DashboardRefs): void {
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

function sessionItem(session: StudySession): HTMLLIElement {
  const item = document.createElement("li");
  item.dataset.sessionId = String(session.session_id);
  const title = document.createElement("strong");
  title.textContent = `${session.hours} 小时`;
  const note = document.createElement("span");
  note.textContent = session.note;
  item.append(title, note);
  return item;
}

export function renderSessions(
  view: SessionListState,
  refs: DashboardRefs,
  append: boolean
): void {
  refs.sessionStatus.dataset.kind = view.kind;
  refs.sessionStatus.textContent = view.message;
  if (view.kind !== "success") return;
  if (!append) refs.sessionList.replaceChildren();
  refs.sessionList.append(...view.page.items.map(sessionItem));
}

export function renderReplay(view: WriteState, refs: DashboardRefs): void {
  refs.replayStatus.dataset.kind = view.kind;
  refs.replayStatus.textContent = view.message;
}
