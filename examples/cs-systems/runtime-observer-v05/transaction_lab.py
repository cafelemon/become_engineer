from __future__ import annotations

import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path
from threading import Event, Thread


@dataclass(frozen=True)
class RollbackResult:
    before: tuple[int, int]
    after: tuple[int, int]


@dataclass(frozen=True)
class ConstraintResult:
    rejected: bool
    balances: tuple[int, int]


@dataclass(frozen=True)
class LockResult:
    blocked: bool
    retry_succeeded: bool


@dataclass(frozen=True)
class SnapshotResult:
    before: int
    during: int
    after: int


def connect(path: Path, *, timeout: float = 1.0) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=timeout, isolation_level=None)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def setup_database(path: Path) -> None:
    with connect(path) as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute(
            """
            CREATE TABLE accounts (
                name TEXT PRIMARY KEY,
                balance INTEGER NOT NULL CHECK (balance >= 0)
            )
            """
        )
        connection.executemany(
            "INSERT INTO accounts(name, balance) VALUES (?, ?)",
            [("alice", 100), ("bob", 100)],
        )


def read_balances(path: Path) -> tuple[int, int]:
    with connect(path) as connection:
        rows = connection.execute(
            "SELECT balance FROM accounts ORDER BY name"
        ).fetchall()
    return rows[0][0], rows[1][0]


def rollback_transfer(path: Path, amount: int = 30) -> RollbackResult:
    before = read_balances(path)
    connection = connect(path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE accounts SET balance = balance - ? WHERE name = 'alice'",
            (amount,),
        )
        raise RuntimeError("simulated failure before credit")
    except RuntimeError:
        connection.rollback()
    finally:
        connection.close()
    return RollbackResult(before=before, after=read_balances(path))


def reject_overdraft(path: Path, amount: int = 130) -> ConstraintResult:
    connection = connect(path)
    rejected = False
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE accounts SET balance = balance - ? WHERE name = 'alice'",
            (amount,),
        )
        connection.commit()
    except sqlite3.IntegrityError:
        rejected = True
        connection.rollback()
    finally:
        connection.close()
    return ConstraintResult(rejected=rejected, balances=read_balances(path))


def lock_wait_then_retry(path: Path) -> LockResult:
    holder = connect(path)
    holder.execute("BEGIN IMMEDIATE")
    holder.execute("UPDATE accounts SET balance = balance + 1 WHERE name = 'alice'")

    attempted = Event()
    blocked = {"value": False}

    def competing_writer() -> None:
        connection = connect(path, timeout=0.05)
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as error:
            blocked["value"] = "locked" in str(error).lower()
        finally:
            connection.close()
            attempted.set()

    thread = Thread(target=competing_writer, name="sqlite-competing-writer")
    thread.start()
    if not attempted.wait(timeout=2):
        holder.rollback()
        holder.close()
        raise TimeoutError("competing writer did not finish")

    holder.rollback()
    holder.close()
    thread.join(timeout=2)

    retry = connect(path)
    try:
        retry.execute("BEGIN IMMEDIATE")
        retry.execute("UPDATE accounts SET balance = balance + 5 WHERE name = 'bob'")
        retry.commit()
        retry_succeeded = True
    except sqlite3.Error:
        retry.rollback()
        retry_succeeded = False
    finally:
        retry.close()

    return LockResult(blocked=blocked["value"], retry_succeeded=retry_succeeded)


def snapshot_read(path: Path) -> SnapshotResult:
    reader = connect(path)
    writer = connect(path)
    try:
        reader.execute("BEGIN")
        before = reader.execute(
            "SELECT balance FROM accounts WHERE name = 'alice'"
        ).fetchone()[0]

        writer.execute("BEGIN IMMEDIATE")
        writer.execute("UPDATE accounts SET balance = 120 WHERE name = 'alice'")
        writer.commit()

        during = reader.execute(
            "SELECT balance FROM accounts WHERE name = 'alice'"
        ).fetchone()[0]
        reader.commit()
        after = reader.execute(
            "SELECT balance FROM accounts WHERE name = 'alice'"
        ).fetchone()[0]
        return SnapshotResult(before=before, during=during, after=after)
    finally:
        reader.close()
        writer.close()


def fresh_database(directory: str, name: str) -> Path:
    path = Path(directory) / name
    setup_database(path)
    return path


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        rollback = rollback_transfer(fresh_database(directory, "rollback.sqlite3"))
        constraint = reject_overdraft(fresh_database(directory, "constraint.sqlite3"))
        lock = lock_wait_then_retry(fresh_database(directory, "lock.sqlite3"))
        snapshot = snapshot_read(fresh_database(directory, "snapshot.sqlite3"))

    print(
        "rollback: "
        f"before={rollback.before[0]},{rollback.before[1]} "
        f"after={rollback.after[0]},{rollback.after[1]}"
    )
    print(
        f"constraint: rejected={constraint.rejected} "
        f"total={sum(constraint.balances)}"
    )
    print(
        f"lock: blocked={lock.blocked} "
        f"retry_succeeded={lock.retry_succeeded}"
    )
    print(
        f"snapshot: before={snapshot.before} "
        f"during={snapshot.during} after={snapshot.after}"
    )


if __name__ == "__main__":
    main()
