import os
import unittest

import psycopg


DATABASE_URL = os.environ.get("RAG_APP_DATABASE_URL")


@unittest.skipUnless(DATABASE_URL, "set RAG_APP_DATABASE_URL for the real PostgreSQL/pgvector test")
class PostgresSchemaTests(unittest.TestCase):
    def connect(self):
        return psycopg.connect(DATABASE_URL)

    def test_vector_extension_is_real(self):
        with self.connect() as connection:
            self.assertEqual("vector", connection.execute("SELECT extname FROM pg_extension WHERE extname='vector'").fetchone()[0])

    def test_rag_tables_exist(self):
        required = {
            "knowledge_sources", "document_versions", "document_blocks", "chunks",
            "embedding_indexes", "chunk_embeddings", "ingestion_jobs", "retrieval_runs",
            "chat_sessions", "chat_messages", "audit_events",
        }
        with self.connect() as connection:
            rows = connection.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'").fetchall()
        self.assertTrue(required <= {row[0] for row in rows})

    def test_source_version_constraints_reject_duplicate_number(self):
        with self.connect() as connection:
            connection.execute("INSERT INTO knowledge_sources VALUES ('schema-src','alice','guide','active')")
            connection.execute("INSERT INTO document_versions VALUES ('schema-v1','schema-src',1,'markdown','one','active')")
            with self.assertRaises(psycopg.errors.UniqueViolation):
                connection.execute("INSERT INTO document_versions VALUES ('schema-v2','schema-src',1,'markdown','two','inactive')")

    def test_embedding_dimension_is_enforced(self):
        with self.connect() as connection:
            connection.execute("INSERT INTO embedding_indexes VALUES ('schema-index','fixed','1',3,true,'cosine','active')")
            connection.execute("INSERT INTO knowledge_sources VALUES ('schema-src2','alice','guide','active')")
            connection.execute("INSERT INTO document_versions VALUES ('schema-v3','schema-src2',1,'markdown','three','active')")
            connection.execute("INSERT INTO document_blocks VALUES ('schema-block','schema-v3',1,'[]')")
            connection.execute("INSERT INTO chunks VALUES ('schema-chunk','schema-v3','schema-block','fixed-v1','fp','body')")
            with self.assertRaises(psycopg.errors.DataException):
                connection.execute("INSERT INTO chunk_embeddings VALUES ('schema-index','schema-chunk','[1,2]'::vector)")


if __name__ == "__main__":
    unittest.main()
