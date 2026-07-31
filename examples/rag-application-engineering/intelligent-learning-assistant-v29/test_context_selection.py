import unittest

from context_selection import (
    Candidate,
    Evidence,
    ExtractiveCompressor,
    FixedReranker,
    citation_valid,
    select_context,
)


SOURCE = "Python venv isolates dependencies. Recreate from lock file. HTTP uses ports."
CANDIDATES = (
    Candidate("c1", "guide", 2, "b1", 1, SOURCE, 0, len(SOURCE), 0.8),
    Candidate("c2", "guide", 2, "b1", 1, SOURCE, 0, 35, 0.7),
    Candidate("c3", "web", 1, "b2", 2, "HTTP ports route requests.", 0, 26, 0.9),
)


class ContextSelectionTests(unittest.TestCase):
    def test_reranker_is_second_stage_and_bounded(self):
        result = select_context("python dependencies", CANDIDATES, FixedReranker(), ExtractiveCompressor(), rerank_limit=2, char_budget=100)
        self.assertEqual(result["reranked"], 2)

    def test_extractive_compressor_keeps_exact_coordinates(self):
        evidence = ExtractiveCompressor().compress("dependencies", CANDIDATES[0], 10.0)[0]
        self.assertTrue(citation_valid(evidence, SOURCE))

    def test_overlap_evidence_is_deduplicated_by_coordinates(self):
        result = select_context("python", CANDIDATES[:2], FixedReranker(), ExtractiveCompressor(), rerank_limit=2, char_budget=100)
        self.assertLess(result["deduped"], result["extracted"])

    def test_character_budget_is_hard(self):
        result = select_context("python dependencies", CANDIDATES, FixedReranker(), ExtractiveCompressor(), rerank_limit=3, char_budget=20)
        self.assertTrue(result["budget_ok"])
        self.assertLessEqual(result["characters"], 20)

    def test_diversity_keeps_distinct_sources_when_relevant(self):
        result = select_context("http ports", CANDIDATES, FixedReranker(), ExtractiveCompressor(), rerank_limit=3, char_budget=100, diversity=2.0)
        self.assertIn("web", {item.source_id for item in result["selected"]})

    def test_long_context_places_second_ranked_at_end(self):
        result = select_context("python http", CANDIDATES, FixedReranker(), ExtractiveCompressor(), rerank_limit=3, char_budget=200)
        if len(result["selected"]) > 2:
            self.assertNotEqual(result["selected"][1].rerank_score, sorted((x.rerank_score for x in result["selected"]), reverse=True)[1])

    def test_generated_summary_cannot_pass_exact_citation(self):
        fake = Evidence("c1", "guide", 2, "b1", 1, 0, 6, "摘要文本", 1.0)
        self.assertFalse(citation_valid(fake, SOURCE))

    def test_empty_query_selects_no_extractive_evidence(self):
        result = select_context("", CANDIDATES, FixedReranker(), ExtractiveCompressor(), rerank_limit=3, char_budget=100)
        self.assertEqual(result["selected"], ())


if __name__ == "__main__":
    unittest.main()
