export function render(view, refs) {
    refs.status.dataset.kind = view.kind;
    refs.status.textContent = view.message;
    refs.content.hidden = view.kind !== "success";
    if (view.kind !== "success")
        return;
    refs.title.textContent = `${view.record.name}的学习面板`;
    refs.description.textContent = view.record.description;
    refs.completedLessons.textContent = `${view.record.completedLessons} 节`;
    refs.hours.textContent = `${view.record.hours} 小时`;
    refs.currentStatus.textContent = view.record.status;
    refs.nextMilestone.textContent = view.record.nextMilestone;
    refs.activeLearner.textContent = view.record.learnerId;
}
export function renderSave(view, refs) {
    refs.saveStatus.dataset.kind = view.kind;
    refs.saveStatus.textContent = view.message;
}
