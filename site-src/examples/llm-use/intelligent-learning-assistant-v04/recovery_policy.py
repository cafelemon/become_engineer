from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


RETRYABLE_CODES = frozenset({"rate_limited", "unavailable", "timeout"})
TERMINAL_CODES = frozenset({
    "completed",
    "refused",
    "invalid_request",
    "authentication_failed",
    "safety_blocked",
    "invalid_output",
    "missing_information",
})


@dataclass(frozen=True)
class AttemptOutcome:
    code: str
    latency_ms: int
    text: str | None = None

    def __post_init__(self) -> None:
        if self.code not in RETRYABLE_CODES | TERMINAL_CODES:
            raise ValueError(f"unknown outcome code: {self.code}")
        if self.latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")
        if self.code == "completed" and not self.text:
            raise ValueError("completed outcome requires text")
        if self.code != "completed" and self.text is not None:
            raise ValueError("only completed outcome may contain text")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int
    attempt_timeout_ms: int
    deadline_ms: int
    backoff_ms: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        if self.attempt_timeout_ms < 1 or self.deadline_ms < 1:
            raise ValueError("timeouts must be positive")
        if len(self.backoff_ms) < self.max_attempts - 1:
            raise ValueError("backoff schedule must cover every retry")
        if any(delay < 0 for delay in self.backoff_ms):
            raise ValueError("backoff values must be non-negative")


@dataclass(frozen=True)
class AttemptRecord:
    number: int
    timeout_ms: int
    outcome: str
    elapsed_ms: int
    next_backoff_ms: int | None


@dataclass(frozen=True)
class RecoveryResult:
    status: str
    terminal_code: str
    attempts: tuple[AttemptRecord, ...]
    elapsed_ms: int
    text: str | None = None


class Clock(Protocol):
    @property
    def now_ms(self) -> int: ...

    def advance(self, milliseconds: int) -> None: ...


class VirtualClock:
    def __init__(self) -> None:
        self._now_ms = 0

    @property
    def now_ms(self) -> int:
        return self._now_ms

    def advance(self, milliseconds: int) -> None:
        if milliseconds < 0:
            raise ValueError("cannot move clock backwards")
        self._now_ms += milliseconds


class ScriptedAdapter:
    def __init__(self, outcomes: Sequence[AttemptOutcome], clock: Clock) -> None:
        if not outcomes:
            raise ValueError("at least one outcome is required")
        self._outcomes = tuple(outcomes)
        self._clock = clock
        self.calls = 0

    def call(self, timeout_ms: int) -> AttemptOutcome:
        if self.calls >= len(self._outcomes):
            raise AssertionError("script exhausted: retry state machine called too often")
        planned = self._outcomes[self.calls]
        self.calls += 1
        if planned.latency_ms > timeout_ms:
            self._clock.advance(timeout_ms)
            return AttemptOutcome("timeout", timeout_ms)
        self._clock.advance(planned.latency_ms)
        return planned


def run_with_recovery(
    adapter: ScriptedAdapter,
    policy: RetryPolicy,
    clock: Clock,
) -> RecoveryResult:
    started_ms = clock.now_ms
    deadline_at = started_ms + policy.deadline_ms
    records: list[AttemptRecord] = []

    for number in range(1, policy.max_attempts + 1):
        remaining_ms = deadline_at - clock.now_ms
        if remaining_ms <= 0:
            return RecoveryResult(
                "failed", "deadline_exceeded", tuple(records), clock.now_ms - started_ms
            )
        timeout_ms = min(policy.attempt_timeout_ms, remaining_ms)
        outcome = adapter.call(timeout_ms)

        if outcome.code == "completed":
            records.append(AttemptRecord(
                number, timeout_ms, outcome.code, clock.now_ms - started_ms, None
            ))
            return RecoveryResult(
                "completed", "completed", tuple(records), clock.now_ms - started_ms, outcome.text
            )

        if outcome.code not in RETRYABLE_CODES:
            records.append(AttemptRecord(
                number, timeout_ms, outcome.code, clock.now_ms - started_ms, None
            ))
            return RecoveryResult(
                "failed", outcome.code, tuple(records), clock.now_ms - started_ms
            )

        if clock.now_ms >= deadline_at:
            records.append(AttemptRecord(
                number, timeout_ms, outcome.code, clock.now_ms - started_ms, None
            ))
            return RecoveryResult(
                "failed", "deadline_exceeded", tuple(records), clock.now_ms - started_ms
            )

        if number == policy.max_attempts:
            records.append(AttemptRecord(
                number, timeout_ms, outcome.code, clock.now_ms - started_ms, None
            ))
            return RecoveryResult(
                "failed", "attempt_budget_exhausted", tuple(records), clock.now_ms - started_ms
            )

        backoff_ms = policy.backoff_ms[number - 1]
        if clock.now_ms + backoff_ms >= deadline_at:
            records.append(AttemptRecord(
                number, timeout_ms, outcome.code, clock.now_ms - started_ms, None
            ))
            return RecoveryResult(
                "failed", "deadline_exceeded", tuple(records), clock.now_ms - started_ms
            )
        records.append(AttemptRecord(
            number, timeout_ms, outcome.code, clock.now_ms - started_ms, backoff_ms
        ))
        clock.advance(backoff_ms)

    raise AssertionError("unreachable")


def _codes(result: RecoveryResult) -> str:
    return ">".join(record.outcome for record in result.attempts)


def fixed_report() -> str:
    policy = RetryPolicy(3, 100, 500, (50, 100))

    transient_clock = VirtualClock()
    transient = run_with_recovery(
        ScriptedAdapter([
            AttemptOutcome("unavailable", 30),
            AttemptOutcome("rate_limited", 30),
            AttemptOutcome("completed", 40, "ready"),
        ], transient_clock),
        policy,
        transient_clock,
    )

    auth_clock = VirtualClock()
    auth = run_with_recovery(
        ScriptedAdapter([AttemptOutcome("authentication_failed", 20)], auth_clock),
        policy,
        auth_clock,
    )

    deadline_clock = VirtualClock()
    deadline = run_with_recovery(
        ScriptedAdapter([
            AttemptOutcome("unavailable", 80),
            AttemptOutcome("unavailable", 80),
        ], deadline_clock),
        RetryPolicy(3, 100, 200, (60, 60)),
        deadline_clock,
    )

    return "\n".join([
        "runtime=python:3.11+,dependencies:stdlib-only,network:disabled,clock:virtual",
        "taxonomy=retryable:rate_limited|unavailable|timeout",
        "taxonomy=terminal:refused|invalid_request|authentication_failed|safety_blocked|invalid_output|missing_information",
        f"transient=status:{transient.status},attempts:{len(transient.attempts)},codes:{_codes(transient)},elapsed_ms:{transient.elapsed_ms}",
        f"authentication=status:{auth.status},terminal:{auth.terminal_code},attempts:{len(auth.attempts)}",
        f"deadline=status:{deadline.status},terminal:{deadline.terminal_code},attempts:{len(deadline.attempts)},elapsed_ms:{deadline.elapsed_ms}",
        "budgets=attempt_timeout:per-call,deadline:whole-operation,max_attempts:hard-cap",
        "backoff=deterministic-for-test,production-jitter:recommended,retry-after:provider-contract",
        "logs=prompt:none,response:none,authorization:none,outcome-code:allowed,attempt:allowed",
        "invariants=retry-transient-only,never-past-deadline,never-unbounded,no-rag,no-tools",
    ])


if __name__ == "__main__":
    print(fixed_report())
