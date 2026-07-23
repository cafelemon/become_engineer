from __future__ import annotations

import unittest

from scaling_lab import distance, fit_standardizer, fixed_report


class ScalingLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = ((2.0, 10.0), (4.0, 20.0), (6.0, 30.0), (8.0, 40.0))

    def test_fit_uses_population_mean_and_scale(self) -> None:
        fitted = fit_standardizer(self.rows)
        self.assertEqual(fitted.means, (5.0, 25.0))
        self.assertAlmostEqual(fitted.scales[0], 5 ** 0.5)
        self.assertAlmostEqual(fitted.scales[1], 125 ** 0.5)

    def test_transformed_training_columns_have_zero_mean_and_unit_variance(self) -> None:
        transformed = fit_standardizer(self.rows).transform(self.rows)
        for column in range(2):
            values = [row[column] for row in transformed]
            self.assertAlmostEqual(sum(values) / len(values), 0)
            self.assertAlmostEqual(sum(value * value for value in values) / len(values), 1)

    def test_validation_is_transformed_with_training_statistics(self) -> None:
        fitted = fit_standardizer(self.rows)
        self.assertEqual(fitted.transform(((10.0, 50.0),))[0], ((10 - 5) / 5 ** 0.5, (50 - 25) / 125 ** 0.5))

    def test_constant_columns_are_explicitly_rejected(self) -> None:
        with self.assertRaises(ValueError):
            fit_standardizer(((1, 4), (2, 4), (3, 4)))

    def test_empty_ragged_and_transform_mismatch_are_rejected(self) -> None:
        for call in (
            lambda: fit_standardizer(()),
            lambda: fit_standardizer(((1, 2), (3,))),
            lambda: fit_standardizer(self.rows).transform(((1,),)),
            lambda: distance((1,), (1, 2)),
        ):
            with self.assertRaises(ValueError):
                call()

    def test_fixed_report_is_deterministic(self) -> None:
        self.assertIn("means=5.000,25.000", fixed_report())
        self.assertIn("raw_distance_first_last=30.594", fixed_report())
        self.assertIn("z_distance_first_last=3.795", fixed_report())
        self.assertTrue(fixed_report().endswith("invariants=train-fit-only,nonzero-scale"))


if __name__ == "__main__":
    unittest.main()

