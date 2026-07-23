import unittest
from auth_lab import AuthService, digest
from fastapi.testclient import TestClient
import app as api_module


class SessionTests(unittest.TestCase):
    def setUp(self): self.auth = AuthService()
    def test_bad_password_is_uniformly_rejected(self): self.assertIsNone(self.auth.login("learner", "wrong")); self.assertIsNone(self.auth.login("missing", "wrong"))
    def test_token_is_opaque_and_only_digest_is_stored(self):
        token, csrf = self.auth.login("learner", "learning-only-password")
        self.assertEqual(self.auth.authenticate(token), "u-learner"); self.assertNotIn(token, self.auth._sessions); self.assertIn(digest(token), self.auth._sessions)
    def test_unsafe_request_needs_matching_csrf(self):
        token, csrf = self.auth.login("learner", "learning-only-password")
        self.assertIsNone(self.auth.authenticate(token, unsafe=True)); self.assertIsNone(self.auth.authenticate(token, "wrong", True)); self.assertEqual(self.auth.authenticate(token, csrf, True), "u-learner")
    def test_logout_revokes_session(self):
        token, _ = self.auth.login("learner", "learning-only-password"); self.auth.logout(token); self.assertIsNone(self.auth.authenticate(token))
    def test_expired_session_is_rejected(self):
        token, _ = self.auth.login("learner", "learning-only-password"); self.auth.expire(token); self.assertIsNone(self.auth.authenticate(token))


class AuthApiTests(unittest.TestCase):
    def setUp(self):
        api_module.auth = AuthService()
        self.client = TestClient(api_module.app)

    def login(self):
        return self.client.post("/api/auth/login", json={"username":"learner", "password":"learning-only-password"})

    def test_login_sets_httponly_samesite_cookie(self):
        response = self.login(); self.assertEqual(response.status_code, 200)
        cookie = response.headers["set-cookie"].lower(); self.assertIn("httponly", cookie); self.assertIn("samesite=lax", cookie)

    def test_uniform_login_error_has_challenge(self):
        one = self.client.post("/api/auth/login", json={"username":"learner", "password":"bad"})
        two = self.client.post("/api/auth/login", json={"username":"missing", "password":"bad"})
        self.assertEqual((one.status_code, one.json()), (two.status_code, two.json())); self.assertEqual(one.headers["www-authenticate"], "Session")

    def test_me_requires_session_then_restores_identity(self):
        anonymous = self.client.get("/api/me"); self.assertEqual(anonymous.status_code, 401)
        self.login(); self.assertEqual(self.client.get("/api/me").json(), {"user_id":"u-learner"})

    def test_logout_requires_csrf_and_revokes_cookie(self):
        login = self.login(); csrf = login.json()["csrf_token"]
        self.assertEqual(self.client.post("/api/auth/logout").status_code, 403)
        logout = self.client.post("/api/auth/logout", headers={"X-CSRF-Token":csrf})
        self.assertEqual(logout.status_code, 204); self.assertEqual(self.client.get("/api/me").status_code, 401)
