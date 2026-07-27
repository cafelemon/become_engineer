"""Idempotently import the v0.8 teaching data into PostgreSQL."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as postgres_insert

from database import engine_for, learners, study_sessions, summary, transaction


def import_sqlite(sqlite_path: Path, database_url: str):
    engine = engine_for(database_url)
    source = sqlite3.connect(sqlite_path)
    source.row_factory = sqlite3.Row
    try:
        with transaction(engine) as target:
            for row in source.execute("SELECT learner_id, name, description FROM learners"):
                target.execute(postgres_insert(learners).values(**dict(row)).on_conflict_do_nothing(index_elements=["learner_id"]))
            for row in source.execute("SELECT learner_id, hours, note, idempotency_key, created_at FROM study_sessions"):
                values = dict(row)
                target.execute(
                    postgres_insert(study_sessions).values(**values).on_conflict_do_nothing(index_elements=["idempotency_key"])
                )
        with engine.connect() as connection:
            return summary(connection)
    finally:
        source.close()
        engine.dispose()
