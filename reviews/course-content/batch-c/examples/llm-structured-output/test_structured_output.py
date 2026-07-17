from __future__ import annotations

import os
import unittest

from structured_output import FIXTURES, parse_learning_request


class StructuredOutputTest(unittest.TestCase):
    def test_valid_fixture(self) -> None:
        request = parse_learning_request(FIXTURES["valid"])
        self.assertEqual(request.goal, "job")
        self.assertEqual(request.weekly_hours, 8)

    def test_bad_fixtures_are_rejected(self) -> None:
        for name in ["invalid-json", "wrong-type", "extra-field", "missing-field", "empty"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                parse_learning_request(FIXTURES[name])

    def test_key_is_not_required_for_offline_mode(self) -> None:
        previous = os.environ.pop("DEEPSEEK_API_KEY", None)
        try:
            self.assertEqual(parse_learning_request(FIXTURES["valid"]).topic, "Python")
        finally:
            if previous is not None:
                os.environ["DEEPSEEK_API_KEY"] = previous


if __name__ == "__main__":
    unittest.main(verbosity=2)
