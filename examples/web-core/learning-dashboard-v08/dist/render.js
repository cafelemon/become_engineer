export function renderSummary(view, refs) {
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
function sessionItem(session) {
    const item = document.createElement("li");
    item.dataset.sessionId = String(session.session_id);
    const title = document.createElement("strong");
    title.textContent = `${session.hours} 小时`;
    const note = document.createElement("span");
    note.textContent = session.note;
    item.append(title, note);
    return item;
}
export function renderSessions(view, refs) {
    refs.sessionStatus.dataset.kind = view.kind;
    refs.sessionStatus.textContent = view.message;
    if (view.kind !== "success" && view.kind !== "empty")
        return;
    refs.sessionList.replaceChildren(...view.page.items.map(sessionItem));
}
function renderErrors(errors, refs) {
    refs.hoursError.textContent = errors.hours ?? "";
    refs.noteError.textContent = errors.note ?? "";
    refs.hoursError.hidden = !errors.hours;
    refs.noteError.hidden = !errors.note;
}
export function renderForm(view, refs) {
    refs.formStatus.dataset.kind = view.kind;
    refs.formStatus.textContent = view.message;
    refs.form.dataset.state = view.kind;
    refs.form.setAttribute("aria-busy", String(view.kind === "submitting"));
    refs.submitButton.disabled = view.kind === "submitting";
    refs.refreshButton.hidden = true;
    renderErrors("errors" in view ? view.errors : {}, refs);
}
export function showRefreshOnly(message, refs) {
    refs.formStatus.dataset.kind = "sync-error";
    refs.formStatus.textContent = message;
    refs.form.dataset.state = "sync-error";
    refs.submitButton.disabled = true;
    refs.refreshButton.hidden = false;
}
