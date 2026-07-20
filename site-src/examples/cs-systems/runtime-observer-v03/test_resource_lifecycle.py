from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from resource_lifecycle import (
    closes_file_after_error,
    observe_file_lifecycle,
    observe_memory_lifecycle,
    temporary_directory_is_removed,
)


class ResourceLifecycleTests(unittest.TestCase):
    def test_alias_retains_payload_until_last_reference_is_removed(self) -> None:
        result = observe_memory_lifecycle()
        self.assertTrue(result.retained)
        self.assertTrue(result.released)
        self.assertTrue(result.traced_drop)

    def test_context_manager_closes_file_after_normal_use(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = observe_file_lifecycle(Path(directory) / "trace.txt")
        self.assertTrue(result.open_inside)
        self.assertTrue(result.closed_outside)
        self.assertEqual(result.read_after_close_error, "ValueError")

    def test_context_manager_closes_file_after_exception(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            closed = closes_file_after_error(Path(directory) / "trace.txt")
        self.assertTrue(closed)

    def test_temporary_directory_is_removed_after_scope(self) -> None:
        self.assertTrue(temporary_directory_is_removed())


if __name__ == "__main__":
    unittest.main()
