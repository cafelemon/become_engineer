const headers = { "Content-Type": "application/json", "X-Subject-ID": "browser-learner", "X-Role": "learner" };
const form = document.querySelector("#run-form");
const status = document.querySelector("#run-status");
const trace = document.querySelector("#trace");
const approve = document.querySelector("#approve");
let runId = "", approvalId = "";
async function json(url, init = {}) { const response = await fetch(url, { ...init, headers: { ...headers, ...init.headers } }); if (!response.ok)
    throw new Error(`${response.status} ${await response.text()}`); return response.json(); }
form.addEventListener("submit", async (event) => { event.preventDefault(); const data = new FormData(form); try {
    const run = await json("/api/agent-runs", { method: "POST", body: JSON.stringify({ goal: data.get("goal") }) });
    runId = run.run_id;
    approvalId = run.approval_id;
    status.textContent = `运行 ${run.state}`;
    trace.textContent = JSON.stringify({ run_id: run.run_id, steps: run.steps, content_boundary: run.content_boundary }, null, 2);
    approve.disabled = false;
}
catch (error) {
    status.textContent = String(error);
} });
approve.addEventListener("click", async () => { const result = await json(`/api/approval-requests/${approvalId}/decision`, { method: "POST", body: JSON.stringify({ decision: "approve" }) }); const run = await json(`/api/agent-runs/${runId}`); status.textContent = `审批 ${result.status}`; trace.textContent = JSON.stringify({ run_id: run.run_id, state: run.state, steps: run.steps }, null, 2); approve.disabled = true; });
export {};
