from __future__ import annotations

import unittest

from vector_shape_lab import dot, euclidean_distance, fixed_report, matrix_shape, matrix_vector


class VectorShapeTests(unittest.TestCase):
    def test_dot_product_is_pairwise_sum(self) -> None:
        self.assertEqual(dot((1, 2, 3), (0.5, -1, 2)), 4.5)
        self.assertEqual(dot((), ()), 0)

    def test_matrix_shape_is_rows_by_columns(self) -> None:
        self.assertEqual(matrix_shape(((1, 2, 3), (4, 5, 6))), (2, 3))
        self.assertEqual(matrix_shape(()), (0, 0))

    def test_matrix_vector_uses_one_dot_product_per_row(self) -> None:
        self.assertEqual(matrix_vector(((1, 2, 3), (2, 0, 1)), (0.5, -1, 2)), (4.5, 3.0))

    def test_distance_uses_matching_dimensions(self) -> None:
        self.assertEqual(euclidean_distance((0, 0), (3, 4)), 5)

    def test_shape_mismatches_are_rejected(self) -> None:
        for call in (
            lambda: dot((1, 2), (1,)),
            lambda: matrix_shape(((1, 2), (3,))),
            lambda: matrix_vector(((1, 2),), (1,)),
            lambda: euclidean_distance((0,), (0, 1)),
        ):
            with self.assertRaises(ValueError):
                call()

    def test_fixed_report_is_machine_independent(self) -> None:
        self.assertEqual(
            fixed_report(),
            "\n".join([
                "vector=1,2,3 weights=0.5,-1,2",
                "dot=4.5",
                "matrix_shape=2x3",
                "matvec=4.5,3.0",
                "distance_0_0_to_3_4=5.0",
                "ragged=reject",
                "invariants=same-length,rectangular-shape",
            ]),
        )


if __name__ == "__main__":
    unittest.main()

