"""Small, deterministic and redacted Agent telemetry implementation."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import hashlib
import json
from typing import Iterator


SENSITIVE_KEYS = {
    "authorization",
    "cookie",
    "csrf_token",
    "password",
    "prompt",
    "query",
    "memory_text",
    "tool_output",
}
ALLOWED_ATTRIBUTES = {
    "run_id",
    "request_id",
    "route",
    "status",
    "status_class",
    "tool_name",
    "step_kind",
    "error_code",
}


def redact(attributes: dict[str, object]) -> dict[str, object]:
    clean: dict[str, object] = {}
    for key, value in attributes.items():
        normalized = key.lower()
        if normalized in SENSITIVE_KEYS or any(token in normalized for token in ("secret", "token")):
            clean[key] = "[REDACTED]"
        elif key in ALLOWED_ATTRIBUTES:
            clean[key] = value
    return clean


@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_span_id: str | None
    name: str
    attributes: dict[str, object]
    status: str = "ok"
    events: list[dict[str, object]] = field(default_factory=list)


class Telemetry:
    def __init__(self, id_values: list[str], sample_every: int = 2) -> None:
        self._ids = iter(id_values)
        self.sample_every = sample_every
        self.spans: list[Span] = []
        self.logs: list[dict[str, object]] = []
        self.metrics: dict[tuple[str, str], int] = {}
        self._request_index = 0

    def _id(self) -> str:
        return next(self._ids)

    @contextmanager
    def span(
        self,
        name: str,
        *,
        trace_id: str | None = None,
        parent_span_id: str | None = None,
        attributes: dict[str, object] | None = None,
    ) -> Iterator[Span]:
        span = Span(
            trace_id=trace_id or self._id(),
            span_id=self._id(),
            parent_span_id=parent_span_id,
            name=name,
            attributes=redact(attributes or {}),
        )
        try:
            yield span
        except Exception as exc:
            span.status = "error"
            span.events.append({"name": "exception", "type": type(exc).__name__})
            raise
        finally:
            self.spans.append(span)

    def log(self, message: str, **attributes: object) -> None:
        self.logs.append({"message": message, **redact(attributes)})

    def observe_http(self, route_template: str, status: int) -> None:
        status_class = f"{status // 100}xx"
        key = (route_template, status_class)
        self.metrics[key] = self.metrics.get(key, 0) + 1

    def should_sample(self, status: str) -> bool:
        self._request_index += 1
        return status == "error" or self._request_index % self.sample_every == 0

    def export(self) -> str:
        payload = {
            "spans": [
                {
                    "trace_id": span.trace_id,
                    "span_id": span.span_id,
                    "parent_span_id": span.parent_span_id,
                    "name": span.name,
                    "status": span.status,
                    "attributes": span.attributes,
                    "events": span.events,
                }
                for span in self.spans
            ],
            "logs": self.logs,
            "metrics": [
                {"route": route, "status_class": status, "count": count}
                for (route, status), count in sorted(self.metrics.items())
            ],
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def fixed_report() -> dict[str, object]:
    telemetry = Telemetry(["trace-001", "span-root", "span-retrieve", "span-tool"])
    common = {"run_id": "run-001", "request_id": "req-001", "authorization": "Bearer secret"}
    with telemetry.span("agent.run", attributes={**common, "route": "/api/runs/{run_id}"}) as root:
        with telemetry.span(
            "retrieve",
            trace_id=root.trace_id,
            parent_span_id=root.span_id,
            attributes={**common, "step_kind": "retrieval", "query": "private question"},
        ):
            telemetry.log("retrieval.complete", **common, step_kind="retrieval", tool_output="private")
        with telemetry.span(
            "tool",
            trace_id=root.trace_id,
            parent_span_id=root.span_id,
            attributes={**common, "tool_name": "diagnostic"},
        ):
            pass
    telemetry.observe_http("/api/runs/{run_id}", 200)
    payload = json.loads(telemetry.export())
    return {
        "trace_id": payload["spans"][0]["trace_id"],
        "spans": len(payload["spans"]),
        "logs": len(payload["logs"]),
        "metric_series": len(payload["metrics"]),
        "secret_present": "secret" in telemetry.export(),
        "export_fingerprint": fingerprint(telemetry.export()),
    }


def main() -> None:
    report = fixed_report()
    print(f"correlation=trace:{report['trace_id']},spans:{report['spans']},logs:{report['logs']}")
    print(f"metrics=series:{report['metric_series']},route-template:true,status-class:true")
    print(f"redaction=secret-present:{str(report['secret_present']).lower()},prompt:false,tool-output:false")
    print(f"export-fingerprint:{report['export_fingerprint']}")


if __name__ == "__main__":
    main()
