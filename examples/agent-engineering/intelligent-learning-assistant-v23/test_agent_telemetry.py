import json
import unittest

from agent_telemetry import Telemetry, fixed_report, redact


class AgentTelemetryTests(unittest.TestCase):
    def test_parent_child_spans_share_trace(self):
        telemetry = Telemetry(["trace", "root", "child"])
        with telemetry.span("root") as root:
            with telemetry.span("child", trace_id=root.trace_id, parent_span_id=root.span_id):
                pass
        self.assertEqual({span.trace_id for span in telemetry.spans}, {"trace"})
        self.assertEqual(telemetry.spans[0].parent_span_id, "root")

    def test_run_and_request_are_correlated(self):
        telemetry = Telemetry(["trace", "span"])
        with telemetry.span("run", attributes={"run_id": "run-1", "request_id": "req-1"}):
            pass
        self.assertEqual(telemetry.spans[0].attributes["run_id"], "run-1")
        self.assertEqual(telemetry.spans[0].attributes["request_id"], "req-1")

    def test_sensitive_values_are_redacted(self):
        clean = redact({"authorization": "Bearer x", "csrf_token": "y", "run_id": "r"})
        self.assertEqual(clean["authorization"], "[REDACTED]")
        self.assertEqual(clean["csrf_token"], "[REDACTED]")
        self.assertEqual(clean["run_id"], "r")

    def test_unknown_high_cardinality_attribute_is_dropped(self):
        self.assertNotIn("user_query_hash", redact({"user_query_hash": "unique"}))

    def test_metrics_use_route_template_and_status_class(self):
        telemetry = Telemetry([])
        telemetry.observe_http("/api/runs/{run_id}", 201)
        telemetry.observe_http("/api/runs/{run_id}", 204)
        self.assertEqual(telemetry.metrics[("/api/runs/{run_id}", "2xx")], 2)

    def test_errors_are_always_sampled(self):
        telemetry = Telemetry([], sample_every=100)
        self.assertTrue(telemetry.should_sample("error"))

    def test_success_sampling_is_deterministic(self):
        telemetry = Telemetry([], sample_every=2)
        self.assertFalse(telemetry.should_sample("ok"))
        self.assertTrue(telemetry.should_sample("ok"))

    def test_fixed_export_contains_no_secret(self):
        report = fixed_report()
        self.assertFalse(report["secret_present"])
        self.assertEqual(report["spans"], 3)


if __name__ == "__main__":
    unittest.main()
