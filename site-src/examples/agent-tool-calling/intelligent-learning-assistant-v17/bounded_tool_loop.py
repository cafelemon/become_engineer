from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class LoopLimits:
    max_rounds: int = 3
    max_tool_calls: int = 4
    deadline_ms: int = 100
    max_same_signature: int = 1


@dataclass(frozen=True)
class ToolCall:
    call_id: str
    name: str
    arguments: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "arguments", MappingProxyType(dict(self.arguments)))

    def signature(self) -> str:
        canonical = json.dumps(
            {"name": self.name, "arguments": dict(self.arguments)},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ModelEvent:
    kind: str
    elapsed_ms: int = 0
    calls: tuple[ToolCall, ...] = ()
    text: str | None = None


@dataclass(frozen=True)
class ToolObservation:
    call_id: str
    tool_name: str
    status: str
    error_code: str | None = None


@dataclass(frozen=True)
class RunResult:
    status: str
    rounds: int
    tool_calls: int
    elapsed_ms: int
    final_text: str | None
    trace: tuple[str, ...]


class ScriptedModel:
    def __init__(self, events: Sequence[ModelEvent]) -> None:
        self.events = tuple(events)
        self.index = 0

    def next(self, observations: Sequence[ToolObservation]) -> ModelEvent:
        del observations
        if self.index >= len(self.events):
            return ModelEvent("refused", text="script exhausted")
        event = self.events[self.index]
        self.index += 1
        return event


class ScriptedTools:
    def __init__(self, failures: Mapping[str, str] | None = None) -> None:
        self.failures = dict(failures or {})
        self.executed: list[str] = []

    def execute(self, call: ToolCall) -> ToolObservation:
        self.executed.append(call.call_id)
        error = self.failures.get(call.call_id)
        if error:
            return ToolObservation(call.call_id, call.name, "error", error)
        return ToolObservation(call.call_id, call.name, "ok")


class BoundedToolLoop:
    TERMINAL = {
        "completed",
        "needs_input",
        "refused",
        "tool_error",
        "round_budget_exceeded",
        "call_budget_exceeded",
        "deadline_exceeded",
        "cycle_detected",
        "protocol_error",
    }

    def __init__(self, limits: LoopLimits = LoopLimits()) -> None:
        if (
            limits.max_rounds < 1
            or limits.max_tool_calls < 1
            or limits.deadline_ms < 1
            or limits.max_same_signature < 1
        ):
            raise ValueError("all limits must be positive")
        self.limits = limits

    def run(self, model: ScriptedModel, tools: ScriptedTools) -> RunResult:
        rounds = 0
        tool_calls = 0
        elapsed = 0
        observations: list[ToolObservation] = []
        signatures: dict[str, int] = {}
        seen_call_ids: set[str] = set()
        trace: list[str] = ["state:start"]

        def stop(status: str, text: str | None = None) -> RunResult:
            trace.append(f"stop:{status}")
            return RunResult(
                status, rounds, tool_calls, elapsed, text, tuple(trace)
            )

        while True:
            if rounds >= self.limits.max_rounds:
                return stop("round_budget_exceeded")
            if elapsed >= self.limits.deadline_ms:
                return stop("deadline_exceeded")

            event = model.next(tuple(observations))
            rounds += 1
            elapsed += event.elapsed_ms
            trace.append(f"round:{rounds}:model:{event.kind}")
            if elapsed > self.limits.deadline_ms:
                return stop("deadline_exceeded")

            if event.kind == "final":
                if event.calls:
                    return stop("protocol_error")
                return stop("completed", event.text)
            if event.kind == "needs_input":
                return stop("needs_input")
            if event.kind == "refused":
                return stop("refused")
            if event.kind != "tool_calls" or not event.calls:
                return stop("protocol_error")
            if tool_calls + len(event.calls) > self.limits.max_tool_calls:
                return stop("call_budget_exceeded")

            event_ids = [call.call_id for call in event.calls]
            if len(set(event_ids)) != len(event_ids) or seen_call_ids.intersection(
                event_ids
            ):
                return stop("protocol_error")

            for call in event.calls:
                signature = call.signature()
                count = signatures.get(signature, 0)
                if count >= self.limits.max_same_signature:
                    return stop("cycle_detected")
                signatures[signature] = count + 1
                seen_call_ids.add(call.call_id)
                observation = tools.execute(call)
                tool_calls += 1
                observations.append(observation)
                trace.append(
                    f"tool:{call.call_id}:{observation.status}"
                    + (
                        f":{observation.error_code}"
                        if observation.error_code is not None
                        else ""
                    )
                )
                if observation.status != "ok":
                    return stop("tool_error")


def call(call_id: str = "call_status", **arguments: Any) -> ToolCall:
    payload = {"learner_id": "learner-001"}
    payload.update(arguments)
    return ToolCall(call_id, "get_learning_status", payload)


def run_script(
    events: Sequence[ModelEvent],
    *,
    limits: LoopLimits = LoopLimits(),
    failures: Mapping[str, str] | None = None,
) -> tuple[RunResult, ScriptedTools]:
    tools = ScriptedTools(failures)
    result = BoundedToolLoop(limits).run(ScriptedModel(events), tools)
    return result, tools


def fixed_report() -> str:
    completed, _ = run_script(
        [
            ModelEvent("tool_calls", elapsed_ms=10, calls=(call(),)),
            ModelEvent("final", elapsed_ms=5, text="status ready"),
        ]
    )
    needs_input, _ = run_script([ModelEvent("needs_input", elapsed_ms=2)])
    refused, _ = run_script([ModelEvent("refused", elapsed_ms=2)])
    tool_error, _ = run_script(
        [ModelEvent("tool_calls", calls=(call(),))],
        failures={"call_status": "tool_unavailable"},
    )
    over_calls, over_call_tools = run_script(
        [
            ModelEvent(
                "tool_calls",
                calls=tuple(call(f"call_{index}", slot=index) for index in range(5)),
            )
        ]
    )
    deadline, deadline_tools = run_script(
        [ModelEvent("tool_calls", elapsed_ms=101, calls=(call(),))]
    )
    cycle, cycle_tools = run_script(
        [
            ModelEvent("tool_calls", calls=(call("call_first"),)),
            ModelEvent("tool_calls", calls=(call("call_second"),)),
        ]
    )
    return "\n".join(
        [
            "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
            "limits=max-rounds:3,max-tool-calls:4,deadline-ms:100,max-same-signature:1",
            f"completed=status:{completed.status},rounds:{completed.rounds},tool-calls:{completed.tool_calls},elapsed-ms:{completed.elapsed_ms}",
            f"branches=needs-input:{needs_input.status},refused:{refused.status},tool-error:{tool_error.status}",
            f"budgets=call-status:{over_calls.status},calls-executed:{len(over_call_tools.executed)},deadline-status:{deadline.status},deadline-calls:{len(deadline_tools.executed)}",
            f"cycle=status:{cycle.status},calls-executed:{len(cycle_tools.executed)},repeat-second-executed:false",
            "termination=completed,needs_input,refused,tool_error,round_budget_exceeded,call_budget_exceeded,deadline_exceeded,cycle_detected,protocol_error",
            "trace=allowlisted-events-only,user-text:none,arguments:none,tool-data:none",
            "invariants=application-owned-state,check-before-execute,monotonic-budgets,explicit-terminal,repeat-detection,no-unbounded-retry,no-network",
        ]
    )


if __name__ == "__main__":
    print(fixed_report())
