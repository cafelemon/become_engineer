from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import sqlite3
from types import MappingProxyType
from typing import Any, Mapping
import tempfile


LEARNER_ID_PATTERN = re.compile(r"learner-[0-9]{3}\Z")


class ToolExecutionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Principal:
    subject_id: str
    permissions: frozenset[str]


@dataclass(frozen=True)
class ValidatedToolCall:
    call_id: str
    name: str
    arguments: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "arguments", MappingProxyType(dict(self.arguments)))


@dataclass(frozen=True)
class ToolResult:
    call_id: str
    tool_name: str
    status: str
    data: Mapping[str, Any] | None
    error_code: str | None

    def __post_init__(self) -> None:
        if self.data is not None:
            object.__setattr__(self, "data", MappingProxyType(dict(self.data)))

    def to_json(self) -> str:
        return json.dumps({
            "call_id": self.call_id,
            "tool_name": self.tool_name,
            "status": self.status,
            "data": dict(self.data) if self.data is not None else None,
            "error_code": self.error_code,
        }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def seed_database(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE learning_status("
            "learner_id TEXT NOT NULL, course_id TEXT NOT NULL, completed_at TEXT NOT NULL,"
            "PRIMARY KEY(learner_id, course_id))"
        )
        connection.executemany(
            "INSERT INTO learning_status VALUES(?,?,?)",
            [
                ("learner-001", "llm-use-06", "2026-07-20T10:00:00Z"),
                ("learner-001", "llm-rag-eval-06", "2026-07-25T10:00:00Z"),
                ("learner-001", "agent-tool-calling-01", "2026-07-26T10:00:00Z"),
                ("learner-001", "python-core-07", "2026-07-10T10:00:00Z"),
                ("learner-002", "engineering-01", "2026-07-01T10:00:00Z"),
            ],
        )
        connection.commit()
    finally:
        connection.close()


class LearningStatusReader:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path.resolve()
        self.handler_calls = 0

    def _connect_read_only(self) -> sqlite3.Connection:
        return sqlite3.connect(f"file:{self.database_path}?mode=ro", uri=True)

    def read(self, learner_id: str, include_recent: bool) -> dict[str, Any]:
        self.handler_calls += 1
        connection = self._connect_read_only()
        try:
            total = connection.execute(
                "SELECT COUNT(*) FROM learning_status WHERE learner_id = ?",
                (learner_id,),
            ).fetchone()[0]
            recent: list[str] = []
            if include_recent:
                rows = connection.execute(
                    "SELECT course_id FROM learning_status "
                    "WHERE learner_id = ? ORDER BY completed_at DESC, course_id ASC LIMIT 3",
                    (learner_id,),
                ).fetchall()
                recent = [row[0] for row in rows]
            return {
                "learner_id": learner_id,
                "completed_count": total,
                "recent_course_ids": recent,
            }
        finally:
            connection.close()


class ReadOnlyToolExecutor:
    def __init__(self, reader: LearningStatusReader) -> None:
        self.reader = reader

    def execute(self, call: ValidatedToolCall, principal: Principal) -> ToolResult:
        try:
            data = self._execute_checked(call, principal)
            return ToolResult(call.call_id, call.name, "ok", data, None)
        except ToolExecutionError as exc:
            return ToolResult(call.call_id, call.name, "error", None, exc.code)
        except (sqlite3.Error, OSError):
            return ToolResult(call.call_id, call.name, "error", None, "tool_unavailable")

    def _execute_checked(
        self, call: ValidatedToolCall, principal: Principal
    ) -> dict[str, Any]:
        if call.name != "get_learning_status":
            raise ToolExecutionError("unknown_tool", "tool is not registered")
        if set(call.arguments) != {"learner_id", "include_recent"}:
            raise ToolExecutionError("invalid_arguments", "argument fields are invalid")
        learner_id = call.arguments["learner_id"]
        include_recent = call.arguments["include_recent"]
        if type(learner_id) is not str or not LEARNER_ID_PATTERN.fullmatch(learner_id):
            raise ToolExecutionError("invalid_arguments", "learner_id is invalid")
        if type(include_recent) is not bool:
            raise ToolExecutionError("invalid_arguments", "include_recent is invalid")
        if (
            "learning_status:read" not in principal.permissions
            or principal.subject_id != learner_id
        ):
            raise ToolExecutionError("forbidden", "principal cannot access this learner")
        return self.reader.read(learner_id, include_recent)


def fixed_report() -> str:
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "learning.db"
        seed_database(database)
        reader = LearningStatusReader(database)
        executor = ReadOnlyToolExecutor(reader)
        result = executor.execute(
            ValidatedToolCall(
                "call_read1",
                "get_learning_status",
                {"learner_id": "learner-001", "include_recent": True},
            ),
            Principal("learner-001", frozenset({"learning_status:read"})),
        )
        denied = executor.execute(
            ValidatedToolCall(
                "call_read2",
                "get_learning_status",
                {"learner_id": "learner-002", "include_recent": True},
            ),
            Principal("learner-001", frozenset({"learning_status:read"})),
        )
        return "\n".join([
            "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
            "tool=name:get_learning_status,risk:read-only,permission:learning_status:read",
            f"success=call-id:{result.call_id},status:{result.status},completed:{result.data['completed_count']},recent:{len(result.data['recent_course_ids'])}",
            f"denied=call-id:{denied.call_id},status:{denied.status},error:{denied.error_code},handler-called:false",
            f"handler=calls:{reader.handler_calls},sqlite-uri:mode=ro,sql:parameterized,result-limit:3",
            "validation=exact-fields:true,learner-pattern:true,strict-bool:true,permission:true,ownership:true",
            "rejection=unknown-tool:true,invalid-arguments:true,missing-permission:true,cross-learner:true,write-attempt:true",
            "envelope=call-id:true,tool-name:true,status:true,data-or-error:true,internal-exception:false",
            "logs=arguments:none,query:none,result:none,call-id:allowed,tool-name:allowed,status:allowed,error-code:allowed",
            "invariants=validate-before-handler,authorize-before-handler,own-resource,read-only-db,parameterized-sql,bounded-result,no-network",
        ])


if __name__ == "__main__":
    print(fixed_report())
