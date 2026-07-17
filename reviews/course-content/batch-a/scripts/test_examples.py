from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


BATCH_ROOT = Path(__file__).resolve().parents[1]


def run_example(relative_path: str, *, stdin: str = "") -> subprocess.CompletedProcess[str]:
    file_path = BATCH_ROOT / relative_path
    return subprocess.run(
        [sys.executable, str(file_path)],
        cwd=file_path.parent,
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )


class BatchAExampleTests(unittest.TestCase):
    def test_profile_basic_output(self) -> None:
        result = run_example("examples/python-variables/profile_basic.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "学习档案\n昵称： 小码\n课程： Python 起步\n")

    def test_profile_types_exposes_four_types(self) -> None:
        result = run_example("examples/python-variables/profile_types.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        for type_name in ("str", "int", "float", "bool"):
            self.assertIn(f"<class '{type_name}'>", result.stdout)

    def test_profile_input_success_and_value_error(self) -> None:
        success = run_example("examples/python-variables/profile_input.py", stdin="小码\nPython 起步\n5\n")
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertIn("下周建议： 6", success.stdout)
        failure = run_example("examples/python-variables/profile_input.py", stdin="小码\nPython 起步\nfive\n")
        self.assertNotEqual(failure.returncode, 0)
        self.assertIn("ValueError", failure.stderr)

    def test_v01_snapshot(self) -> None:
        result = run_example("examples/study-reporter/v0.1/main.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("本周计划：5 小时", result.stdout)

    def test_v03_snapshot(self) -> None:
        result = run_example("examples/study-reporter/v0.3/main.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("进度：60%", result.stdout)
        self.assertIn("状态：进行中", result.stdout)

    def test_v05_snapshot_uses_json_without_mutating_it(self) -> None:
        data_path = BATCH_ROOT / "examples/study-reporter/v0.5/data/study_records.json"
        before = data_path.read_bytes()
        result = run_example("examples/study-reporter/v0.5/main.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "学习进度\n- Python 起步: 60%\n- 工程基础: 100%\n")
        self.assertEqual(data_path.read_bytes(), before)
        self.assertEqual(len(json.loads(before)), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
