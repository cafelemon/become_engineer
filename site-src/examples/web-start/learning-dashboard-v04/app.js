(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.LearningDashboard = api;
  if (root.document) api.mount(root.document, root.fetch.bind(root));
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const API_ROOT = "/api";

  function loadingView(profileId) {
    return { kind: "loading", message: `正在向 API 请求 ${profileId}……` };
  }

  function isSummary(value) {
    return Boolean(
      value &&
      typeof value === "object" &&
      typeof value.learner_id === "string" &&
      typeof value.learner_name === "string" &&
      typeof value.description === "string" &&
      Number.isInteger(value.completed_lessons) &&
      typeof value.completed_hours === "number" &&
      typeof value.status === "string" &&
      typeof value.next_milestone === "string"
    );
  }

  function summaryToRecord(summary) {
    if (!isSummary(summary)) throw new TypeError("API 返回的数据不符合学习报告契约。");
    return {
      name: summary.learner_name,
      description: summary.description,
      completedLessons: summary.completed_lessons,
      hours: summary.completed_hours,
      status: summary.status,
      nextMilestone: summary.next_milestone
    };
  }

  async function fetchSummary(profileId, fetchImpl) {
    const path = profileId === "unavailable"
      ? `${API_ROOT}/demo-unavailable`
      : `${API_ROOT}/learning-summary/${encodeURIComponent(profileId)}`;
    let response;
    try {
      response = await fetchImpl(path, { headers: { Accept: "application/json" } });
    } catch (error) {
      return { kind: "error", message: "连接不到本地 API。先确认 Uvicorn 还在运行。" };
    }

    if (response.status === 404) {
      return { kind: "empty", message: "API 正常响应，但没有找到这位学习者。" };
    }
    if (response.status === 422) {
      return { kind: "error", message: "学习者 ID 格式不符合接口约定。" };
    }
    if (!response.ok) {
      return { kind: "error", message: `API 返回 ${response.status}，这次没有更新页面。` };
    }

    try {
      const summary = await response.json();
      const record = summaryToRecord(summary);
      return { kind: "success", message: `已从 API 读取${record.name}。`, record };
    } catch (error) {
      return { kind: "error", message: "响应是成功状态，但 JSON 不符合页面约定。" };
    }
  }

  function render(view, refs) {
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
  }

  function mount(doc, fetchImpl) {
    const refs = {
      status: doc.querySelector("[data-view-status]"),
      content: doc.querySelector("[data-view-content]"),
      title: doc.querySelector('[data-field="title"]'),
      description: doc.querySelector('[data-field="description"]'),
      completedLessons: doc.querySelector('[data-field="completed-lessons"]'),
      hours: doc.querySelector('[data-field="hours"]'),
      currentStatus: doc.querySelector('[data-field="status"]'),
      nextMilestone: doc.querySelector('[data-field="next-milestone"]')
    };
    const buttons = Array.from(doc.querySelectorAll("[data-profile-id]"));
    if (!buttons.length || !fetchImpl || Object.values(refs).some((element) => !element)) return false;

    buttons.forEach(function (button) {
      button.addEventListener("click", async function () {
        const profileId = button.dataset.profileId;
        buttons.forEach(function (candidate) {
          candidate.setAttribute("aria-pressed", String(candidate === button));
          candidate.disabled = true;
        });
        render(loadingView(profileId), refs);
        const view = await fetchSummary(profileId, fetchImpl);
        render(view, refs);
        buttons.forEach(function (candidate) { candidate.disabled = false; });
      });
    });
    return true;
  }

  return { API_ROOT, loadingView, isSummary, summaryToRecord, fetchSummary, render, mount };
});
