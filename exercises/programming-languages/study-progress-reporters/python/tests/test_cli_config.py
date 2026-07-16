import io
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from contextlib import redirect_stderr, redirect_stdout

from study_progress_reporter.cli import main
from study_progress_reporter.config import ConfigError, apply_cli_overrides, load_config


class ConfigurationTests(unittest.TestCase):
    def test_no_explicit_config_uses_quiet_defaults(self) -> None:
        config = load_config(None)
        self.assertIsNone(config.report_tag)
        self.assertIsNone(config.audit_output)
        self.assertEqual(config.log_level, "WARNING")

    def test_toml_loads_all_public_sections(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "reporter.toml"
            path.write_text(
                '[report]\ntag = "基础"\n[audit]\noutput = "audit.txt"\n'
                '[logging]\nlevel = "info"\n',
                encoding="utf-8",
            )
            config = load_config(path)
        self.assertEqual(config.report_tag, "基础")
        self.assertEqual(config.audit_output, Path("audit.txt"))
        self.assertEqual(config.log_level, "INFO")

    def test_cli_values_override_toml_values(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "reporter.toml"
            path.write_text(
                '[report]\ntag = "基础"\n[audit]\noutput = "old.txt"\n'
                '[logging]\nlevel = "WARNING"\n',
                encoding="utf-8",
            )
            config = apply_cli_overrides(
                load_config(path),
                report_tag="工程",
                audit_output=Path("new.txt"),
                log_level="DEBUG",
            )
        self.assertEqual(config.report_tag, "工程")
        self.assertEqual(config.audit_output, Path("new.txt"))
        self.assertEqual(config.log_level, "DEBUG")

    def test_malformed_toml_and_unknown_fields_are_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            malformed = root / "malformed.toml"
            malformed.write_text("[report\ntag = 1", encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(malformed)

            unknown = root / "unknown.toml"
            unknown.write_text("[report]\ncolour = 'blue'\n", encoding="utf-8")
            with self.assertRaisesRegex(ConfigError, "未知字段"):
                load_config(unknown)

    def test_wrong_types_empty_values_and_log_levels_are_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            wrong_type = root / "wrong.toml"
            wrong_type.write_text("[report]\ntag = 3\n", encoding="utf-8")
            with self.assertRaisesRegex(ConfigError, "非空字符串"):
                load_config(wrong_type)

            empty = root / "empty.toml"
            empty.write_text("[audit]\noutput = '  '\n", encoding="utf-8")
            with self.assertRaisesRegex(ConfigError, "非空字符串"):
                load_config(empty)

            bad_level = root / "level.toml"
            bad_level.write_text("[logging]\nlevel = 'TRACE'\n", encoding="utf-8")
            with self.assertRaisesRegex(ConfigError, "logging.level"):
                load_config(bad_level)


class CliTests(unittest.TestCase):
    def run_main(self, arguments: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(arguments)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_default_report_preserves_stdout_and_is_quiet(self) -> None:
        code, stdout, stderr = self.run_main(["report"])
        self.assertEqual(code, 0)
        self.assertIn("总体进度：87.1%", stdout)
        self.assertEqual(stderr, "")

    def test_tag_filter_is_observable_without_mutating_default_report(self) -> None:
        code, filtered, stderr = self.run_main(["report", "--tag", "工程"])
        self.assertEqual(code, 0)
        self.assertIn("工程复盘", filtered)
        self.assertNotIn("Python 起步", filtered)
        self.assertEqual(stderr, "")
        _, default, _ = self.run_main(["report"])
        self.assertIn("Python 起步", default)

    def test_explicit_config_applies_tag_and_info_logging(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "reporter.toml"
            path.write_text(
                '[report]\ntag = "工程"\n[logging]\nlevel = "INFO"\n',
                encoding="utf-8",
            )
            code, stdout, stderr = self.run_main(
                ["--config", str(path), "report"]
            )
        self.assertEqual(code, 0)
        self.assertIn("工程复盘", stdout)
        self.assertNotIn("Python 起步", stdout)
        self.assertIn("INFO study_progress_reporter", stderr)

    def test_command_line_overrides_config(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "reporter.toml"
            path.write_text(
                '[report]\ntag = "工程"\n[logging]\nlevel = "DEBUG"\n',
                encoding="utf-8",
            )
            code, stdout, stderr = self.run_main(
                ["--config", str(path), "--log-level", "WARNING", "report", "--tag", "基础"]
            )
        self.assertEqual(code, 0)
        self.assertIn("Python 起步", stdout)
        self.assertNotIn("工程复盘", stdout)
        self.assertEqual(stderr, "")

    def test_audit_requires_output_and_reports_io_failure(self) -> None:
        code, stdout, stderr = self.run_main(["audit"])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("需要 --output", stderr)

        with TemporaryDirectory() as directory:
            missing = Path(directory) / "missing" / "audit.txt"
            code, stdout, stderr = self.run_main(
                ["audit", "--output", str(missing)]
            )
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("无法写入审计文件", stderr)

    def test_audit_success_and_failed_write_preserve_old_file(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "audit.txt"
            code, stdout, stderr = self.run_main(
                ["--log-level", "INFO", "audit", "--output", str(output)]
            )
            self.assertEqual(code, 0)
            self.assertEqual(stdout, "")
            self.assertTrue(output.read_text(encoding="utf-8").startswith("学习审计快照"))
            self.assertIn("审计文件已写入", stderr)

            output.write_text("旧内容\n", encoding="utf-8")
            bad_config = root / "bad.toml"
            bad_config.write_text("[logging\n", encoding="utf-8")
            code, _, _ = self.run_main(
                ["--config", str(bad_config), "audit", "--output", str(output)]
            )
            self.assertEqual(code, 1)
            self.assertEqual(output.read_text(encoding="utf-8"), "旧内容\n")

    def test_invalid_config_returns_one_on_stderr(self) -> None:
        code, stdout, stderr = self.run_main(
            ["--config", "missing.toml", "report"]
        )
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("错误：无法读取配置", stderr)

    def test_module_entry_help_and_console_script_contract(self) -> None:
        environment = dict(os.environ)
        result = subprocess.run(
            [sys.executable, "-m", "study_progress_reporter", "report"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=environment,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("总体进度：87.1%", result.stdout)
        self.assertEqual(result.stderr, "")

        help_result = subprocess.run(
            [sys.executable, "-m", "study_progress_reporter", "--help"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=environment,
        )
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("report", help_result.stdout)
        self.assertIn("audit", help_result.stdout)

    def test_argparse_syntax_error_uses_exit_code_two(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "study_progress_reporter", "unknown"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("usage:", result.stderr)


if __name__ == "__main__":
    unittest.main()
