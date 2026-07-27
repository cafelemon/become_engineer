from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


EXPECTED_FIELDS = {"goal", "topic", "weekly_hours", "current_level"}


class StructuredOutputError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class LearningRequest:
    goal: str
    topic: str
    weekly_hours: int
    current_level: str


FIXTURES = {
    "valid": '{"goal":"job","topic":"Python","weekly_hours":8,"current_level":"beginner"}',
    "empty": "",
    "invalid-json": '{"goal":"job","topic":"Python",}',
    "array": '["job","Python",8,"beginner"]',
    "extra": '{"goal":"job","topic":"Python","weekly_hours":8,"current_level":"beginner","phone":"123"}',
    "missing": '{"goal":"job","topic":"Python","weekly_hours":8}',
    "wrong-type": '{"goal":"job","topic":"Python","weekly_hours":"8","current_level":"beginner"}',
    "bool-hours": '{"goal":"job","topic":"Python","weekly_hours":true,"current_level":"beginner"}',
    "out-of-range": '{"goal":"job","topic":"Python","weekly_hours":80,"current_level":"beginner"}',
    "invalid-enum": '{"goal":"unknown","topic":"Python","weekly_hours":8,"current_level":"expert"}',
}


def _require_string(payload: dict[str, Any], field: str) -> str:
    value = payload[field]
    if not isinstance(value, str):
        raise StructuredOutputError("wrong_type", f"{field} must be a string")
    return value


def parse_learning_request(content: str) -> LearningRequest:
    if not isinstance(content, str) or not content.strip():
        raise StructuredOutputError("empty_response", "model returned no content")
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as error:
        raise StructuredOutputError("invalid_json", "content is not valid JSON") from error
    if not isinstance(payload, dict):
        raise StructuredOutputError("not_object", "top-level JSON must be an object")
    fields = set(payload)
    extra = fields - EXPECTED_FIELDS
    missing = EXPECTED_FIELDS - fields
    if extra:
        raise StructuredOutputError("extra_fields", f"unexpected fields: {sorted(extra)}")
    if missing:
        raise StructuredOutputError("missing_fields", f"missing fields: {sorted(missing)}")

    goal = _require_string(payload, "goal")
    topic = _require_string(payload, "topic")
    level = _require_string(payload, "current_level")
    hours = payload["weekly_hours"]
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise StructuredOutputError("wrong_type", "weekly_hours must be an integer")
    if goal not in {"interest", "job"}:
        raise StructuredOutputError("invalid_enum", "goal is not supported")
    if level not in {"beginner", "basic"}:
        raise StructuredOutputError("invalid_enum", "current_level is not supported")
    if not topic.strip() or len(topic.strip()) > 60:
        raise StructuredOutputError("out_of_range", "topic length must be between 1 and 60")
    if not 1 <= hours <= 40:
        raise StructuredOutputError("out_of_range", "weekly_hours must be between 1 and 40")
    return LearningRequest(goal, topic.strip(), hours, level)


def recovery_action(error: StructuredOutputError) -> str:
    if error.code == "missing_fields":
        return "ask_user"
    if error.code in {
        "empty_response", "invalid_json", "not_object", "extra_fields",
        "wrong_type", "out_of_range", "invalid_enum",
    }:
        return "reject_or_regenerate"
    return "stop"


def fixed_report() -> str:
    valid = parse_learning_request(FIXTURES["valid"])
    failures: list[str] = []
    for name, content in FIXTURES.items():
        if name == "valid":
            continue
        try:
            parse_learning_request(content)
        except StructuredOutputError as error:
            failures.append(f"{name}:{error.code}")
    return "\n".join([
        "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
        f"valid=goal:{valid.goal},topic:{valid.topic},weekly_hours:{valid.weekly_hours},level:{valid.current_level}",
        "pipeline=nonempty->json-syntax->object->field-set->types->enums-and-ranges->domain-object",
        f"failures={','.join(failures)}",
        "coercion=string-to-int:false,bool-to-int:false,extra-fields:false",
        "missing_information=recovery:ask_user",
        "malformed_output=recovery:reject_or_regenerate,budget:not-yet-implemented",
        "schema_prompt=helpful-but-application-validation-required",
        "logs=raw_content:none,validation_code:allowed",
        "invariants=model-proposes,application-validates,no-silent-repair,no-rag,no-tools",
    ])


if __name__ == "__main__":
    print(fixed_report())
