from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text

from database import engine_for, summary
from migrate_sqlite import import_sqlite

ROOT = Path(__file__).resolve().parent
URL = os.environ.get("WEB_ENGINEERING_DATABASE_URL", "postgresql+psycopg://dashboard:dashboard@127.0.0.1:55439/dashboard")


def alembic_config() -> Config:
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", URL)
    return config


@unittest.skipUnless(os.environ.get("WEB_ENGINEERING_POSTGRES") == "1", "requires the real local PostgreSQL container")
class PostgreSQLMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        config = alembic_config()
        command.downgrade(config, "base")
        command.upgrade(config, "head")

    def test_upgrade_head_creates_foreign_key_schema(self) -> None:
        engine = create_engine(URL)
        with engine.connect() as connection:
            self.assertEqual(connection.scalar(text("SELECT current_setting('server_version_num')::int / 10000")), 16)
            self.assertEqual(connection.scalar(text("SELECT to_regclass('public.learners')")), "learners")
            self.assertEqual(connection.scalar(text("SELECT to_regclass('public.users')")), "users")
            self.assertEqual(connection.scalar(text("SELECT to_regclass('public.auth_sessions')")), "auth_sessions")
            self.assertEqual(connection.scalar(text("SELECT to_regclass('public.audit_events')")), "audit_events")
        engine.dispose()

    def test_sqlite_import_is_idempotent_and_preserves_totals(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            sqlite_path = Path(temporary) / "legacy.sqlite3"
            import sqlite3
            source = sqlite3.connect(sqlite_path)
            source.executescript("CREATE TABLE learners(learner_id TEXT PRIMARY KEY, name TEXT, description TEXT); CREATE TABLE study_sessions(learner_id TEXT, hours REAL, note TEXT, idempotency_key TEXT, created_at TEXT);")
            source.execute("INSERT INTO learners VALUES ('xiaoma', '小码', '迁移练习')")
            source.execute("INSERT INTO study_sessions VALUES ('xiaoma', 1.25, 'first', 'legacy-0001', '2026-07-22T00:00:00Z')")
            source.commit(); source.close()
            first = import_sqlite(sqlite_path, URL)
            second = import_sqlite(sqlite_path, URL)
        self.assertEqual(first, second)
        self.assertEqual((second.learners, second.sessions, str(second.hours)), (1, 1, "1.25"))

    def test_failed_transaction_rolls_back_all_rows(self) -> None:
        engine = engine_for(URL)
        with self.assertRaises(Exception):
            with engine.begin() as connection:
                connection.execute(text("INSERT INTO learners(learner_id, name, description) VALUES ('rollback', '回滚', 'x')"))
                connection.execute(text("INSERT INTO study_sessions(learner_id, hours, note, idempotency_key) VALUES ('missing', 1, 'bad', 'bad-key')"))
        with engine.connect() as connection:
            self.assertEqual(connection.scalar(text("SELECT count(*) FROM learners WHERE learner_id = 'rollback'")), 0)
        engine.dispose()

    def test_downgrade_removes_tables(self) -> None:
        config = alembic_config()
        command.downgrade(config, "base")
        engine = create_engine(URL)
        with engine.connect() as connection:
            self.assertIsNone(connection.scalar(text("SELECT to_regclass('public.study_sessions')")))
        engine.dispose()
