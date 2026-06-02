"""Check registry."""

from __future__ import annotations

from django_pytest.analysis.checks.anti_patterns import AntiPatternCheck
from django_pytest.analysis.checks.base import Check
from django_pytest.analysis.checks.coverage_gaps import CoverageGapCheck
from django_pytest.analysis.checks.parallelization import ParallelizationCheck
from django_pytest.analysis.checks.slow_tests import SlowTestCheck


def default_checks() -> list[Check]:
    return [
        SlowTestCheck(),
        AntiPatternCheck(),
        ParallelizationCheck(),
        CoverageGapCheck(),
    ]


__all__ = [
    "AntiPatternCheck",
    "Check",
    "CoverageGapCheck",
    "ParallelizationCheck",
    "SlowTestCheck",
    "default_checks",
]
