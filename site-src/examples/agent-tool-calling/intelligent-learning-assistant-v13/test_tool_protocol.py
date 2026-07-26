import unittest

from tool_protocol import (
    LEARNING_TOOLS,
    ArgumentSpec,
    ToolCall,
    ToolDefinition,
    ToolProtocolError,
    ToolRegistry,
    fixed_report,
)


class ToolProtocolTests(unittest.TestCase):
    def test_manifest_is_canonical_and_fingerprint_is_stable(self) -> None:
        manifest = LEARNING_TOOLS.manifest()
        self.assertEqual(manifest[0]["name"], "get_learning_status")
        self.assertFalse(manifest[0]["parameters"]["additionalProperties"])
        self.assertTrue(manifest[0]["strict"])
        self.assertEqual(LEARNING_TOOLS.fingerprint(), LEARNING_TOOLS.fingerprint())

    def test_valid_candidate_becomes_immutable_but_is_not_executed(self) -> None:
        validated = LEARNING_TOOLS.validate_call(
            ToolCall(
                "call_ab12",
                "get_learning_status",
                '{"learner_id":"learner-001","include_recent":true}',
            )
        )
        self.assertEqual(validated.arguments["learner_id"], "learner-001")
        with self.assertRaises(TypeError):
            validated.arguments["learner_id"] = "other"

    def test_bad_call_id_and_unknown_tool_are_rejected(self) -> None:
        for call, code in [
            (ToolCall("../call", "get_learning_status", "{}"), "invalid_call_id"),
            (ToolCall("call_ab12", "run_shell", "{}"), "unknown_tool"),
        ]:
            with self.subTest(code=code):
                with self.assertRaises(ToolProtocolError) as raised:
                    LEARNING_TOOLS.validate_call(call)
                self.assertEqual(raised.exception.code, code)

    def test_arguments_must_be_json_object(self) -> None:
        for payload, code in [
            ("{bad", "arguments_json_invalid"),
            ('["learner-001",true]', "arguments_not_object"),
            ('"text"', "arguments_not_object"),
        ]:
            with self.subTest(code=code):
                with self.assertRaises(ToolProtocolError) as raised:
                    LEARNING_TOOLS.validate_call(
                        ToolCall("call_ab12", "get_learning_status", payload)
                    )
                self.assertEqual(raised.exception.code, code)

    def test_missing_and_extra_arguments_are_rejected(self) -> None:
        for payload, code in [
            ('{"learner_id":"learner-001"}', "arguments_missing"),
            (
                '{"learner_id":"learner-001","include_recent":true,"admin":true}',
                "arguments_extra",
            ),
        ]:
            with self.subTest(code=code):
                with self.assertRaises(ToolProtocolError) as raised:
                    LEARNING_TOOLS.validate_call(
                        ToolCall("call_ab12", "get_learning_status", payload)
                    )
                self.assertEqual(raised.exception.code, code)

    def test_strict_types_reject_bool_string_and_integer_coercion(self) -> None:
        for payload in [
            '{"learner_id":123,"include_recent":true}',
            '{"learner_id":"learner-001","include_recent":"true"}',
            '{"learner_id":"learner-001","include_recent":1}',
        ]:
            with self.subTest(payload=payload):
                with self.assertRaises(ToolProtocolError) as raised:
                    LEARNING_TOOLS.validate_call(
                        ToolCall("call_ab12", "get_learning_status", payload)
                    )
                self.assertEqual(raised.exception.code, "argument_type_invalid")

    def test_string_length_and_registry_definition_are_validated(self) -> None:
        for learner_id in ["x", "x" * 25]:
            with self.subTest(learner_id=learner_id):
                with self.assertRaises(ToolProtocolError) as raised:
                    LEARNING_TOOLS.validate_call(
                        ToolCall(
                            "call_ab12",
                            "get_learning_status",
                            f'{{"learner_id":"{learner_id}","include_recent":false}}',
                        )
                    )
                self.assertEqual(raised.exception.code, "argument_value_invalid")
        with self.assertRaises(ToolProtocolError) as duplicate:
            definition = ToolDefinition("same_tool", "read only", {"id": ArgumentSpec(str)})
            ToolRegistry((definition, definition))
        self.assertEqual(duplicate.exception.code, "duplicate_tool")

    def test_fixed_report_keeps_candidate_as_proposal(self) -> None:
        report = fixed_report()
        self.assertIn("candidate=call-id:call_demo1", report)
        self.assertIn("executed:false", report)
        self.assertIn("model-output:proposal-only", report)
        self.assertIn("no-handler,no-side-effects,no-network", report)


if __name__ == "__main__":
    unittest.main()
