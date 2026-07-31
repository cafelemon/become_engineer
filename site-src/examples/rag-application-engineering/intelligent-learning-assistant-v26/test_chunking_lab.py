import unittest

from chunking_lab import (
    Block,
    FixedWindowChunker,
    ParentChildChunker,
    RecursiveChunker,
    SemanticBreakpointChunker,
    StructureAwareChunker,
    evaluate,
    fixed_embed,
)


BLOCKS = (
    Block("b1", "Python 环境要隔离。venv 保存依赖。HTTP 端口连接服务。", ("Guide",), 1),
    Block("b2", "SQLite 事务要原子提交。", ("Database",), 2),
)


class ChunkingLabTests(unittest.TestCase):
    def test_fixed_window_preserves_coordinates_and_overlap(self):
        chunks = FixedWindowChunker(18, 4).chunk(BLOCKS[:1])
        self.assertEqual(chunks[0].start, 0)
        self.assertEqual(chunks[1].start, 14)
        self.assertEqual(chunks[0].text, BLOCKS[0].text[chunks[0].start:chunks[0].end])

    def test_invalid_fixed_window_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid_window"):
            FixedWindowChunker(10, 10)

    def test_recursive_prefers_separator(self):
        chunks = RecursiveChunker(24).chunk(BLOCKS[:1])
        self.assertTrue(chunks[0].text.endswith("。"))

    def test_structure_aware_preserves_heading_and_page(self):
        chunks = StructureAwareChunker().chunk(BLOCKS)
        self.assertEqual(chunks[1].heading_path, ("Database",))
        self.assertEqual(chunks[1].page, 2)

    def test_semantic_breakpoint_uses_adapter_and_threshold(self):
        chunks = SemanticBreakpointChunker(fixed_embed, 0.25).chunk(BLOCKS[:1])
        self.assertGreaterEqual(len(chunks), 2)
        self.assertIn("adapter=fixed", chunks[0].strategy_version)

    def test_parent_child_assigns_stable_parent(self):
        chunks = ParentChildChunker(12).chunk(BLOCKS[:1])
        self.assertTrue(all(chunk.parent_id for chunk in chunks))
        self.assertEqual(len({chunk.parent_id for chunk in chunks}), 1)

    def test_evaluation_reports_four_strategy_metrics(self):
        chunks = FixedWindowChunker(18, 4).chunk(BLOCKS)
        metrics = evaluate(chunks, {("b2", len(BLOCKS[1].text))}, "venv")
        self.assertEqual(
            set(metrics),
            {"boundary_coverage", "context_precision", "mean_size", "max_size", "duplicate_rate"},
        )

    def test_strategy_identity_changes_with_parameters(self):
        self.assertNotEqual(FixedWindowChunker(18, 4).version, FixedWindowChunker(20, 4).version)


if __name__ == "__main__":
    unittest.main()
