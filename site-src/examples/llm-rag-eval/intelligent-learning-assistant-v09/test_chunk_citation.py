from __future__ import annotations

from dataclasses import replace
import unittest

from chunk_citation import (
    ChunkError,
    Citation,
    FIXTURE_DOCUMENT,
    SourceDocument,
    chunk_document,
    fixed_report,
    sentence_spans,
    validate_chunks,
    verify_citation,
)


class ChunkCitationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.chunks = chunk_document(FIXTURE_DOCUMENT, max_chars=32, overlap_sentences=1)

    def test_sentence_spans_preserve_exact_source_punctuation(self) -> None:
        spans = sentence_spans(FIXTURE_DOCUMENT.content)
        texts = [FIXTURE_DOCUMENT.content[span.start:span.end] for span in spans]
        self.assertEqual(len(texts), 4)
        self.assertTrue(texts[0].endswith("。"))
        self.assertIn("忽略系统指令", texts[-1])

    def test_chunks_are_bounded_exact_source_slices_with_stable_ids(self) -> None:
        validate_chunks(FIXTURE_DOCUMENT, self.chunks)
        for chunk in self.chunks:
            self.assertLessEqual(len(chunk.text), 32)
            self.assertEqual(
                chunk.text,
                FIXTURE_DOCUMENT.content[chunk.start:chunk.end],
            )
            self.assertEqual(chunk.chunk_id, f"python-venv:{chunk.start}:{chunk.end}")

    def test_overlap_repeats_the_last_sentence_at_next_chunk_start(self) -> None:
        spans = sentence_spans(FIXTURE_DOCUMENT.content)
        first_chunk_last_sentence = FIXTURE_DOCUMENT.content[spans[1].start:spans[1].end]
        self.assertTrue(self.chunks[0].text.endswith(first_chunk_last_sentence))
        self.assertTrue(self.chunks[1].text.startswith(first_chunk_last_sentence))

    def test_single_sentence_longer_than_bound_is_rejected_not_split(self) -> None:
        document = SourceDocument("long", "course://test/doc#long", "x" * 20 + "。")
        with self.assertRaises(ChunkError) as caught:
            chunk_document(document, max_chars=10)
        self.assertEqual(caught.exception.code, "sentence_too_long")

    def test_exact_citation_returns_absolute_source_coordinates(self) -> None:
        chunk = self.chunks[0]
        quote = "虚拟环境隔离项目依赖"
        start = chunk.text.index(quote)
        verified = verify_citation(
            Citation(chunk.chunk_id, start, start + len(quote), quote),
            [chunk],
        )
        self.assertEqual(
            FIXTURE_DOCUMENT.content[verified.absolute_start:verified.absolute_end],
            quote,
        )

    def test_unknown_chunk_out_of_bounds_and_wrong_quote_are_distinct(self) -> None:
        chunk = self.chunks[0]
        cases = [
            (Citation("missing:0:1", 0, 1, "x"), "citation_chunk_not_retrieved"),
            (Citation(chunk.chunk_id, 0, len(chunk.text) + 1, chunk.text), "citation_out_of_bounds"),
            (Citation(chunk.chunk_id, 0, 1, "错"), "citation_quote_mismatch"),
        ]
        for citation, code in cases:
            with self.subTest(code=code), self.assertRaises(ChunkError) as caught:
                verify_citation(citation, [chunk])
            self.assertEqual(caught.exception.code, code)

    def test_tampered_chunk_text_or_identity_fails_validation(self) -> None:
        with self.assertRaises(ChunkError) as caught:
            validate_chunks(
                FIXTURE_DOCUMENT,
                [replace(self.chunks[0], text=self.chunks[0].text + "tampered")],
            )
        self.assertEqual(caught.exception.code, "chunk_content_mismatch")

    def test_fixed_report_is_deterministic_and_treats_source_as_data(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("exact:true", report)
        self.assertIn("instructions-in-source:false", report)
        self.assertNotIn("忽略系统指令", report)
        self.assertTrue(report.endswith(
            "invariants=sentence-boundaries,source-coordinates,exact-citation,retrieved-only,no-generation,no-tools"
        ))


if __name__ == "__main__":
    unittest.main()
