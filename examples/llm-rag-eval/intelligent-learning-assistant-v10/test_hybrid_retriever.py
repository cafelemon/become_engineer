import math
import unittest

from hybrid_retriever import (
    FIXTURE_VECTORS,
    FixtureEmbeddingAdapter,
    RetrievalError,
    VectorIndex,
    VectorRecord,
    cosine_similarity,
    fixed_report,
    reciprocal_rank_fusion,
    validate_vector,
)


class HybridRetrieverTests(unittest.TestCase):
    def test_fixture_adapter_preserves_batch_order_and_rejects_unknown(self) -> None:
        adapter = FixtureEmbeddingAdapter(FIXTURE_VECTORS)
        self.assertEqual(
            adapter.embed(("HTTP 超时需要截止时间", "Python 虚拟环境隔离依赖")),
            ((1.0, 0.0), (0.8, 0.2)),
        )
        with self.assertRaisesRegex(RetrievalError, "fixture"):
            adapter.embed(("没有固定向量",))

    def test_vector_validation_rejects_bad_shape_values_and_zero(self) -> None:
        for vector, dimension, code in [
            ((1.0,), 2, "dimension_mismatch"),
            ((math.nan, 1.0), None, "invalid_vector"),
            ((math.inf, 1.0), None, "invalid_vector"),
            ((True, 1.0), None, "invalid_vector"),
            ((0.0, 0.0), None, "zero_vector"),
        ]:
            with self.subTest(code=code):
                with self.assertRaises(RetrievalError) as raised:
                    validate_vector(vector, dimension=dimension)
                self.assertEqual(raised.exception.code, code)

    def test_cosine_similarity_is_normalized_and_checks_dimension(self) -> None:
        self.assertAlmostEqual(cosine_similarity((1.0, 0.0), (2.0, 0.0)), 1.0)
        self.assertAlmostEqual(cosine_similarity((1.0, 0.0), (0.0, 1.0)), 0.0)
        with self.assertRaisesRegex(RetrievalError, "dimension"):
            cosine_similarity((1.0, 0.0), (1.0,))

    def test_vector_index_stabilizes_equal_score_by_chunk_id(self) -> None:
        index = VectorIndex([
            VectorRecord("chunk-b", (2.0, 2.0)),
            VectorRecord("chunk-a", (1.0, 1.0)),
        ])
        self.assertEqual(
            [hit.chunk_id for hit in index.search((1.0, 1.0), top_k=2)],
            ["chunk-a", "chunk-b"],
        )

    def test_vector_index_validates_top_k_and_adapter_batch_shape(self) -> None:
        index = VectorIndex([VectorRecord("chunk-a", (1.0, 0.0))])
        for invalid in [True, 0, -1, 1.5]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(RetrievalError) as raised:
                    index.search((1.0, 0.0), top_k=invalid)
                self.assertEqual(raised.exception.code, "invalid_top_k")

        class ShortAdapter:
            def embed(self, texts):
                return ((1.0, 0.0),)

        with self.assertRaisesRegex(RetrievalError, "batch"):
            VectorIndex.from_texts({"a": "A", "b": "B"}, ShortAdapter())

    def test_rrf_combines_ranks_without_comparing_raw_scores(self) -> None:
        hits = reciprocal_rank_fusion(
            (
                ("chunk-python", "chunk-http", "chunk-sqlite"),
                ("chunk-http", "chunk-python", "chunk-sqlite"),
            ),
            allowed_chunk_ids={"chunk-python", "chunk-http", "chunk-sqlite"},
            rank_constant=60,
            top_k=3,
        )
        self.assertEqual([hit.chunk_id for hit in hits], ["chunk-http", "chunk-python", "chunk-sqlite"])
        self.assertEqual(hits[0].ranks, (2, 1))
        self.assertAlmostEqual(hits[0].score, 1 / 62 + 1 / 61)

    def test_rrf_rejects_duplicate_and_unknown_ranked_chunks(self) -> None:
        with self.assertRaises(RetrievalError) as duplicate:
            reciprocal_rank_fusion(
                (("a", "a"),), allowed_chunk_ids={"a"}, top_k=1
            )
        self.assertEqual(duplicate.exception.code, "duplicate_ranked_chunk")
        with self.assertRaises(RetrievalError) as unknown:
            reciprocal_rank_fusion(
                (("missing",),), allowed_chunk_ids={"a"}, top_k=1
            )
        self.assertEqual(unknown.exception.code, "unknown_ranked_chunk")

    def test_fixed_report_is_offline_and_does_not_claim_semantics(self) -> None:
        report = fixed_report()
        self.assertIn("semantic-claim:false,provider-call:false", report)
        self.assertIn("fused-ranking=chunk-http,chunk-python,chunk-sqlite", report)
        self.assertIn("no-semantic-claim,no-generation,no-tools", report)


if __name__ == "__main__":
    unittest.main()
