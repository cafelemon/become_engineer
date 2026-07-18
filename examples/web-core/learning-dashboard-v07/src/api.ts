import {
  isLearningSummary,
  isStudySessionPage,
  isStudySessionWriteResult,
  summaryToRecord,
  type PageState,
  type SessionListState,
  type WriteState
} from "./contracts.js";

const API_ROOT = "/api";

export function loadingState(profileId: string): PageState {
  return { kind: "loading", message: `正在读取 ${profileId} 的汇总……` };
}

export async function fetchSummary(
  profileId: string,
  fetchImpl: typeof fetch = fetch
): Promise<PageState> {
  let response: Response;
  try {
    response = await fetchImpl(`${API_ROOT}/learning-summary/${encodeURIComponent(profileId)}`, {
      headers: { Accept: "application/json" }
    });
  } catch {
    return { kind: "error", message: "连接不到本地 API。先确认 Uvicorn 还在运行。" };
  }

  if (response.status === 404) return { kind: "empty", message: "没有这位学习者。" };
  if (!response.ok) return { kind: "error", message: `API 返回 ${response.status}。` };

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    return { kind: "contract-error", message: "汇总接口返回的不是可读取 JSON。" };
  }
  if (!isLearningSummary(payload)) {
    return { kind: "contract-error", message: "汇总结果不符合 LearningSummary。" };
  }

  const record = summaryToRecord(payload);
  return { kind: "success", message: `已读取${record.name}。`, record };
}

export async function fetchSessionPage(
  learnerId: string,
  afterId = 0,
  fetchImpl: typeof fetch = fetch
): Promise<SessionListState> {
  const query = new URLSearchParams({ limit: "2", after_id: String(afterId) });
  let response: Response;
  try {
    response = await fetchImpl(
      `${API_ROOT}/learners/${encodeURIComponent(learnerId)}/study-sessions?${query}`,
      { headers: { Accept: "application/json" } }
    );
  } catch {
    return { kind: "error", message: "学习时段没有加载。先检查本地服务。" };
  }

  if (response.status === 404) return { kind: "error", message: "没有这位学习者。" };
  if (!response.ok) return { kind: "error", message: `列表接口返回 ${response.status}。` };

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    return { kind: "contract-error", message: "列表接口返回的不是可读取 JSON。" };
  }
  if (!isStudySessionPage(payload)) {
    return { kind: "contract-error", message: "列表结果不符合 StudySessionPage。" };
  }
  if (payload.items.length === 0) {
    return { kind: "empty", message: "后面没有更多学习时段。", page: payload };
  }
  return {
    kind: "success",
    message: `本页读取 ${payload.items.length} 条记录。`,
    page: payload
  };
}

export async function createStudySession(
  learnerId: string,
  idempotencyKey: string,
  fetchImpl: typeof fetch = fetch
): Promise<WriteState> {
  let response: Response;
  try {
    response = await fetchImpl(
      `${API_ROOT}/learners/${encodeURIComponent(learnerId)}/study-sessions`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          "Idempotency-Key": idempotencyKey
        },
        body: JSON.stringify({ hours: 1, note: "REST 与幂等练习" })
      }
    );
  } catch {
    return { kind: "error", message: "连接不到本地 API，这次请求没有完成。" };
  }

  if (response.status === 409) {
    return { kind: "error", message: "同一个幂等键不能改成另一份请求内容。" };
  }
  if (response.status === 422) {
    return { kind: "error", message: "请求头或学习时段没有通过校验。" };
  }
  if (!response.ok) {
    return { kind: "error", message: `写入接口返回 ${response.status}。` };
  }

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    return { kind: "contract-error", message: "写入接口返回的不是可读取 JSON。" };
  }
  if (!isStudySessionWriteResult(payload)) {
    return { kind: "contract-error", message: "写入结果不符合 StudySessionWriteResult。" };
  }

  return {
    kind: "saved",
    message: payload.replayed ? "重复请求命中了原记录，没有再插入。" : "新记录已创建。",
    result: payload,
    httpStatus: response.status
  };
}
