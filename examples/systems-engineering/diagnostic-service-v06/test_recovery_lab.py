from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class RecoveryLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("c++")
        if compiler is None:
            raise unittest.SkipTest("a C++20 compiler is required")
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.binary = Path(cls.temporary.name) / "recovery_lab"
        source = Path(__file__).with_name("recovery_lab.cpp")
        build = subprocess.run(
            [
                compiler,
                "-std=c++20",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(source),
                "-o",
                str(cls.binary),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if build.returncode != 0:
            raise AssertionError(build.stdout + build.stderr)
        cls.result = subprocess.run(
            [str(cls.binary)], text=True, capture_output=True, check=False, timeout=5
        )
        cls.lines = cls.result.stdout.splitlines()

    def test_descriptor_leak_is_observed_then_closed(self) -> None:
        self.assertIn("fault=descriptor-leak injected=1", self.lines)
        self.assertIn("detector=fd-still-open", self.lines)
        self.assertIn("fd_after_recovery=closed", self.lines)

    def test_failed_child_is_reaped_with_status_preserved(self) -> None:
        self.assertIn("child_fault=exit-7", self.lines)
        self.assertIn("child_recovery=reaped", self.lines)

    def test_broken_transport_is_recreated(self) -> None:
        self.assertIn("transport_fault=EPIPE-observed", self.lines)
        self.assertIn("transport_recovery=reconnected", self.lines)

    def test_temporary_artifact_is_removed(self) -> None:
        self.assertIn("temporary_artifact=removed", self.lines)

    def test_all_recovery_invariants_hold(self) -> None:
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assertIn("resource_baseline=restored", self.lines)


if __name__ == "__main__":
    unittest.main()
