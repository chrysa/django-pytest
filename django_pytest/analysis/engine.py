"""Orchestrates checks into a single report."""

from __future__ import annotations

from pathlib import Path

from django_pytest.analysis.checks import Check
from django_pytest.analysis.checks import default_checks
from django_pytest.analysis.context import AnalysisContext
from django_pytest.analysis.context import build_context
from django_pytest.analysis.models import Report


class AnalysisEngine:
    """Runs a set of checks against an :class:`AnalysisContext`."""

    def __init__(self, checks: list[Check] | None = None) -> None:
        self.checks = checks if checks is not None else default_checks()

    def run(self, ctx: AnalysisContext) -> Report:
        report = Report()
        for check in self.checks:
            report.extend(check.analyze(ctx))
        return report


def analyze(
    root: Path,
    test_paths: list[Path],
    *,
    slow_threshold: float = 1.0,
    coverage_threshold: float = 0.80,
    checks: list[Check] | None = None,
) -> Report:
    """Convenience entry point: build a context and run the engine."""

    ctx = build_context(
        root,
        test_paths,
        slow_threshold=slow_threshold,
        coverage_threshold=coverage_threshold,
    )
    return AnalysisEngine(checks).run(ctx)
