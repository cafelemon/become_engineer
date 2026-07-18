from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Literal


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


class LearnerNotFoundError(LookupError):
    pass


class LearningDatabase:
    """A small SQLite boundary used by the Web v0.6 lesson."""

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
            connection.executemany(
                """
                INSERT OR IGNORE INTO learners(
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
                        "让学习记录在重启后仍然存在",
                    ),
                    (
                        "afei",
                        "阿飞",
                        "已经完成 Web 起步，正在把内存数据迁移到 SQLite。",
                        13,
                        "本周已完成",
                        "为学习记录设计 REST 资源",
                    ),
                ],
            )
            connection.executemany(
                """
                INSERT OR IGNORE INTO study_sessions(id, learner_id, hours, note)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (1, "xiaoma", 7.5, "Web v0.5 契约检查"),
                    (2, "afei", 10.0, "Web 核心学习记录"),
                ],
            )

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
            status=row["status"],
            next_milestone=str(row["next_milestone"]),
        )

    def add_session(self, learner_id: str, hours: float, note: str) -> StudySessionRow:
        self.initialize()
        with self.transaction() as connection:
            learner = connection.execute(
                "SELECT id FROM learners WHERE id = ?",
                (learner_id,),
            ).fetchone()
            if learner is None:
                raise LearnerNotFoundError(learner_id)

            cursor = connection.execute(
                """
                INSERT INTO study_sessions(learner_id, hours, note)
                VALUES (?, ?, ?)
                """,
                (learner_id, hours, note),
            )
            session_id = cursor.lastrowid

        if session_id is None:
            raise sqlite3.DatabaseError("SQLite did not return a session id")

        return StudySessionRow(
            session_id=session_id,
            learner_id=learner_id,
            hours=hours,
            note=note,
        )

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
