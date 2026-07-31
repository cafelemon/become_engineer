import unittest

from evaluation_trace import EvalCase, RunRecord, Trace, aggregate, evaluate


CASE = EvalCase("c1", "completed", ("source-1",), ("search",), 5, 500, 10)


def record(**overrides):
    values = dict(terminal="completed", evidence=("source-1",), tools=("search",), context_evidence=("source-1",), steps=("authorize", "retrieve", "search", "answer"), latency_ms=100, cost_units=4)
    values.update(overrides)
    return RunRecord(**values)


class EvaluationTraceTests(unittest.TestCase):
    def test_good_run_passes_all_layers(self): self.assertTrue(evaluate(CASE, record())["passed"])

    def test_retrieval_failure_is_localized_before_outcome(self):
        result = evaluate(CASE, record(evidence=(), context_evidence=(), terminal="refused"))
        self.assertEqual("retrieval", result["first_failure"])

    def test_tool_violation_is_detected(self):
        self.assertEqual("tool", evaluate(CASE, record(tools=("delete",)))["first_failure"])

    def test_context_drop_is_separate_from_retrieval(self):
        self.assertEqual("context", evaluate(CASE, record(context_evidence=()))["first_failure"])

    def test_trajectory_budget_is_checked(self):
        self.assertEqual("trajectory", evaluate(CASE, record(steps=("x",) * 6))["first_failure"])

    def test_latency_and_cost_are_release_checks(self):
        self.assertEqual("latency", evaluate(CASE, record(latency_ms=501))["first_failure"])
        self.assertEqual("cost", evaluate(CASE, record(cost_units=11))["first_failure"])

    def test_trace_redacts_sensitive_fields(self):
        trace = Trace("run", "request"); trace.add("tool", {"authorization": "secret", "route": "search", "chain_of_thought": "hidden"})
        self.assertEqual("[REDACTED]", trace.spans[0]["attributes"]["authorization"])
        self.assertEqual("[REDACTED]", trace.spans[0]["attributes"]["chain_of_thought"])

    def test_aggregate_keeps_layer_metrics(self):
        summary = aggregate([evaluate(CASE, record()), evaluate(CASE, record(context_evidence=()))])
        self.assertEqual(0.5, summary["context_pass_rate"])
        self.assertFalse(summary["gate_pass"])


if __name__ == "__main__": unittest.main()
