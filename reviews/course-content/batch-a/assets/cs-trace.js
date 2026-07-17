(function () {
  "use strict";

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(initDemos);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initDemos, { once: true });
  } else {
    initDemos();
  }

  function initDemos() {
    document.querySelectorAll("[data-scan-demo]").forEach(function (demo) {
      if (demo.dataset.initialized === "true") return;
      demo.dataset.initialized = "true";
      const values = String(demo.dataset.values || "").split(",").map(Number);
      const target = Number(demo.dataset.target);
      const cells = demo.querySelector("[data-scan-cells]");
      const count = demo.querySelector("[data-scan-count]");
      const message = demo.querySelector("[data-scan-message]");
      const previous = demo.querySelector("[data-scan-prev]");
      const next = demo.querySelector("[data-scan-next]");
      const reset = demo.querySelector("[data-scan-reset]");
      let position = -1;
      let stoppedAt = values.indexOf(target);
      if (stoppedAt < 0) stoppedAt = values.length - 1;

      values.forEach(function (value, index) {
        const cell = document.createElement("div");
        cell.className = "be-scan-demo__cell";
        cell.dataset.index = String(index);
        const label = document.createElement("span");
        label.textContent = "下标 " + index;
        const strong = document.createElement("strong");
        strong.textContent = String(value);
        cell.append(label, strong);
        cells.append(cell);
      });

      previous.addEventListener("click", function () {
        position = Math.max(-1, position - 1);
        render();
      });
      next.addEventListener("click", function () {
        position = Math.min(stoppedAt, position + 1);
        render();
      });
      reset.addEventListener("click", function () {
        position = -1;
        render();
        next.focus();
      });

      function render() {
        Array.from(cells.children).forEach(function (cell, index) {
          delete cell.dataset.state;
          if (position >= 0 && index < position) cell.dataset.state = "visited";
          if (index === position) cell.dataset.state = values[index] === target ? "found" : "current";
        });
        count.textContent = String(position + 1);
        previous.disabled = position < 0;
        next.disabled = position >= stoppedAt;
        if (position < 0) {
          message.textContent = "还没开始。先猜一猜要比较几次。";
        } else if (values[position] === target) {
          message.textContent = "第 " + (position + 1) + " 次看到 " + values[position] + "，和目标相等，找到了。";
        } else {
          message.textContent = "第 " + (position + 1) + " 次看到 " + values[position] + "，还不是目标，继续往后找。";
        }
      }

      render();
    });
  }
})();
