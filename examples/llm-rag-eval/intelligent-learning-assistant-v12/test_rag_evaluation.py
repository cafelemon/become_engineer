from dataclasses import replace
import unittest

from rag_evaluation import (
    ALLOWED_CHUNKS,
    BASELINE_OUTPUTS,
    CANDIDATE_OUTPUTS,
    FIXTURE_CASES,
    EvalCase,
    EvaluationError,
    SystemOutput,
    dataset_fingerprint,
    delivery_gate,
    evaluate,
    fixed_report,
)


class RagEvaluationTests(unittest.TestCase):
    def test_fixed_baseline_and_candidate_metrics_are_exact(self) -> None:
        baseline = evaluate(
            FIXTURE_CASES, BASELINE_OUTPUTS, allowed_chunk_ids=ALLOWED_CHUNKS, top_k=3
        )
        candidate = evaluate(
            FIXTURE_CASES, CANDIDATE_OUTPUTS, allowed_chunk_ids=ALLOWED_CHUNKS, top_k=3
        )
        self.assertAlmostEqual(baseline.recall_at_k, 2 / 3)
        self.assertAlmostEqual(baseline.mrr, 0.75)
        self.assertEqual(candidate.recall_at_k, 1.0)
        self.assertEqual(candidate.mrr, 1.0)
        self.assertEqual(candidate.citation_validity, 1.0)
        self.assertEqual(candidate.abstention_accuracy, 1.0)

    def test_recall_supports_multiple_relevant_chunks(self) -> None:
        cases = (EvalCase("multi", "两项", ("a", "b"), True),)
        outputs = {"multi": SystemOutput(("a", "c", "b"), "answered", (True,))}
        report = evaluate(cases, outputs, allowed_chunk_ids={"a", "b", "c"}, top_k=2)
        self.assertEqual(report.recall_at_k, 0.5)
        self.assertEqual(report.mrr, 1.0)

    def test_dataset_fingerprint_is_order_independent_but_content_sensitive(self) -> None:
        self.assertEqual(dataset_fingerprint(FIXTURE_CASES), dataset_fingerprint(tuple(reversed(FIXTURE_CASES))))
        changed = (replace(FIXTURE_CASES[0], query="改过的问题"), *FIXTURE_CASES[1:])
        self.assertNotEqual(dataset_fingerprint(FIXTURE_CASES), dataset_fingerprint(changed))

    def test_input_contract_rejects_bad_top_k_and_output_coverage(self) -> None:
        for top_k in [True, 0, -1, 1.5]:
            with self.subTest(top_k=top_k):
                with self.assertRaises(EvaluationError) as raised:
                    evaluate(FIXTURE_CASES, BASELINE_OUTPUTS, allowed_chunk_ids=ALLOWED_CHUNKS, top_k=top_k)
                self.assertEqual(raised.exception.code, "invalid_top_k")
        missing = dict(BASELINE_OUTPUTS)
        missing.pop("python-env")
        with self.assertRaises(EvaluationError) as coverage:
            evaluate(FIXTURE_CASES, missing, allowed_chunk_ids=ALLOWED_CHUNKS, top_k=3)
        self.assertEqual(coverage.exception.code, "output_coverage_mismatch")

    def test_bad_rankings_and_output_shapes_are_rejected(self) -> None:
        for output, code in [
            (SystemOutput(("chunk-python", "chunk-python"), "answered", (True,)), "duplicate_ranked_chunk"),
            (SystemOutput(("missing",), "answered", (True,)), "unknown_ranked_chunk"),
            (SystemOutput(("chunk-python",), "answered", ()), "invalid_output_shape"),
            (SystemOutput((), "abstained", (True,)), "invalid_output_shape"),
        ]:
            outputs = dict(BASELINE_OUTPUTS)
            outputs["python-env"] = output
            with self.subTest(code=code):
                with self.assertRaises(EvaluationError) as raised:
                    evaluate(FIXTURE_CASES, outputs, allowed_chunk_ids=ALLOWED_CHUNKS, top_k=3)
                self.assertEqual(raised.exception.code, code)

    def test_delivery_gate_accepts_improvement_on_same_protocol(self) -> None:
        baseline = evaluate(FIXTURE_CASES, BASELINE_OUTPUTS, allowed_chunk_ids=ALLOWED_CHUNKS, top_k=3)
        candidate = evaluate(FIXTURE_CASES, CANDIDATE_OUTPUTS, allowed_chunk_ids=ALLOWED_CHUNKS, top_k=3)
        self.assertEqual(delivery_gate(baseline, candidate).reasons, ())
        self.assertTrue(delivery_gate(baseline, candidate).allowed)

    def test_delivery_gate_reports_quality_and_safety_regressions(self) -> None:
        baseline = evaluate(FIXTURE_CASES, BASELINE_OUTPUTS, allowed_chunk_ids=ALLOWED_CHUNKS, top_k=3)
        bad_outputs = dict(CANDIDATE_OUTPUTS)
        bad_outputs["http-timeout"] = SystemOutput(("chunk-python",), "answered", (True,))
        bad_outputs["sqlite-rollback"] = SystemOutput(("chunk-http",), "answered", (False,))
        bad_outputs["unknown-garden"] = SystemOutput(("chunk-other",), "answered", (True,))
        bad = evaluate(FIXTURE_CASES, bad_outputs, allowed_chunk_ids=ALLOWED_CHUNKS, top_k=3)
        result = delivery_gate(baseline, bad)
        self.assertFalse(result.allowed)
        self.assertEqual(
            result.reasons,
            (
                "recall_at_k_regressed",
                "mrr_regressed",
                "citation_validity_below_1",
                "abstention_accuracy_below_1",
            ),
        )

    def test_fixed_report_freezes_denominators_and_artifacts(self) -> None:
        report = fixed_report()
        self.assertIn("baseline=recall@3:0.666667,mrr:0.750000", report)
        self.assertIn("candidate=recall@3:1.000000,mrr:1.000000", report)
        self.assertIn("gate=allowed:true,reasons:none", report)
        self.assertIn("denominators=recall:answerable-cases", report)
        self.assertIn("no-regression,no-generation,no-tools", report)


if __name__ == "__main__":
    unittest.main()
