from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class FdPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("c++")
        if compiler is None:
            raise unittest.SkipTest("a C++20 compiler is required")
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.binary = Path(cls.temporary.name) / "fd_pipeline"
        source = Path(__file__).with_name("fd_pipeline.cpp")
        compile_result = subprocess.run(
            [compiler, "-std=c++20", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(cls.binary)],
            text=True,
            capture_output=True,
            check=False,
        )
        if compile_result.returncode != 0:
            raise AssertionError(compile_result.stdout + compile_result.stderr)
        cls.completed = subprocess.run(
            [str(cls.binary)],
            text=True,
            capture_output=True,
            check=False,
            timeout=5,
        )
        cls.lines = cls.completed.stdout.splitlines()

    def test_real_pipe_roundtrip(self) -> None:
        self.assertEqual(self.completed.returncode, 0, self.completed.stderr)
        self.assertIn("payload_bytes=11", self.lines)
        self.assertIn("roundtrip=pass", self.lines)

    def test_limited_io_requires_repeated_calls(self) -> None:
        self.assertIn("write_calls=4 read_calls=4", self.lines)

    def test_move_transfers_ownership_once(self) -> None:
        self.assertIn("move_source=empty move_target=closed-after-write", self.lines)

    def test_descriptor_is_closed_deterministically(self) -> None:
        self.assertIn("read_end_before_close=open", self.lines)
        self.assertIn("read_end_after_close=closed", self.lines)
        self.assertEqual(self.lines[-1], "all_descriptors=closed")


if __name__ == "__main__":
    unittest.main()
