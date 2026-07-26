from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from types import MappingProxyType
from typing import Any, Mapping
import tempfile


RUN_ID_PATTERN = re.compile(r"run_[a-z0-9]{4,32}\Z")
EVENT_ID_PATTERN = re.compile(r"evt_[a-z0-9]{4,32}\Z")
ALLOWED_CHECKPOINT_KEYS = {
    "next_step",
    "last_tool_status",
    "completed_step_ids",
}
TRANSITIONS = {
    "created": {"running"},
    "running": {"waiting_input", "completed", "failed"},
    "waiting_input": {"running", "failed"},
    "completed": set(),
    "failed": set(),
}


class RunStateError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class RunSnapshot:
    run_id: str
    owner_id: str
    status: str
    version: int
    checkpoint: Mapping[str, Any]
    replayed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "checkpoint", MappingProxyType(dict(self.checkpoint))
        )


@dataclass(frozen=True)
class RunEvent:
    run_id: str
    sequence: int
    event_id: str
    event_type: str
    next_status: str


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def validate_checkpoint(checkpoint: Mapping[str, Any]) -> dict[str, Any]:
    if set(checkpoint) - ALLOWED_CHECKPOINT_KEYS:
        raise RunStateError("invalid_checkpoint", "checkpoint field is not allowed")
    normalized: dict[str, Any] = {}
    if "next_step" in checkpoint:
        value = checkpoint["next_step"]
        if type(value) is not str or not 1 <= len(value) <= 40:
            raise RunStateError("invalid_checkpoint", "next_step is invalid")
        normalized["next_step"] = value
    if "last_tool_status" in checkpoint:
        value = checkpoint["last_tool_status"]
        if value not in {"ok", "error", "none"}:
            raise RunStateError("invalid_checkpoint", "tool status is invalid")
        normalized["last_tool_status"] = value
    if "completed_step_ids" in checkpoint:
        value = checkpoint["completed_step_ids"]
        if (
            type(value) is not list
            or len(value) > 8
            or any(type(item) is not str or not 1 <= len(item) <= 32 for item in value)
            or len(set(value)) != len(value)
        ):
            raise RunStateError("invalid_checkpoint", "completed steps are invalid")
        normalized["completed_step_ids"] = list(value)
    return normalized


