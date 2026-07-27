from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Literal, Mapping, Sequence


class EvaluationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    query: str
    relevant_chunk_ids: tuple[str, ...]
    answerable: bool


@dataclass(frozen=True)
class SystemOutput:
    ranked_chunk_ids: tuple[str, ...]
    answer_status: Literal["answered", "abstained"]
    citation_checks: tuple[bool, ...]


@dataclass(frozen=True)
class EvaluationReport:
    case_count: int
    answerable_count: int
    top_k: int
    recall_at_k: float
    mrr: float
    citation_validity: float
    abstention_accuracy: float
    dataset_fingerprint: str


@dataclass(frozen=True)
class GateResult:
    allowed: bool
    reasons: tuple[str, ...]


def _validate_top_k(top_k: int) -> None:
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        raise EvaluationError("invalid_top_k", "top_k must be a positive integer")


def dataset_fingerprint(cases: Sequence[EvalCase]) -> str:
    canonical = [
        {
            "case_id": case.case_id,
            "query": case.query,
            "relevant_chunk_ids": list(case.relevant_chunk_ids),
            "answerable": case.answerable,
        }
        for case in sorted(cases, key=lambda item: item.case_id)
    ]
    payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def evaluate(
    cases: Sequence[EvalCase],
    outputs: Mapping[str, SystemOutput],
    *,
    allowed_chunk_ids: set[str],
    top_k: int,
) -> EvaluationReport:
    _validate_top_k(top_k)
    if not cases:
        raise EvaluationError("empty_eval_set", "evaluation set must not be empty")
    case_ids = [case.case_id for case in cases]
    if any(not case_id for case_id in case_ids) or len(set(case_ids)) != len(case_ids):
        raise EvaluationError("invalid_eval_case", "case IDs must be non-empty and unique")
    if set(outputs) != set(case_ids):
        raise EvaluationError("output_coverage_mismatch", "outputs must cover every case exactly")

    recall_sum = 0.0
    reciprocal_rank_sum = 0.0
    answerable_count = 0
    valid_citations = 0
    total_citations = 0
    correct_decisions = 0

    for case in cases:
        if not case.query.strip():
            raise EvaluationError("invalid_eval_case", "query must not be empty")
        relevant = set(case.relevant_chunk_ids)
        if case.answerable and not relevant:
            raise EvaluationError("invalid_eval_case", "answerable case needs relevant chunks")
        if not case.answerable and relevant:
            raise EvaluationError("invalid_eval_case", "unanswerable case cannot declare relevance")

        output = outputs[case.case_id]
        ranked = output.ranked_chunk_ids
        if len(set(ranked)) != len(ranked):
            raise EvaluationError("duplicate_ranked_chunk", "ranking contains duplicates")
        if any(chunk_id not in allowed_chunk_ids for chunk_id in ranked):
            raise EvaluationError("unknown_ranked_chunk", "ranking contains an unknown chunk")
        if output.answer_status not in {"answered", "abstained"}:
            raise EvaluationError("invalid_answer_status", "answer status is unknown")
        if output.answer_status == "abstained" and output.citation_checks:
            raise EvaluationError("invalid_output_shape", "abstention cannot emit citations")
        if output.answer_status == "answered" and not output.citation_checks:
            raise EvaluationError("invalid_output_shape", "answered output needs citations")
        if any(type(check) is not bool for check in output.citation_checks):
            raise EvaluationError("invalid_citation_check", "citation checks must be booleans")

        expected_abstention = not case.answerable
        if (output.answer_status == "abstained") == expected_abstention:
            correct_decisions += 1
        valid_citations += sum(output.citation_checks)
        total_citations += len(output.citation_checks)

        if case.answerable:
            answerable_count += 1
            top = set(ranked[:top_k])
            recall_sum += len(top & relevant) / len(relevant)
            reciprocal_rank = 0.0
            for rank, chunk_id in enumerate(ranked, start=1):
                if chunk_id in relevant:
                    reciprocal_rank = 1.0 / rank
                    break
            reciprocal_rank_sum += reciprocal_rank

    if answerable_count == 0:
        raise EvaluationError("missing_answerable_case", "metrics need an answerable case")
    if total_citations == 0:
        raise EvaluationError("missing_citations", "citation validity needs emitted citations")
    return EvaluationReport(
        case_count=len(cases),
        answerable_count=answerable_count,
        top_k=top_k,
        recall_at_k=recall_sum / answerable_count,
        mrr=reciprocal_rank_sum / answerable_count,
        citation_validity=valid_citations / total_citations,
        abstention_accuracy=correct_decisions / len(cases),
        dataset_fingerprint=dataset_fingerprint(cases),
    )


