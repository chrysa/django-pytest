"""Engine orchestration and reporters."""

from __future__ import annotations

import json
from pathlib import Path

from django_pytest.analysis.engine import AnalysisEngine
from django_pytest.analysis.engine import analyze
from django_pytest.analysis.models import Finding
from django_pytest.analysis.models import Report
from django_pytest.analysis.models import Severity
from django_pytest.reporters.json_reporter import render_json
from django_pytest.reporters.terminal import render_terminal


def test_engine_aggregates_all_checks(tmp_path: Path) -> None:
    (tmp_path / "tests_x.py").write_text("def test_x():\n    value = 1\n", encoding="utf-8")
    report = analyze(tmp_path, [tmp_path])
    # Missing-assert (high) + slow-info + coverage-info at least.
    assert report.findings
    check_ids = {f.check_id for f in report.findings}
    assert "anti-patterns" in check_ids


def test_report_max_severity_and_counts() -> None:
    report = Report()
    report.add(Finding(check_id="c", severity=Severity.LOW, message="a"))
    report.add(Finding(check_id="c", severity=Severity.HIGH, message="b"))
    assert report.max_severity == Severity.HIGH
    assert report.counts()[Severity.HIGH] == 1
    assert report.counts()[Severity.LOW] == 1


def test_empty_engine_returns_empty_report(tmp_path: Path) -> None:
    from django_pytest.analysis.context import AnalysisContext

    result = AnalysisEngine(checks=[]).run(AnalysisContext(root=tmp_path))
    assert result.findings == []


def test_terminal_reporter_renders_findings() -> None:
    report = Report()
    report.add(
        Finding(
            check_id="anti-patterns", severity=Severity.HIGH, message="boom", suggestion="fix it", path="t.py", line=3
        )
    )
    out = render_terminal(report, color=False)
    assert "HIGH" in out
    assert "boom" in out
    assert "t.py:3" in out
    assert "fix it" in out


def test_terminal_reporter_handles_empty() -> None:
    out = render_terminal(Report(), color=False)
    assert "healthy" in out


def test_json_reporter_is_valid_json() -> None:
    report = Report()
    report.add(Finding(check_id="slow-tests", severity=Severity.MEDIUM, message="slow", test_id="t::a"))
    payload = json.loads(render_json(report))
    assert payload["max_severity"] == "medium"
    assert payload["findings"][0]["check_id"] == "slow-tests"
    assert payload["findings"][0]["test_id"] == "t::a"
