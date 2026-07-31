import io
import sqlite3
import unittest

from pypdf import PdfWriter

from document_ingestion import IngestionStore, parse_document


def blank_pdf() -> bytes:
    buffer = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.write(buffer)
    return buffer.getvalue()


class DocumentIngestionTests(unittest.TestCase):
    def setUp(self):
        self.store = IngestionStore(sqlite3.connect(":memory:"))
        self.store.create_source("source", "owner-a", "Guide")

    def test_markdown_preserves_heading_path(self):
        blocks = parse_document("text/markdown", b"# Setup\nCreate venv.\n# Run\nStart app.")
        self.assertEqual(blocks[0].heading_path, ("Setup",))
        self.assertEqual(blocks[1].heading_path, ("Run",))

    def test_html_extracts_visible_text(self):
        blocks = parse_document("text/html", b"<h1>Setup</h1><p>Create venv.</p>")
        self.assertEqual(blocks[0].heading_path, ("Setup",))
        self.assertIn("Create venv.", blocks[0].text)

    def test_blank_pdf_requires_ocr(self):
        with self.assertRaisesRegex(ValueError, "ocr_required"):
            parse_document("application/pdf", blank_pdf())

    def test_duplicate_upload_replays_version(self):
        first = self.store.upload("source", "text/markdown", b"# A\nBody")
        second = self.store.upload("source", "text/markdown", b"# A\nBody")
        self.assertEqual(first, (1, False))
        self.assertEqual(second, (1, True))

    def test_successful_job_can_activate(self):
        version, _ = self.store.upload("source", "text/markdown", b"# A\nBody")
        self.assertEqual(self.store.run_job("source:v1"), "indexed")
        self.store.activate("source", version)
        self.assertEqual(self.store.active_version("source"), 1)

    def test_failed_version_does_not_replace_active(self):
        version, _ = self.store.upload("source", "text/markdown", b"# A\nBody")
        self.store.run_job("source:v1")
        self.store.activate("source", version)
        self.store.upload("source", "application/pdf", blank_pdf())
        self.assertEqual(self.store.run_job("source:v2"), "ocr_required")
        with self.assertRaisesRegex(ValueError, "version_not_ready"):
            self.store.activate("source", 2)
        self.assertEqual(self.store.active_version("source"), 1)

    def test_previous_indexed_version_can_be_reactivated(self):
        self.store.upload("source", "text/markdown", b"# A\nOne")
        self.store.run_job("source:v1")
        self.store.activate("source", 1)
        self.store.upload("source", "text/markdown", b"# A\nTwo")
        self.store.run_job("source:v2")
        self.store.activate("source", 2)
        self.store.db.execute(
            "UPDATE versions SET status='indexed' WHERE source_id='source' AND version=1"
        )
        self.store.activate("source", 1)
        self.assertEqual(self.store.active_version("source"), 1)

    def test_deactivate_removes_active_pointer(self):
        self.store.upload("source", "text/markdown", b"# A\nBody")
        self.store.run_job("source:v1")
        self.store.activate("source", 1)
        self.store.deactivate("source")
        self.assertIsNone(self.store.active_version("source"))


if __name__ == "__main__":
    unittest.main()
