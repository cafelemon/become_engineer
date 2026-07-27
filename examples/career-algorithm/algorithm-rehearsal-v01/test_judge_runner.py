from __future__ import annotations

import json
from pathlib import Path
import tempfile
import textwrap
import unittest

from judge_runner import load_cases, normalize_output, run_suite


class JudgeRunnerTests(unittest.TestCase):
    def make_workspace(self, solution: str, cases: list[dict[str, str]]) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "solution.py").write_text(textwrap.dedent(solution), encoding="utf-8")
        (root / "cases.json").write_text(
            json.dumps({"version": 1, "cases": cases}),
            encoding="utf-8",
        )
        return root

    def test_reference_solution_passes_real_subprocess_cases(self) -> None:
        root = Path(__file__).parent
        lines, exit_code = run_suite(root, "solution.py", "cases.json", 1.0)
        self.assertEqual(exit_code, 0)
        self.assertIn("summary passed=3 total=3", lines)

    def test_wrong_answer_is_distinct_from_runtime_error(self) -> None:
        root = self.make_workspace(
            """\
            print("not the expected output")
            """,
            [{"id": "one", "input": "1\n8\n", "expected": "1\n8\n"}],
        )
        lines, exit_code = run_suite(root, "solution.py", "cases.json", 1.0)
        self.assertEqual(exit_code, 1)
        self.assertIn("status=wrong-answer reason=stdout-mismatch", lines[0])

    def test_nonzero_exit_is_runtime_error(self) -> None:
        root = self.make_workspace(
            """\
            raise SystemExit(7)
            """,
            [{"id": "one", "input": "", "expected": "anything\n"}],
        )
        lines, exit_code = run_suite(root, "solution.py", "cases.json", 1.0)
        self.assertEqual(exit_code, 1)
        self.assertIn("status=runtime-error reason=exit-7", lines[0])

    def test_timeout_is_deterministic(self) -> None:
        root = self.make_workspace(
            """\
            while True:
                pass
            """,
            [{"id": "one", "input": "", "expected": ""}],
        )
        lines, exit_code = run_suite(root, "solution.py", "cases.json", 0.05)
        self.assertEqual(exit_code, 1)
        self.assertIn("status=timeout reason=time-limit-exceeded", lines[0])

    def test_solution_cannot_escape_workspace(self) -> None:
        root = self.make_workspace(
            "print('ok')",
            [{"id": "one", "input": "", "expected": "ok\n"}],
        )
        with self.assertRaisesRegex(ValueError, "escapes workspace"):
            run_suite(root, "../outside.py", "cases.json", 1.0)

    def test_case_contract_rejects_duplicate_ids(self) -> None:
        root = self.make_workspace(
            "print('ok')",
            [
                {"id": "same", "input": "", "expected": "ok\n"},
                {"id": "same", "input": "", "expected": "ok\n"},
            ],
        )
        with self.assertRaisesRegex(ValueError, "unique"):
            load_cases(root / "cases.json")

    def test_output_normalization_keeps_internal_difference(self) -> None:
        self.assertEqual(normalize_output("1 2  \r\n"), "1 2\n")
        self.assertNotEqual(normalize_output("1  2\n"), normalize_output("1 2\n"))


if __name__ == "__main__":
    unittest.main()
