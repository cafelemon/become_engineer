from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[4]
BATCH = ROOT / "reviews/course-content/batch-b/examples"


def run(command: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, check=check, text=True, capture_output=True)


class BatchBExamplesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.c_compiler = shutil.which("clang") or shutil.which("gcc")
        self.cpp_compiler = shutil.which("clang++") or shutil.which("g++")
        if not self.c_compiler or not self.cpp_compiler:
            self.skipTest("需要 clang/gcc 与 clang++/g++")

    def test_cpp_build_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "study_status"
            run([self.cpp_compiler, "-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wshadow", str(BATCH / "cpp-build/study_status.cpp"), "-o", str(binary)])
            result = run([str(binary)])
            self.assertEqual(result.stdout, "学习状态卡\n课程：C++ 起步\n本周计划：5 小时\n")

    def test_c_memory_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "device_event"
            run([self.c_compiler, "-std=c17", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wshadow", str(BATCH / "c-memory/device_event.c"), "-o", str(binary)])
            result = run([str(binary)])
            self.assertIn("pin=13, level=1, sequence=1\n", result.stdout)
            self.assertIn("event address=", result.stdout)

    def test_bfs_reachable_and_unreachable(self) -> None:
        result = run([shutil.which("python3") or "python3", str(BATCH / "bfs/bfs_demo.py")])
        self.assertEqual(result.stdout, "path A->E: A -> B -> D -> E\npath A->F: []\n")

    def test_raii_success_and_missing_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            binary = work / "raii_scope"
            run([self.cpp_compiler, "-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wshadow", str(BATCH / "cpp-raii/raii_scope.cpp"), "-o", str(binary)])
            success = run([str(binary), "audit.txt"], cwd=work)
            self.assertEqual(success.stdout, "进入：write_audit\n离开：write_audit\n写入：成功\n")
            self.assertEqual((work / "audit.txt").read_text(encoding="utf-8"), "学习审计快照\n")
            failed = run([str(binary), "missing/audit.txt"], cwd=work, check=False)
            self.assertEqual(failed.returncode, 1)
            self.assertEqual(failed.stdout, "进入：write_audit\n离开：write_audit\n写入：失败\n")

    def test_gpio_event_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "device_event_test"
            run([
                self.c_compiler, "-std=c17", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wshadow",
                str(BATCH / "gpio/device_event.c"), str(BATCH / "gpio/device_event_test.c"),
                "-I", str(BATCH / "gpio"), "-o", str(binary)
            ])
            result = run([str(binary)])
            self.assertEqual(result.stdout, "device event tests passed\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
