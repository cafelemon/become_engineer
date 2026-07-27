from __future__ import annotations

import unittest

from stream_assembler import (
    StreamAssembler,
    StreamEvent,
    StreamProtocolError,
    assemble,
    fixed_report,
)


class StreamAssemblerTests(unittest.TestCase):
    def test_ordered_deltas_complete_exact_text(self) -> None:
        result = assemble([
            StreamEvent(0, "response.created"),
            StreamEvent(1, "output_text.delta", "学习"),
            StreamEvent(2, "output_text.delta", "计划"),
            StreamEvent(3, "response.completed", finish_reason="stop"),
        ])
        self.assertEqual((result.status, result.text), ("completed", "学习计划"))
        self.assertEqual(result.events_seen, 4)

    def test_gap_and_duplicate_sequence_are_rejected(self) -> None:
        for bad_sequence in [0, 2]:
            with self.subTest(sequence=bad_sequence):
                assembler = StreamAssembler()
                assembler.feed(StreamEvent(0, "response.created"))
                with self.assertRaises(StreamProtocolError) as caught:
                    assembler.feed(StreamEvent(bad_sequence, "output_text.delta", "x"))
                self.assertEqual(caught.exception.code, "sequence_mismatch")

    def test_created_must_be_first_and_unique(self) -> None:
        with self.assertRaises(StreamProtocolError) as caught:
            StreamAssembler().feed(StreamEvent(0, "output_text.delta", "x"))
        self.assertEqual(caught.exception.code, "missing_created")

        assembler = StreamAssembler()
        assembler.feed(StreamEvent(0, "response.created"))
        with self.assertRaises(StreamProtocolError) as caught:
            assembler.feed(StreamEvent(1, "response.created"))
        self.assertEqual(caught.exception.code, "duplicate_created")

    def test_incomplete_preserves_partial_but_is_not_completed(self) -> None:
        result = assemble([
            StreamEvent(0, "response.created"),
            StreamEvent(1, "output_text.delta", "未完"),
            StreamEvent(2, "response.incomplete", finish_reason="max_output"),
        ])
        self.assertEqual(result.status, "incomplete")
        self.assertEqual(result.text, "未完")
        self.assertNotEqual(result.status, "completed")

    def test_refusal_has_no_output_text(self) -> None:
        result = assemble([
            StreamEvent(0, "response.created"),
            StreamEvent(1, "response.refused", finish_reason="safety"),
        ])
        self.assertEqual((result.status, result.text), ("refused", ""))

        with self.assertRaises(StreamProtocolError) as caught:
            assemble([
                StreamEvent(0, "response.created"),
                StreamEvent(1, "output_text.delta", "partial"),
                StreamEvent(2, "response.refused", finish_reason="safety"),
            ])
        self.assertEqual(caught.exception.code, "partial_before_refusal")

    def test_cancel_preserves_partial_and_stops_consumption(self) -> None:
        assembler = StreamAssembler()
        assembler.feed(StreamEvent(0, "response.created"))
        assembler.feed(StreamEvent(1, "output_text.delta", "部分"))
        result = assembler.cancel()
        self.assertEqual((result.status, result.text), ("cancelled", "部分"))
        with self.assertRaises(StreamProtocolError) as caught:
            assembler.feed(StreamEvent(2, "response.completed", finish_reason="stop"))
        self.assertEqual(caught.exception.code, "event_after_terminal")

    def test_missing_terminal_and_output_bound_are_enforced(self) -> None:
        assembler = StreamAssembler(max_chars=3)
        assembler.feed(StreamEvent(0, "response.created"))
        assembler.feed(StreamEvent(1, "output_text.delta", "abc"))
        with self.assertRaises(StreamProtocolError) as caught:
            assembler.feed(StreamEvent(2, "output_text.delta", "d"))
        self.assertEqual(caught.exception.code, "output_too_large")

        open_stream = StreamAssembler()
        open_stream.feed(StreamEvent(0, "response.created"))
        with self.assertRaises(StreamProtocolError) as caught:
            open_stream.finalize()
        self.assertEqual(caught.exception.code, "missing_terminal")

    def test_fixed_report_is_deterministic_and_never_promotes_partial(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("incomplete=status:incomplete,partial:未完", report)
        self.assertIn("partial-is-complete:false", report)
        self.assertTrue(report.endswith(
            "invariants=created-first,one-terminal,cancel-stops-consumption,no-rag,no-tools"
        ))


if __name__ == "__main__":
    unittest.main()
