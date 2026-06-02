"""AST-based anti-pattern detection."""

from __future__ import annotations

from pathlib import Path

from django_pytest.analysis.checks.anti_patterns import AntiPatternCheck
from django_pytest.analysis.context import build_context
from django_pytest.analysis.models import Severity
from django_pytest.analysis.runtime import RunData
from django_pytest.analysis.runtime import TestRecord


SAMPLE = """
import time


def test_no_assertion():
    value = 1 + 1


def test_sleeps():
    time.sleep(2)
    assert True


def test_has_print():
    print("debug")
    assert 1 == 1


def test_clean():
    assert 2 + 2 == 4
"""


def _write_sample(tmp_path: Path) -> None:
    (tmp_path / "tests_sample.py").write_text(SAMPLE, encoding="utf-8")


def test_detects_missing_assert(tmp_path: Path) -> None:
    _write_sample(tmp_path)
    ctx = build_context(tmp_path, [tmp_path])
    findings = AntiPatternCheck().analyze(ctx)
    msgs = [f.message for f in findings]
    assert any("test_no_assertion" in m and "no assertion" in m for m in msgs)


def test_flags_missing_assert_as_high(tmp_path: Path) -> None:
    _write_sample(tmp_path)
    ctx = build_context(tmp_path, [tmp_path])
    findings = AntiPatternCheck().analyze(ctx)
    high = [f for f in findings if f.severity == Severity.HIGH]
    assert any("test_no_assertion" in f.message for f in high)


def test_detects_sleep_and_print(tmp_path: Path) -> None:
    _write_sample(tmp_path)
    ctx = build_context(tmp_path, [tmp_path])
    msgs = [f.message for f in AntiPatternCheck().analyze(ctx)]
    assert any("sleep" in m for m in msgs)
    assert any("print" in m for m in msgs)


def test_clean_test_not_flagged(tmp_path: Path) -> None:
    _write_sample(tmp_path)
    ctx = build_context(tmp_path, [tmp_path])
    findings = AntiPatternCheck().analyze(ctx)
    assert not any("test_clean" in f.message for f in findings)


def test_db_marker_without_queries_flagged(tmp_path: Path) -> None:
    src = """
import pytest


@pytest.mark.django_db
def test_db_unused():
    assert 1 == 1
"""
    (tmp_path / "tests_db.py").write_text(src, encoding="utf-8")
    runtime = RunData()
    runtime.tests["tests_db.py::test_db_unused"] = TestRecord(
        nodeid="tests_db.py::test_db_unused",
        uses_db=True,
        query_count=0,
    )
    ctx = build_context(tmp_path, [tmp_path])
    ctx.runtime = runtime
    msgs = [f.message for f in AntiPatternCheck().analyze(ctx)]
    assert any("no queries" in m for m in msgs)
