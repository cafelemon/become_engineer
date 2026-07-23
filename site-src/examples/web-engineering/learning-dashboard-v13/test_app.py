import os, unittest
from fastapi.testclient import TestClient
from app import app

class HealthTests(unittest.TestCase):
    def setUp(self): self.client = TestClient(app)
    def test_live_does_not_depend_on_database(self): self.assertEqual(self.client.get("/health/live").json(), {"status":"live"})
    def test_ready_rejects_missing_database_config(self):
        previous=os.environ.pop("DATABASE_URL", None)
        try: self.assertEqual(self.client.get("/health/ready").status_code, 503)
        finally:
            if previous is not None: os.environ["DATABASE_URL"]=previous
    def test_ready_rejects_unreachable_database(self):
        previous=os.environ.get("DATABASE_URL"); previous_file=os.environ.get("DATABASE_PASSWORD_FILE")
        os.environ["DATABASE_URL"]="postgresql://dashboard:{password}@127.0.0.1:1/dashboard"
        os.environ["DATABASE_PASSWORD_FILE"]=__file__
        try: self.assertEqual(self.client.get("/health/ready").status_code, 503)
        finally:
            if previous is None: os.environ.pop("DATABASE_URL", None)
            else: os.environ["DATABASE_URL"]=previous
            if previous_file is None: os.environ.pop("DATABASE_PASSWORD_FILE", None)
            else: os.environ["DATABASE_PASSWORD_FILE"]=previous_file
    def test_lifespan_marks_app_stopping_after_client_closes(self):
        with TestClient(app) as client: self.assertTrue(client.app.state.accepting_requests)
        self.assertFalse(app.state.accepting_requests)
