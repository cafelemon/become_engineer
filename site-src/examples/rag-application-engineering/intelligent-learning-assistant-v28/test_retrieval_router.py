import unittest

from retrieval_router import Document, RetrievalPlan, acl_filter, retrieve, route, rrf


DOCS = (
    Document("python-1", "learner-a", "python", "python venv environment", (1.0, 0.0), "python-parent"),
    Document("python-2", "learner-a", "python", "dependency install", (0.8, 0.2), "python-parent"),
    Document("http-1", "learner-a", "web", "http port status", (0.0, 1.0), "http-parent"),
    Document("private-1", "learner-b", "python", "python private secret", (1.0, 0.0), "private-parent"),
)


class RetrievalRouterTests(unittest.TestCase):
    def test_normal_query_routes_to_hybrid(self):
        self.assertEqual(route("Python 环境").strategy, "hybrid")

    def test_identifier_routes_to_lexical(self):
        self.assertEqual(route("查找 HTTP-404").strategy, "lexical")

    def test_decomposition_is_bounded(self):
        plan = route("比较 Python 和 HTTP 以及 SQLite")
        self.assertEqual(plan.strategy, "decompose")
        self.assertLessEqual(len(plan.rewrites), 3)

    def test_unknown_filter_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown_filter"):
            route("python", {"raw_sql": "1=1"})

    def test_acl_and_metadata_filter_before_ranking(self):
        authorized = acl_filter(DOCS, "learner-a", (("course", "python"),))
        self.assertEqual({doc.chunk_id for doc in authorized}, {"python-1", "python-2"})

    def test_rrf_deduplicates_and_stabilizes_ties(self):
        self.assertEqual(rrf((("a", "b"), ("b", "a")), 2), ("a", "b"))

    def test_candidate_budget_is_enforced(self):
        plan = RetrievalPlan("python", "hybrid", 8, 8, 1)
        result = retrieve(plan, "learner-a", DOCS, (1.0, 0.0))
        self.assertEqual(len(result["chunk_ids"]), 1)
        self.assertTrue(result["budget_ok"])

    def test_parent_ids_are_deduplicated(self):
        result = retrieve(route("python"), "learner-a", DOCS, (1.0, 0.0))
        self.assertEqual(result["parent_ids"].count("python-parent"), 1)
        self.assertNotIn("private-parent", result["parent_ids"])


if __name__ == "__main__":
    unittest.main()
