"use strict";

let pyodide = null;
let loading = null;

self.addEventListener("message", function (event) {
  const data = event.data || {};
  if (data.type === "init") initialize();
  if (data.type === "run") runCode(String(data.code || ""));
});

function initialize() {
  if (pyodide) {
    self.postMessage({ type: "ready" });
    return;
  }
  if (loading) return;
  loading = (async function () {
    try {
      importScripts("https://cdn.jsdelivr.net/pyodide/v0.29.4/full/pyodide.js");
      pyodide = await loadPyodide({ indexURL: "https://cdn.jsdelivr.net/pyodide/v0.29.4/full/" });
      self.postMessage({ type: "ready" });
    } catch (error) {
      self.postMessage({ type: "error", message: "Pyodide 加载失败：" + String(error && error.message || error) });
    }
  })();
}

async function runCode(code) {
  if (!pyodide) {
    self.postMessage({ type: "error", message: "Python 运行时尚未就绪。" });
    return;
  }
  try {
    pyodide.globals.set("__be_sample_code", code);
    const proxy = await pyodide.runPythonAsync(`
import contextlib
import io
import traceback

_be_stdout = io.StringIO()
_be_stderr = io.StringIO()
_be_success = True
with contextlib.redirect_stdout(_be_stdout), contextlib.redirect_stderr(_be_stderr):
    try:
        exec(compile(__be_sample_code, "<浏览器样板>", "exec"), {})
    except BaseException:
        _be_success = False
        traceback.print_exc()
(_be_stdout.getvalue(), _be_stderr.getvalue(), _be_success)
`);
    const result = proxy.toJs();
    proxy.destroy();
    self.postMessage({ type: "result", stdout: result[0], stderr: result[1], success: result[2] });
  } catch (error) {
    self.postMessage({ type: "error", message: "运行失败：" + String(error && error.message || error) });
  } finally {
    try { pyodide.globals.delete("__be_sample_code"); } catch (_) { /* no-op */ }
  }
}
