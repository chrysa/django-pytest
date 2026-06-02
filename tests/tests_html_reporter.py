"""HTML reporter output."""

from __future__ import annotations

from django_pytest.analysis.models import Finding
from django_pytest.analysis.models import Report
from django_pytest.analysis.models import Severity
from django_pytest.reporters.html_reporter import render_html


def test_html_is_standalone_document() -> None:
    out = render_html(Report())
    assert out.startswith("<!doctype html>")
    assert "<style>" in out
    assert "healthy" in out


def test_html_renders_findings_and_escapes() -> None:
    report = Report()
    report.add(
        Finding(
            check_id="anti-patterns",
            severity=Severity.HIGH,
            message="dangerous <script>",
            suggestion="fix & sanitize",
            path="t.py",
            line=5,
        )
    )
    out = render_html(report)
    assert "HIGH" in out
    assert "&lt;script&gt;" in out  # escaped
    assert "<script>" not in out.replace("<scriptt", "")  # no raw injection
    assert "t.py:5" in out
    assert "fix &amp; sanitize" in out
