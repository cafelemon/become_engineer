from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Literal, cast


LearningStatus = Literal["起步中", "按计划推进", "本周已完成"]


@dataclass(frozen=True)
class LearningSummaryRow:
    learner_id: str
    learner_name: str
    description: str
    completed_lessons: int
    completed_hours: float
    status: LearningStatus
    next_milestone: str


@dataclass(frozen=True)
class StudySessionRow:
    session_id: int
    learner_id: str
    hours: float
    note: str
    created_at: str


@dataclass(frozen=True)
class StudySessionPageRow:
    items: tuple[StudySessionRow, ...]
    next_after_id: int | None


class LearnerNotFoundError(LookupError):
    pass


class StudySessionNotFoundError(LookupError):
    pass


class IdempotencyConflictError(ValueError):
    pass


class LearningDatabase:
    """SQLite persistence boundary for the Web v0.8 form-state lesson."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.schema_path = Path(__file__).with_name("schema.sql")

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=1.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        schema = self.schema_path.read_text(encoding="utf-8")

        with self.transaction() as connection:
            connection.executescript(schema)
            already_seeded = connection.execute(
                "SELECT 1 FROM learners LIMIT 1"
            ).fetchone()
            if already_seeded is not None:
                return
            connection.executemany(
                """
                INSERT INTO learners(
                    id, name, description, completed_lessons, status, next_milestone
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        "xiaoma",
                        "小码",
                        "正在学习 Python 与 Web，希望把练习做成可以展示的作品。",
                        8,
                        "按计划推进",
                        "把学习时段表单接入完整数据流",
                    ),
                    (
                        "afei",
                        "阿飞",
                        "已经完成 REST 资源，正在整理表单校验和失败恢复。",
                        14,
                        "本周已完成",
                        "进入 Web 工程化",
                    ),
                ],
            )
            connection.executemany(
                """
                INSERT INTO study_sessions(
                    id, learner_id, hours, note, idempotency_key
                ) VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (1, "xiaoma", 2.0, "HTML 与语义结构", None),
                    (2, "xiaoma", 2.5, "响应式 CSS", None),
                    (3, "xiaoma", 3.0, "HTTP 与 SQLite", None),
                    (4, "afei", 10.0, "Web 核心学习记录", None),
                ],
            )

    @staticmethod
    def _session_from_row(row: sqlite3.Row) -> StudySessionRow:
        return StudySessionRow(
            session_id=int(row["id"]),
            learner_id=str(row["learner_id"]),
            hours=float(row["hours"]),
            note=str(row["note"]),
            created_at=str(row["created_at"]),
        )

    @staticmethod
    def _require_learner(connection: sqlite3.Connection, learner_id: str) -> None:
        row = connection.execute(
            "SELECT id FROM learners WHERE id = ?",
            (learner_id,),
        ).fetchone()
        if row is None:
            raise LearnerNotFoundError(learner_id)

    def get_summary(self, learner_id: str) -> LearningSummaryRow:
        self.initialize()
        connection = self.connect()
        try:
            row = connection.execute(
                """
                SELECT
                    learners.id AS learner_id,
                    learners.name AS learner_name,
                    learners.description,
                    learners.completed_lessons,
                    COALESCE(SUM(study_sessions.hours), 0.0) AS completed_hours,
                    learners.status,
                    learners.next_milestone
                FROM learners
                LEFT JOIN study_sessions
                    ON study_sessions.learner_id = learners.id
                WHERE learners.id = ?
                GROUP BY learners.id
                """,
                (learner_id,),
            ).fetchone()
        finally:
            connection.close()

        if row is None:
            raise LearnerNotFoundError(learner_id)

        return LearningSummaryRow(
            learner_id=str(row["learner_id"]),
            learner_name=str(row["learner_name"]),
            description=str(row["description"]),
            completed_lessons=int(row["completed_lessons"]),
            completed_hours=float(row["completed_hours"]),
            status=cast(LearningStatus, row["status"]),
            next_milestone=str(row["next_milestone"]),
        )

    def list_sessions(
        self,
        learner_id: str,
        *,
        limit: int,
        after_id: int,
    ) -> StudySessionPageRow:
        self.initialize()
        connection = self.connect()
        try:
            self._require_learner(connection, learner_id)
            rows = connection.execute(
                """
                SELECT id, learner_id, hours, note, created_at
                FROM study_sessions
                WHERE learner_id = ? AND id > ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (learner_id, after_id, limit + 1),
            ).fetchall()
        finally:
            connection.close()

        visible_rows = rows[:limit]
        items = tuple(self._session_from_row(row) for row in visible_rows)
        next_after_id = items[-1].session_id if len(rows) > limit and items else None
        return StudySessionPageRow(items=items, next_after_id=next_after_id)

    def get_session(self, session_id: int) -> StudySessionRow:
        self.initialize()
        connection = self.connect()
        try:
            row = connection.execute(
                """
                SELECT id, learner_id, hours, note, created_at
                FROM study_sessions
                WHERE id = ?
                """,
                (session_id,),
            ).fetchone()
        finally:
            connection.close()

        if row is None:
            raise StudySessionNotFoundError(session_id)
        return self._session_from_row(row)

    def create_session(
        self,
        learner_id: str,
        hours: float,
        note: str,
        idempotency_key: str,
    ) -> tuple[StudySessionRow, bool]:
        self.initialize()
        with self.transaction() as connection:
            self._require_learner(connection, learner_id)
            existing = connection.execute(
                """
                SELECT id, learner_id, hours, note, created_at
                FROM study_sessions
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()
            if existing is not None:
                row = self._session_from_row(existing)
                if row.learner_id != learner_id or row.hours != hours or row.note != note:
                    raise IdempotencyConflictError(idempotency_key)
                return row, True

            cursor = connection.execute(
                """
                INSERT INTO study_sessions(
                    learner_id, hours, note, idempotency_key
                ) VALUES (?, ?, ?, ?)
                """,
                (learner_id, hours, note, idempotency_key),
            )
            session_id = cursor.lastrowid
            if session_id is None:
                raise sqlite3.DatabaseError("SQLite did not return a session id")
            row = connection.execute(
                """
                SELECT id, learner_id, hours, note, created_at
                FROM study_sessions
                WHERE id = ?
                """,
                (session_id,),
            ).fetchone()

        if row is None:
            raise sqlite3.DatabaseError("Created session could not be read back")
        return self._session_from_row(row), False

    def replace_session(self, session_id: int, hours: float, note: str) -> StudySessionRow:
        self.initialize()
        with self.transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE study_sessions
                SET hours = ?, note = ?
                WHERE id = ?
                """,
                (hours, note, session_id),
            )
            if cursor.rowcount == 0:
                raise StudySessionNotFoundError(session_id)
            row = connection.execute(
                """
                SELECT id, learner_id, hours, note, created_at
                FROM study_sessions
                WHERE id = ?
                """,
                (session_id,),
            ).fetchone()

        if row is None:
            raise sqlite3.DatabaseError("Updated session could not be read back")
        return self._session_from_row(row)

    def delete_session(self, session_id: int) -> None:
        self.initialize()
        with self.transaction() as connection:
            cursor = connection.execute(
                "DELETE FROM study_sessions WHERE id = ?",
                (session_id,),
            )
            if cursor.rowcount == 0:
                raise StudySessionNotFoundError(session_id)

    def session_count(self, learner_id: str) -> int:
        self.initialize()
        connection = self.connect()
        try:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM study_sessions WHERE learner_id = ?",
                (learner_id,),
            ).fetchone()
        finally:
            connection.close()
        return int(row["count"] if row is not None else 0)

    def schema_version(self) -> int:
        self.initialize()
        connection = self.connect()
        try:
            row = connection.execute("PRAGMA user_version").fetchone()
        finally:
            connection.close()
        return int(row[0] if row is not None else 0)
