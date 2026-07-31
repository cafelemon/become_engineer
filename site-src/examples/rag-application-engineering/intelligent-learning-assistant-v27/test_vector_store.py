import os
import unittest

from vector_store import EmbeddingContract, VectorStore


DATABASE_URL = os.environ["RAG_PGVECTOR_URL"]
CONTRACT = EmbeddingContract("fixture-embedding", "1", 3, True)


class VectorStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = VectorStore(DATABASE_URL)
        cls.store.migrate()

    @classmethod
    def tearDownClass(cls):
        cls.store.close()

    def setUp(self):
        self.store.reset()

    def create_active(self, index_id="idx-v1"):
        self.store.create_index(index_id, CONTRACT)
        self.store.add(
            index_id,
            (
                ("python", "owner-a", "guide", 1, "Python venv", (1.0, 0.0, 0.0)),
                ("http", "owner-a", "guide", 1, "HTTP port", (0.0, 1.0, 0.0)),
                ("private", "owner-b", "private", 1, "Private", (1.0, 0.0, 0.0)),
            ),
        )
        self.store.mark_ready(index_id)
        self.store.activate(index_id)

    def test_migration_installs_vector_extension(self):
        version = self.store.db.execute("SELECT extversion FROM pg_extension WHERE extname='vector'").fetchone()
        self.assertIsNotNone(version)

    def test_contract_rejects_dimension_mismatch(self):
        self.store.create_index("idx", CONTRACT)
        with self.assertRaisesRegex(ValueError, "embedding_dimension"):
            self.store.add("idx", (("x", "owner-a", "s", 1, "x", (1.0, 0.0)),))

    def test_exact_cosine_search_returns_nearest(self):
        self.create_active()
        self.assertEqual(self.store.search("owner-a", (1.0, 0.0, 0.0))[0][0], "python")

    def test_acl_filter_excludes_other_owner(self):
        self.create_active()
        ids = [row[0] for row in self.store.search("owner-a", (1.0, 0.0, 0.0))]
        self.assertNotIn("private", ids)

    def test_hnsw_index_exists(self):
        definition = self.store.db.execute(
            "SELECT indexdef FROM pg_indexes WHERE indexname='chunk_embeddings_hnsw_cosine'"
        ).fetchone()[0]
        self.assertIn("USING hnsw", definition)

    def test_incremental_upsert_updates_same_chunk(self):
        self.create_active()
        self.store.add("idx-v1", (("python", "owner-a", "guide", 2, "Changed", (0.0, 1.0, 0.0)),))
        self.assertEqual(self.store.search("owner-a", (0.0, 1.0, 0.0))[0][0], "http")
        count = self.store.db.execute(
            "SELECT count(*) FROM chunk_embeddings WHERE index_id='idx-v1' AND chunk_id='python'"
        ).fetchone()[0]
        self.assertEqual(count, 1)

    def test_building_index_does_not_change_active(self):
        self.create_active()
        self.store.create_index("idx-v2", CONTRACT)
        self.assertEqual(self.store.active_index(), "idx-v1")

    def test_ready_index_switch_is_atomic(self):
        self.create_active()
        self.store.create_index("idx-v2", CONTRACT)
        self.store.add("idx-v2", (("sqlite", "owner-a", "db", 1, "SQLite", (0.0, 0.0, 1.0)),))
        self.store.mark_ready("idx-v2")
        self.store.activate("idx-v2")
        self.assertEqual(self.store.active_index(), "idx-v2")
        self.assertEqual(self.store.search("owner-a", (0.0, 0.0, 1.0))[0][0], "sqlite")


if __name__ == "__main__":
    unittest.main()
