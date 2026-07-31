"""Five chunking strategies with shared coordinates and deterministic evaluation."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import re
from typing import Callable, Protocol


@dataclass(frozen=True)
class Block:
    block_id: str
    text: str
    heading_path: tuple[str, ...] = ()
    page: int | None = None


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    block_id: str
    start: int
    end: int
    text: str
    strategy_version: str
    heading_path: tuple[str, ...] = ()
    page: int | None = None
    parent_id: str | None = None


class Chunker(Protocol):
    version: str

    def chunk(self, blocks: tuple[Block, ...]) -> tuple[Chunk, ...]: ...


def _chunk(block: Block, start: int, end: int, version: str, parent_id: str | None = None) -> Chunk:
    identity = f"{block.block_id}:{start}:{end}:{version}:{parent_id or '-'}"
    return Chunk(
        chunk_id=hashlib.sha256(identity.encode()).hexdigest()[:12],
        block_id=block.block_id,
        start=start,
        end=end,
        text=block.text[start:end],
        strategy_version=version,
        heading_path=block.heading_path,
        page=block.page,
        parent_id=parent_id,
    )


class FixedWindowChunker:
    def __init__(self, size: int, overlap: int = 0) -> None:
        if size <= 0 or overlap < 0 or overlap >= size:
            raise ValueError("invalid_window")
        self.size, self.overlap = size, overlap
        self.version = f"fixed-v1:size={size}:overlap={overlap}"

    def chunk(self, blocks: tuple[Block, ...]) -> tuple[Chunk, ...]:
        result: list[Chunk] = []
        step = self.size - self.overlap
        for block in blocks:
            for start in range(0, len(block.text), step):
                end = min(start + self.size, len(block.text))
                result.append(_chunk(block, start, end, self.version))
                if end == len(block.text):
                    break
        return tuple(result)


class RecursiveChunker:
    def __init__(self, max_chars: int) -> None:
        self.max_chars = max_chars
        self.version = f"recursive-v1:max={max_chars}"

    def chunk(self, blocks: tuple[Block, ...]) -> tuple[Chunk, ...]:
        result: list[Chunk] = []
        for block in blocks:
            cursor = 0
            while cursor < len(block.text):
                limit = min(cursor + self.max_chars, len(block.text))
                if limit < len(block.text):
                    candidates = [
                        block.text.rfind(separator, cursor, limit)
                        for separator in ("\n\n", "\n", "。", "；", " ")
                    ]
                    boundary = max(candidates)
                    if boundary > cursor:
                        limit = boundary + 1
                result.append(_chunk(block, cursor, limit, self.version))
                cursor = limit
        return tuple(result)


class StructureAwareChunker:
    version = "structure-v1:heading+page"

    def chunk(self, blocks: tuple[Block, ...]) -> tuple[Chunk, ...]:
        return tuple(_chunk(block, 0, len(block.text), self.version) for block in blocks)


def cosine_distance(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("embedding_dimension")
    dot = sum(a * b for a, b in zip(left, right))
    nl = math.sqrt(sum(value * value for value in left))
    nr = math.sqrt(sum(value * value for value in right))
    if not nl or not nr:
        raise ValueError("zero_embedding")
    return 1 - dot / (nl * nr)


class SemanticBreakpointChunker:
    def __init__(self, embed: Callable[[str], tuple[float, ...]], threshold: float) -> None:
        self.embed, self.threshold = embed, threshold
        self.version = f"semantic-v1:adapter=fixed:threshold={threshold:.2f}"

    def chunk(self, blocks: tuple[Block, ...]) -> tuple[Chunk, ...]:
        result: list[Chunk] = []
        for block in blocks:
            spans = [(match.start(), match.end()) for match in re.finditer(r"[^。.!?]+[。.!?]?", block.text) if match.group().strip()]
            start = spans[0][0] if spans else 0
            for current, following in zip(spans, spans[1:]):
                left = block.text[current[0]:current[1]]
                right = block.text[following[0]:following[1]]
                if cosine_distance(self.embed(left), self.embed(right)) > self.threshold:
                    result.append(_chunk(block, start, current[1], self.version))
                    start = following[0]
            if spans:
                result.append(_chunk(block, start, spans[-1][1], self.version))
        return tuple(result)


class ParentChildChunker:
    def __init__(self, child_size: int) -> None:
        self.child_size = child_size
        self.version = f"parent-child-v1:child={child_size}"

    def chunk(self, blocks: tuple[Block, ...]) -> tuple[Chunk, ...]:
        children: list[Chunk] = []
        for block in blocks:
            parent_id = hashlib.sha256(f"parent:{block.block_id}:{block.text}".encode()).hexdigest()[:12]
            for start in range(0, len(block.text), self.child_size):
                children.append(
                    _chunk(block, start, min(start + self.child_size, len(block.text)), self.version, parent_id)
                )
        return tuple(children)


def evaluate(chunks: tuple[Chunk, ...], gold_boundaries: set[tuple[str, int]], relevant_phrase: str) -> dict[str, float]:
    if not chunks:
        raise ValueError("chunks_required")
    predicted = {(chunk.block_id, chunk.end) for chunk in chunks}
    covered = len(gold_boundaries & predicted)
    selected = [chunk for chunk in chunks if any(token in chunk.text for token in relevant_phrase.split())]
    selected_chars = sum(len(chunk.text) for chunk in selected)
    relevant_chars = sum(chunk.text.count(relevant_phrase) * len(relevant_phrase) for chunk in selected)
    total_chars = sum(len(chunk.text) for chunk in chunks)
    unique_chars = len({(chunk.block_id, pos) for chunk in chunks for pos in range(chunk.start, chunk.end)})
    sizes = [len(chunk.text) for chunk in chunks]
    return {
        "boundary_coverage": covered / len(gold_boundaries) if gold_boundaries else 1.0,
        "context_precision": relevant_chars / selected_chars if selected_chars else 0.0,
        "mean_size": sum(sizes) / len(sizes),
        "max_size": float(max(sizes)),
        "duplicate_rate": 1 - unique_chars / total_chars if total_chars else 0.0,
    }


def fixed_embed(text: str) -> tuple[float, ...]:
    lower = text.lower()
    return (
        1.0 if any(word in lower for word in ("python", "venv", "环境")) else 0.1,
        1.0 if any(word in lower for word in ("http", "port", "端口")) else 0.1,
        1.0 if any(word in lower for word in ("sqlite", "事务")) else 0.1,
    )


def fixed_report() -> None:
    blocks = (
        Block("b1", "Python 环境要隔离。venv 保存依赖。HTTP 端口连接服务。", ("Guide",), 1),
        Block("b2", "SQLite 事务要原子提交。", ("Database",), 2),
    )
    strategies: tuple[Chunker, ...] = (
        FixedWindowChunker(18, 4),
        RecursiveChunker(24),
        StructureAwareChunker(),
        SemanticBreakpointChunker(fixed_embed, 0.25),
        ParentChildChunker(16),
    )
    print(f"strategies:{len(strategies)},models=fixed,recursive,structure,semantic,parent-child")
    for strategy in strategies:
        chunks = strategy.chunk(blocks)
        metrics = evaluate(chunks, {("b1", len(blocks[0].text)), ("b2", len(blocks[1].text))}, "venv")
        print(
            f"{strategy.version}=chunks:{len(chunks)},boundary:{metrics['boundary_coverage']:.2f},"
            f"duplicate:{metrics['duplicate_rate']:.2f}"
        )
    print("claim=fixture-adapter:true,real-semantic-model:false")


if __name__ == "__main__":
    fixed_report()
