"""PostgreSQL boundary for the Web Engineering migration lesson.

The lesson deliberately uses SQLAlchemy Core rather than an ORM: table shape,
transactions and migration order remain visible to the learner.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal
from sqlalchemy import Column, DateTime, ForeignKey, Integer, MetaData, Numeric, String, Table, Text, create_engine, func, select
from sqlalchemy.engine import Connection, Engine

metadata = MetaData()
learners = Table(
    "learners", metadata,
    Column("learner_id", String(32), primary_key=True),
    Column("name", String(80), nullable=False),
    Column("description", Text, nullable=False),
)
study_sessions = Table(
    "study_sessions", metadata,
    Column("session_id", Integer, primary_key=True),
    Column("learner_id", ForeignKey("learners.learner_id", ondelete="CASCADE"), nullable=False),
    Column("hours", Numeric(5, 2), nullable=False),
    Column("note", String(200), nullable=False),
    Column("idempotency_key", String(80), nullable=False, unique=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)


def engine_for(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True, pool_size=4, max_overflow=0)


@contextmanager
def transaction(engine: Engine):
    """A visible commit-or-rollback boundary used by the import lesson."""
    with engine.begin() as connection:
        yield connection


@dataclass(frozen=True)
class ImportSummary:
    learners: int
    sessions: int
    hours: Decimal


def summary(connection: Connection) -> ImportSummary:
    learner_count = connection.scalar(select(func.count()).select_from(learners)) or 0
    session_count = connection.scalar(select(func.count()).select_from(study_sessions)) or 0
    hours = connection.scalar(select(func.coalesce(func.sum(study_sessions.c.hours), 0))) or Decimal("0")
    return ImportSummary(int(learner_count), int(session_count), Decimal(hours))
