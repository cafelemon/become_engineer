import subprocess
import sys
import unittest

from traceable_linear_structures_lab import build_linked_report, build_queue_report, build_stack_report


EXPECTED = {
    "linked": """可追踪线性结构实验
链表：7 -> 3 -> 9
find=3：index=1，visits=2
pop_front=7
remaining：3 -> 9""",
    "stack": """栈实验
push：7, 3, 9
top=9，size=3
pop=9
remaining(top->bottom)：3, 7""",
    "queue": """队列实验
enqueue：7, 3, 9
front=7，back=9，size=3
dequeue=7
remaining(front->back)：3, 9""",
}


class ReportingTests(unittest.TestCase):
    def test_builders(self) -> None:
        self.assertEqual(build_linked_report(), EXPECTED["linked"])
        self.assertEqual(build_stack_report(), EXPECTED["stack"])
        self.assertEqual(build_queue_report(), EXPECTED["queue"])

    def test_module_modes_and_default(self) -> None:
        for arguments, key in (([], "linked"), (["linked"], "linked"), (["stack"], "stack"), (["queue"], "queue")):
            result = subprocess.run(
                [sys.executable, "-m", "traceable_linear_structures_lab", *arguments],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.rstrip("\n"), EXPECTED[key])
            self.assertEqual(result.stderr, "")

    def test_unknown_mode_returns_two(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "traceable_linear_structures_lab", "unknown"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("用法", result.stderr)


if __name__ == "__main__":
    unittest.main()
