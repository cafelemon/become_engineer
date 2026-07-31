import unittest

from knowledge_service import KnowledgeService


class KnowledgeServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = KnowledgeService()
        self.source = self.service.create_source("alice", "guide")

    def upload(self, content="ACL 必须在召回前执行。"):
        return self.service.upload("alice", self.source["source_id"], "markdown", content)

    def test_duplicate_upload_replays_version_and_job(self):
        first = self.upload()
        replay = self.upload()
        self.assertTrue(replay["replayed"])
        self.assertEqual(first["version"]["version_id"], replay["version"]["version_id"])

    def test_new_version_atomically_becomes_active(self):
        self.upload("第一版")
        second = self.upload("第二版")
        versions = self.service.list_versions("alice", self.source["source_id"])
        self.assertEqual(["inactive", "active"], [item["status"] for item in versions])
        self.assertEqual(2, second["version"]["version"])

    def test_rollback_changes_active_version(self):
        self.upload("第一版")
        self.upload("第二版")
        active = self.service.rollback("alice", self.source["source_id"], 1)
        self.assertEqual(1, active["version"])
        self.assertEqual("active", active["status"])

    def test_acl_runs_before_retrieval_candidates(self):
        self.upload()
        other = self.service.create_source("bob", "private")
        self.service.upload("bob", other["source_id"], "markdown", "ACL 私有内容")
        run = self.service.debug_retrieval("alice", "ACL")
        self.assertEqual(1, run["stages"]["authorized"])
        self.assertTrue(all(item["source_id"] != other["source_id"] for item in run["candidates"]))

    def test_inactive_source_is_not_retrieved(self):
        self.upload()
        self.service.deactivate("alice", self.source["source_id"])
        self.assertEqual(0, self.service.debug_retrieval("alice", "ACL")["stages"]["authorized"])

    def test_chat_refuses_without_evidence(self):
        session = self.service.create_session("alice")
        answer = self.service.chat("alice", session["session_id"], "不存在的答案")
        self.assertTrue(answer["refused"])
        self.assertEqual([], answer["citations"])

    def test_chat_returns_versioned_exact_citation(self):
        self.upload()
        session = self.service.create_session("alice")
        answer = self.service.chat("alice", session["session_id"], "ACL")
        self.assertFalse(answer["refused"])
        self.assertEqual({"source_id", "version", "page", "block_id", "chunk_id"}, set(answer["citations"][0]))

    def test_cross_subject_session_is_hidden(self):
        session = self.service.create_session("alice")
        with self.assertRaises(KeyError):
            self.service.chat("bob", session["session_id"], "ACL")

    def test_prompt_and_context_package_are_recorded(self):
        self.upload()
        session = self.service.create_session("alice")
        answer = self.service.chat("alice", session["session_id"], "ACL")
        self.assertEqual("grounded-answer-v1", answer["prompt_version"])
        self.assertEqual(answer["citations"], answer["context_package"])

    def test_metrics_are_low_cardinality(self):
        self.service.debug_retrieval("alice", "ACL")
        metrics = self.service.metrics()
        self.assertIn("rag_retrievals_total 1", metrics)
        self.assertNotIn(self.source["source_id"], metrics)


if __name__ == "__main__":
    unittest.main()
