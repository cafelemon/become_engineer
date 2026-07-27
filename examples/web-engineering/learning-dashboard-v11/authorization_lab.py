"""Ownership and default-deny authorization laboratory."""
from __future__ import annotations

from dataclasses import dataclass

PERMISSIONS = {"learner": {"status:read", "session:write"}, "operator": {"diagnostic:run"}}

@dataclass(frozen=True)
class AuditEvent: subject: str; action: str; resource: str; result: str; request_id: str

class Authorizer:
    def __init__(self): self.events: list[AuditEvent] = []
    def allow(self, role: str, subject: str | None, action: str, owner: str | None, request_id: str) -> int:
        if subject is None: result, status = "unauthenticated", 401
        elif action not in PERMISSIONS.get(role, set()): result, status = "forbidden", 403
        elif owner is not None and owner != subject: result, status = "not_found", 404
        else: result, status = "allowed", 200
        self.events.append(AuditEvent(subject or "anonymous", action, owner or "diagnostic", result, request_id))
        return status

    def safe_log(self) -> list[dict[str, str]]:
        return [event.__dict__.copy() for event in self.events]
