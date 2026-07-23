import unittest

from regression_cases import (
    linear_membership,
    parse_counted_values,
    shortest_hops,
    should_switch,
    stable_unique,
)


class RegressionCaseTests(unittest.TestCase):
    def test_contract_count_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "count mismatch"):
            parse_counted_values("2\n9\n")

    def test_boundary_empty_sequence(self) -> None:
        self.assertEqual(stable_unique(parse_counted_values("0\n\n")), [])

    def test_implementation_bfs_shared_neighbor(self) -> None:
        graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
        self.assertEqual(shortest_hops(graph, "a", "d"), 2)

    def test_complexity_membership_operation_bound(self) -> None:
        answers, checks = linear_membership(list(range(100)), list(range(50, 150)))
        self.assertEqual(checks, 100)
        self.assertEqual(sum(answers), 50)

    def test_strategy_checkpoint_switch_rule(self) -> None:
        self.assertFalse(should_switch(False, False, False))
        self.assertTrue(should_switch(False, False, True))
        self.assertFalse(should_switch(True, False, True))


if __name__ == "__main__":
    unittest.main()
