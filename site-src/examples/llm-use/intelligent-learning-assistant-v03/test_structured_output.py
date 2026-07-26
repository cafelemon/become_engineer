from __future__ import annotations

import unittest

from structured_output import (
    FIXTURES,
    StructuredOutputError,
    fixed_report,
    parse_learning_request,
    recovery_action,
)


class StructuredOutputTests(unittest.TestCase):
    def test_valid_object_becomes_immutable_domain_value(self) -> None:
        result = parse_learning_request(FIXTURES["valid"])
        self.assertEqual((result.goal, result.topic), ("job", "Python"))
        self.assertEqual((result.weekly_hours, result.current_level), (8, "beginner"))

    def test_empty_invalid_json_and_non_object_have_distinct_codes(self) -> None:
        expected = {"empty": "empty_response", "invalid-json": "invalid_json", "array": "not_object"}
        for name, code in expected.items():
            with self.subTest(name=name), self.assertRaises(StructuredOutputError) as caught:
                parse_learning_request(FIXTURES[name])
            self.assertEqual(caught.exception.code, code)

    def test_extra_and_missing_fields_are_rejected_separately(self) -> None:
        for name, code in {"extra": "extra_fields", "missing": "missing_fields"}.items():
            with self.subTest(name=name), self.assertRaises(StructuredOutputError) as caught:
                parse_learning_request(FIXTURES[name])
            self.assertEqual(caught.exception.code, code)

    def test_string_and_boolean_are_not_coerced_to_integer(self) -> None:
        for name in ["wrong-type", "bool-hours"]:
            with self.subTest(name=name), self.assertRaises(StructuredOutputError) as caught:
                parse_learning_request(FIXTURES[name])
            self.assertEqual(caught.exception.code, "wrong_type")

    def test_range_and_enum_rules_are_enforced_after_types(self) -> None:
        expected = {"out-of-range": "out_of_range", "invalid-enum": "invalid_enum"}
        for name, code in expected.items():
            with self.subTest(name=name), self.assertRaises(StructuredOutputError) as caught:
                parse_learning_request(FIXTURES[name])
            self.assertEqual(caught.exception.code, code)

    def test_missing_information_requires_user_clarification(self) -> None:
        try:
            parse_learning_request(FIXTURES["missing"])
        except StructuredOutputError as error:
            self.assertEqual(recovery_action(error), "ask_user")

    def test_malformed_output_never_enters_domain_object(self) -> None:
        for name, content in FIXTURES.items():
            if name == "valid":
                continue
            with self.subTest(name=name), self.assertRaises(StructuredOutputError):
                parse_learning_request(content)

    def test_fixed_report_is_deterministic_and_forbids_silent_repair(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("bool-to-int:false", report)
        self.assertIn("missing_information=recovery:ask_user", report)
        self.assertTrue(report.endswith(
            "invariants=model-proposes,application-validates,no-silent-repair,no-rag,no-tools"
        ))


if __name__ == "__main__":
    unittest.main()
