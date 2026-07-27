from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class NonblockingSocketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("c++")
        if compiler is None:
            raise unittest.SkipTest("a C++20 compiler is required")
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.binary = Path(cls.temporary.name) / "nonblocking_socket"
        source = Path(__file__).with_name("nonblocking_socket.cpp")
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

    def test_real_local_socketpair_is_nonblocking(self) -> None:
        self.assertIn("transport=unix-socketpair", self.lines)
        self.assertIn("writer=nonblocking", self.lines)

    def test_full_send_buffer_reports_backpressure(self) -> None:
        self.assertIn("backpressure=EAGAIN-observed", self.lines)
        self.assertIn("poll_while_full=not-writable", self.lines)

    def test_peer_drain_restores_write_readiness(self) -> None:
        self.assertIn("peer_drain=performed", self.lines)
        self.assertIn("poll_after_drain=writable", self.lines)

    def test_resumed_message_is_readable_and_preserved(self) -> None:
        self.assertIn("resume_send=pass", self.lines)
        self.assertIn("reader_event=readable", self.lines)

    def test_descriptors_close_on_every_exit_path(self) -> None:
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assertIn("socketpair=closed-by-raii", self.lines)


if __name__ == "__main__":
    unittest.main()
