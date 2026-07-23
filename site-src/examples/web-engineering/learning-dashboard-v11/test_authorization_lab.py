import unittest
from authorization_lab import Authorizer

class AuthorizationTests(unittest.TestCase):
    def setUp(self): self.auth = Authorizer()
    def test_anonymous_is_401(self): self.assertEqual(self.auth.allow("learner", None, "status:read", "u1", "r1"), 401)
    def test_owner_can_read(self): self.assertEqual(self.auth.allow("learner", "u1", "status:read", "u1", "r2"), 200)
    def test_other_owner_is_hidden(self): self.assertEqual(self.auth.allow("learner", "u2", "status:read", "u1", "r3"), 404)
    def test_default_deny_and_operator_action(self): self.assertEqual(self.auth.allow("learner", "u1", "diagnostic:run", None, "r4"), 403); self.assertEqual(self.auth.allow("operator", "op", "diagnostic:run", None, "r5"), 200)
    def test_audit_never_receives_credentials(self):
        self.auth.allow("learner", "u1", "status:read", "u1", "req-safe")
        self.assertEqual(self.auth.events[-1].request_id, "req-safe")
        self.assertNotIn("authorization", str(self.auth.safe_log()).lower())
    def test_unknown_role_is_default_denied(self): self.assertEqual(self.auth.allow("admin", "u1", "status:read", "u1", "r6"), 403)
    def test_operator_cannot_read_learner_resource(self): self.assertEqual(self.auth.allow("operator", "op", "status:read", "op", "r7"), 403)
    def test_audit_records_result_and_request_id(self):
        self.auth.allow("learner", "u1", "session:write", "u1", "request-8")
        self.assertEqual((self.auth.events[-1].result, self.auth.events[-1].request_id), ("allowed", "request-8"))
