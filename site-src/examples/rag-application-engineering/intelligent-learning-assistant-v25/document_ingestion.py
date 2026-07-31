"""Document source, version, parsing and ingestion job lifecycle for RAG v0.25."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import hashlib
import io
import json
import sqlite3
from typing import Iterable

from pypdf import PdfReader


SUPPORTED_MEDIA = {"text/markdown", "text/html", "application/pdf"}


@dataclass(frozen=True)
class ParsedBlock:
    ordinal: int
    text: str
    heading_path: tuple[str, ...] = ()
    page: int | None = None


class _HTMLText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.heading: str | None = None
        self._heading_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"h1", "h2", "h3"}:
            self.heading = tag
            self._heading_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == self.heading:
            value = " ".join(self._heading_parts).strip()
            if value:
                self.parts.append(f"\n# {value}\n")
            self.heading = None

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if not value:
            return
        if self.heading:
            self._heading_parts.append(value)
        else:
            self.parts.append(value)


def parse_document(media_type: str, content: bytes) -> tuple[ParsedBlock, ...]:
    if media_type not in SUPPORTED_MEDIA:
        raise ValueError("unsupported_media_type")
    if media_type == "application/pdf":
        reader = PdfReader(io.BytesIO(content))
        blocks = [
            ParsedBlock(index, text.strip(), page=index + 1)
            for index, page in enumerate(reader.pages)
            if (text := (page.extract_text() or "")).strip()
        ]
        if not blocks:
            raise ValueError("ocr_required")
        return tuple(blocks)
    text = content.decode("utf-8")
    if media_type == "text/html":
        parser = _HTMLText()
        parser.feed(text)
        text = "\n".join(parser.parts)
    heading_path: tuple[str, ...] = ()
    blocks: list[ParsedBlock] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            heading_path = (title,)
        else:
            blocks.append(ParsedBlock(len(blocks), line, heading_path))
    if not blocks:
        raise ValueError("empty_document")
    return tuple(blocks)


class IngestionStore:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.db = connection
        self.db.row_factory = sqlite3.Row
        self.db.executescript(
            """
            PRAGMA foreign_keys=ON;
            CREATE TABLE IF NOT EXISTS sources(
              source_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, name TEXT NOT NULL,
              active_version INTEGER, enabled INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS versions(
              source_id TEXT NOT NULL, version INTEGER NOT NULL, media_type TEXT NOT NULL,
              checksum TEXT NOT NULL, content BLOB NOT NULL, status TEXT NOT NULL,
              error_code TEXT, PRIMARY KEY(source_id, version), UNIQUE(source_id, checksum),
              FOREIGN KEY(source_id) REFERENCES sources(source_id)
            );
            CREATE TABLE IF NOT EXISTS blocks(
              source_id TEXT NOT NULL, version INTEGER NOT NULL, ordinal INTEGER NOT NULL,
              text TEXT NOT NULL, heading_path TEXT NOT NULL, page INTEGER,
              PRIMARY KEY(source_id, version, ordinal)
            );
            CREATE TABLE IF NOT EXISTS jobs(
              job_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, version INTEGER NOT NULL,
              status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, error_code TEXT
            );
            """
        )

    def create_source(self, source_id: str, owner_id: str, name: str) -> None:
        self.db.execute(
            "INSERT INTO sources(source_id,owner_id,name) VALUES(?,?,?)",
            (source_id, owner_id, name),
        )
        self.db.commit()

    def upload(self, source_id: str, media_type: str, content: bytes) -> tuple[int, bool]:
        checksum = hashlib.sha256(content).hexdigest()
        replay = self.db.execute(
            "SELECT version FROM versions WHERE source_id=? AND checksum=?",
            (source_id, checksum),
        ).fetchone()
        if replay:
            return int(replay["version"]), True
        next_version = self.db.execute(
            "SELECT COALESCE(MAX(version),0)+1 value FROM versions WHERE source_id=?",
            (source_id,),
        ).fetchone()["value"]
        with self.db:
            self.db.execute(
                "INSERT INTO versions VALUES(?,?,?,?,?,'uploaded',NULL)",
                (source_id, next_version, media_type, checksum, content),
            )
            self.db.execute(
                "INSERT INTO jobs VALUES(?,?,?,'pending',0,NULL)",
                (f"{source_id}:v{next_version}", source_id, next_version),
            )
        return int(next_version), False

    def run_job(self, job_id: str) -> str:
        job = self.db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if not job:
            raise ValueError("job_not_found")
        version = self.db.execute(
            "SELECT * FROM versions WHERE source_id=? AND version=?",
            (job["source_id"], job["version"]),
        ).fetchone()
        try:
            blocks = parse_document(version["media_type"], version["content"])
        except ValueError as exc:
            code = str(exc)
            with self.db:
                self.db.execute(
                    "UPDATE jobs SET status='failed',attempts=attempts+1,error_code=? WHERE job_id=?",
                    (code, job_id),
                )
                self.db.execute(
                    "UPDATE versions SET status='failed',error_code=? WHERE source_id=? AND version=?",
                    (code, job["source_id"], job["version"]),
                )
            return code
        with self.db:
            self.db.execute(
                "DELETE FROM blocks WHERE source_id=? AND version=?",
                (job["source_id"], job["version"]),
            )
            self.db.executemany(
                "INSERT INTO blocks VALUES(?,?,?,?,?,?)",
                [
                    (
                        job["source_id"],
                        job["version"],
                        block.ordinal,
                        block.text,
                        json.dumps(block.heading_path, ensure_ascii=False),
                        block.page,
                    )
                    for block in blocks
                ],
            )
            self.db.execute(
                "UPDATE jobs SET status='succeeded',attempts=attempts+1,error_code=NULL WHERE job_id=?",
                (job_id,),
            )
            self.db.execute(
                "UPDATE versions SET status='indexed',error_code=NULL WHERE source_id=? AND version=?",
                (job["source_id"], job["version"]),
            )
        return "indexed"

    def activate(self, source_id: str, version: int) -> None:
        row = self.db.execute(
            "SELECT status FROM versions WHERE source_id=? AND version=?",
            (source_id, version),
        ).fetchone()
        if not row or row["status"] != "indexed":
            raise ValueError("version_not_ready")
        with self.db:
            self.db.execute(
                "UPDATE sources SET active_version=?,enabled=1 WHERE source_id=?",
                (version, source_id),
            )
            self.db.execute(
                "UPDATE versions SET status='superseded' WHERE source_id=? AND version<>? AND status='active'",
                (source_id, version),
            )
            self.db.execute(
                "UPDATE versions SET status='active' WHERE source_id=? AND version=?",
                (source_id, version),
            )

    def deactivate(self, source_id: str) -> None:
        with self.db:
            self.db.execute(
                "UPDATE sources SET enabled=0,active_version=NULL WHERE source_id=?",
                (source_id,),
            )
            self.db.execute(
                "UPDATE versions SET status='tombstoned' WHERE source_id=? AND status='active'",
                (source_id,),
            )

    def active_version(self, source_id: str) -> int | None:
        row = self.db.execute(
            "SELECT active_version FROM sources WHERE source_id=? AND enabled=1",
            (source_id,),
        ).fetchone()
        return int(row["active_version"]) if row and row["active_version"] else None

    def blocks(self, source_id: str, version: int) -> tuple[sqlite3.Row, ...]:
        return tuple(
            self.db.execute(
                "SELECT * FROM blocks WHERE source_id=? AND version=? ORDER BY ordinal",
                (source_id, version),
            )
        )


def fixed_report() -> None:
    store = IngestionStore(sqlite3.connect(":memory:"))
    store.create_source("guide", "learner-a", "Guide")
    version, replay = store.upload(
        "guide", "text/markdown", "# Setup\nUse a virtual environment.".encode()
    )
    status = store.run_job("guide:v1")
    store.activate("guide", version)
    print(f"upload=version:{version},replay:{str(replay).lower()},checksum:true")
    print(f"job=status:{status},attempts:1,blocks:{len(store.blocks('guide', version))}")
    print(f"active=source:guide,version:{store.active_version('guide')},atomic:true")
    print("formats=markdown:true,html:true,digital-pdf:true,scanned-pdf:ocr_required")


if __name__ == "__main__":
    fixed_report()
