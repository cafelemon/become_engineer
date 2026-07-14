import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import main


class MainTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.data_dir = self.root / "data"
        self.data_dir.mkdir()
        self.input_path = self.data_dir / "study_records.json"
        self.output_path = self.root / "output" / "study_report.txt"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_document(self, document):
        self.input_path.write_text(
            json.dumps(document, ensure_ascii=False),
            encoding="utf-8",
        )

    def test_success_returns_zero_and_writes_expected_report(self):
        self.write_document(
            {
                "records": [
                    {
                        "course": "异常与测试",
                        "target_hours": 4,
                        "finished_hours": 4,
                        "tags": ["Python", "测试"],
                    }
                ]
            }
        )
        before = self.input_path.read_bytes()
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main.main(
                self.input_path,
                self.data_dir,
                self.output_path,
            )

        self.assertEqual(exit_code, 0)
        self.assertIn("异常与测试: 100%，已完成", stdout.getvalue())
        self.assertEqual(
            self.output_path.read_text(encoding="utf-8"),
            "学习进度报告\n"
            "总计划：4 小时\n"
            "总完成：4 小时\n"
            "课程状态：\n"
            "- 异常与测试: 100%，已完成\n"
            "唯一标签：Python, 测试\n",
        )
        self.assertEqual(self.input_path.read_bytes(), before)

    def test_missing_file_returns_nonzero_and_uses_stderr(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = main.main(
                self.input_path,
                self.data_dir,
                self.output_path,
            )
        self.assertEqual(exit_code, 1)
        self.assertIn("找不到文件", stderr.getvalue())
        self.assertFalse(self.output_path.exists())

    def test_bad_json_returns_nonzero_and_reports_location(self):
        self.input_path.write_text('{"records": [}', encoding="utf-8")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = main.main(
                self.input_path,
                self.data_dir,
                self.output_path,
            )
        self.assertEqual(exit_code, 1)
        self.assertIn("JSON 格式无效", stderr.getvalue())
        self.assertIn("第 1 行", stderr.getvalue())

    def test_invalid_record_returns_nonzero(self):
        self.write_document(
            {
                "records": [
                    {
                        "course": "异常与测试",
                        "target_hours": -1,
                        "finished_hours": 0,
                        "tags": ["Python"],
                    }
                ]
            }
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = main.main(
                self.input_path,
                self.data_dir,
                self.output_path,
            )
        self.assertEqual(exit_code, 1)
        self.assertIn("target_hours 必须大于 0", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()

