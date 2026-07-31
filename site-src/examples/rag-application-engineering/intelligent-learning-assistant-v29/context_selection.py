"""Deterministic reranking, extractive compression and context selection."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Protocol


@dataclass(frozen=True)
class Candidate:
    chunk_id: str
    source_id: str
    version: int
    block_id: str
    page: int | None
    source_text: str
    start: int
    end: int
    retrieval_score: float

    @property
    def text(self) -> str:
        return self.source_text[self.start:self.end]


@dataclass(frozen=True)
class Evidence:
    chunk_id: str
    source_id: str
    version: int
    block_id: str
    page: int | None
    start: int
    end: int
    text: str
    rerank_score: float


class Reranker(Protocol):
    def score(self, query: str, candidate: Candidate) -> float: ...


class ContextCompressor(Protocol):
    def compress(self, query: str, candidate: Candidate, score: float) -> tuple[Evidence, ...]: ...


class FixedReranker:
    """Fixture adapter: validates second-stage contracts, not model quality."""

    def score(self, query: str, candidate: Candidate) -> float:
        terms = set(query.lower().split())
        overlap = sum(term in candidate.text.lower() for term in terms)
        return overlap * 10 + candidate.retrieval_score


class ExtractiveCompressor:
    def compress(self, query: str, candidate: Candidate, score: float) -> tuple[Evidence, ...]:
        terms = set(query.lower().split())
        evidence: list[Evidence] = []
        for match in re.finditer(r"[^。.!?]+[。.!?]?", candidate.text):
            sentence = match.group()
            if sentence.strip() and any(term in sentence.lower() for term in terms):
                start = candidate.start + match.start()
                end = candidate.start + match.end()
                evidence.append(
                    Evidence(
                        candidate.chunk_id,
                        candidate.source_id,
                        candidate.version,
                        candidate.block_id,
                        candidate.page,
                        start,
                        end,
                        candidate.source_text[start:end],
                        score,
                    )
                )
        return tuple(evidence)


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))


def _similarity(left: str, right: str) -> float:
    a, b = _tokens(left), _tokens(right)
    return len(a & b) / len(a | b) if a | b else 0.0


def select_context(
    query: str,
    candidates: tuple[Candidate, ...],
    reranker: Reranker,
    compressor: ContextCompressor,
    *,
    rerank_limit: int,
    char_budget: int,
    diversity: float = 0.35,
) -> dict[str, object]:
    ranked = sorted(
        ((reranker.score(query, candidate), candidate) for candidate in candidates),
        key=lambda row: (-row[0], row[1].chunk_id),
    )[:rerank_limit]
    extracted = [
        evidence
        for score, candidate in ranked
        for evidence in compressor.compress(query, candidate, score)
    ]
    deduped: list[Evidence] = []
    seen_coordinates: set[tuple[str, int, int, int]] = set()
    for evidence in extracted:
        identity = (evidence.source_id, evidence.version, evidence.start, evidence.end)
        if identity not in seen_coordinates:
            seen_coordinates.add(identity)
            deduped.append(evidence)
    selected: list[Evidence] = []
    remaining = list(deduped)
    used = 0
    while remaining:
        scored = [
            (
                item.rerank_score
                - diversity * max((_similarity(item.text, chosen.text) for chosen in selected), default=0.0),
                item,
            )
            for item in remaining
        ]
        _, best = max(scored, key=lambda row: (row[0], row[1].chunk_id))
        remaining.remove(best)
        if used + len(best.text) > char_budget:
            continue
        selected.append(best)
        used += len(best.text)
    if len(selected) > 2:
        ordered = [selected[0], *selected[2:], selected[1]]
    else:
        ordered = selected
    return {
        "retrieved": len(candidates),
        "reranked": len(ranked),
        "extracted": len(extracted),
        "deduped": len(deduped),
        "selected": tuple(ordered),
        "characters": used,
        "budget_ok": used <= char_budget,
    }


def citation_valid(evidence: Evidence, source_text: str) -> bool:
    return evidence.text == source_text[evidence.start:evidence.end]


def fixed_report() -> None:
    source = "Python venv isolates dependencies. Recreate from lock file. HTTP uses ports."
    candidates = (
        Candidate("c1", "guide", 2, "b1", 1, source, 0, len(source), 0.8),
        Candidate("c2", "guide", 2, "b1", 1, source, 0, 35, 0.7),
    )
    result = select_context(
        "python dependencies",
        candidates,
        FixedReranker(),
        ExtractiveCompressor(),
        rerank_limit=2,
        char_budget=80,
    )
    valid = all(citation_valid(item, source) for item in result["selected"])
    print(f"pipeline=retrieved:{result['retrieved']},reranked:{result['reranked']},extracted:{result['extracted']},deduped:{result['deduped']}")
    print(f"context=selected:{len(result['selected'])},characters:{result['characters']},budget-ok:{str(result['budget_ok']).lower()}")
    print(f"citation=source:guide,version:2,page:1,exact:{str(valid).lower()}")
    print("adapters=reranker:fixed,compressor:extractive,real-cross-encoder:false")


if __name__ == "__main__":
    fixed_report()
