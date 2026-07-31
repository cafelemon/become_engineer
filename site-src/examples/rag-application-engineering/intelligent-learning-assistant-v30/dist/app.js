const headers = { "Content-Type": "application/json", "X-Subject-ID": "learner-browser" };
const upload = document.querySelector("#upload");
const chat = document.querySelector("#chat");
const ingestion = document.querySelector("#ingestion-status");
const sourceDetail = document.querySelector("#source-detail");
const answerStatus = document.querySelector("#answer-status");
const retrievalDetail = document.querySelector("#retrieval-detail");
const citations = document.querySelector("#citations");
let sourceId = "", sessionId = "";
async function json(url, init = {}) { const response = await fetch(url, { ...init, headers: { ...headers, ...init.headers } }); if (!response.ok)
    throw new Error(`${response.status} ${await response.text()}`); return response.json(); }
upload.addEventListener("submit", async (event) => {
    event.preventDefault();
    ingestion.textContent = "正在接入…";
    const data = new FormData(upload);
    try {
        const source = await json("/api/knowledge-sources", { method: "POST", body: JSON.stringify({ name: data.get("name") }) });
        sourceId = source.source_id;
        const result = await json(`/api/knowledge-sources/${sourceId}/versions`, { method: "POST", body: JSON.stringify({ kind: "markdown", content: data.get("content") }) });
        ingestion.textContent = `索引作业 ${result.job.status}`;
        sourceDetail.textContent = JSON.stringify({ source, version: result.version, job: result.job }, null, 2);
    }
    catch (error) {
        ingestion.textContent = `接入失败：${String(error)}`;
        ingestion.focus();
    }
});
chat.addEventListener("submit", async (event) => {
    event.preventDefault();
    answerStatus.textContent = "正在检索…";
    const data = new FormData(chat);
    try {
        if (!sessionId) {
            sessionId = (await json("/api/chat/sessions", { method: "POST" })).session_id;
        }
        const debug = await json("/api/retrieval/debug", { method: "POST", body: JSON.stringify({ query: data.get("question") }) });
        const answer = await json(`/api/chat/sessions/${sessionId}/messages`, { method: "POST", body: JSON.stringify({ question: data.get("question") }) });
        answerStatus.textContent = answer.answer;
        retrievalDetail.textContent = JSON.stringify({ stages: debug.stages, context: answer.context_package, prompt_version: answer.prompt_version }, null, 2);
        citations.replaceChildren(...answer.citations.map((item) => { const li = document.createElement("li"); li.textContent = `${item.source_id} v${item.version} p${item.page} ${item.block_id} ${item.chunk_id}`; return li; }));
    }
    catch (error) {
        answerStatus.textContent = `回答失败：${String(error)}`;
        answerStatus.focus();
    }
});
export {};
