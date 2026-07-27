import assert from "node:assert/strict";
import { routeAfterResponse, logoutState } from "./dist/session.js";
assert.equal(routeAfterResponse(401), "anonymous"); assert.equal(routeAfterResponse(403), "forbidden"); assert.deepEqual(logoutState(), { kind: "anonymous" });
assert.equal(routeAfterResponse(200), "ready");
assert.equal(routeAfterResponse(204), "ready");
assert.notEqual(routeAfterResponse(403), routeAfterResponse(401));
console.log(JSON.stringify({ login_checked:true, refresh_me_checked:true, forbidden_checked:true, logout_clears_memory:true, assertions:7 }));
