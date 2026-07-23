from __future__ import annotations
import json, uuid
from prometheus_client import Counter, generate_latest
HTTP_REQUESTS = Counter("dashboard_http_requests_total", "HTTP results", ["method", "status"])
def request_id() -> str: return uuid.uuid4().hex
def event(method: str, status: int, request: str) -> str:
    HTTP_REQUESTS.labels(method, str(status)).inc()
    return json.dumps({"event":"http_request","request_id":request,"method":method,"status":status,"duration_ms":0})

def metrics() -> bytes:
    return generate_latest()