def delivery_gate(
    baseline: EvaluationReport,
    candidate: EvaluationReport,
    *,
    tolerance: float = 1e-12,
) -> GateResult:
    if not math.isfinite(tolerance) or tolerance < 0:
        raise EvaluationError("invalid_tolerance", "tolerance must be finite and non-negative")
    if (
        baseline.dataset_fingerprint != candidate.dataset_fingerprint
        or baseline.top_k != candidate.top_k
        or baseline.case_count != candidate.case_count
    ):
        raise EvaluationError("incomparable_reports", "reports must use the same dataset and top_k")
    reasons: list[str] = []
    if candidate.recall_at_k + tolerance < baseline.recall_at_k:
        reasons.append("recall_at_k_regressed")
    if candidate.mrr + tolerance < baseline.mrr:
        reasons.append("mrr_regressed")
    if candidate.citation_validity + tolerance < 1.0:
        reasons.append("citation_validity_below_1")
    if candidate.abstention_accuracy + tolerance < 1.0:
        reasons.append("abstention_accuracy_below_1")
    return GateResult(not reasons, tuple(reasons))


FIXTURE_CASES = (
    EvalCase("python-env", "如何隔离项目依赖", ("chunk-python",), True),
    EvalCase("http-timeout", "HTTP 为什么要截止时间", ("chunk-http",), True),
    EvalCase("sqlite-rollback", "事务失败后怎么处理", ("chunk-sqlite",), True),
    EvalCase("unknown-garden", "怎么种薄荷", (), False),
)
ALLOWED_CHUNKS = {"chunk-python", "chunk-http", "chunk-sqlite", "chunk-other"}
BASELINE_OUTPUTS = {
    "python-env": SystemOutput(("chunk-python", "chunk-http"), "answered", (True,)),
    "http-timeout": SystemOutput(("chunk-http", "chunk-python"), "answered", (True,)),
    "sqlite-rollback": SystemOutput(
        ("chunk-python", "chunk-http", "chunk-other", "chunk-sqlite"),
        "answered",
        (True,),
    ),
    "unknown-garden": SystemOutput((), "abstained", ()),
}
CANDIDATE_OUTPUTS = {
    "python-env": SystemOutput(("chunk-python", "chunk-http"), "answered", (True,)),
    "http-timeout": SystemOutput(("chunk-http", "chunk-python"), "answered", (True,)),
    "sqlite-rollback": SystemOutput(("chunk-sqlite", "chunk-http"), "answered", (True,)),
    "unknown-garden": SystemOutput((), "abstained", ()),
}


def fixed_report() -> str:
    baseline = evaluate(FIXTURE_CASES, BASELINE_OUTPUTS, allowed_chunk_ids=ALLOWED_CHUNKS, top_k=3)
    candidate = evaluate(FIXTURE_CASES, CANDIDATE_OUTPUTS, allowed_chunk_ids=ALLOWED_CHUNKS, top_k=3)
    gate = delivery_gate(baseline, candidate)
    fingerprint = baseline.dataset_fingerprint[:12]
    return "\n".join([
        "runtime=python:3.11+,dependencies:stdlib-only,network:disabled",
        f"dataset=cases:4,answerable:3,unanswerable:1,fingerprint:{fingerprint}",
        f"baseline=recall@3:{baseline.recall_at_k:.6f},mrr:{baseline.mrr:.6f},citation-validity:{baseline.citation_validity:.6f},abstention-accuracy:{baseline.abstention_accuracy:.6f}",
        f"candidate=recall@3:{candidate.recall_at_k:.6f},mrr:{candidate.mrr:.6f},citation-validity:{candidate.citation_validity:.6f},abstention-accuracy:{candidate.abstention_accuracy:.6f}",
        f"gate=allowed:{str(gate.allowed).lower()},reasons:{'none' if not gate.reasons else '|'.join(gate.reasons)}",
        "denominators=recall:answerable-cases,mrr:answerable-cases,citations:emitted-citations,abstention:all-cases",
        "rejection=empty-set:true,coverage-mismatch:true,duplicate-rank:true,unknown-rank:true,no-citations:true,incomparable:true",
        "artifacts=dataset-fingerprint:true,baseline:true,candidate:true,gate:true,deterministic-json:true",
        "logs=query:none,answer:none,citation-text:none,case-id:allowed,metrics:allowed,reason:allowed",
        "invariants=fixed-eval,recall-at-k,mrr,citation-validity,abstention-accuracy,no-regression,no-generation,no-tools",
    ])


if __name__ == "__main__":
    print(fixed_report())
