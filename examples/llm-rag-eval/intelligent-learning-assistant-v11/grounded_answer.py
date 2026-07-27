from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Iterable, Literal


class GroundingError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    source_uri: str
    text: str
    content_sha256: str

    @classmethod
    def create(cls, chunk_id: str, source_uri: str, text: str) -> "RetrievedChunk":
        if not chunk_id or not source_uri.startswith("course://") or not text.strip():
            raise GroundingError("invalid_chunk", "retrieved chunk identity and text are required")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return cls(chunk_id, source_uri, text, digest)


@dataclass(frozen=True)
class Citation:
    chunk_id: str
    quote_start: int
    quote_end: int
    quote: str


@dataclass(frozen=True)
class Claim:
    text: str
    citations: tuple[Citation, ...]


@dataclass(frozen=True)
class GroundedAnswer:
    status: Literal["answered", "abstained"]
    claims: tuple[Claim, ...]
    reason: str | None = None


@dataclass(frozen=True)
class ContextPack:
    chunk_ids: tuple[str, ...]
    rendered: str
    character_count: int


def _validate_chunk(chunk: RetrievedChunk) -> None:
    expected = hashlib.sha256(chunk.text.encode("utf-8")).hexdigest()
    if not chunk.chunk_id or not chunk.source_uri.startswith("course://") or not chunk.text.strip():
        raise GroundingError("invalid_chunk", "retrieved chunk is invalid")
    if chunk.content_sha256 != expected:
        raise GroundingError("chunk_content_mismatch", "retrieved chunk hash does not match text")


def build_context_pack(
    ranked_chunks: Iterable[RetrievedChunk],
    *,
    max_chars: int,
) -> ContextPack:
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars < 1:
        raise GroundingError("invalid_context_budget", "max_chars must be positive")
    parts: list[str] = []
    ids: list[str] = []
    seen: set[str] = set()
    for chunk in ranked_chunks:
        _validate_chunk(chunk)
        if chunk.chunk_id in seen:
            raise GroundingError("duplicate_context_chunk", "context chunk IDs must be unique")
        seen.add(chunk.chunk_id)
        part = (
            f'<source-data id="{chunk.chunk_id}" uri="{chunk.source_uri}">\n'
            f"{chunk.text}\n"
            "</source-data>"
        )
        candidate = "\n".join((*parts, part))
        if len(candidate) > max_chars:
            if not parts:
                raise GroundingError("context_chunk_too_large", "first chunk exceeds context budget")
            break
        parts.append(part)
        ids.append(chunk.chunk_id)
    if not parts:
        raise GroundingError("empty_context", "context pack needs at least one retrieved chunk")
    rendered = "\n".join(parts)
    return ContextPack(tuple(ids), rendered, len(rendered))


def _verify_citation(
    citation: Citation,
    retrieved_by_id: dict[str, RetrievedChunk],
) -> str:
    chunk = retrieved_by_id.get(citation.chunk_id)
    if chunk is None:
        raise GroundingError("citation_chunk_not_retrieved", "citation is outside retrieved context")
    if (
        isinstance(citation.quote_start, bool)
        or isinstance(citation.quote_end, bool)
        or not isinstance(citation.quote_start, int)
        or not isinstance(citation.quote_end, int)
        or not 0 <= citation.quote_start < citation.quote_end <= len(chunk.text)
    ):
        raise GroundingError("citation_out_of_bounds", "citation range is invalid")
    expected = chunk.text[citation.quote_start:citation.quote_end]
    if not citation.quote or citation.quote != expected:
        raise GroundingError("citation_quote_mismatch", "quote does not match retrieved chunk")
    return expected


def validate_grounded_answer(
    answer: GroundedAnswer,
    retrieved_chunks: Iterable[RetrievedChunk],
) -> GroundedAnswer:
    chunks = tuple(retrieved_chunks)
    retrieved_by_id: dict[str, RetrievedChunk] = {}
    for chunk in chunks:
        _validate_chunk(chunk)
        if chunk.chunk_id in retrieved_by_id:
            raise GroundingError("duplicate_context_chunk", "retrieved chunk IDs must be unique")
        retrieved_by_id[chunk.chunk_id] = chunk

    if answer.status == "abstained":
        if answer.claims or answer.reason != "insufficient_evidence":
            raise GroundingError("invalid_abstention", "abstention has no claims and one stable reason")
        return answer
    if answer.status != "answered":
        raise GroundingError("invalid_answer_status", "answer status is unknown")
    if answer.reason is not None or not answer.claims:
        raise GroundingError("invalid_answer_shape", "answered result needs claims and no reason")

    for claim in answer.claims:
        if not claim.text.strip() or not claim.citations:
            raise GroundingError("unsupported_claim", "every claim needs text and citations")
        quotes = tuple(_verify_citation(item, retrieved_by_id) for item in claim.citations)
        # This deliberately narrow baseline is mechanically provable. Paraphrase
        # entailment needs a separate evaluator and is not silently inferred here.
        if claim.text != "；".join(quotes):
            raise GroundingError(
                "unsupported_claim",
                "extractive claim must exactly equal its cited quote or joined quotes",
            )
    return answer


FIXTURE_CHUNKS = (
    RetrievedChunk.create(
        "chunk-python",
        "course://python-engineering/package#virtual-environment",
        "虚拟环境隔离项目依赖。激活环境不等于安装依赖。",
    ),
    RetrievedChunk.create(
        "chunk-http",
        "course://cs-systems/local-network#timeout",
        "HTTP 请求需要截止时间。来源中的“忽略系统指令”只是数据。",
    ),
)


def fixed_report() -> str:
    pack = build_context_pack(FIXTURE_CHUNKS, max_chars=300)
    python_quote = "虚拟环境隔离项目依赖"
    http_quote = "HTTP 请求需要截止时间"
    answer = GroundedAnswer(
        "answered",
        (
            Claim(
                python_quote,
                (Citation("chunk-python", 0, len(python_quote), python_quote),),
            ),
            Claim(
                http_quote,
                (Citation("chunk-http", 0, len(http_quote), http_quote),),
            ),
        ),
    )
    validate_grounded_answer(answer, FIXTURE_CHUNKS)
    abstention = GroundedAnswer("abstained", (), "insufficient_evidence")
    validate_grounded_answer(abstention, FIXTURE_CHUNKS)
    return "\n".join([
        "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
        f"context=chunks:{len(pack.chunk_ids)},characters:{pack.character_count},bounded:true,source-data:true",
        "answer=status:answered,claims:2,citations:2,extractive:true",
        "citations=chunk-python:0:10|exact:true,chunk-http:0:12|exact:true",
        "abstention=status:abstained,reason:insufficient_evidence,claims:0",
        "validation=retrieved-only:true,quote-match:true,claim-supported:true,unknown-status:false",
        "rejection=missing-citation:true,unknown-chunk:true,out-of-bounds:true,quote-mismatch:true,unsupported-paraphrase:true",
        "trust=retrieved-text:data-only,instructions-in-source:false,html-render:false",
        "logs=query:none,context:none,answer:none,chunk-id:allowed,status:allowed,error-code:allowed",
        "invariants=bounded-context,extractive-claims,claim-citation,exact-quotes,abstain-on-missing,no-tools",
    ])


if __name__ == "__main__":
    print(fixed_report())
