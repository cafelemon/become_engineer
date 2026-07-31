"""PostgreSQL/pgvector index lifecycle with strict embedding contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector


@dataclass(frozen=True)
class EmbeddingContract:
    model_name: str
    model_version: str
    dimension: int
    normalized: bool
    distance: str = "cosine"

    def validate(self, vector: tuple[float, ...]) -> None:
        if self.dimension != 3:
            raise ValueError("unsupported_dimension")
        if len(vector) != self.dimension:
            raise ValueError("embedding_dimension")
        if self.distance != "cosine":
            raise ValueError("unsupported_distance")


class VectorStore:
    def __init__(self, database_url: str) -> None:
        self.db = psycopg.connect(database_url, autocommit=False)
        self._vector_registered = False

    def close(self) -> None:
        self.db.close()

    def migrate(self) -> None:
        sql = Path(__file__).with_name("migration.sql").read_text()
        with self.db.transaction():
            self.db.execute(sql)
        if not self._vector_registered:
            register_vector(self.db)
            self._vector_registered = True

    def reset(self) -> None:
        with self.db.transaction():
            self.db.execute("TRUNCATE chunk_embeddings, embedding_indexes")

    def create_index(self, index_id: str, contract: EmbeddingContract) -> None:
        contract.validate((1.0, 0.0, 0.0))
        with self.db.transaction():
            self.db.execute(
                """
                INSERT INTO embedding_indexes
                  (index_id,model_name,model_version,dimension,normalized,distance,status)
                VALUES (%s,%s,%s,%s,%s,%s,'building')
                """,
                (
                    index_id,
                    contract.model_name,
                    contract.model_version,
                    contract.dimension,
                    contract.normalized,
                    contract.distance,
                ),
            )

    def _contract(self, index_id: str) -> EmbeddingContract:
        row = self.db.execute(
            "SELECT model_name,model_version,dimension,normalized,distance FROM embedding_indexes WHERE index_id=%s",
            (index_id,),
        ).fetchone()
        if not row:
            raise ValueError("index_not_found")
        return EmbeddingContract(*row)

    def add(
        self,
        index_id: str,
        rows: Iterable[tuple[str, str, str, int, str, tuple[float, ...]]],
    ) -> None:
        contract = self._contract(index_id)
        values = tuple(rows)
        for row in values:
            contract.validate(row[-1])
        with self.db.transaction():
            with self.db.cursor() as cursor:
                cursor.executemany(
                    """
                    INSERT INTO chunk_embeddings
                      (index_id,chunk_id,owner_id,source_id,source_version,text_value,embedding)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT(index_id,chunk_id) DO UPDATE
                      SET text_value=EXCLUDED.text_value, embedding=EXCLUDED.embedding
                    """,
                    [(index_id, *row[:-1], Vector(list(row[-1]))) for row in values],
                )

    def mark_ready(self, index_id: str) -> None:
        with self.db.transaction():
            self.db.execute(
                "UPDATE embedding_indexes SET status='ready' WHERE index_id=%s AND status='building'",
                (index_id,),
            )

    def activate(self, index_id: str) -> None:
        with self.db.transaction():
            status = self.db.execute(
                "SELECT status FROM embedding_indexes WHERE index_id=%s FOR UPDATE",
                (index_id,),
            ).fetchone()
            if not status or status[0] not in {"ready", "active"}:
                raise ValueError("index_not_ready")
            self.db.execute(
                "UPDATE embedding_indexes SET status='retired' WHERE status='active' AND index_id<>%s",
                (index_id,),
            )
            self.db.execute(
                "UPDATE embedding_indexes SET status='active' WHERE index_id=%s",
                (index_id,),
            )

    def active_index(self) -> str | None:
        row = self.db.execute(
            "SELECT index_id FROM embedding_indexes WHERE status='active'"
        ).fetchone()
        return row[0] if row else None

    def search(
        self, owner_id: str, query: tuple[float, ...], limit: int = 3
    ) -> list[tuple[str, float]]:
        index_id = self.active_index()
        if not index_id:
            raise ValueError("active_index_missing")
        self._contract(index_id).validate(query)
        rows = self.db.execute(
            """
            SELECT chunk_id, embedding <=> %s AS distance
            FROM chunk_embeddings
            WHERE owner_id=%s AND index_id=%s
            ORDER BY embedding <=> %s, chunk_id
            LIMIT %s
            """,
            (Vector(list(query)), owner_id, index_id, Vector(list(query)), limit),
        ).fetchall()
        return [(row[0], float(row[1])) for row in rows]
