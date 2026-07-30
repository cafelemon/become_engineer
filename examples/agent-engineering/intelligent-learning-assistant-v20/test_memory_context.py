from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from memory_context import ContextAssembler, MemoryError, MemoryStore, fixed_report


class MemoryContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.store = MemoryStore(Path(self.temp.name) / "memory.sqlite3")
        self.assembler = ContextAssembler(self.store)

    def tearDown(self) -> None:
        self.store.close()
        self.temp.cleanup()

    def add(self, **overrides) -> None:
        values = {
            "memory_id": "fact-1",
            "subject_id": "learner-a",
            "content": "prefers examples",
            "source_id": "profile-form",
            "consent": True,
            "expires_at": 200,
            "priority": 5,
        }
        values.update(overrides)
        self.store.add_fact(**values)

    def assemble(self, **overrides):
        values = {
            "subject_id": "learner-a",
            "now": 100,
            "working_memory": [],
            "budget_chars": 100,
        }
        values.update(overrides)
        return self.assembler.assemble(**values)

    def test_persistent_fact_survives_new_store(self):
        self.add()
        database = Path(self.temp.name) / "memory.sqlite3"
        self.store.close()
        self.store = MemoryStore(database)
        self.assembler = ContextAssembler(self.store)
        self.assertEqual(self.assemble().entries[0].entry_id, "fact-1")

    def test_source_is_required(self):
        with self.assertRaises(MemoryError):
            self.add(source_id="")

    def test_unconsented_fact_is_excluded(self):
        self.add(consent=False)
        self.assertEqual(self.assemble().entries, ())

    def test_expired_fact_is_excluded(self):
        self.add(expires_at=100)
        self.assertEqual(self.assemble().entries, ())

    def test_subjects_are_isolated(self):
        self.add(subject_id="learner-b")
        self.assertEqual(self.assemble(subject_id="learner-a").entries, ())

    def test_budget_selection_is_deterministic(self):
        self.add(memory_id="fact-b", content="bbbb", priority=5)
        self.add(memory_id="fact-a", content="aaaa", priority=5)
        bundle = self.assemble(budget_chars=4)
        self.assertEqual([entry.entry_id for entry in bundle.entries], ["fact-a"])
        self.assertEqual(bundle.used_chars, 4)

    def test_working_memory_is_ephemeral_and_first(self):
        self.add()
        bundle = self.assemble(
            working_memory=[{"content": "current goal", "source_id": "run-20"}]
        )
        self.assertEqual([entry.category for entry in bundle.entries], ["working", "fact"])
        self.assertEqual(self.store.count(), 1)

    def test_hidden_reasoning_is_rejected_and_report_is_fixed(self):
        with self.assertRaises(MemoryError):
            self.assemble(
                working_memory=[
                    {
                        "content": "visible",
                        "source_id": "run-20",
                        "reasoning": "hidden",
                    }
                ]
            )
        report = fixed_report()
        self.assertIn("eligible=1", report)
        self.assertIn("limit-chars:29", report)
        self.assertIn("hidden-reasoning:true", report)


if __name__ == "__main__":
    unittest.main()
