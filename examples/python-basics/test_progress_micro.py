import unittest


def calculate_progress(target_hours, finished_hours):
    if target_hours <= 0:
        raise ValueError("target_hours 必须大于 0")
    return min(finished_hours / target_hours, 1.0)


class ProgressTests(unittest.TestCase):
    def test_caps_over_completion(self):
        self.assertEqual(calculate_progress(2, 3), 1.0)

    def test_rejects_zero_target(self):
        with self.assertRaises(ValueError):
            calculate_progress(0, 2)


if __name__ == "__main__":
    unittest.main()
