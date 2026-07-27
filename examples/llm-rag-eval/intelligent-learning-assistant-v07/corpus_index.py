from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Iterable


SCHEMA_VERSION = 1
DOCUMENT_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DOCUMENT_FIELDS = {"document_id", "title", "source_uri", "updated_at", "content", "content_sha256"}
SNAPSHOT_FIELDS = {"schema_version", "corpus_id", "documents", "fingerprint"}


class CorpusError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class CorpusDocument:
    document_id: str
    title: str
    source_uri: str
    updated_at: str
    content: str

    def __post_init__(self) -> None:
        if not DOCUMENT_ID.fullmatch(self.document_id):
            raise CorpusError("invalid_document", "document_id must be a stable slug")
        if not self.title.strip() or len(self.title) > 120:
            raise CorpusError("invalid_document", "title must contain 1 to 120 characters")
        if not self.source_uri.startswith("course://") or "#" not in self.source_uri:
            raise CorpusError("invalid_document", "source_uri must be course URI with anchor")
        try:
            parsed = datetime.fromisoformat(self.updated_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise CorpusError("invalid_document", "updated_at must be ISO-8601") from exc
        if parsed.tzinfo is None:
            raise CorpusError("invalid_document", "updated_at must include timezone")
        if not self.content.strip():
            raise CorpusError("invalid_document", "content must not be empty")


@dataclass(frozen=True)
class CorpusSnapshot:
    schema_version: int
    corpus_id: str
    documents: tuple[dict[str, str], ...]
    fingerprint: str


FIXTURE_DOCUMENTS = (
    CorpusDocument(
        "python-venv",
        "Python 虚拟环境",
        "course://python-engineering/package#virtual-environment",
        "2026-07-26T00:00:00Z",
        "虚拟环境隔离项目依赖。激活环境不等于安装依赖，仍要执行明确的安装命令。",
    ),
    CorpusDocument(
        "http-status",
        "HTTP 状态码边界",
        "course://web-core/http#status-codes",
        "2026-07-26T00:00:00Z",
        "401 表示缺少或无效身份，403 表示身份有效但权限不足，404 也可隐藏不可见资源。",
    ),
    CorpusDocument(
        "sqlite-transaction",
        "SQLite 事务",
        "course://cs-systems/transaction#rollback",
        "2026-07-26T00:00:00Z",
        "事务中途失败后执行回滚，才能避免只提交一半修改。SQLite 行为不能外推为所有数据库实现。",
    ),
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _document_record(document: CorpusDocument) -> dict[str, str]:
    return {
        "document_id": document.document_id,
        "title": document.title,
        "source_uri": document.source_uri,
        "updated_at": document.updated_at,
        "content": document.content,
        "content_sha256": _sha256_text(document.content),
    }


def build_snapshot(corpus_id: str, documents: Iterable[CorpusDocument]) -> CorpusSnapshot:
    if not DOCUMENT_ID.fullmatch(corpus_id):
        raise CorpusError("invalid_corpus", "corpus_id must be a stable slug")
    ordered = sorted(documents, key=lambda item: item.document_id)
    if not ordered:
        raise CorpusError("empty_corpus", "corpus must contain at least one document")
    ids = [document.document_id for document in ordered]
    if len(ids) != len(set(ids)):
        raise CorpusError("duplicate_document_id", "document_id must be unique")
    source_uris = [document.source_uri for document in ordered]
    if len(source_uris) != len(set(source_uris)):
        raise CorpusError("duplicate_source_uri", "source_uri must be unique")
    records = tuple(_document_record(document) for document in ordered)
    identity = {
        "schema_version": SCHEMA_VERSION,
        "corpus_id": corpus_id,
        "documents": records,
    }
    return CorpusSnapshot(
        SCHEMA_VERSION,
        corpus_id,
        records,
        hashlib.sha256(_canonical(identity)).hexdigest(),
    )


def snapshot_payload(snapshot: CorpusSnapshot) -> dict[str, Any]:
    return {
        "schema_version": snapshot.schema_version,
        "corpus_id": snapshot.corpus_id,
        "documents": list(snapshot.documents),
        "fingerprint": snapshot.fingerprint,
    }


def save_snapshot(snapshot: CorpusSnapshot, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _canonical(snapshot_payload(snapshot)) + b"\n"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary_name = temporary.name
            temporary.write(data)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def _require_exact_fields(payload: dict[str, Any], expected: set[str], code: str) -> None:
    if set(payload) != expected:
        raise CorpusError(code, "manifest fields do not match schema")


def load_snapshot(path: Path) -> CorpusSnapshot:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CorpusError("invalid_snapshot", "snapshot is not readable JSON") from exc
    if not isinstance(payload, dict):
        raise CorpusError("invalid_snapshot", "snapshot must be an object")
    _require_exact_fields(payload, SNAPSHOT_FIELDS, "invalid_snapshot")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise CorpusError("unsupported_schema", "snapshot schema version is unsupported")
    if not isinstance(payload["documents"], list) or not payload["documents"]:
        raise CorpusError("invalid_snapshot", "documents must be a non-empty list")

    documents: list[CorpusDocument] = []
    for raw in payload["documents"]:
        if not isinstance(raw, dict):
            raise CorpusError("invalid_snapshot", "document record must be an object")
        _require_exact_fields(raw, DOCUMENT_FIELDS, "invalid_snapshot")
        content = raw["content"]
        if not isinstance(content, str) or raw["content_sha256"] != _sha256_text(content):
            raise CorpusError("content_hash_mismatch", "document content hash does not match")
        documents.append(CorpusDocument(
            raw["document_id"],
            raw["title"],
            raw["source_uri"],
            raw["updated_at"],
            content,
        ))
    rebuilt = build_snapshot(payload["corpus_id"], documents)
    if payload["fingerprint"] != rebuilt.fingerprint:
        raise CorpusError("snapshot_fingerprint_mismatch", "snapshot fingerprint does not match")
    if list(rebuilt.documents) != payload["documents"]:
        raise CorpusError("noncanonical_order", "documents must use canonical document_id order")
    return rebuilt


def fixed_report() -> str:
    snapshot = build_snapshot("become-engineer-public", FIXTURE_DOCUMENTS)
    reordered = build_snapshot("become-engineer-public", reversed(FIXTURE_DOCUMENTS))
    return "\n".join([
        "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
        f"corpus=id:{snapshot.corpus_id},schema:{snapshot.schema_version},documents:{len(snapshot.documents)}",
        f"order={','.join(record['document_id'] for record in snapshot.documents)}",
        f"fingerprint={snapshot.fingerprint}",
        f"reordered=fingerprint-equal:{snapshot.fingerprint == reordered.fingerprint}",
        "identity=document-id+title+source-uri+updated-at+content+content-sha256",
        "validation=empty:false,duplicate-id:false,duplicate-source:false,extra-fields:false",
        "persistence=utf8-json,canonical:true,temporary-write:true,fsync:true,atomic-replace:true",
        "logs=content:none,source-uri:none,corpus-id:allowed,fingerprint:allowed,count:allowed",
        "invariants=source-before-index,content-hash-verified,input-order-independent,no-rag-generation,no-tools",
    ])


if __name__ == "__main__":
    print(fixed_report())
