import {
  isLearningSummary,
  summaryToRecord,
  type PageState
} from "./contracts.js";

const API_ROOT = "/api";

export function loadingState(profileId: string): PageState {
  return { kind: "loading", message: `正在读取 ${profileId}……` };
}

export function endpointFor(profileId: string): string {
  if (profileId === "unavailable") return `${API_ROOT}/demo-unavailable`;
  if (profileId === "contract-drift") return `${API_ROOT}/demo-contract-drift`;
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
    return { kind: "empty", message: "API 正常响应，但没有这位学习者。" };
  }
  if (response.status === 422) {
    return { kind: "error", message: "学习者 ID 没通过接口校验。" };
  }
  if (!response.ok) {
    return { kind: "error", message: `API 返回 ${response.status}，页面保留原来的内容。` };
  }

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    return { kind: "contract-error", message: "接口返回了 200，但正文不是可读取的 JSON。" };
  }

  if (!isLearningSummary(payload)) {
    return {
      kind: "contract-error",
      message: "接口返回了 200，但字段或类型不符合 LearningSummary。"
    };
  }

  const record = summaryToRecord(payload);
  return { kind: "success", message: `已读取${record.name}。`, record };
}
