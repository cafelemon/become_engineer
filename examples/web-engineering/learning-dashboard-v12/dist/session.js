export function routeAfterResponse(status) { return status === 401 ? "anonymous" : status === 403 ? "forbidden" : "ready"; }
export function logoutState() { return { kind: "anonymous" }; }
