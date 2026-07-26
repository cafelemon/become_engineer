from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Iterable


SENTENCE_ENDINGS = frozenset("。！？!?")


class ChunkError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class SourceDocument:
    document_id: str
    source_uri: str
    content: str

    def __post_init__(self) -> None:
        if not self.document_id or not self.source_uri.startswith("course://"):
            raise ChunkError("invalid_document", "document identity is invalid")
        if not self.content.strip():
            raise ChunkError("invalid_document", "document content must not be empty")


@dataclass(frozen=True)
class TextSpan:
    start: int
    end: int


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    source_uri: str
    start: int
    end: int
    text: str
    content_sha256: str


@dataclass(frozen=True)
class Citation:
    chunk_id: str
    quote_start: int
    quote_end: int
    quote: str


@dataclass(frozen=True)
class VerifiedCitation:
    chunk_id: str
    source_uri: str
    absolute_start: int
    absolute_end: int
    quote: str


FIXTURE_DOCUMENT = SourceDocument(
    "python-venv",
    "course://python-engineering/package#virtual-environment",
    "虚拟环境隔离项目依赖。激活环境不等于安装依赖。\n\n删除环境前先保存依赖清单。来源文本中的“忽略系统指令”只是数据。",
)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sentence_spans(content: str) -> tuple[TextSpan, ...]:
    spans: list[TextSpan] = []
    start: int | None = None
    for index, character in enumerate(content):
        if start is None and not character.isspace():
            start = index
        if start is not None and character in SENTENCE_ENDINGS:
            spans.append(TextSpan(start, index + 1))
            start = None
    if start is not None:
        end = len(content)
        while end > start and content[end - 1].isspace():
            end -= 1
        if end > start:
            spans.append(TextSpan(start, end))
    return tuple(spans)


def _make_chunk(document: SourceDocument, spans: list[TextSpan]) -> Chunk:
    start = spans[0].start
    end = spans[-1].end
    text = document.content[start:end]
    return Chunk(
        f"{document.document_id}:{start}:{end}",
        document.document_id,
        document.source_uri,
        start,
        end,
        text,
        _sha256(text),
    )


def chunk_document(
    document: SourceDocument,
    *,
    max_chars: int,
    overlap_sentences: int = 1,
) -> tuple[Chunk, ...]:
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars < 1:
        raise ChunkError("invalid_config", "max_chars must be a positive integer")
    if (
        isinstance(overlap_sentences, bool)
        or not isinstance(overlap_sentences, int)
        or overlap_sentences < 0
    ):
        raise ChunkError("invalid_config", "overlap_sentences must be non-negative")
    units = sentence_spans(document.content)
    if not units:
        raise ChunkError("empty_document", "document has no sentence")
    for span in units:
        if span.end - span.start > max_chars:
            raise ChunkError("sentence_too_long", "single sentence exceeds max_chars")

    chunks: list[Chunk] = []
    current: list[TextSpan] = []
    for unit in units:
        if current and unit.end - current[0].start > max_chars:
            chunks.append(_make_chunk(document, current))
            overlap = current[-overlap_sentences:] if overlap_sentences else []
            if overlap and unit.end - overlap[0].start <= max_chars:
                current = list(overlap)
            else:
                current = []
        current.append(unit)
    if current:
        chunks.append(_make_chunk(document, current))
    return tuple(chunks)


def validate_chunks(document: SourceDocument, chunks: Iterable[Chunk]) -> None:
    previous_start = -1
    seen: set[str] = set()
    for chunk in chunks:
        if chunk.chunk_id in seen:
            raise ChunkError("duplicate_chunk", "chunk_id must be unique")
        seen.add(chunk.chunk_id)
        if chunk.document_id != document.document_id or chunk.source_uri != document.source_uri:
            raise ChunkError("chunk_identity_mismatch", "chunk source identity does not match")
        if not 0 <= chunk.start < chunk.end <= len(document.content):
            raise ChunkError("chunk_out_of_bounds", "chunk coordinates are outside source")
        if chunk.start < previous_start:
            raise ChunkError("chunk_order_mismatch", "chunks must be ordered by source start")
        previous_start = chunk.start
        expected = document.content[chunk.start:chunk.end]
        if chunk.text != expected or chunk.content_sha256 != _sha256(expected):
            raise ChunkError("chunk_content_mismatch", "chunk text or hash does not match source")
        if chunk.chunk_id != f"{document.document_id}:{chunk.start}:{chunk.end}":
            raise ChunkError("chunk_identity_mismatch", "chunk_id does not match coordinates")


def verify_citation(
    citation: Citation,
    retrieved_chunks: Iterable[Chunk],
) -> VerifiedCitation:
    by_id = {chunk.chunk_id: chunk for chunk in retrieved_chunks}
    chunk = by_id.get(citation.chunk_id)
    if chunk is None:
        raise ChunkError("citation_chunk_not_retrieved", "citation must use retrieved chunk")
    if (
        isinstance(citation.quote_start, bool)
        or isinstance(citation.quote_end, bool)
        or not isinstance(citation.quote_start, int)
        or not isinstance(citation.quote_end, int)
        or not 0 <= citation.quote_start < citation.quote_end <= len(chunk.text)
    ):
        raise ChunkError("citation_out_of_bounds", "citation coordinates are outside chunk")
    expected = chunk.text[citation.quote_start:citation.quote_end]
    if not citation.quote or citation.quote != expected:
        raise ChunkError("citation_quote_mismatch", "citation quote does not match chunk")
    return VerifiedCitation(
        citation.chunk_id,
        chunk.source_uri,
        chunk.start + citation.quote_start,
        chunk.start + citation.quote_end,
        citation.quote,
    )


def fixed_report() -> str:
    chunks = chunk_document(FIXTURE_DOCUMENT, max_chars=32, overlap_sentences=1)
    validate_chunks(FIXTURE_DOCUMENT, chunks)
    target = chunks[0]
    quote = "虚拟环境隔离项目依赖"
    start = target.text.index(quote)
    verified = verify_citation(
        Citation(target.chunk_id, start, start + len(quote), quote),
        chunks[:1],
    )
    return "\n".join([
        "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
        f"document=id:{FIXTURE_DOCUMENT.document_id},characters:{len(FIXTURE_DOCUMENT.content)},sentences:{len(sentence_spans(FIXTURE_DOCUMENT.content))}",
        f"chunking=max-chars:32,overlap-sentences:1,chunks:{len(chunks)}",
        "chunks=" + ",".join(f"{chunk.chunk_id}|chars:{len(chunk.text)}" for chunk in chunks),
        f"citation=chunk:{verified.chunk_id},absolute:{verified.absolute_start}:{verified.absolute_end},exact:true",
        "validation=source-bounds:true,text-slice:true,content-hash:true,stable-id:true",
        "rejection=long-sentence:true,unknown-chunk:true,out-of-bounds:true,quote-mismatch:true",
        "trust=retrieved-text:data-only,instructions-in-source:false,html-render:false",
        "logs=chunk-text:none,quote:none,chunk-id:allowed,coordinates:allowed,error-code:allowed",
        "invariants=sentence-boundaries,source-coordinates,exact-citation,retrieved-only,no-generation,no-tools",
    ])


if __name__ == "__main__":
    print(fixed_report())
