(function () {
  "use strict";

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(initRunners);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRunners, { once: true });
  } else {
    initRunners();
  }

  function initRunners() {
    const script = Array.from(document.scripts).find(function (item) {
      return /\/python-runner\.js(?:\?|$)/.test(item.src);
    });
    if (!script) return;
    const workerUrl = new URL("python-worker.js", script.src).href;

    document.querySelectorAll("[data-python-runner]").forEach(function (mount, index) {
      if (mount.dataset.initialized === "true") return;
      mount.dataset.initialized = "true";
      const sourceUrl = new URL(mount.dataset.pythonSource, document.baseURI).href;
      setupRunner(mount, sourceUrl, workerUrl, index);
    });
  }

  function setupRunner(mount, sourceUrl, workerUrl, index) {
    let original = "";
    let worker = null;
    let workerReady = false;
    let pendingRun = false;
    let runTimer = null;
    let loadTimer = null;

    const toolbar = document.createElement("div");
    toolbar.className = "be-python-runner__toolbar";
    const title = document.createElement("strong");
    title.textContent = "浏览器微型运行器";
    const status = document.createElement("span");
    status.className = "be-python-runner__status";
    status.textContent = "正在读取示例";
    toolbar.append(title, status);

    const textarea = document.createElement("textarea");
    textarea.id = "be-python-code-" + index;
    textarea.setAttribute("aria-label", "可编辑 Python 示例代码");
    textarea.spellcheck = false;

    const actions = document.createElement("div");
    actions.className = "be-python-runner__actions";
    const run = document.createElement("button");
    run.type = "button";
    run.textContent = "运行代码";
    run.disabled = true;
    const reset = document.createElement("button");
    reset.type = "button";
    reset.textContent = "恢复示例";
    reset.disabled = true;
    actions.append(run, reset);

    const output = document.createElement("pre");
    output.className = "be-python-runner__output";
    output.setAttribute("aria-live", "polite");
    output.textContent = "先猜一猜输出，再点击“运行代码”。";

    fetch(sourceUrl, { credentials: "same-origin" })
      .then(function (response) {
        if (!response.ok) throw new Error("示例代码请求失败: " + response.status);
        return response.text();
      })
      .then(function (code) {
        original = code.trimEnd() + "\n";
        textarea.value = original;
        run.disabled = false;
        reset.disabled = false;
        status.textContent = "代码只在这一页运行，不会自动保存";
        mount.dataset.ready = "true";
      })
      .catch(function () {
        status.textContent = "示例没能加载，请改用页面里的本地命令";
        output.dataset.kind = "error";
        output.textContent = "页面运行器暂时用不了，但上面的代码和本地运行方式仍然可以使用。";
      });

    mount.prepend(toolbar, textarea, actions, output);

    run.addEventListener("click", function () {
      output.dataset.kind = "";
      output.textContent = workerReady ? "正在运行……" : "第一次运行要先加载 Python（约 12MB），请稍等……";
      run.disabled = true;
      pendingRun = true;
      if (!worker) startWorker();
      else if (workerReady) execute();
    });

    reset.addEventListener("click", function () {
      textarea.value = original;
      output.dataset.kind = "";
      output.textContent = "示例已经恢复。想好输出后，再点一次运行。";
    });

    function startWorker() {
      worker = new Worker(workerUrl);
      loadTimer = window.setTimeout(function () {
        failWorker("Python 加载时间太久了。请检查网络，或者直接使用页面里的本地命令。");
      }, 30000);
      worker.addEventListener("message", function (event) {
        const data = event.data || {};
        if (data.type === "ready") {
          window.clearTimeout(loadTimer);
          workerReady = true;
          status.textContent = "Python 0.29.4 已准备好";
          if (pendingRun) execute();
        } else if (data.type === "result") {
          window.clearTimeout(runTimer);
          pendingRun = false;
          run.disabled = false;
          output.dataset.kind = data.success ? "success" : "error";
          output.textContent = (data.stdout || "") + (data.stderr || "") || "程序正常结束，没有输出。";
        } else if (data.type === "error") {
          window.clearTimeout(loadTimer);
          window.clearTimeout(runTimer);
          failWorker(data.message || "页面里没能运行成功，请改用本地命令。");
        }
      });
      worker.addEventListener("error", function () {
        failWorker("页面运行器加载失败。你仍然可以照着本地命令继续练习。");
      });
      worker.postMessage({ type: "init" });
    }

    function execute() {
      if (!worker || !workerReady) return;
      pendingRun = false;
      output.textContent = "正在运行……";
      worker.postMessage({ type: "run", code: textarea.value });
      runTimer = window.setTimeout(function () {
        if (worker) worker.terminate();
        worker = null;
        workerReady = false;
        run.disabled = false;
        output.dataset.kind = "error";
        output.textContent = "代码运行超过 3 秒，已经停止。检查一下是否写出了不会结束的循环。";
        status.textContent = "下次点击运行时会重新准备环境";
      }, 3000);
    }

    function failWorker(message) {
      if (worker) worker.terminate();
      worker = null;
      workerReady = false;
      pendingRun = false;
      run.disabled = false;
      output.dataset.kind = "error";
      output.textContent = message;
      status.textContent = "可以改用本地 Python 继续";
    }
  }
})();
