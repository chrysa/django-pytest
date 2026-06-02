"""Slow-test, parallelization and coverage-gap checks."""

from __future__ import annotations

from pathlib import Path

from django_pytest.analysis.checks.coverage_gaps import CoverageGapCheck
from django_pytest.analysis.checks.parallelization import ParallelizationCheck
from django_pytest.analysis.checks.slow_tests import SlowTestCheck
from django_pytest.analysis.context import AnalysisContext
from django_pytest.analysis.context import FileCoverage
from django_pytest.analysis.models import Severity
from django_pytest.analysis.runtime import RunData
from django_pytest.analysis.runtime import TestRecord


def _ctx(tmp_path: Path, runtime: RunData | None = None) -> AnalysisContext:
    return AnalysisContext(root=tmp_path, runtime=runtime)


def test_slow_test_no_runtime_yields_info(tmp_path: Path) -> None:
    findings = SlowTestCheck().analyze(_ctx(tmp_path))
    assert len(findings) == 1
    assert findings[0].severity == Severity.INFO


def test_slow_test_flagged(tmp_path: Path) -> None:
    runtime = RunData()
    runtime.record(TestRecord(nodeid="t::fast", duration=0.1))
    runtime.record(TestRecord(nodeid="t::slow", duration=6.0, query_count=40))
    findings = SlowTestCheck().analyze(_ctx(tmp_path, runtime))
    assert len(findings) == 1
    assert findings[0].test_id == "t::slow"
    assert findings[0].severity == Severity.HIGH
    assert "N+1" in findings[0].suggestion


def test_parallelization_suggested_for_slow_suite(tmp_path: Path) -> None:
    runtime = RunData(total_duration=20.0)
    runtime.tests = {f"t::{i}": TestRecord(nodeid=f"t::{i}", duration=2.0, uses_db=True) for i in range(10)}
    findings = ParallelizationCheck().analyze(_ctx(tmp_path, runtime))
    assert any(f.check_id == "parallelization" for f in findings)
    assert any("workers" in f.message or "worker" in f.suggestion for f in findings)


def test_parallelization_skipped_when_already_parallel(tmp_path: Path) -> None:
    runtime = RunData(total_duration=20.0, xdist_workers=4)
    runtime.tests = {"t::a": TestRecord(nodeid="t::a", duration=20.0)}
    findings = ParallelizationCheck().analyze(_ctx(tmp_path, runtime))
    assert findings == []


def test_coverage_gap_prioritizes_most_untested(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    ctx.coverage = [
        FileCoverage(filename="a.py", line_rate=0.5, missing_lines=5),
        FileCoverage(filename="b.py", line_rate=0.2, missing_lines=40),
        FileCoverage(filename="c.py", line_rate=0.95, missing_lines=1),
    ]
    findings = CoverageGapCheck().analyze(ctx)
    assert findings[0].path == "b.py"
    assert findings[0].severity == Severity.HIGH
    assert all(f.path != "c.py" for f in findings)


def test_coverage_gap_without_report_yields_info(tmp_path: Path) -> None:
    findings = CoverageGapCheck().analyze(_ctx(tmp_path))
    assert findings[0].severity == Severity.INFO
