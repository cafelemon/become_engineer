import json
import tempfile
import unittest
from pathlib import Path

from data_io import load_records, write_report


class DataIoTests(unittest.TestCase):
    def write_document(self, directory, document):
        path = Path(directory) / "records.json"
        path.write_text(
            json.dumps(document, ensure_ascii=False),
            encoding="utf-8",
        )
        return path

    def test_loads_utf8_without_modifying_input(self):
        with tempfile.TemporaryDirectory() as directory:
            document = {
                "records": [
                    {
                        "course": "文件与 JSON",
                        "target_hours": 3,
                        "finished_hours": 2,
                        "tags": ["中文", "Python"],
                    }
                ]
            }
            path = self.write_document(directory, document)
            before = path.read_bytes()

            records = load_records(path)

            self.assertEqual(records[0]["course"], "文件与 JSON")
            self.assertEqual(path.read_bytes(), before)

    def test_missing_file_is_preserved_as_file_not_found(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.json"
            with self.assertRaises(FileNotFoundError):
                load_records(path)

    def test_bad_json_is_preserved_as_decode_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"records": [}', encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                load_records(path)

    def test_rejects_missing_field_wrong_type_and_invalid_number(self):
        invalid_documents = [
            {"records": [{"course": "函数"}]},
            {
                "records": [
                    {
                        "course": "函数",
                        "target_hours": "4",
                        "finished_hours": 2,
                        "tags": ["Python"],
                    }
                ]
            },
            {
                "records": [
                    {
                        "course": "函数",
                        "target_hours": 0,
                        "finished_hours": 0,
                        "tags": ["Python"],
                    }
                ]
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            for document in invalid_documents:
                with self.subTest(document=document):
                    path = self.write_document(directory, document)
                    with self.assertRaises(ValueError):
                        load_records(path)

    def test_writes_report_to_a_new_output_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "output" / "report.txt"
            write_report(path, "学习报告\n")
            self.assertEqual(path.read_text(encoding="utf-8"), "学习报告\n")


if __name__ == "__main__":
    unittest.main()

