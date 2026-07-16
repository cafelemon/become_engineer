from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import tomllib
from typing import Final


VALID_LOG_LEVELS: Final = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class ConfigError(ValueError):
    """Raised when an explicit application configuration is invalid."""


@dataclass(frozen=True)
class AppConfig:
    report_tag: str | None = None
    audit_output: Path | None = None
    log_level: str = "WARNING"


def _section(data: object, name: str, allowed: set[str]) -> dict[str, object]:
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"[{name}] 必须是 TOML 表")
    unknown = set(data) - allowed
    if unknown:
        raise ConfigError(f"[{name}] 包含未知字段：{', '.join(sorted(unknown))}")
    return data


def _optional_text(section: dict[str, object], key: str, label: str) -> str | None:
    value = section.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{label} 必须是非空字符串")
    return value


def load_config(path: Path | None) -> AppConfig:
    if path is None:
        return AppConfig()
    try:
        with path.open("rb") as config_file:
            raw = tomllib.load(config_file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ConfigError(f"无法读取配置 {path}: {error}") from error

    unknown_sections = set(raw) - {"report", "audit", "logging"}
    if unknown_sections:
        raise ConfigError(f"配置包含未知表：{', '.join(sorted(unknown_sections))}")

    report = _section(raw.get("report"), "report", {"tag"})
    audit = _section(raw.get("audit"), "audit", {"output"})
    logging_section = _section(raw.get("logging"), "logging", {"level"})
    tag = _optional_text(report, "tag", "report.tag")
    output_text = _optional_text(audit, "output", "audit.output")
    level = _optional_text(logging_section, "level", "logging.level") or "WARNING"
    normalized_level = level.upper()
    if normalized_level not in VALID_LOG_LEVELS:
        raise ConfigError(
            "logging.level 必须是 DEBUG、INFO、WARNING、ERROR 或 CRITICAL"
        )
    return AppConfig(
        report_tag=tag,
        audit_output=Path(output_text) if output_text is not None else None,
        log_level=normalized_level,
    )


def apply_cli_overrides(
    config: AppConfig,
    *,
    report_tag: str | None = None,
    audit_output: Path | None = None,
    log_level: str | None = None,
) -> AppConfig:
    normalized_level = config.log_level
    if log_level is not None:
        normalized_level = log_level.upper()
        if normalized_level not in VALID_LOG_LEVELS:
            raise ConfigError(
                "--log-level 必须是 DEBUG、INFO、WARNING、ERROR 或 CRITICAL"
            )
    return replace(
        config,
        report_tag=report_tag if report_tag is not None else config.report_tag,
        audit_output=(
            audit_output if audit_output is not None else config.audit_output
        ),
        log_level=normalized_level,
    )

