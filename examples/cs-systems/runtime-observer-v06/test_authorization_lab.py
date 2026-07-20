from __future__ import annotations

import unittest

from authorization_lab import build_demo


class AuthorizationLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app, self.viewer_token, self.operator_token = build_demo()

    def test_missing_and_invalid_credentials_return_401_with_challenge(self) -> None:
        missing = self.app.handle("GET", "/status", None)
        invalid = self.app.handle("GET", "/status", "Bearer invalid-token")
        self.assertEqual(missing.status, 401)
        self.assertEqual(invalid.status, 401)
        self.assertTrue(missing.headers["WWW-Authenticate"].startswith("Bearer "))

    def test_viewer_can_read_status(self) -> None:
        response = self.app.handle(
            "GET", "/status", f"Bearer {self.viewer_token}"
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, {"status": "ok"})

    def test_authenticated_viewer_cannot_run_diagnostics(self) -> None:
        response = self.app.handle(
            "POST", "/diagnostics", f"Bearer {self.viewer_token}"
        )
        self.assertEqual(response.status, 403)
        self.assertEqual(response.body, {"error": "insufficient_permission"})

    def test_operator_can_run_diagnostics_and_unlisted_route_is_denied(self) -> None:
        allowed = self.app.handle(
            "POST", "/diagnostics", f"Bearer {self.operator_token}"
        )
        unlisted = self.app.handle(
            "DELETE", "/status", f"Bearer {self.operator_token}"
        )
        self.assertEqual(allowed.status, 200)
        self.assertEqual(allowed.body, {"diagnostic": "completed"})
        self.assertEqual(unlisted.status, 404)

    def test_store_and_audit_log_do_not_keep_raw_tokens(self) -> None:
        self.app.handle("GET", "/status", f"Bearer {self.viewer_token}")
        self.app.handle("POST", "/diagnostics", f"Bearer {self.operator_token}")
        stored = " ".join(self.app.tokens.stored_digests())
        logged = "\n".join(self.app.audit_log)
        for token in (self.viewer_token, self.operator_token):
            self.assertNotIn(token, stored)
            self.assertNotIn(token, logged)


if __name__ == "__main__":
    unittest.main()
