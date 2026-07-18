(function () {
  "use strict";

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(initCSDemos);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCSDemos, { once: true });
  } else {
    initCSDemos();
  }

  function initCSDemos() {
    initScanDemos();
    initGrowthDemos();
    initGridDemos();
    initBFSDemos();
  }

  function initScanDemos() {
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
          if (index === position) {
            cell.dataset.state = values[index] === target ? "found" : "current";
          }
        });
        count.textContent = String(position + 1);
        previous.disabled = position < 0;
        next.disabled = position >= stoppedAt;

        if (position < 0) {
          message.textContent = "还没开始。先猜一猜要比较几次。";
        } else if (values[position] === target) {
          message.textContent =
            "第 " + (position + 1) + " 次看到 " + values[position] +
            "，和目标相等，找到了。";
        } else {
          message.textContent =
            "第 " + (position + 1) + " 次看到 " + values[position] +
            "，还不是目标，继续往后找。";
        }
      }

      render();
    });
  }

  function initGrowthDemos() {
    document.querySelectorAll("[data-growth-demo]").forEach(function (demo) {
      if (demo.dataset.initialized === "true") return;
      demo.dataset.initialized = "true";

      const sizes = String(demo.dataset.sizes || "")
        .split(",")
        .map(Number)
        .filter(function (value) { return Number.isInteger(value) && value >= 0; });
      if (sizes.length === 0) return;

      const sizeText = demo.querySelector("[data-growth-size]");
      const changeText = demo.querySelector("[data-growth-change]");
      const message = demo.querySelector("[data-growth-message]");
      const previous = demo.querySelector("[data-growth-prev]");
      const next = demo.querySelector("[data-growth-next]");
      const reset = demo.querySelector("[data-growth-reset]");
      const maxSize = Math.max.apply(null, sizes);
      const maxPairs = pairCount(maxSize);
      let position = 0;

      previous.addEventListener("click", function () {
        position = Math.max(0, position - 1);
        render();
      });
      next.addEventListener("click", function () {
        position = Math.min(sizes.length - 1, position + 1);
        render();
      });
      reset.addEventListener("click", function () {
        position = 0;
        render();
        next.focus();
      });

      function render() {
        const size = sizes[position];
        const counts = {
          constant: size > 0 ? 1 : 0,
          linear: size,
          pairs: pairCount(size)
        };
        sizeText.textContent = String(size);
        changeText.textContent = position === 0
          ? "起点"
          : "n × " + formatRatio(size / sizes[position - 1]);

        Object.keys(counts).forEach(function (key) {
          const value = counts[key];
          const output = demo.querySelector('[data-growth-value="' + key + '"]');
          const bar = demo.querySelector('[data-growth-bar="' + key + '"]');
          output.textContent = String(value);
          const denominator = key === "pairs" ? maxPairs : maxSize;
          const percentage = denominator === 0 ? 0 : value / denominator * 100;
          bar.style.setProperty(
            "--be-growth-width",
            Math.max(value > 0 ? 2 : 0, percentage) + "%"
          );
        });

        previous.disabled = position === 0;
        next.disabled = position === sizes.length - 1;
        if (position === 0) {
          message.textContent = "先记住 1、4、6。下一组会把输入增加到 8 项。";
        } else {
          const previousSize = sizes[position - 1];
          const previousPairs = pairCount(previousSize);
          const pairRatio = previousPairs === 0 ? 0 : counts.pairs / previousPairs;
          message.textContent =
            "n 从 " + previousSize + " 变成 " + size +
            "：读取仍为 1，扫描变为 " + counts.linear +
            "，两两比较变为 " + counts.pairs +
            "（约为上一组的 " + pairRatio.toFixed(2) + " 倍）。";
        }
      }

      render();
    });
  }

  function pairCount(size) {
    return size * (size - 1) / 2;
  }

  function formatRatio(value) {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }

  function initGridDemos() {
    document.querySelectorAll("[data-grid-demo]").forEach(function (demo) {
      if (demo.dataset.initialized === "true") return;
      demo.dataset.initialized = "true";

      const rows = Number(demo.dataset.rows);
      const columns = Number(demo.dataset.columns);
      const values = String(demo.dataset.values || "").split(",").map(Number);
      const rowLabels = String(demo.dataset.rowLabels || "").split(",");
      const columnLabels = String(demo.dataset.columnLabels || "").split(",");
      const board = demo.querySelector("[data-grid-board]");
      const coordinate = demo.querySelector("[data-grid-coordinate]");
      const flatIndex = demo.querySelector("[data-grid-index]");
      const valueText = demo.querySelector("[data-grid-value]");
      const message = demo.querySelector("[data-grid-message]");
      const reset = demo.querySelector("[data-grid-reset]");

      if (!Number.isInteger(rows) || !Number.isInteger(columns) ||
          rows < 1 || columns < 1 || values.length !== rows * columns) {
        message.textContent = "网格数据不完整，请改用下方静态表核对。";
        return;
      }

      board.style.setProperty("--be-grid-columns", String(columns));
      values.forEach(function (value, index) {
        const row = Math.floor(index / columns);
        const column = index % columns;
        const button = document.createElement("button");
        button.type = "button";
        button.dataset.gridCell = "";
        button.dataset.row = String(row);
        button.dataset.column = String(column);
        button.dataset.index = String(index);
        const label = (rowLabels[row] || "第" + (row + 1) + "行") +
          " · " + (columnLabels[column] || "第" + (column + 1) + "列");
        button.setAttribute("aria-label", label + "，值 " + value);

        const small = document.createElement("small");
        small.textContent = label;
        const strong = document.createElement("strong");
        strong.textContent = String(value);
        const code = document.createElement("code");
        code.textContent = "(" + row + ", " + column + ")";
        button.append(small, strong, code);
        button.addEventListener("click", function () {
          selectCell(button, row, column, index, value, label);
        });
        board.append(button);
      });

      reset.addEventListener("click", function () {
        board.querySelectorAll("[data-grid-cell]").forEach(function (cell) {
          cell.removeAttribute("data-selected");
          cell.setAttribute("aria-pressed", "false");
        });
        coordinate.textContent = "（还没选择）";
        flatIndex.textContent = "—";
        valueText.textContent = "—";
        message.textContent = "先选一格。行列坐标从 0 开始。";
        const first = board.querySelector("[data-grid-cell]");
        if (first) first.focus();
      });

      function selectCell(button, row, column, index, value, label) {
        board.querySelectorAll("[data-grid-cell]").forEach(function (cell) {
          cell.removeAttribute("data-selected");
          cell.setAttribute("aria-pressed", "false");
        });
        button.dataset.selected = "true";
        button.setAttribute("aria-pressed", "true");
        coordinate.textContent = "(" + row + ", " + column + ")";
        flatIndex.textContent = String(index);
        valueText.textContent = String(value);
        message.textContent = label + "：" + row + " × " + columns +
          " + " + column + " = " + index + "，这里保存的值是 " + value + "。";
      }
    });
  }

  function initBFSDemos() {
    const frames = [
      { title: "先把 0 放进队列", queue: "队列：0", distance: "距离：0=0", parent: "父节点：0←无" },
      { title: "取出 0，发现 1 和 2", queue: "队列：1, 2", distance: "距离：1=1, 2=1", parent: "父节点：1←0, 2←0" },
      { title: "取出 1，第一次发现 3", queue: "队列：2, 3", distance: "距离：3=2", parent: "父节点：3←1" },
      { title: "取出 2，3 已经在队列里", queue: "队列：3", distance: "跳过重复发现 3", parent: "父节点仍是 3←1" },
      { title: "取出 3，发现 4", queue: "队列：4", distance: "距离：4=3", parent: "父节点：4←3" },
      { title: "沿父节点倒着走，再反转", queue: "4←3←1←0", distance: "路径：0→1→3→4", parent: "最少经过 3 条边" }
    ];

    document.querySelectorAll("[data-bfs-trace]").forEach(function (demo) {
      if (demo.dataset.initialized === "true") return;
      demo.dataset.initialized = "true";
      const title = demo.querySelector("[data-bfs-title]");
      const queue = demo.querySelector("[data-bfs-queue]");
      const distance = demo.querySelector("[data-bfs-distance]");
      const parent = demo.querySelector("[data-bfs-parent]");
      const position = demo.querySelector("[data-bfs-position]");
      const previous = demo.querySelector("[data-bfs-prev]");
      const next = demo.querySelector("[data-bfs-next]");
      const reset = demo.querySelector("[data-bfs-reset]");
      let index = 0;

      previous.addEventListener("click", function () { index = Math.max(0, index - 1); render(); });
      next.addEventListener("click", function () { index = Math.min(frames.length - 1, index + 1); render(); });
      reset.addEventListener("click", function () { index = 0; render(); next.focus(); });

      function render() {
        const frame = frames[index];
        title.textContent = frame.title;
        queue.textContent = frame.queue;
        distance.textContent = frame.distance;
        parent.textContent = frame.parent;
        position.textContent = (index + 1) + " / " + frames.length;
        previous.disabled = index === 0;
        next.disabled = index === frames.length - 1;
      }
      render();
    });
  }
})();
