from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from portfolio_check import PortfolioError, load_report

ROOT = Path(__file__).resolve().parent


class PortfolioCheckTests(unittest.TestCase):
    def test_sample_has_four_evidence_kinds_and_two_experiments(self) -> None:
        report = load_report(ROOT / "portfolio.json", ROOT)
        self.assertEqual([kind for kind, _ in report.evidence], ["code", "tests", "readme", "reflection"])
        self.assertEqual(
            [trial.route for trial in report.route_trials[:2]],
            ["application-engineering", "algorithm"],
        )

    def test_output_is_deterministic(self) -> None:
        report = load_report(ROOT / "portfolio.json", ROOT)
        self.assertEqual(report.as_text(), load_report(ROOT / "portfolio.json", ROOT).as_text())
        self.assertIn("decision=two-week-trial-not-career-conclusion", report.as_text())

    def test_missing_evidence_is_rejected(self) -> None:
        payload = json.loads((ROOT / "portfolio.json").read_text(encoding="utf-8"))
        payload["artifacts"] = payload["artifacts"][:-1]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "portfolio.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(PortfolioError, "missing evidence kinds: reflection"):
                load_report(path, ROOT)

    def test_path_escape_is_rejected(self) -> None:
        payload = json.loads((ROOT / "portfolio.json").read_text(encoding="utf-8"))
        payload["artifacts"][0]["path"] = "../outside.py"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "portfolio.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(PortfolioError, "escapes workspace"):
                load_report(path, ROOT)

    def test_unknown_route_is_rejected(self) -> None:
        payload = json.loads((ROOT / "portfolio.json").read_text(encoding="utf-8"))
        payload["route_trials"][0]["route"] = "instant-expert"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "portfolio.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(PortfolioError, "unknown route"):
                load_report(path, ROOT)

    def test_interest_must_be_bounded(self) -> None:
        payload = json.loads((ROOT / "portfolio.json").read_text(encoding="utf-8"))
        payload["route_trials"][0]["interest"] = 6
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "portfolio.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(PortfolioError, "integer from 1 to 5"):
                load_report(path, ROOT)


if __name__ == "__main__":
    unittest.main()
