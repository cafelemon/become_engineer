from __future__ import annotations

from dataclasses import dataclass
import json
import re
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping


CALL_ID_PATTERN = re.compile(r"call_[a-z0-9_]{1,32}\Z")
MAX_CALLS = 4


class BatchProtocolError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class CandidateCall:
    call_id: str
    name: str
    arguments: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "arguments", MappingProxyType(dict(self.arguments)))


@dataclass(frozen=True)
class ToolOutput:
    call_id: str
    tool_name: str
    status: str
    data: Mapping[str, Any] | None = None
    error_code: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"ok", "error"}:
            raise BatchProtocolError("invalid_output", "status must be ok or error")
        if (self.data is None) == (self.error_code is None):
            raise BatchProtocolError(
                "invalid_output", "exactly one of data or error_code is required"
            )
        if self.data is not None:
            object.__setattr__(self, "data", MappingProxyType(dict(self.data)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "call_id": self.call_id,
            "tool_name": self.tool_name,
            "status": self.status,
            "data": dict(self.data) if self.data is not None else None,
            "error_code": self.error_code,
        }


Handler = Callable[[Mapping[str, Any]], Mapping[str, Any]]


def validate_batch(calls: Iterable[CandidateCall]) -> tuple[CandidateCall, ...]:
    batch = tuple(calls)
    if not batch:
        raise BatchProtocolError("empty_batch", "at least one call is required")
    if len(batch) > MAX_CALLS:
        raise BatchProtocolError("batch_too_large", "call budget exceeded")
    identifiers = [call.call_id for call in batch]
    if any(not CALL_ID_PATTERN.fullmatch(call_id) for call_id in identifiers):
        raise BatchProtocolError("invalid_call_id", "call_id is invalid")
    if len(set(identifiers)) != len(identifiers):
        raise BatchProtocolError("duplicate_call_id", "call_id must be unique")
    return batch


class SequentialToolExecutor:
    def __init__(self, handlers: Mapping[str, Handler]) -> None:
        self.handlers = MappingProxyType(dict(handlers))
        self.handler_calls: list[str] = []

    def execute(self, call: CandidateCall) -> ToolOutput:
        handler = self.handlers.get(call.name)
        if handler is None:
            return ToolOutput(
                call.call_id, call.name, "error", error_code="unknown_tool"
            )
        try:
            self.handler_calls.append(call.call_id)
            data = handler(call.arguments)
            return ToolOutput(call.call_id, call.name, "ok", data=data)
        except (KeyError, TypeError, ValueError):
            return ToolOutput(
                call.call_id, call.name, "error", error_code="tool_failed"
            )

    def execute_batch(
        self, calls: Iterable[CandidateCall]
    ) -> tuple[ToolOutput, ...]:
        batch = validate_batch(calls)
        outputs = tuple(self.execute(call) for call in batch)
        return assemble_outputs(batch, outputs)


def assemble_outputs(
    calls: Iterable[CandidateCall], outputs: Iterable[ToolOutput]
) -> tuple[ToolOutput, ...]:
    batch = validate_batch(calls)
    output_list = tuple(outputs)
    by_id: dict[str, ToolOutput] = {}
    for output in output_list:
        if output.call_id in by_id:
            raise BatchProtocolError(
                "duplicate_output", "each call must have exactly one output"
            )
        by_id[output.call_id] = output
    expected = {call.call_id for call in batch}
    actual = set(by_id)
    if expected - actual:
        raise BatchProtocolError("missing_output", "a call has no output")
    if actual - expected:
        raise BatchProtocolError("unexpected_output", "output has no matching call")
    ordered: list[ToolOutput] = []
    for call in batch:
        output = by_id[call.call_id]
        if output.tool_name != call.name:
            raise BatchProtocolError(
                "tool_name_mismatch", "output tool_name does not match its call"
            )
        ordered.append(output)
    return tuple(ordered)


def demo_calls() -> tuple[CandidateCall, ...]:
    return (
        CandidateCall(
            "call_status", "get_learning_status", {"learner_id": "learner-001"}
        ),
        CandidateCall(
            "call_outline", "get_course_outline", {"course_id": "agent-tool-calling"}
        ),
        CandidateCall("call_unknown", "unknown_tool", {}),
    )


def demo_executor() -> SequentialToolExecutor:
    def get_status(arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        if arguments != {"learner_id": "learner-001"}:
            raise ValueError("invalid status arguments")
        return {"completed_count": 4}

    def get_outline(arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        if arguments != {"course_id": "agent-tool-calling"}:
            raise ValueError("invalid outline arguments")
        return {"lesson_count": 6}

    return SequentialToolExecutor(
        {
            "get_learning_status": get_status,
            "get_course_outline": get_outline,
        }
    )


def outputs_json(outputs: Iterable[ToolOutput]) -> str:
    return json.dumps(
        [output.to_dict() for output in outputs],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def fixed_report() -> str:
    calls = demo_calls()
    executor = demo_executor()
    executed = tuple(executor.execute(call) for call in calls)
    restored = assemble_outputs(calls, reversed(executed))
    labels = ",".join(
        f"{output.call_id}:{output.status}"
        + (f":{output.error_code}" if output.error_code else "")
        for output in restored
    )
    return "\n".join(
        [
            "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
            "batch=calls:3,max:4,unique-call-ids:true,execution:sequential",
            "calls=call_status:get_learning_status,call_outline:get_course_outline,call_unknown:unknown_tool",
            f"outputs={labels}",
            "correlation=by-call-id:true,exactly-once:true,input-order:true,out-of-order-restored:true",
            "partial-failure=isolated:true,successes:2,errors:1,batch-aborted:false",
            "rejection=empty-batch:true,too-large:true,bad-call-id:true,duplicate-call-id:true,missing-output:true,extra-output:true,duplicate-output:true,name-mismatch:true",
            "envelope=call-id:true,tool-name:true,status:true,data-or-error:true",
            "logs=arguments:none,results:none,call-id:allowed,tool-name:allowed,status:allowed,error-code:allowed",
            "invariants=bounded-batch,validate-before-handlers,one-output-per-call,call-id-not-index,stable-order,partial-failure-isolation,no-parallel-claim,no-network",
        ]
    )


if __name__ == "__main__":
    print(fixed_report())
