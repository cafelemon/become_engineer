from __future__ import annotations

import unittest

from bm25_retriever import (
    BM25Index,
    FIXTURE_DOCUMENTS,
    RetrievalError,
    SearchDocument,
    fixed_report,
    tokenize,
)


class BM25RetrieverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.index = BM25Index(FIXTURE_DOCUMENTS)

    def test_tokenizer_normalizes_ascii_and_adds_han_unigrams_and_bigrams(self) -> None:
        tokens = tokenize("ＰＹＴＨＯＮ 权限")
        self.assertIn("python", tokens)
        self.assertIn("zh1:权", tokens)
        self.assertIn("zh2:权限", tokens)

    def test_fixed_queries_rank_expected_documents_first(self) -> None:
        cases = {
            "403 权限不足": "http-status",
            "虚拟环境 项目依赖": "python-venv",
            "事务 回滚": "sqlite-transaction",
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                self.assertEqual(self.index.search(query)[0].document_id, expected)

    def test_empty_and_out_of_vocabulary_queries_return_no_results(self) -> None:
        self.assertEqual(self.index.search("   "), ())
        self.assertEqual(self.index.search("量子香蕉"), ())

    def test_top_k_is_bounded_and_rejects_boolean_or_zero(self) -> None:
        results = self.index.search("环境 事务 身份", top_k=2)
        self.assertLessEqual(len(results), 2)
        for value in [True, 0, -1, 1.5]:
            with self.subTest(value=value), self.assertRaises(RetrievalError) as caught:
                self.index.search("环境", value)  # type: ignore[arg-type]
            self.assertEqual(caught.exception.code, "invalid_top_k")

    def test_equal_scores_use_document_id_as_stable_tie_breaker(self) -> None:
        documents = [
            SearchDocument("zeta", "same", "shared token"),
            SearchDocument("alpha", "same", "shared token"),
        ]
        index = BM25Index(reversed(documents))
        self.assertEqual(
            [result.document_id for result in index.search("shared")],
            ["alpha", "zeta"],
        )

    def test_rare_term_has_higher_idf_than_common_term(self) -> None:
        index = BM25Index([
            SearchDocument("a", "common", "common rare"),
            SearchDocument("b", "common", "common other"),
            SearchDocument("c", "common", "common third"),
        ])
        self.assertGreater(
            index.inverse_document_frequency("rare"),
            index.inverse_document_frequency("common"),
        )

    def test_explanation_contributions_sum_to_result_score(self) -> None:
        result = self.index.search("403 权限不足")[0]
        explanation = self.index.explain("403 权限不足", result.document_id)
        self.assertAlmostEqual(sum(explanation.values()), result.score)
        self.assertEqual(tuple(sorted(explanation)), result.matched_terms)

    def test_fixed_report_is_deterministic_and_names_tokenizer_limit(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("query-unknown=none", report)
        self.assertIn("general-segmentation:false", report)
        self.assertTrue(report.endswith(
            "invariants=lexical-baseline,explainable-contributions,stable-ties,no-embedding,no-generation,no-tools"
        ))


if __name__ == "__main__":
    unittest.main()
