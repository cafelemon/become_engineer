from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class BoundedQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("c++")
        if compiler is None:
            raise unittest.SkipTest("a C++20 compiler is required")
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.binary = Path(cls.temporary.name) / "bounded_queue"
        source = Path(__file__).with_name("bounded_queue.cpp")
        result = subprocess.run(
            [compiler, "-std=c++20", "-pthread", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(cls.binary)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        cls.result = subprocess.run(
            [str(cls.binary)], text=True, capture_output=True, check=False, timeout=5
        )
        cls.lines = cls.result.stdout.splitlines()

    def test_capacity_creates_deterministic_backpressure(self) -> None:
        self.assertIn("capacity=1", self.lines)
        self.assertIn("backpressure=observed waiting_producers=1", self.lines)

    def test_every_accepted_item_is_processed(self) -> None:
        self.assertIn("accepted=3 processed=3", self.lines)
        self.assertIn("invariant=accepted-equals-processed", self.lines)

    def test_fifo_order_is_preserved(self) -> None:
        self.assertIn("order=1,2,3", self.lines)

    def test_close_rejects_new_work(self) -> None:
        self.assertIn("push_after_close=rejected", self.lines)

    def test_closed_drained_queue_wakes_consumer(self) -> None:
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assertIn("pop_after_drain=closed", self.lines)


if __name__ == "__main__":
    unittest.main()
