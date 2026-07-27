import unittest

from study_summary import summarize


class StudySummaryTests(unittest.TestCase):
    def test_summary(self) -> None:
        self.assertEqual(summarize([1.0, 0.5, 1.25]), {"sessions": 3, "total_hours": 2.75})

    def test_empty_input(self) -> None:
        self.assertEqual(summarize([]), {"sessions": 0, "total_hours": 0})

    def test_negative_hours_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-negative"):
            summarize([1.0, -0.5])


if __name__ == "__main__":
    unittest.main()
