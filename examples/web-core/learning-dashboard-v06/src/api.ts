import {
  isLearningSummary,
  isStudySessionCreated,
  summaryToRecord,
  type PageState,
  type SaveState
} from "./contracts.js";

const API_ROOT = "/api";

export function loadingState(profileId: string): PageState {
  return { kind: "loading", message: `正在从 SQLite 读取 ${profileId}……` };
}

export function endpointFor(profileId: string): string {
  if (profileId === "unavailable") return `${API_ROOT}/demo-unavailable`;
  return `${API_ROOT}/learning-summary/${encodeURIComponent(profileId)}`;
}

export async function fetchSummary(
  profileId: string,
  fetchImpl: typeof fetch = fetch
): Promise<PageState> {
  let response: Response;

  try {
    response = await fetchImpl(endpointFor(profileId), {
      headers: { Accept: "application/json" }
    });
  } catch {
    return { kind: "error", message: "连接不到本地 API。先确认 Uvicorn 还在运行。" };
  }

  if (response.status === 404) {
    return { kind: "empty", message: "数据库可以读取，但没有这位学习者。" };
  }
  if (response.status === 422) {
    return { kind: "error", message: "学习者 ID 没通过接口校验。" };
  }
  if (!response.ok) {
    return { kind: "error", message: `API 返回 ${response.status}，页面没有改动旧数据。` };
  }

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    return { kind: "contract-error", message: "接口返回成功，但正文不是可读取的 JSON。" };
  }

  if (!isLearningSummary(payload)) {
    return { kind: "contract-error", message: "数据库结果没有满足 LearningSummary 契约。" };
  }

  const record = summaryToRecord(payload);
  return { kind: "success", message: `已从 SQLite 读取${record.name}。`, record };
}

export async function saveStudySession(
  learnerId: string,
  hours: number,
  note: string,
  fetchImpl: typeof fetch = fetch
): Promise<SaveState> {
  let response: Response;

  try {
    response = await fetchImpl(`${API_ROOT}/study-sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ learner_id: learnerId, hours, note })
    });
  } catch {
    return { kind: "error", message: "连接不到本地 API，这次学习时段没有保存。" };
  }

  if (response.status === 404) {
    return { kind: "error", message: "没有找到这位学习者，学习时段没有保存。" };
  }
  if (response.status === 422) {
    return { kind: "error", message: "小时数或备注没有通过校验。" };
  }
  if (!response.ok) {
    return { kind: "error", message: `API 返回 ${response.status}，事务已经回滚。` };
  }

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    return { kind: "contract-error", message: "保存接口返回了无法读取的 JSON。" };
  }

  if (!isStudySessionCreated(payload)) {
    return { kind: "contract-error", message: "保存接口的响应不符合 StudySessionCreated。" };
  }

  return {
    kind: "saved",
    message: `已保存 ${payload.hours} 小时；现在重启服务，记录仍然会在。`,
    session: payload
  };
}
