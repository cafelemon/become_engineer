from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping, Protocol, Sequence


class RetrievalError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class EmbeddingAdapter(Protocol):
    def embed(self, texts: Sequence[str]) -> tuple[tuple[float, ...], ...]:
        """Return one finite, non-zero vector for every input text."""


@dataclass(frozen=True)
class FixtureEmbeddingAdapter:
    vectors: Mapping[str, tuple[float, ...]]

    def embed(self, texts: Sequence[str]) -> tuple[tuple[float, ...], ...]:
        output: list[tuple[float, ...]] = []
        for text in texts:
            if text not in self.vectors:
                raise RetrievalError("fixture_text_unknown", "fixture has no vector for text")
            output.append(tuple(self.vectors[text]))
        return tuple(output)


@dataclass(frozen=True)
class VectorRecord:
    chunk_id: str
    vector: tuple[float, ...]


@dataclass(frozen=True)
class VectorHit:
    chunk_id: str
    score: float


@dataclass(frozen=True)
class FusedHit:
    chunk_id: str
    score: float
    ranks: tuple[int | None, ...]


def _validate_top_k(top_k: int) -> None:
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        raise RetrievalError("invalid_top_k", "top_k must be a positive integer")


def validate_vector(vector: Sequence[float], *, dimension: int | None = None) -> tuple[float, ...]:
    if not vector:
        raise RetrievalError("invalid_vector", "vector must not be empty")
    values: list[float] = []
    for value in vector:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise RetrievalError("invalid_vector", "vector values must be real numbers")
        number = float(value)
        if not math.isfinite(number):
            raise RetrievalError("invalid_vector", "vector values must be finite")
        values.append(number)
    if dimension is not None and len(values) != dimension:
        raise RetrievalError("dimension_mismatch", "vectors must share one dimension")
    if math.sqrt(sum(value * value for value in values)) == 0:
        raise RetrievalError("zero_vector", "cosine similarity is undefined for zero vector")
    return tuple(values)


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    left_values = validate_vector(left)
    right_values = validate_vector(right, dimension=len(left_values))
    numerator = sum(a * b for a, b in zip(left_values, right_values, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left_values))
    right_norm = math.sqrt(sum(value * value for value in right_values))
    return numerator / (left_norm * right_norm)


class VectorIndex:
    def __init__(self, records: Iterable[VectorRecord]) -> None:
        materialized = tuple(records)
        if not materialized:
            raise RetrievalError("empty_index", "vector index must not be empty")
        dimension: int | None = None
        seen: set[str] = set()
        normalized: list[VectorRecord] = []
        for record in materialized:
            if not record.chunk_id or record.chunk_id in seen:
                raise RetrievalError("duplicate_chunk", "chunk IDs must be non-empty and unique")
            seen.add(record.chunk_id)
            vector = validate_vector(record.vector, dimension=dimension)
            dimension = len(vector) if dimension is None else dimension
            normalized.append(VectorRecord(record.chunk_id, vector))
        self._records = tuple(normalized)
        self.dimension = dimension

    @classmethod
    def from_texts(
        cls,
        chunks: Mapping[str, str],
        adapter: EmbeddingAdapter,
    ) -> "VectorIndex":
        if not chunks:
            raise RetrievalError("empty_index", "chunks must not be empty")
        ordered = tuple(sorted(chunks.items()))
        vectors = adapter.embed(tuple(text for _, text in ordered))
        if len(vectors) != len(ordered):
            raise RetrievalError("adapter_shape_mismatch", "adapter returned wrong batch size")
        return cls(
            VectorRecord(chunk_id, tuple(vector))
            for (chunk_id, _), vector in zip(ordered, vectors, strict=True)
        )

    def search(self, query_vector: Sequence[float], *, top_k: int) -> tuple[VectorHit, ...]:
        _validate_top_k(top_k)
        query = validate_vector(query_vector, dimension=self.dimension)
        hits = [
            VectorHit(record.chunk_id, cosine_similarity(query, record.vector))
            for record in self._records
        ]
        hits.sort(key=lambda hit: (-hit.score, hit.chunk_id))
        return tuple(hits[:top_k])


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[str]],
    *,
    allowed_chunk_ids: set[str],
    rank_constant: int = 60,
    top_k: int,
) -> tuple[FusedHit, ...]:
    _validate_top_k(top_k)
    if (
        isinstance(rank_constant, bool)
        or not isinstance(rank_constant, int)
        or rank_constant < 1
    ):
        raise RetrievalError("invalid_rank_constant", "rank_constant must be positive")
    if not rankings:
        raise RetrievalError("empty_rankings", "at least one ranking is required")

    scores: dict[str, float] = {}
    ranks_by_id: dict[str, list[int | None]] = {}
    for list_index, ranking in enumerate(rankings):
        seen: set[str] = set()
        for rank, chunk_id in enumerate(ranking, start=1):
            if chunk_id in seen:
                raise RetrievalError("duplicate_ranked_chunk", "ranking contains a duplicate")
            if chunk_id not in allowed_chunk_ids:
                raise RetrievalError("unknown_ranked_chunk", "ranking contains an unknown chunk")
            seen.add(chunk_id)
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (rank_constant + rank)
            ranks_by_id.setdefault(chunk_id, [None] * len(rankings))[list_index] = rank

    hits = [
        FusedHit(chunk_id, score, tuple(ranks_by_id[chunk_id]))
        for chunk_id, score in scores.items()
    ]
    hits.sort(key=lambda hit: (-hit.score, hit.chunk_id))
    return tuple(hits[:top_k])


