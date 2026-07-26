from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from types import MappingProxyType
from typing import Any, Mapping


CALL_ID_PATTERN = re.compile(r"call_[a-z0-9]{4,32}\Z")
TOOL_NAME_PATTERN = re.compile(r"[a-z][a-z0-9_]{2,63}\Z")


class ToolProtocolError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ArgumentSpec:
    value_type: type
    required: bool = True
    min_length: int | None = None
    max_length: int | None = None


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    arguments: Mapping[str, ArgumentSpec]

    def __post_init__(self) -> None:
        if not TOOL_NAME_PATTERN.fullmatch(self.name):
            raise ToolProtocolError("invalid_tool_definition", "tool name is invalid")
        if not self.description.strip() or not self.arguments:
            raise ToolProtocolError("invalid_tool_definition", "description and arguments are required")
        object.__setattr__(self, "arguments", MappingProxyType(dict(self.arguments)))


@dataclass(frozen=True)
class ToolCall:
    call_id: str
    name: str
    arguments_json: str


@dataclass(frozen=True)
class ValidatedToolCall:
    call_id: str
    name: str
    arguments: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "arguments", MappingProxyType(dict(self.arguments)))


class ToolRegistry:
    def __init__(self, definitions: tuple[ToolDefinition, ...]) -> None:
        if not definitions:
            raise ToolProtocolError("empty_registry", "registry must contain a tool")
        by_name: dict[str, ToolDefinition] = {}
        for definition in definitions:
            if definition.name in by_name:
                raise ToolProtocolError("duplicate_tool", "tool names must be unique")
            by_name[definition.name] = definition
        self._definitions = MappingProxyType(by_name)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._definitions))

    def definition(self, name: str) -> ToolDefinition:
        try:
            return self._definitions[name]
        except KeyError as exc:
            raise ToolProtocolError("unknown_tool", "tool is not registered") from exc

    def manifest(self) -> tuple[dict[str, Any], ...]:
        output: list[dict[str, Any]] = []
        for name in self.names:
            definition = self._definitions[name]
            properties: dict[str, Any] = {}
            required: list[str] = []
            for argument_name in sorted(definition.arguments):
                spec = definition.arguments[argument_name]
                json_type = {str: "string", bool: "boolean", int: "integer"}.get(spec.value_type)
                if json_type is None:
                    raise ToolProtocolError("invalid_tool_definition", "unsupported argument type")
                property_schema: dict[str, Any] = {"type": json_type}
                if spec.min_length is not None:
                    property_schema["minLength"] = spec.min_length
                if spec.max_length is not None:
                    property_schema["maxLength"] = spec.max_length
                properties[argument_name] = property_schema
                if spec.required:
                    required.append(argument_name)
            output.append({
                "type": "function",
                "name": definition.name,
                "description": definition.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False,
                },
                "strict": True,
            })
        return tuple(output)

    def fingerprint(self) -> str:
        payload = json.dumps(
            self.manifest(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def validate_call(self, call: ToolCall) -> ValidatedToolCall:
        if not CALL_ID_PATTERN.fullmatch(call.call_id):
            raise ToolProtocolError("invalid_call_id", "call_id is invalid")
        definition = self.definition(call.name)
        try:
            raw = json.loads(call.arguments_json)
        except json.JSONDecodeError as exc:
            raise ToolProtocolError("arguments_json_invalid", "arguments are not valid JSON") from exc
        if type(raw) is not dict:
            raise ToolProtocolError("arguments_not_object", "arguments must be a JSON object")

        expected = set(definition.arguments)
        actual = set(raw)
        required = {name for name, spec in definition.arguments.items() if spec.required}
        if missing := required - actual:
            raise ToolProtocolError("arguments_missing", f"missing required arguments: {sorted(missing)}")
        if extra := actual - expected:
            raise ToolProtocolError("arguments_extra", f"unexpected arguments: {sorted(extra)}")

        validated: dict[str, Any] = {}
        for name in sorted(actual):
            value = raw[name]
            spec = definition.arguments[name]
            if type(value) is not spec.value_type:
                raise ToolProtocolError("argument_type_invalid", f"{name} has wrong type")
            if isinstance(value, str):
                if spec.min_length is not None and len(value) < spec.min_length:
                    raise ToolProtocolError("argument_value_invalid", f"{name} is too short")
                if spec.max_length is not None and len(value) > spec.max_length:
                    raise ToolProtocolError("argument_value_invalid", f"{name} is too long")
            validated[name] = value
        return ValidatedToolCall(call.call_id, call.name, validated)


LEARNING_TOOLS = ToolRegistry((
    ToolDefinition(
        "get_learning_status",
        "读取一个合成学习者的课程完成状态，不执行写入。",
        {
            "learner_id": ArgumentSpec(str, min_length=3, max_length=24),
            "include_recent": ArgumentSpec(bool),
        },
    ),
))


def fixed_report() -> str:
    candidate = ToolCall(
        "call_demo1",
        "get_learning_status",
        '{"learner_id":"learner-001","include_recent":true}',
    )
    validated = LEARNING_TOOLS.validate_call(candidate)
    return "\n".join([
        "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
        f"registry=tools:{len(LEARNING_TOOLS.names)},names:{','.join(LEARNING_TOOLS.names)},strict:true",
        f"manifest=fingerprint:{LEARNING_TOOLS.fingerprint()[:12]},additional-properties:false",
        f"candidate=call-id:{validated.call_id},tool:{validated.name},arguments:2,executed:false",
        "validation=call-id:true,known-tool:true,json-object:true,required:true,exact-fields:true,strict-types:true",
        "rejection=bad-call-id:true,unknown-tool:true,bad-json:true,array-arguments:true,missing:true,extra:true,type:true,length:true",
        "trust=model-output:proposal-only,application-validates:true,application-executes:false",
        "logs=arguments:none,user-text:none,call-id:allowed,tool-name:allowed,error-code:allowed",
        "invariants=allowlisted-registry,canonical-manifest,immutable-arguments,no-handler,no-side-effects,no-network",
    ])


if __name__ == "__main__":
    print(fixed_report())
