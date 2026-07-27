from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from corpus_index import (
    CorpusDocument,
    CorpusError,
    FIXTURE_DOCUMENTS,
    build_snapshot,
    fixed_report,
    load_snapshot,
    save_snapshot,
)


class CorpusIndexTests(unittest.TestCase):
    def test_document_contract_rejects_unstable_identity_and_missing_source_anchor(self) -> None:
        for document_id, source_uri in [
            ("Bad ID", "course://python/topic#anchor"),
            ("good-id", "https://example.com/topic"),
            ("good-id", "course://python/topic"),
        ]:
            with self.subTest(document_id=document_id, source_uri=source_uri), self.assertRaises(CorpusError):
                CorpusDocument(document_id, "title", source_uri, "2026-07-26T00:00:00Z", "body")

    def test_reordered_input_produces_same_canonical_fingerprint(self) -> None:
        forward = build_snapshot("public-corpus", FIXTURE_DOCUMENTS)
        backward = build_snapshot("public-corpus", reversed(FIXTURE_DOCUMENTS))
        self.assertEqual(forward.fingerprint, backward.fingerprint)
        self.assertEqual(forward.documents, backward.documents)

    def test_duplicate_id_and_source_are_rejected_separately(self) -> None:
        first = FIXTURE_DOCUMENTS[0]
        duplicate_id = CorpusDocument(
            first.document_id, "other", "course://other/topic#anchor",
            first.updated_at, "other content",
        )
        with self.assertRaises(CorpusError) as caught:
            build_snapshot("public-corpus", [first, duplicate_id])
        self.assertEqual(caught.exception.code, "duplicate_document_id")

        duplicate_source = CorpusDocument(
            "other-id", "other", first.source_uri, first.updated_at, "other content"
        )
        with self.assertRaises(CorpusError) as caught:
            build_snapshot("public-corpus", [first, duplicate_source])
        self.assertEqual(caught.exception.code, "duplicate_source_uri")

    def test_content_change_changes_document_hash_and_snapshot_fingerprint(self) -> None:
        original = build_snapshot("public-corpus", [FIXTURE_DOCUMENTS[0]])
        changed_document = CorpusDocument(
            FIXTURE_DOCUMENTS[0].document_id,
            FIXTURE_DOCUMENTS[0].title,
            FIXTURE_DOCUMENTS[0].source_uri,
            FIXTURE_DOCUMENTS[0].updated_at,
            FIXTURE_DOCUMENTS[0].content + " changed",
        )
        changed = build_snapshot("public-corpus", [changed_document])
        self.assertNotEqual(
            original.documents[0]["content_sha256"],
            changed.documents[0]["content_sha256"],
        )
        self.assertNotEqual(original.fingerprint, changed.fingerprint)

    def test_atomic_save_and_verified_load_round_trip(self) -> None:
        snapshot = build_snapshot("public-corpus", FIXTURE_DOCUMENTS)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index" / "corpus.json"
            save_snapshot(snapshot, path)
            loaded = load_snapshot(path)
            self.assertEqual(loaded, snapshot)
            self.assertEqual(list(path.parent.glob(f".{path.name}.*")), [])

    def test_tampered_content_is_rejected_before_snapshot_fingerprint(self) -> None:
        snapshot = build_snapshot("public-corpus", FIXTURE_DOCUMENTS)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.json"
            save_snapshot(snapshot, path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["documents"][0]["content"] += " tampered"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(CorpusError) as caught:
                load_snapshot(path)
            self.assertEqual(caught.exception.code, "content_hash_mismatch")

    def test_extra_manifest_field_and_noncanonical_order_are_rejected(self) -> None:
        snapshot = build_snapshot("public-corpus", FIXTURE_DOCUMENTS)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.json"
            save_snapshot(snapshot, path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["secret"] = "not allowed"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(CorpusError) as caught:
                load_snapshot(path)
            self.assertEqual(caught.exception.code, "invalid_snapshot")

    def test_fixed_report_is_deterministic_and_does_not_log_content(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("reordered=fingerprint-equal:True", report)
        self.assertIn("logs=content:none,source-uri:none", report)
        for document in FIXTURE_DOCUMENTS:
            self.assertNotIn(document.content, report)
        self.assertTrue(report.endswith(
            "invariants=source-before-index,content-hash-verified,input-order-independent,no-rag-generation,no-tools"
        ))


if __name__ == "__main__":
    unittest.main()
