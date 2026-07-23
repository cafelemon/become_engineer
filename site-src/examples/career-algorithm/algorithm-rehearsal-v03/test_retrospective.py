from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from retrospective import build_report, load_records


class RetrospectiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = Path(__file__).parent / "failures.json"
        cls.payload = json.loads(cls.path.read_text(encoding="utf-8"))

    def write_payload(self, payload: dict) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "failures.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_sample_covers_all_five_categories(self) -> None:
        records = load_records(self.path)
        report = build_report(records)
        self.assertEqual(len(records), 5)
        self.assertIn("contract", report[-3])
        self.assertEqual(report[-2], "gate=pass records=5")

    def test_unknown_category_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["category"] = "guess"
        with self.assertRaisesRegex(ValueError, "category"):
            load_records(self.write_payload(payload))

    def test_unknown_observed_status_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["observed_status"] = "maybe"
        with self.assertRaisesRegex(ValueError, "status"):
            load_records(self.write_payload(payload))

    def test_duplicate_regression_id_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["records"][1]["regression_id"] = payload["records"][0]["regression_id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            load_records(self.write_payload(payload))

    def test_missing_smaller_probe_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["smaller_probe"] = ""
        with self.assertRaisesRegex(ValueError, "non-empty"):
            load_records(self.write_payload(payload))

    def test_unresolved_record_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["after"] = "still-failing"
        with self.assertRaisesRegex(ValueError, "regression-pass"):
            load_records(self.write_payload(payload))

    def test_timeline_link_is_required(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["linked_event"] = "missing-separator"
        with self.assertRaisesRegex(ValueError, "timeline"):
            load_records(self.write_payload(payload))


if __name__ == "__main__":
    unittest.main()
