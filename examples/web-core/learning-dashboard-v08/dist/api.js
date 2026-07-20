import { isLearningSummary, isRecordValue, isStudySessionPage, isStudySessionWriteResult, summaryToRecord } from "./contracts.js";
const API_ROOT = "/api";
export function loadingState(profileId) {
    return { kind: "loading", message: `正在读取 ${profileId} 的汇总……` };
}
export async function fetchSummary(profileId, fetchImpl = fetch) {
    let response;
    try {
        response = await fetchImpl(`${API_ROOT}/learning-summary/${encodeURIComponent(profileId)}`, {
            headers: { Accept: "application/json" }
        });
    }
    catch {
        return { kind: "error", message: "连接不到本地 API。先确认 Uvicorn 还在运行。" };
    }
    if (response.status === 404)
        return { kind: "empty", message: "没有这位学习者。" };
    if (!response.ok)
        return { kind: "error", message: `API 返回 ${response.status}。` };
    let payload;
    try {
        payload = await response.json();
    }
    catch {
        return { kind: "contract-error", message: "汇总接口返回的不是可读取 JSON。" };
    }
    if (!isLearningSummary(payload)) {
        return { kind: "contract-error", message: "汇总结果不符合 LearningSummary。" };
    }
    const record = summaryToRecord(payload);
    return { kind: "success", message: `已读取${record.name}。`, record };
}
export async function fetchSessionPage(learnerId, afterId = 0, fetchImpl = fetch) {
    const query = new URLSearchParams({ limit: "50", after_id: String(afterId) });
    let response;
    try {
        response = await fetchImpl(`${API_ROOT}/learners/${encodeURIComponent(learnerId)}/study-sessions?${query}`, { headers: { Accept: "application/json" } });
    }
    catch {
        return { kind: "error", message: "学习时段没有加载。先检查本地服务。" };
    }
    if (response.status === 404)
        return { kind: "error", message: "没有这位学习者。" };
    if (!response.ok)
        return { kind: "error", message: `列表接口返回 ${response.status}。` };
    let payload;
    try {
        payload = await response.json();
    }
    catch {
        return { kind: "contract-error", message: "列表接口返回的不是可读取 JSON。" };
    }
    if (!isStudySessionPage(payload)) {
        return { kind: "contract-error", message: "列表结果不符合 StudySessionPage。" };
    }
    if (payload.items.length === 0) {
        return { kind: "empty", message: "还没有学习时段。", page: payload };
    }
    return {
        kind: "success",
        message: `已从服务器读取 ${payload.items.length} 条记录。`,
        page: payload
    };
}
function fieldMessage(field, errorType, fallback) {
    if (field === "hours") {
        if (errorType.includes("multiple_of"))
            return "小时数需要按 0.25 递增。";
        return "服务器要求小时数大于 0、不超过 24。";
    }
    if (errorType.includes("too_long"))
        return "服务器要求备注不超过 200 个字符。";
    if (errorType.includes("too_short"))
        return "服务器要求备注至少 2 个字符。";
    if (errorType.includes("value_error"))
        return "备注不能只包含空格。";
    return fallback;
}
export function serverFieldErrors(payload) {
    if (!isRecordValue(payload) || !Array.isArray(payload.detail))
        return {};
    const errors = {};
    for (const item of payload.detail) {
        if (!isRecordValue(item) || !Array.isArray(item.loc) || typeof item.msg !== "string") {
            continue;
        }
        const fieldValue = item.loc.at(-1);
        if (fieldValue !== "hours" && fieldValue !== "note")
            continue;
        const field = fieldValue;
        const errorType = typeof item.type === "string" ? item.type : "";
        errors[field] = fieldMessage(field, errorType, item.msg);
    }
    return errors;
}
export async function createStudySession(learnerId, draft, idempotencyKey, fetchImpl = fetch) {
    let response;
    try {
        response = await fetchImpl(`${API_ROOT}/learners/${encodeURIComponent(learnerId)}/study-sessions`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
                "Idempotency-Key": idempotencyKey
            },
            body: JSON.stringify(draft)
        });
    }
    catch {
        return {
            kind: "network-error",
            message: "没有收到服务器响应。表单还在，原样重试会继续使用同一个请求键。"
        };
    }
    let payload = null;
    if (response.status !== 204) {
        try {
            payload = await response.json();
        }
        catch {
            return { kind: "contract-error", message: "服务器返回的不是可读取 JSON。" };
        }
    }
    if (response.status === 422) {
        const errors = serverFieldErrors(payload);
        if (Object.keys(errors).length > 0) {
            return { kind: "field-error", message: "服务器没有接受这次输入。", errors };
        }
        return { kind: "server-error", message: "请求没有通过服务器校验。" };
    }
    if (response.status === 409) {
        return { kind: "server-error", message: "请求键对应的内容发生了变化，请重新填写后再提交。" };
    }
    if (!response.ok) {
        return { kind: "server-error", message: `服务器返回 ${response.status}，表单内容没有清空。` };
    }
    if (!isStudySessionWriteResult(payload)) {
        return { kind: "contract-error", message: "写入结果不符合 StudySessionWriteResult。" };
    }
    return {
        kind: "saved",
        message: payload.replayed ? "服务器找回了刚才那次保存，没有重复新增。" : "学习时段已保存。",
        result: payload,
        httpStatus: response.status
    };
}