FIXTURE_VECTORS = {
    "Python 虚拟环境隔离依赖": (0.8, 0.2),
    "HTTP 超时需要截止时间": (1.0, 0.0),
    "SQLite 事务失败后回滚": (0.0, 1.0),
    "连接为什么超时": (1.0, 0.0),
    "相同方向 A": (1.0, 1.0),
    "相同方向 B": (2.0, 2.0),
}


def fixed_report() -> str:
    chunks = {
        "chunk-http": "HTTP 超时需要截止时间",
        "chunk-python": "Python 虚拟环境隔离依赖",
        "chunk-sqlite": "SQLite 事务失败后回滚",
    }
    adapter = FixtureEmbeddingAdapter(FIXTURE_VECTORS)
    index = VectorIndex.from_texts(chunks, adapter)
    query_vector = adapter.embed(("连接为什么超时",))[0]
    vector_hits = index.search(query_vector, top_k=3)
    lexical = ("chunk-python", "chunk-http", "chunk-sqlite")
    vector = tuple(hit.chunk_id for hit in vector_hits)
    fused = reciprocal_rank_fusion(
        (lexical, vector),
        allowed_chunk_ids=set(chunks),
        rank_constant=60,
        top_k=3,
    )
    return "\n".join([
        "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
        "embedding=adapter:fixture,batch:true,dimension:2,semantic-claim:false,provider-call:false",
        "vector-ranking=" + ",".join(hit.chunk_id for hit in vector_hits),
        "vector-scores=" + ",".join(f"{hit.chunk_id}:{hit.score:.6f}" for hit in vector_hits),
        "lexical-ranking=" + ",".join(lexical),
        "fusion=method:rrf,rank-constant:60,top-k:3",
        "fused-ranking=" + ",".join(hit.chunk_id for hit in fused),
        "fused-ranks=" + ",".join(
            f"{hit.chunk_id}:{'/'.join('-' if rank is None else str(rank) for rank in hit.ranks)}"
            for hit in fused
        ),
        "validation=finite:true,dimension:true,nonzero:true,bool-rejected:true,stable-ties:true",
        "rejection=unknown-fixture:true,batch-shape:true,duplicate-rank:true,unknown-rank:true",
        "logs=query-text:none,chunk-text:none,vectors:none,chunk-id:allowed,score:allowed,error-code:allowed",
        "invariants=replaceable-adapter,cosine,stable-top-k,rrf-ranks,no-semantic-claim,no-generation,no-tools",
    ])


if __name__ == "__main__":
    print(fixed_report())
