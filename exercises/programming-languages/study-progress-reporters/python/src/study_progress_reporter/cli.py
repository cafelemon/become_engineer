from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

from study_progress_reporter.analysis import filter_by_tag
from study_progress_reporter.config import ConfigError, apply_cli_overrides, load_config
from study_progress_reporter.fixtures import sample_records
from study_progress_reporter.logging_setup import configure_logging
from study_progress_reporter.reporting import build_report, write_audit_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="study-progress",
        description="生成学习进度报告或审计快照。",
    )
    parser.add_argument("--config", type=Path, help="显式 TOML 配置文件")
    parser.add_argument("--log-level", help="DEBUG/INFO/WARNING/ERROR/CRITICAL")
    subparsers = parser.add_subparsers(dest="command", required=True)

    report_parser = subparsers.add_parser("report", help="输出学习进度报告")
    report_parser.add_argument("--tag", help="只报告包含该标签的记录")

    audit_parser = subparsers.add_parser("audit", help="写入学习审计快照")
    audit_parser.add_argument("--output", type=Path, help="审计输出路径")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        config = apply_cli_overrides(
            load_config(arguments.config),
            report_tag=getattr(arguments, "tag", None),
            audit_output=getattr(arguments, "output", None),
            log_level=arguments.log_level,
        )
    except ConfigError as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1

    logger = configure_logging(config.log_level)
    records = sample_records()
    logger.info("执行命令：%s", arguments.command)

    if arguments.command == "report":
        selected_records = (
            filter_by_tag(records, config.report_tag)
            if config.report_tag is not None
            else records
        )
        print(build_report(selected_records))
        return 0

    if config.audit_output is None:
        logger.error("audit 需要 --output 或 [audit].output")
        return 1
    if not write_audit_snapshot(records, config.audit_output):
        logger.error("无法写入审计文件：%s", config.audit_output)
        return 1
    logger.info("审计文件已写入：%s", config.audit_output)
    return 0
