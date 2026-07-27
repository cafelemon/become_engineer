from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import math
import re
import unicodedata
from typing import Iterable


TOKEN_PATTERN = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]+")


class RetrievalError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class SearchDocument:
    document_id: str
    title: str
    content: str

    def __post_init__(self) -> None:
        if not self.document_id or not self.title.strip() or not self.content.strip():
            raise RetrievalError("invalid_document", "document fields must not be empty")


@dataclass(frozen=True)
class SearchResult:
    document_id: str
    score: float
    matched_terms: tuple[str, ...]


FIXTURE_DOCUMENTS = (
    SearchDocument(
        "python-venv",
        "Python 虚拟环境",
        "虚拟环境隔离项目依赖。激活环境不等于安装依赖，仍要执行明确的安装命令。",
    ),
    SearchDocument(
        "http-status",
        "HTTP 状态码边界",
        "401 表示缺少或无效身份，403 表示身份有效但权限不足，404 也可隐藏不可见资源。",
    ),
    SearchDocument(
        "sqlite-transaction",
        "SQLite 事务",
        "事务中途失败后执行回滚，才能避免只提交一半修改。SQLite 行为不能外推为所有数据库实现。",
    ),
)


def tokenize(text: str) -> tuple[str, ...]:
    if not isinstance(text, str):
        raise RetrievalError("invalid_query", "text must be a string")
    normalized = unicodedata.normalize("NFKC", text).lower()
    tokens: list[str] = []
    for match in TOKEN_PATTERN.findall(normalized):
        if match.isascii():
            tokens.append(match)
            continue
        characters = list(match)
        tokens.extend(f"zh1:{character}" for character in characters)
        tokens.extend(
            f"zh2:{characters[index]}{characters[index + 1]}"
            for index in range(len(characters) - 1)
        )
    return tuple(tokens)


class BM25Index:
    def __init__(
        self,
        documents: Iterable[SearchDocument],
        *,
        k1: float = 1.2,
        b: float = 0.75,
    ) -> None:
        if not math.isfinite(k1) or k1 <= 0:
            raise RetrievalError("invalid_config", "k1 must be positive and finite")
        if not math.isfinite(b) or not 0 <= b <= 1:
            raise RetrievalError("invalid_config", "b must be between 0 and 1")
        ordered = sorted(documents, key=lambda document: document.document_id)
        if not ordered:
            raise RetrievalError("empty_index", "index requires documents")
        if len({document.document_id for document in ordered}) != len(ordered):
            raise RetrievalError("duplicate_document_id", "document_id must be unique")

        self.k1 = k1
        self.b = b
        self.documents = tuple(ordered)
        self.term_frequencies: dict[str, Counter[str]] = {}
        self.document_lengths: dict[str, int] = {}
        postings: dict[str, set[str]] = defaultdict(set)
        for document in self.documents:
            terms = tokenize(f"{document.title} {document.content}")
            frequencies = Counter(terms)
            self.term_frequencies[document.document_id] = frequencies
            self.document_lengths[document.document_id] = len(terms)
            for term in frequencies:
                postings[term].add(document.document_id)
        self.postings = {term: frozenset(ids) for term, ids in postings.items()}
        self.average_length = sum(self.document_lengths.values()) / len(self.documents)

    def inverse_document_frequency(self, term: str) -> float:
        document_frequency = len(self.postings.get(term, ()))
        if document_frequency == 0:
            return 0.0
        count = len(self.documents)
        return math.log(1 + (count - document_frequency + 0.5) / (document_frequency + 0.5))

    def explain(self, query: str, document_id: str) -> dict[str, float]:
        if document_id not in self.term_frequencies:
            raise RetrievalError("unknown_document", "document_id is not indexed")
        query_terms = tuple(sorted(set(tokenize(query))))
        frequencies = self.term_frequencies[document_id]
        length = self.document_lengths[document_id]
        contributions: dict[str, float] = {}
        for term in query_terms:
            frequency = frequencies.get(term, 0)
            if frequency == 0:
                continue
            denominator = frequency + self.k1 * (
                1 - self.b + self.b * length / self.average_length
            )
            contributions[term] = (
                self.inverse_document_frequency(term)
                * frequency
                * (self.k1 + 1)
                / denominator
            )
        return contributions

    def search(self, query: str, top_k: int = 3) -> tuple[SearchResult, ...]:
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise RetrievalError("invalid_top_k", "top_k must be a positive integer")
        query_terms = tuple(sorted(set(tokenize(query))))
        if not query_terms:
            return ()
        candidates: set[str] = set()
        for term in query_terms:
            candidates.update(self.postings.get(term, ()))
        results: list[SearchResult] = []
        for document_id in candidates:
            contributions = self.explain(query, document_id)
            score = sum(contributions.values())
            if score > 0:
                results.append(SearchResult(
                    document_id,
                    score,
                    tuple(sorted(contributions)),
                ))
        results.sort(key=lambda item: (-item.score, item.document_id))
        return tuple(results[:top_k])


def _format_results(results: tuple[SearchResult, ...]) -> str:
    if not results:
        return "none"
    return ",".join(f"{result.document_id}:{result.score:.6f}" for result in results)


def fixed_report() -> str:
    index = BM25Index(FIXTURE_DOCUMENTS)
    permissions = index.search("403 权限不足")
    environment = index.search("虚拟环境 项目依赖")
    transaction = index.search("事务 回滚")
    unknown = index.search("量子香蕉")
    return "\n".join([
        "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
        f"index=documents:{len(index.documents)},terms:{len(index.postings)},average-length:{index.average_length:.6f}",
        f"query-permission={_format_results(permissions)}",
        f"query-environment={_format_results(environment)}",
        f"query-transaction={_format_results(transaction)}",
        f"query-unknown={_format_results(unknown)}",
        "tokenizer=unicode-nfkc+lower+ascii-terms+han-unigram-bigram,general-segmentation:false",
        "bm25=k1:1.2,b:0.75,idf:log1p-rsj,query-terms:deduplicated",
        "ranking=score-desc,document-id-asc,zero-score:excluded,top-k:bounded",
        "invariants=lexical-baseline,explainable-contributions,stable-ties,no-embedding,no-generation,no-tools",
    ])


if __name__ == "__main__":
    print(fixed_report())
