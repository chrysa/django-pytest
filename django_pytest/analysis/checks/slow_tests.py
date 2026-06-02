"""Flags slow tests using runtime durations captured by the plugin."""

from __future__ import annotations

from django_pytest.analysis.checks.base import Check
from django_pytest.analysis.context import AnalysisContext
from django_pytest.analysis.models import Finding
from django_pytest.analysis.models import Severity


TOP_N = 10


class SlowTestCheck(Check):
    id = "slow-tests"
    name = "Slow tests"

    def analyze(self, ctx: AnalysisContext) -> list[Finding]:
        runtime = ctx.runtime
        if runtime is None or not runtime.tests:
            return [
                Finding(
                    check_id=self.id,
                    severity=Severity.INFO,
                    message="No runtime data available.",
                    suggestion="Run `manage.py pytest` (or `pytest --dpytest`) once to collect timings.",
                )
            ]

        slow = [rec for rec in runtime.tests.values() if rec.duration >= ctx.slow_threshold]
        slow.sort(key=lambda r: r.duration, reverse=True)

        findings: list[Finding] = []
        for record in slow[:TOP_N]:
            findings.append(
                Finding(
                    check_id=self.id,
                    severity=self._severity(record.duration, ctx.slow_threshold),
                    message=f"{record.nodeid} took {record.duration:.2f}s ({record.query_count} queries).",
                    suggestion=self._suggestion(record.query_count),
                    test_id=record.nodeid,
                )
            )
        return findings

    @staticmethod
    def _severity(duration: float, threshold: float) -> Severity:
        if duration >= threshold * 5:
            return Severity.HIGH
        if duration >= threshold * 2:
            return Severity.MEDIUM
        return Severity.LOW

    @staticmethod
    def _suggestion(query_count: int) -> str:
        if query_count > 30:
            return "High query count suggests N+1 — use select_related/prefetch_related or setUpTestData."
        return "Mark with @pytest.mark.slow, mock external I/O, or share fixtures via setUpTestData."
