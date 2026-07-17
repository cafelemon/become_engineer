(function () {
  "use strict";

  const onReady = window.document$ && typeof window.document$.subscribe === "function"
    ? function (callback) { window.document$.subscribe(callback); }
    : function (callback) {
        if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", callback, { once: true });
        else callback();
      };

  onReady(function () {
    initApiDemo();
    initFixtureDemos();
    initTraceDemos();
  });

  function initApiDemo() {
    const root = document.querySelector("[data-api-demo]");
    if (!root || root.dataset.ready === "true") return;
    root.dataset.ready = "true";
    const result = root.querySelector("[data-api-result]");
    root.querySelectorAll("button[data-learner-id]").forEach(function (button) {
      button.addEventListener("click", async function () {
        const learnerId = button.dataset.learnerId;
        result.dataset.kind = "loading";
        result.replaceChildren(make("strong", "正在请求……"), make("p", "浏览器正在联系 127.0.0.1:8780。"));
        try {
          const response = await fetch("http://127.0.0.1:8780/api/learning-summary/" + encodeURIComponent(learnerId));
          const body = await response.json().catch(function () { return {}; });
          if (!response.ok) throw new Error(response.status + " " + (body.detail || "请求失败"));
          result.dataset.kind = "success";
          result.replaceChildren(
            make("strong", response.status + " · 已取得 " + body.learner_name + " 的学习报告"),
            make("pre", JSON.stringify(body, null, 2))
          );
        } catch (error) {
          result.dataset.kind = "error";
          result.replaceChildren(
            make("strong", "这次没有拿到数据"),
            make("p", error instanceof TypeError ? "本地 API 没有响应。先确认 Uvicorn 正在 8780 端口运行。" : error.message)
          );
        }
      });
    });
  }

  function initFixtureDemos() {
    document.querySelectorAll("[data-fixture-demo]").forEach(function (root) {
      if (root.dataset.ready === "true") return;
      root.dataset.ready = "true";
      const output = root.querySelector("[data-fixture-result]");
      const fixtures = JSON.parse(root.querySelector("script[type='application/json']").textContent);
      root.querySelectorAll("button[data-fixture]").forEach(function (button) {
        button.addEventListener("click", function () {
          const fixture = fixtures[button.dataset.fixture];
          output.replaceChildren(make("strong", fixture.title), make("p", fixture.message), make("pre", fixture.content));
        });
      });
    });
  }

  function initTraceDemos() {
    document.querySelectorAll("[data-trace-demo]").forEach(function (root) {
      if (root.dataset.ready === "true") return;
      const source = root.querySelector("script[type='application/json']");
      const stage = root.querySelector("[data-trace-stage]");
      const position = root.querySelector("[data-trace-position]");
      const previous = root.querySelector("[data-trace-previous]");
      const next = root.querySelector("[data-trace-next]");
      const reset = root.querySelector("[data-trace-reset]");
      if (!source || !stage || !position || !previous || !next || !reset) return;
      root.dataset.ready = "true";
      const steps = JSON.parse(source.textContent);
      let index = 0;
      function render() {
        const step = steps[index];
        stage.replaceChildren(make("strong", step.title), make("p", step.body), make("pre", step.code || ""));
        position.textContent = String(index + 1) + " / " + String(steps.length);
        previous.disabled = index === 0;
        next.disabled = index === steps.length - 1;
      }
      previous.addEventListener("click", function () { if (index > 0) index -= 1; render(); });
      next.addEventListener("click", function () { if (index < steps.length - 1) index += 1; render(); });
      reset.addEventListener("click", function () { index = 0; render(); });
      render();
    });
  }

  function make(tag, text) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    return node;
  }
})();
