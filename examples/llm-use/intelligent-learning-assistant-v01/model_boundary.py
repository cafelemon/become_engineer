from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol


Role = Literal["system", "user", "assistant"]
Status = Literal["completed", "refused", "incomplete"]


@dataclass(frozen=True)
class Message:
    role: Role
    content: str


@dataclass(frozen=True)
class ModelRequest:
    model: str
    messages: tuple[Message, ...]
    max_output_units: int


@dataclass(frozen=True)
class ProviderResponse:
    provider_request_id: str
    status: Status
    text: str
    input_units: int
    output_units: int
    finish_reason: str


@dataclass(frozen=True)
class ModelResult:
    status: Status
    text: str | None
    input_units: int
    output_units: int
    finish_reason: str
    request_id: str


class ModelAdapter(Protocol):
    def complete(self, request: ModelRequest) -> ProviderResponse:
        ...


class ScriptedAdapter:
    def __init__(self, case: str) -> None:
        self.case = case
        self.calls: list[ModelRequest] = []

    def complete(self, request: ModelRequest) -> ProviderResponse:
        self.calls.append(request)
        fixtures = {
            "completed": ProviderResponse(
                "offline-001", "completed", "先完成 Python 起步，再做一个可运行项目。",
                18, 14, "stop",
            ),
            "refused": ProviderResponse(
                "offline-002", "refused", "不能帮助获取他人的私人学习记录。",
                16, 12, "safety",
            ),
            "incomplete": ProviderResponse(
                "offline-003", "incomplete", "先完成 Python", 18, 4, "max_output_units",
            ),
            "empty": ProviderResponse(
                "offline-004", "completed", "   ", 18, 0, "stop",
            ),
        }
        if self.case not in fixtures:
            raise RuntimeError(f"unknown offline case: {self.case}")
        return fixtures[self.case]


def build_request(question: str) -> ModelRequest:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string")
    return ModelRequest(
        model="offline-learning-assistant-v01",
        messages=(
            Message("system", "只回答公开课程学习问题；不知道时明确说明。"),
            Message("user", question.strip()),
        ),
        max_output_units=80,
    )


def validate_request(request: ModelRequest) -> None:
    if not request.model.strip():
        raise ValueError("model must be declared")
    if not 1 <= request.max_output_units <= 500:
        raise ValueError("max_output_units must be between 1 and 500")
    if len(request.messages) < 2:
        raise ValueError("request needs system and user messages")
    if request.messages[0].role != "system" or request.messages[-1].role != "user":
        raise ValueError("request must start with system and end with user")
    for message in request.messages:
        if message.role not in {"system", "user", "assistant"}:
            raise ValueError("message role is not supported")
        if not message.content.strip():
            raise ValueError("message content must not be empty")


def call_model(adapter: ModelAdapter, request: ModelRequest) -> ModelResult:
    validate_request(request)
    response = adapter.complete(request)
    if response.status not in {"completed", "refused", "incomplete"}:
        raise ValueError("provider returned an unknown status")
    if response.input_units < 0 or response.output_units < 0:
        raise ValueError("usage units must be non-negative")
    if not response.provider_request_id.strip():
        raise ValueError("provider request id is required")
    if not response.finish_reason.strip():
        raise ValueError("finish reason is required")
    text = response.text.strip()
    if response.status == "completed" and not text:
        raise ValueError("completed response must contain text")
    return ModelResult(
        status=response.status,
        text=text or None,
        input_units=response.input_units,
        output_units=response.output_units,
        finish_reason=response.finish_reason,
        request_id=response.provider_request_id,
    )


def fixed_report() -> str:
    request = build_request("我刚开始学编程，下一步做什么？")
    completed = call_model(ScriptedAdapter("completed"), request)
    refused = call_model(ScriptedAdapter("refused"), request)
    incomplete = call_model(ScriptedAdapter("incomplete"), request)
    return "\n".join([
        "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
        f"request=model:{request.model},messages:system|user,max_output_units:{request.max_output_units}",
        f"completed=status:{completed.status},finish:{completed.finish_reason},usage:{completed.input_units}|{completed.output_units},text:present",
        f"refused=status:{refused.status},finish:{refused.finish_reason},text:present",
        f"incomplete=status:{incomplete.status},finish:{incomplete.finish_reason},text:partial",
        "empty_completed=rejected",
        "invalid_request=rejected-before-adapter",
        "normalized_result=status+text+usage+finish_reason+request_id",
        "logs=authorization:none,raw_prompt:none,raw_response:none",
        "invariants=model-is-untrusted-adapter,application-validates,offline-first,no-rag,no-tools",
    ])


if __name__ == "__main__":
    print(fixed_report())