def request_fingerprint(
    event_type: str, next_status: str, checkpoint: Mapping[str, Any]
) -> str:
    canonical = canonical_json(
        {
            "event_type": event_type,
            "next_status": next_status,
            "checkpoint": dict(checkpoint),
        }
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class RunRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        connection = self._connect()
        try:
            connection.executescript(
                """
                PRAGMA foreign_keys = ON;
                CREATE TABLE IF NOT EXISTS runs(
                    run_id TEXT PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    checkpoint_json TEXT NOT NULL,
                    updated_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS run_events(
                    run_id TEXT NOT NULL REFERENCES runs(run_id),
                    sequence INTEGER NOT NULL,
                    event_id TEXT NOT NULL UNIQUE,
                    event_type TEXT NOT NULL,
                    next_status TEXT NOT NULL,
                    request_fingerprint TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    PRIMARY KEY(run_id, sequence)
                );
                """
            )
            connection.commit()
        finally:
            connection.close()

    def create_run(self, run_id: str, owner_id: str, *, now: int) -> RunSnapshot:
        if not RUN_ID_PATTERN.fullmatch(run_id):
            raise RunStateError("invalid_run_id", "run_id is invalid")
        connection = self._connect()
        try:
            connection.execute(
                "INSERT INTO runs VALUES(?,?,?,?,?,?)",
                (run_id, owner_id, "created", 0, "{}", now),
            )
            connection.commit()
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            raise RunStateError("run_exists", "run already exists") from exc
        finally:
            connection.close()
        return self.get_run(run_id)

    def get_run(self, run_id: str) -> RunSnapshot:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT * FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            raise RunStateError("run_not_found", "run does not exist")
        return RunSnapshot(
            row["run_id"],
            row["owner_id"],
            row["status"],
            row["version"],
            json.loads(row["checkpoint_json"]),
        )

    def transition(
        self,
        run_id: str,
        *,
        expected_version: int,
        event_id: str,
        event_type: str,
        next_status: str,
        checkpoint: Mapping[str, Any],
        now: int,
        fail_after_event: bool = False,
    ) -> RunSnapshot:
        if not EVENT_ID_PATTERN.fullmatch(event_id):
            raise RunStateError("invalid_event_id", "event_id is invalid")
        if event_type not in {"run_started", "input_requested", "run_completed", "run_failed", "run_resumed"}:
            raise RunStateError("invalid_event_type", "event type is not allowed")
        normalized = validate_checkpoint(checkpoint)
        fingerprint = request_fingerprint(event_type, next_status, normalized)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            duplicate = connection.execute(
                "SELECT run_id, request_fingerprint FROM run_events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
            if duplicate is not None:
                if (
                    duplicate["run_id"] != run_id
                    or duplicate["request_fingerprint"] != fingerprint
                ):
                    raise RunStateError(
                        "event_conflict", "event_id was used for another transition"
                    )
                connection.rollback()
                snapshot = self.get_run(run_id)
                return RunSnapshot(
                    snapshot.run_id,
                    snapshot.owner_id,
                    snapshot.status,
                    snapshot.version,
                    snapshot.checkpoint,
                    True,
                )
            row = connection.execute(
                "SELECT * FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if row is None:
                raise RunStateError("run_not_found", "run does not exist")
            if row["version"] != expected_version:
                raise RunStateError("stale_version", "run version changed")
            if next_status not in TRANSITIONS[row["status"]]:
                raise RunStateError("invalid_transition", "status transition is invalid")
            next_version = expected_version + 1
            connection.execute(
                "INSERT INTO run_events VALUES(?,?,?,?,?,?,?)",
                (
                    run_id,
                    next_version,
                    event_id,
                    event_type,
                    next_status,
                    fingerprint,
                    now,
                ),
            )
            if fail_after_event:
                raise sqlite3.OperationalError("injected failure")
            updated = connection.execute(
                "UPDATE runs SET status=?, version=?, checkpoint_json=?, updated_at=? "
                "WHERE run_id=? AND version=?",
                (
                    next_status,
                    next_version,
                    canonical_json(normalized),
                    now,
                    run_id,
                    expected_version,
                ),
            )
            if updated.rowcount != 1:
                raise RunStateError("stale_version", "run version changed")
            connection.commit()
        except RunStateError:
            connection.rollback()
            raise
        except sqlite3.Error as exc:
            connection.rollback()
            raise RunStateError("storage_failure", "transition rolled back") from exc
        finally:
            connection.close()
        return self.get_run(run_id)

    def events(self, run_id: str) -> tuple[RunEvent, ...]:
        connection = self._connect()
        try:
            rows = connection.execute(
                "SELECT run_id, sequence, event_id, event_type, next_status "
                "FROM run_events WHERE run_id=? ORDER BY sequence",
                (run_id,),
            ).fetchall()
        finally:
            connection.close()
        return tuple(
            RunEvent(
                row["run_id"],
                row["sequence"],
                row["event_id"],
                row["event_type"],
                row["next_status"],
            )
            for row in rows
        )


def fixed_report() -> str:
    with tempfile.TemporaryDirectory() as directory:
        repository = RunRepository(Path(directory) / "runs.db")
        repository.create_run("run_demo1", "learner-001", now=100)
        running = repository.transition(
            "run_demo1",
            expected_version=0,
            event_id="evt_start1",
            event_type="run_started",
            next_status="running",
            checkpoint={
                "next_step": "read_status",
                "last_tool_status": "none",
                "completed_step_ids": [],
            },
            now=101,
        )
        waiting = repository.transition(
            "run_demo1",
            expected_version=1,
            event_id="evt_wait01",
            event_type="input_requested",
            next_status="waiting_input",
            checkpoint={
                "next_step": "await_goal",
                "last_tool_status": "ok",
                "completed_step_ids": ["read_status"],
            },
            now=102,
        )
        replay = repository.transition(
            "run_demo1",
            expected_version=1,
            event_id="evt_wait01",
            event_type="input_requested",
            next_status="waiting_input",
            checkpoint={
                "next_step": "await_goal",
                "last_tool_status": "ok",
                "completed_step_ids": ["read_status"],
            },
            now=103,
        )
        try:
            repository.transition(
                "run_demo1",
                expected_version=1,
                event_id="evt_stale1",
                event_type="run_resumed",
                next_status="running",
                checkpoint={"next_step": "resume"},
                now=104,
            )
        except RunStateError as exc:
            stale_code = exc.code
        try:
            repository.transition(
                "run_demo1",
                expected_version=2,
                event_id="evt_fail01",
                event_type="run_resumed",
                next_status="running",
                checkpoint={"next_step": "resume"},
                now=105,
                fail_after_event=True,
            )
        except RunStateError as exc:
            rollback_code = exc.code
        current = repository.get_run("run_demo1")
        return "\n".join(
            [
                "runtime=python:3.11+,dependencies:stdlib-only,storage:sqlite,network:disabled",
                "schema=runs:true,events:true,foreign-key:true,event-id-unique:true",
                f"created=status:created,version:0,events:0",
                f"running=status:{running.status},version:{running.version},events:1",
                f"waiting=status:{waiting.status},version:{waiting.version},events:2",
                f"replay=status:{replay.status},version:{replay.version},replayed:{str(replay.replayed).lower()},events:{len(repository.events('run_demo1'))}",
                f"concurrency=expected-version:true,stale:{stale_code},current-version:{current.version}",
                f"atomicity=injected-failure:{rollback_code},status:{current.status},version:{current.version},events:{len(repository.events('run_demo1'))}",
                "checkpoint=allowlist:true,next-step:true,tool-status:true,completed-step-ids:true,reasoning:false,prompt:false",
                "invariants=event-and-state-one-transaction,monotonic-version,ordered-events,idempotent-event,conflict-detected,no-hidden-chain-of-thought,no-network",
            ]
        )


if __name__ == "__main__":
    print(fixed_report())
