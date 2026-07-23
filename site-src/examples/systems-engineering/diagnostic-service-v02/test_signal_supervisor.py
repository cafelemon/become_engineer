from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class SignalSupervisorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("c++")
        if compiler is None:
            raise unittest.SkipTest("a C++20 compiler is required")
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.binary = Path(cls.temporary.name) / "signal_supervisor"
        source = Path(__file__).with_name("signal_supervisor.cpp")
        result = subprocess.run(
            [compiler, "-std=c++20", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(cls.binary)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)

    def run_supervisor(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(self.binary), *args],
            text=True,
            capture_output=True,
            check=False,
            timeout=5,
        )

    def test_sigterm_becomes_main_loop_notification(self) -> None:
        result = self.run_supervisor()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("signal_handler=notification-only", result.stdout)
        self.assertIn("supervisor_event=SIGTERM", result.stdout)

    def test_worker_is_stopped_and_reaped(self) -> None:
        result = self.run_supervisor()
        self.assertIn("worker_cleanup=confirmed-by-exit", result.stdout)
        self.assertIn("worker_exit=0", result.stdout)
        self.assertIn("worker_reaped=yes", result.stdout)

    def test_nonzero_worker_exit_is_reported_not_hidden(self) -> None:
        result = self.run_supervisor("--child-exit", "7")
        self.assertEqual(result.returncode, 1)
        self.assertIn("worker_exit=7", result.stdout)
        self.assertIn("supervision_result=child-failure", result.stdout)

    def test_invalid_child_exit_is_configuration_error(self) -> None:
        result = self.run_supervisor("--child-exit", "126")
        self.assertEqual(result.returncode, 2)
        self.assertIn("argument_error=child exit must be from 0 to 125", result.stderr)

    def test_self_pipe_is_closed_after_reap(self) -> None:
        result = self.run_supervisor()
        self.assertIn("self_pipe=closed", result.stdout)
        self.assertEqual(result.stdout.splitlines()[-1], "supervision_result=pass")


if __name__ == "__main__":
    unittest.main()
