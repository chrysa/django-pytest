"""Suggests parallelization strategy based on runtime totals."""

from __future__ import annotations

import importlib.util
import os

from django_pytest.analysis.checks.base import Check
from django_pytest.analysis.context import AnalysisContext
from django_pytest.analysis.models import Finding
from django_pytest.analysis.models import Severity


MIN_RUNTIME_FOR_XDIST = 5.0


class ParallelizationCheck(Check):
    id = "parallelization"
    name = "Parallelization"

    def analyze(self, ctx: AnalysisContext) -> list[Finding]:
        runtime = ctx.runtime
        if runtime is None or runtime.total_duration <= 0:
            return []

        findings: list[Finding] = []
        total = runtime.total_duration
        cpu = os.cpu_count() or 1

        if runtime.xdist_workers > 0:
            return findings  # already running parallel

        if total >= MIN_RUNTIME_FOR_XDIST and len(runtime.tests) >= 2:
            workers = max(2, cpu)
            estimated = total / workers
            if importlib.util.find_spec("xdist") is not None:
                hint = f"pytest-xdist is installed — run with `-n {workers}`"
            else:
                hint = f"install pytest-xdist, then run with `-n {workers}`"
            findings.append(
                Finding(
                    check_id=self.id,
                    severity=Severity.MEDIUM,
                    message=(
                        f"Suite runs serially in {total:.1f}s across {len(runtime.tests)} tests; "
                        f"~{estimated:.1f}s estimated on {workers} workers."
                    ),
                    suggestion=f"{hint}. Use a unique test DB per worker (--create-db) to avoid contention.",
                )
            )

        db_tests = sum(1 for rec in runtime.tests.values() if rec.uses_db)
        if db_tests and db_tests == len(runtime.tests):
            findings.append(
                Finding(
                    check_id=self.id,
                    severity=Severity.LOW,
                    message=f"All {db_tests} tests hit the database.",
                    suggestion="Split DB-bound from pure-logic tests with markers so unit tests can run without DB setup.",
                )
            )
        return findings
