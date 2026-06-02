"""Reports prioritized coverage gaps from a coverage.xml report."""

from __future__ import annotations

from django_pytest.analysis.checks.base import Check
from django_pytest.analysis.context import AnalysisContext
from django_pytest.analysis.models import Finding
from django_pytest.analysis.models import Severity


TOP_N = 10


class CoverageGapCheck(Check):
    id = "coverage-gaps"
    name = "Coverage gaps"

    def analyze(self, ctx: AnalysisContext) -> list[Finding]:
        if not ctx.coverage:
            return [
                Finding(
                    check_id=self.id,
                    severity=Severity.INFO,
                    message="No coverage.xml found.",
                    suggestion="Run `manage.py pytest --cov --cov-report=xml` to enable gap analysis.",
                )
            ]

        gaps = [c for c in ctx.coverage if c.line_rate < ctx.coverage_threshold and c.missing_lines > 0]
        # Prioritize by absolute uncovered lines, then by how far below threshold.
        gaps.sort(key=lambda c: (c.missing_lines, ctx.coverage_threshold - c.line_rate), reverse=True)

        findings: list[Finding] = []
        for cov in gaps[:TOP_N]:
            findings.append(
                Finding(
                    check_id=self.id,
                    severity=self._severity(cov.line_rate, ctx.coverage_threshold),
                    message=f"{cov.filename}: {cov.line_rate * 100:.0f}% covered, {cov.missing_lines} lines untested.",
                    suggestion="Add tests for the uncovered branches; prioritize this file — it has the most untested lines.",
                    path=cov.filename,
                )
            )
        return findings

    @staticmethod
    def _severity(rate: float, threshold: float) -> Severity:
        if rate < threshold * 0.5:
            return Severity.HIGH
        if rate < threshold * 0.8:
            return Severity.MEDIUM
        return Severity.LOW
