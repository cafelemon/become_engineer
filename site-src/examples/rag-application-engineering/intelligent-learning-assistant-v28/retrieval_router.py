"""Strict query planning, ACL-first multi-route retrieval and RRF fusion."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


@dataclass(frozen=True)
class Document:
    chunk_id: str
    owner_id: str
    course: str
    text: str
    vector: tuple[float, ...]
    parent_id: str | None = None


@dataclass(frozen=True)
class RetrievalPlan:
    normalized_query: str
    strategy: str
    lexical_k: int
    vector_k: int
    max_candidates: int
    filters: tuple[tuple[str, str], ...] = ()
    rewrites: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.strategy not in {"lexical", "vector", "hybrid", "multi_query", "decompose"}:
            raise ValueError("unknown_strategy")
        if min(self.lexical_k, self.vector_k, self.max_candidates) < 0:
            raise ValueError("negative_budget")
        if self.lexical_k + self.vector_k > 40 or self.max_candidates > 40:
            raise ValueError("candidate_budget")
        if any(key not in {"course"} for key, _ in self.filters):
            raise ValueError("unknown_filter")


def normalize_query(query: str) -> str:
    return " ".join(query.strip().lower().split())


def route(query: str, filters: dict[str, str] | None = None) -> RetrievalPlan:
    normalized = normalize_query(query)
    safe_filters = tuple(sorted((filters or {}).items()))
    if re.search(r"\b[A-Z]{2,}-?\d+\b", query) or "错误码" in query:
        return RetrievalPlan(normalized, "lexical", 8, 0, 8, safe_filters)
    if "分别" in normalized or "比较" in normalized:
        parts = tuple(part.strip() for part in re.split(r"以及|和|与", normalized) if part.strip())
        return RetrievalPlan(normalized, "decompose", 6, 6, 12, safe_filters, parts[:3])
    if "换句话" in normalized or "同义" in normalized:
        return RetrievalPlan(normalized, "multi_query", 6, 6, 12, safe_filters, (normalized.replace("换句话", ""),))
    return RetrievalPlan(normalized, "hybrid", 8, 8, 12, safe_filters)


def _dot(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right):
        raise ValueError("vector_dimension")
    return sum(a * b for a, b in zip(left, right))


def acl_filter(documents: Iterable[Document], subject_id: str, filters: tuple[tuple[str, str], ...]) -> tuple[Document, ...]:
    values = dict(filters)
    return tuple(
        document
        for document in documents
        if document.owner_id == subject_id
        and (not values.get("course") or document.course == values["course"])
    )


def lexical_rank(query: str, documents: tuple[Document, ...], limit: int) -> tuple[str, ...]:
    terms = set(normalize_query(query).split())
    scored = [
        (sum(term in document.text.lower() for term in terms), document.chunk_id)
        for document in documents
    ]
    return tuple(chunk_id for score, chunk_id in sorted(scored, key=lambda row: (-row[0], row[1])) if score > 0)[:limit]


def vector_rank(query_vector: tuple[float, ...], documents: tuple[Document, ...], limit: int) -> tuple[str, ...]:
    return tuple(
        document.chunk_id
        for document in sorted(documents, key=lambda document: (-_dot(query_vector, document.vector), document.chunk_id))[:limit]
    )


def rrf(rankings: tuple[tuple[str, ...], ...], limit: int, k: int = 60) -> tuple[str, ...]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking, 1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1 / (k + rank)
    return tuple(chunk_id for chunk_id, _ in sorted(scores.items(), key=lambda row: (-row[1], row[0])))[:limit]


def retrieve(
    plan: RetrievalPlan,
    subject_id: str,
    documents: tuple[Document, ...],
    query_vector: tuple[float, ...],
) -> dict[str, object]:
    authorized = acl_filter(documents, subject_id, plan.filters)
    queries = (plan.normalized_query, *plan.rewrites)
    lexical_lists = tuple(lexical_rank(query, authorized, plan.lexical_k) for query in queries if plan.lexical_k)
    vector_list = vector_rank(query_vector, authorized, plan.vector_k) if plan.vector_k else ()
    fused = rrf((*lexical_lists, vector_list), plan.max_candidates)
    by_id = {document.chunk_id: document for document in authorized}
    parents = tuple(dict.fromkeys(by_id[chunk_id].parent_id or chunk_id for chunk_id in fused))
    return {
        "authorized": len(authorized),
        "lexical_candidates": sum(len(items) for items in lexical_lists),
        "vector_candidates": len(vector_list),
        "fused_candidates": len(fused),
        "chunk_ids": fused,
        "parent_ids": parents,
        "budget_ok": len(fused) <= plan.max_candidates,
    }


def fixed_report() -> None:
    documents = (
        Document("python-1", "learner-a", "python", "python venv environment", (1.0, 0.0), "python-parent"),
        Document("http-1", "learner-a", "web", "http port status", (0.0, 1.0), "http-parent"),
        Document("private-1", "learner-b", "python", "python private secret", (1.0, 0.0), "private-parent"),
    )
    plan = route("Python venv", {"course": "python"})
    result = retrieve(plan, "learner-a", documents, (1.0, 0.0))
    print(f"plan=strategy:{plan.strategy},lexical:{plan.lexical_k},vector:{plan.vector_k},max:{plan.max_candidates}")
    print(f"filter=authorized:{result['authorized']},private-candidate:{'private-1' in result['chunk_ids']}")
    print(f"candidates=lexical:{result['lexical_candidates']},vector:{result['vector_candidates']},fused:{result['fused_candidates']}")
    print(f"result={','.join(result['chunk_ids'])},budget-ok:{str(result['budget_ok']).lower()},sql-from-model:false")


if __name__ == "__main__":
    fixed_report()
