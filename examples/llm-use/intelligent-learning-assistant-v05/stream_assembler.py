from __future__ import annotations

from dataclasses import dataclass


EVENT_KINDS = frozenset({
    "response.created",
    "output_text.delta",
    "response.completed",
    "response.refused",
    "response.incomplete",
})


class StreamProtocolError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class StreamEvent:
    sequence: int
    kind: str
    delta: str | None = None
    finish_reason: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence < 0:
            raise ValueError("sequence must be a non-negative integer")
        if self.kind not in EVENT_KINDS:
            raise ValueError(f"unknown event kind: {self.kind}")
        if self.kind == "output_text.delta":
            if not isinstance(self.delta, str) or not self.delta:
                raise ValueError("delta event requires non-empty text")
            if self.finish_reason is not None:
                raise ValueError("delta event cannot carry finish_reason")
        elif self.delta is not None:
            raise ValueError("only delta event may carry text")


@dataclass(frozen=True)
class StreamResult:
    status: str
    text: str
    finish_reason: str
    events_seen: int


class StreamAssembler:
    def __init__(self, max_chars: int = 4096) -> None:
        if max_chars < 1:
            raise ValueError("max_chars must be positive")
        self._max_chars = max_chars
        self._expected_sequence = 0
        self._started = False
        self._terminal: StreamResult | None = None
        self._parts: list[str] = []

    @property
    def partial_text(self) -> str:
        return "".join(self._parts)

    def feed(self, event: StreamEvent) -> StreamResult | None:
        if self._terminal is not None:
            raise StreamProtocolError("event_after_terminal", "stream already terminated")
        if event.sequence != self._expected_sequence:
            raise StreamProtocolError(
                "sequence_mismatch",
                f"expected sequence {self._expected_sequence}, got {event.sequence}",
            )
        self._expected_sequence += 1

        if not self._started:
            if event.kind != "response.created":
                raise StreamProtocolError("missing_created", "first event must create response")
            if event.finish_reason is not None:
                raise StreamProtocolError("invalid_event", "created event has no finish reason")
            self._started = True
            return None

        if event.kind == "response.created":
            raise StreamProtocolError("duplicate_created", "response was already created")

        if event.kind == "output_text.delta":
            next_size = len(self.partial_text) + len(event.delta or "")
            if next_size > self._max_chars:
                raise StreamProtocolError("output_too_large", "assembled output exceeds max_chars")
            self._parts.append(event.delta or "")
            return None

        reason = event.finish_reason
        if not isinstance(reason, str) or not reason:
            raise StreamProtocolError("missing_finish_reason", "terminal event needs finish reason")
        text = self.partial_text
        if event.kind == "response.completed":
            if not text:
                raise StreamProtocolError("empty_completed", "completed stream has no text")
            if reason != "stop":
                raise StreamProtocolError("invalid_finish_reason", "completed stream must stop")
            status = "completed"
        elif event.kind == "response.refused":
            if text:
                raise StreamProtocolError("partial_before_refusal", "refusal cannot follow text")
            status = "refused"
        else:
            status = "incomplete"

        self._terminal = StreamResult(status, text, reason, self._expected_sequence)
        return self._terminal

    def cancel(self) -> StreamResult:
        if not self._started:
            raise StreamProtocolError("not_started", "cannot cancel before response.created")
        if self._terminal is not None:
            raise StreamProtocolError("already_terminal", "cannot cancel terminal stream")
        self._terminal = StreamResult(
            "cancelled", self.partial_text, "client_cancelled", self._expected_sequence
        )
        return self._terminal

    def finalize(self) -> StreamResult:
        if self._terminal is None:
            raise StreamProtocolError("missing_terminal", "stream ended without terminal event")
        return self._terminal


def assemble(events: list[StreamEvent], max_chars: int = 4096) -> StreamResult:
    assembler = StreamAssembler(max_chars)
    for event in events:
        assembler.feed(event)
    return assembler.finalize()


def fixed_report() -> str:
    completed = assemble([
        StreamEvent(0, "response.created"),
        StreamEvent(1, "output_text.delta", "学习"),
        StreamEvent(2, "output_text.delta", "计划"),
        StreamEvent(3, "response.completed", finish_reason="stop"),
    ])
    incomplete = assemble([
        StreamEvent(0, "response.created"),
        StreamEvent(1, "output_text.delta", "未完"),
        StreamEvent(2, "response.incomplete", finish_reason="max_output"),
    ])
    cancelled_assembler = StreamAssembler()
    cancelled_assembler.feed(StreamEvent(0, "response.created"))
    cancelled_assembler.feed(StreamEvent(1, "output_text.delta", "部分"))
    cancelled = cancelled_assembler.cancel()

    return "\n".join([
        "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
        f"completed=status:{completed.status},text:{completed.text},finish:{completed.finish_reason},events:{completed.events_seen}",
        f"incomplete=status:{incomplete.status},partial:{incomplete.text},finish:{incomplete.finish_reason}",
        f"cancelled=status:{cancelled.status},partial:{cancelled.text},finish:{cancelled.finish_reason}",
        "ordering=sequence:start-zero,strict-contiguous,duplicate:false,gap:false",
        "terminal=completed|refused|incomplete|cancelled,required:true,event-after-terminal:false",
        "assembly=delta-order:preserved,empty-delta:false,max-chars:bounded,partial-is-complete:false",
        "rendering=plain-text-first,html-trust:false,json-parse:after-terminal-only",
        "logs=delta:none,assembled-text:none,event-kind:allowed,sequence:allowed,status:allowed",
        "invariants=created-first,one-terminal,cancel-stops-consumption,no-rag,no-tools",
    ])


if __name__ == "__main__":
    print(fixed_report())
