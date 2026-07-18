(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.LearningDashboard = api;
  if (root.document) api.mount(root.document);
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const PROFILES = Object.freeze({
    xiaoma: Object.freeze({
      name: "小码",
      description: "正在学习 Python 与 Web，希望把练习做成可以展示的作品。",
      completedLessons: 7,
      hours: 6.5,
      status: "按计划推进",
      nextMilestone: "连接页面状态"
    }),
    afei: Object.freeze({
      name: "阿飞",
      description: "已经完成 Python 起步，正在补齐 Web 的浏览器基础。",
      completedLessons: 12,
      hours: 9,
      status: "本周已完成",
      nextMilestone: "连接本地 API"
    })
  });

  function getView(profileId) {
    if (profileId === "broken") {
      return { kind: "error", message: "模拟读取失败，请稍后重试。" };
    }
    const record = PROFILES[profileId];
    if (!record) return { kind: "empty", message: "没有找到这位学习者。" };
    return { kind: "success", message: `已显示${record.name}。`, record };
  }

  function loadingView(profileId) {
    return { kind: "loading", message: `正在读取 ${profileId}……` };
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

  function mount(doc, schedule) {
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
    if (!buttons.length || Object.values(refs).some((element) => !element)) return false;
    const defer = schedule || function (callback) { globalThis.setTimeout(callback, 250); };

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        const profileId = button.dataset.profileId;
        buttons.forEach(function (candidate) {
          candidate.setAttribute("aria-pressed", String(candidate === button));
        });
        render(loadingView(profileId), refs);
        defer(function () { render(getView(profileId), refs); });
      });
    });
    return true;
  }

  return { PROFILES, getView, loadingView, render, mount };
});
