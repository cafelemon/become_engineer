export type SessionState = { kind: "anonymous" } | { kind: "ready"; userId: string; csrf: string } | { kind: "forbidden" };
export function routeAfterResponse(status: number): SessionState["kind"] { return status === 401 ? "anonymous" : status === 403 ? "forbidden" : "ready"; }
export function logoutState(): SessionState { return { kind: "anonymous" }; }
