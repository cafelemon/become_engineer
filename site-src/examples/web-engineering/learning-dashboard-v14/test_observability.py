import json, unittest
from observability import event, metrics, request_id
from release_guard import decide
class ObservabilityTests(unittest.TestCase):
 def test_structured_event_has_low_cardinality_labels(self):
  record=json.loads(event("GET",200,request_id())); self.assertEqual(set(record), {"event","request_id","method","status","duration_ms"}); self.assertEqual(record["status"],200)
 def test_request_id_is_generated_per_request(self): self.assertNotEqual(request_id(),request_id())
 def test_metrics_expose_low_cardinality_counter(self): self.assertIn(b"dashboard_http_requests_total", metrics())
 def test_log_does_not_contain_authorization_values(self): self.assertNotIn("authorization", event("POST",403,"safe-id").lower())
 def test_release_requires_restore_evidence(self): self.assertEqual(decide(True,True,False).reason,"restore-not-verified")
 def test_release_blocks_incompatible_rollback(self): self.assertEqual(decide(True,False,True).reason,"unsafe-database-rollback")
 def test_failed_readiness_stops_release(self): self.assertEqual(decide(False,True,True).reason,"candidate-not-ready")
 def test_healthy_compatible_candidate_is_allowed(self): self.assertTrue(decide(True,True,True).allowed)
