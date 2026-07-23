"""Validate a first project portfolio and propose reversible route trials."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REQUIRED_KINDS = ("code", "tests", "readme", "reflection")
ROUTES = {
    "application-engineering": {
        "signals": {"interface", "data-flow", "web"},
        "next": "python-core or web-start",
    },
    "systems-engineering": {
        "signals": {"runtime", "resource", "cpp"},
        "next": "cpp-start and cs-systems-core",
    },
    "algorithm": {
        "signals": {"correctness", "trace", "complexity"},
        "next": "algorithm-foundation",
    },
    "ai-model": {
        "signals": {"data", "experiment", "metric"},
        "next": "ai-math-data",
    },
    "llm-agent": {
        "signals": {"contract", "evaluation", "tool"},
        "next": "llm-use",
    },
    "device-systems": {
        "signals": {"hardware", "timing", "reliability"},
        "next": "c-start",
    },
}


class PortfolioError(ValueError):
    pass


@dataclass(frozen=True)
class RouteTrial:
    route: str
    interest: int
    matched_signals: tuple[str, ...]
    note: str

    @property
    def evidence_count(self) -> int:
        return len(self.matched_signals)


@dataclass(frozen=True)
class PortfolioReport:
    project_id: str
    evidence: tuple[tuple[str, str], ...]
    route_trials: tuple[RouteTrial, ...]

    def as_text(self) -> str:
        lines = [f"project={self.project_id}"]
        lines.extend(f"evidence {kind}=pass path={path}" for kind, path in self.evidence)
        lines.append("gate=pass")
        for trial in self.route_trials:
            lines.append(
                "trial "
                f"route={trial.route} interest={trial.interest} "
                f"matched={trial.evidence_count} next={ROUTES[trial.route]['next']}"
            )
        selected = ",".join(trial.route for trial in self.route_trials[:2])
        lines.append(f"next_experiments={selected}")
        lines.append("decision=two-week-trial-not-career-conclusion")
        return "\n".join(lines)


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PortfolioError(f"{label} must be an object")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PortfolioError(f"{label} must be non-empty text")
    return value.strip()


def _safe_file(workspace: Path, raw_path: Any) -> Path:
    relative = Path(_text(raw_path, "artifact.path"))
    if relative.is_absolute():
        raise PortfolioError("artifact path must be relative")
    workspace = workspace.resolve()
    resolved = (workspace / relative).resolve()
    if not resolved.is_relative_to(workspace):
        raise PortfolioError("artifact path escapes workspace")
    if not resolved.is_file() or resolved.stat().st_size == 0:
        raise PortfolioError(f"artifact is missing or empty: {relative.as_posix()}")
    return relative


def load_report(manifest_path: Path, workspace: Path) -> PortfolioReport:
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PortfolioError(f"cannot read manifest: {exc}") from exc
    root = _object(payload, "manifest")
    project_id = _text(root.get("project_id"), "project_id")

    raw_artifacts = root.get("artifacts")
    if not isinstance(raw_artifacts, list):
        raise PortfolioError("artifacts must be a list")
    found: dict[str, str] = {}
    for index, raw in enumerate(raw_artifacts):
        item = _object(raw, f"artifacts[{index}]")
        kind = _text(item.get("kind"), "artifact.kind")
        if kind not in REQUIRED_KINDS:
            raise PortfolioError(f"unknown artifact kind: {kind}")
        if kind in found:
            raise PortfolioError(f"duplicate artifact kind: {kind}")
        _text(item.get("claim"), "artifact.claim")
        relative = _safe_file(workspace, item.get("path"))
        found[kind] = relative.as_posix()
    missing = [kind for kind in REQUIRED_KINDS if kind not in found]
    if missing:
        raise PortfolioError(f"missing evidence kinds: {','.join(missing)}")

    raw_trials = root.get("route_trials")
    if not isinstance(raw_trials, list) or not raw_trials:
        raise PortfolioError("route_trials must contain at least one trial")
    trials: list[RouteTrial] = []
    seen_routes: set[str] = set()
    for index, raw in enumerate(raw_trials):
        item = _object(raw, f"route_trials[{index}]")
        route = _text(item.get("route"), "trial.route")
        if route not in ROUTES:
            raise PortfolioError(f"unknown route: {route}")
        if route in seen_routes:
            raise PortfolioError(f"duplicate route trial: {route}")
        seen_routes.add(route)
        interest = item.get("interest")
        if not isinstance(interest, int) or isinstance(interest, bool) or not 1 <= interest <= 5:
            raise PortfolioError("trial.interest must be an integer from 1 to 5")
        signals = item.get("signals")
        if not isinstance(signals, list) or not all(isinstance(signal, str) for signal in signals):
            raise PortfolioError("trial.signals must be a list of strings")
        unknown = set(signals) - ROUTES[route]["signals"]
        if unknown:
            raise PortfolioError(f"unknown signals for {route}: {','.join(sorted(unknown))}")
        trials.append(
            RouteTrial(
                route=route,
                interest=interest,
                matched_signals=tuple(sorted(set(signals))),
                note=_text(item.get("note"), "trial.note"),
            )
        )
    trials.sort(key=lambda trial: (-trial.interest, -trial.evidence_count, trial.route))
    evidence = tuple((kind, found[kind]) for kind in REQUIRED_KINDS)
    return PortfolioReport(project_id, evidence, tuple(trials))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("portfolio.json"))
    parser.add_argument("--workspace", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        print(load_report(args.manifest, args.workspace).as_text())
    except PortfolioError as exc:
        print(f"portfolio_error={exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
