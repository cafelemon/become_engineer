from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
import secrets
from types import MappingProxyType
from typing import Any, Mapping


LEARNER_ID_PATTERN = re.compile(r"learner-[0-9]{3}\Z")
IDEMPOTENCY_PATTERN = re.compile(r"idem_[a-z0-9]{6,32}\Z")


class ControlledWriteError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Principal:
    subject_id: str
    permissions: frozenset[str]


@dataclass(frozen=True)
class WriteCall:
    call_id: str
    name: str
    arguments: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "arguments", MappingProxyType(dict(self.arguments)))


@dataclass(frozen=True)
class ConfirmationGrant:
    grant_id: str
    subject_id: str
    call_id: str
    tool_name: str
    arguments_fingerprint: str
    expires_at: int


@dataclass(frozen=True)
class WriteResult:
    call_id: str
    tool_name: str
    status: str
    replayed: bool
    data: Mapping[str, Any] | None = None
    error_code: str | None = None

    def __post_init__(self) -> None:
        if self.data is not None:
            object.__setattr__(self, "data", MappingProxyType(dict(self.data)))


def arguments_fingerprint(arguments: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        dict(arguments), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ConfirmationAuthority:
    def __init__(self) -> None:
        self._nonce = secrets.token_hex(16)
        self._grants: dict[str, ConfirmationGrant] = {}
        self._consumed: set[str] = set()

    def issue(
        self,
        call: WriteCall,
        principal: Principal,
        *,
        now: int,
        human_approved: bool,
        ttl_seconds: int = 60,
    ) -> ConfirmationGrant:
        if not human_approved:
            raise ControlledWriteError(
                "confirmation_required", "a human must explicitly approve"
            )
        digest = hashlib.sha256(
            f"{self._nonce}:{principal.subject_id}:{call.call_id}:{now}".encode()
        ).hexdigest()[:20]
        grant = ConfirmationGrant(
            f"grant_{digest}",
            principal.subject_id,
            call.call_id,
            call.name,
            arguments_fingerprint(call.arguments),
            now + ttl_seconds,
        )
        self._grants[grant.grant_id] = grant
        return grant

    def consume(
        self,
        grant: ConfirmationGrant | None,
        call: WriteCall,
        principal: Principal,
        *,
        now: int,
    ) -> None:
        if grant is None:
            raise ControlledWriteError(
                "confirmation_required", "confirmation is missing"
            )
        stored = self._grants.get(grant.grant_id)
        if stored != grant or grant.grant_id in self._consumed:
            raise ControlledWriteError(
                "invalid_confirmation", "confirmation is unknown or already used"
            )
        if now > grant.expires_at:
            raise ControlledWriteError("confirmation_expired", "confirmation expired")
        expected = (
            principal.subject_id,
            call.call_id,
            call.name,
            arguments_fingerprint(call.arguments),
        )
        actual = (
            grant.subject_id,
            grant.call_id,
            grant.tool_name,
            grant.arguments_fingerprint,
        )
        if actual != expected:
            raise ControlledWriteError(
                "confirmation_mismatch", "confirmation is bound to another action"
            )
        self._consumed.add(grant.grant_id)


class LearningPlanStore:
    def __init__(self) -> None:
        self.goals: dict[str, int] = {}
        self.idempotency: dict[
            tuple[str, str, str], tuple[str, Mapping[str, Any]]
        ] = {}
        self.write_count = 0

    def replay_or_conflict(
        self, principal: Principal, call: WriteCall
    ) -> WriteResult | None:
        key = (
            principal.subject_id,
            call.name,
            str(call.arguments["idempotency_key"]),
        )
        existing = self.idempotency.get(key)
        if existing is None:
            return None
        fingerprint, data = existing
        if fingerprint != arguments_fingerprint(call.arguments):
            raise ControlledWriteError(
                "idempotency_conflict", "key was used with different arguments"
            )
        return WriteResult(call.call_id, call.name, "ok", True, data=data)

    def write(self, principal: Principal, call: WriteCall) -> Mapping[str, Any]:
        learner_id = str(call.arguments["learner_id"])
        weekly_minutes = int(call.arguments["weekly_minutes"])
        data = MappingProxyType(
            {"learner_id": learner_id, "weekly_minutes": weekly_minutes}
        )
        self.goals[learner_id] = weekly_minutes
        self.write_count += 1
        key = (
            principal.subject_id,
            call.name,
            str(call.arguments["idempotency_key"]),
        )
        self.idempotency[key] = (arguments_fingerprint(call.arguments), data)
        return data


class ControlledWriteExecutor:
    def __init__(
        self, store: LearningPlanStore, confirmations: ConfirmationAuthority
    ) -> None:
        self.store = store
        self.confirmations = confirmations

    def execute(
        self,
        call: WriteCall,
        principal: Principal,
        *,
        confirmation: ConfirmationGrant | None,
        now: int,
    ) -> WriteResult:
        try:
            self._validate_and_authorize(call, principal)
            replay = self.store.replay_or_conflict(principal, call)
            if replay is not None:
                return replay
            self.confirmations.consume(confirmation, call, principal, now=now)
            data = self.store.write(principal, call)
            return WriteResult(call.call_id, call.name, "ok", False, data=data)
        except ControlledWriteError as exc:
            return WriteResult(
                call.call_id, call.name, "error", False, error_code=exc.code
            )

    @staticmethod
    def _validate_and_authorize(call: WriteCall, principal: Principal) -> None:
        if call.name != "set_weekly_goal":
            raise ControlledWriteError("unknown_tool", "tool is not registered")
        if set(call.arguments) != {
            "learner_id",
            "weekly_minutes",
            "idempotency_key",
        }:
            raise ControlledWriteError("invalid_arguments", "fields are invalid")
        learner_id = call.arguments["learner_id"]
        minutes = call.arguments["weekly_minutes"]
        key = call.arguments["idempotency_key"]
        if type(learner_id) is not str or not LEARNER_ID_PATTERN.fullmatch(learner_id):
            raise ControlledWriteError("invalid_arguments", "learner_id is invalid")
        if type(minutes) is not int or not 30 <= minutes <= 600:
            raise ControlledWriteError("invalid_arguments", "weekly_minutes is invalid")
        if type(key) is not str or not IDEMPOTENCY_PATTERN.fullmatch(key):
            raise ControlledWriteError("invalid_arguments", "idempotency_key is invalid")
        if (
            "learning_plan:write" not in principal.permissions
            or principal.subject_id != learner_id
        ):
            raise ControlledWriteError("forbidden", "principal cannot write this plan")


def demo_call(**arguments: Any) -> WriteCall:
    payload = {
        "learner_id": "learner-001",
        "weekly_minutes": 180,
        "idempotency_key": "idem_week001",
    }
    payload.update(arguments)
    return WriteCall("call_write1", "set_weekly_goal", payload)


def fixed_report() -> str:
    principal = Principal("learner-001", frozenset({"learning_plan:write"}))
    store = LearningPlanStore()
    authority = ConfirmationAuthority()
    executor = ControlledWriteExecutor(store, authority)
    call = demo_call()
    denied = executor.execute(call, principal, confirmation=None, now=100)
    grant = authority.issue(
        call, principal, now=100, human_approved=True, ttl_seconds=60
    )
    written = executor.execute(call, principal, confirmation=grant, now=101)
    replay = executor.execute(
        WriteCall("call_write2", call.name, call.arguments),
        principal,
        confirmation=None,
        now=102,
    )
    return "\n".join(
        [
            "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
            "tool=name:set_weekly_goal,risk:write,permission:learning_plan:write,default:deny",
            f"unconfirmed=status:{denied.status},error:{denied.error_code},writes:0",
            f"confirmed=status:{written.status},minutes:{written.data['weekly_minutes']},replayed:{str(written.replayed).lower()}",
            f"retry=status:{replay.status},replayed:{str(replay.replayed).lower()},writes:{store.write_count}",
            "confirmation=human:true,bound-subject:true,bound-call:true,bound-tool:true,bound-arguments:true,expires:true,single-use:true",
            "idempotency=scoped-subject-tool-key:true,same-payload:replay,different-payload:conflict",
            "rejection=unknown-tool:true,invalid-arguments:true,forbidden:true,missing-confirmation:true,expired:true,mismatch:true,reused-grant:true,idempotency-conflict:true",
            "logs=grant:none,idempotency-key:none,arguments:none,call-id:allowed,tool-name:allowed,status:allowed,error-code:allowed",
            "invariants=validate-authorize-confirm-write,default-deny,write-once,replay-safe,no-model-confirmation,no-network",
        ]
    )


if __name__ == "__main__":
    print(fixed_report())
