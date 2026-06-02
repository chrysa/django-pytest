"""Integration tests for the Django-facing pieces (commands, runner, admin)."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from django.core.management import call_command
from django.test import RequestFactory

from django_pytest.runner import PytestRunner


def test_testcheck_json_output() -> None:
    out = StringIO()
    call_command("testcheck", "tests", format="json", stdout=out)
    payload = json.loads(out.getvalue())
    assert "max_severity" in payload
    assert "findings" in payload


def test_testcheck_html_to_file(tmp_path: Path) -> None:
    target = tmp_path / "report.html"
    out = StringIO()
    call_command("testcheck", "tests", format="html", output=str(target), stdout=out)
    assert target.is_file()
    assert target.read_text(encoding="utf-8").startswith("<!doctype html>")


def test_testcheck_terminal_default() -> None:
    out = StringIO()
    call_command("testcheck", "tests", stdout=out)
    assert "test analysis" in out.getvalue()


def test_testcheck_fail_on_high(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "tests_bad.py").write_text("def test_x():\n    value = 1\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    out = StringIO()
    with pytest.raises(SystemExit) as exc:
        call_command("testcheck", format="json", fail_on="high", stdout=out)
    assert exc.value.code == 1


def test_runner_delegates_to_pytest(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr("pytest.main", lambda args: calls.append(args) or 0)
    runner = PytestRunner(verbosity=2, failfast=True)
    assert runner.run_tests(["tests/"]) == 0
    assert calls and "--exitfirst" in calls[0] and "-v" in calls[0]


def test_pytest_command_forwards_args(monkeypatch: pytest.MonkeyPatch) -> None:
    from django_pytest.management.commands.pytest import Command

    captured: list[list[str]] = []
    monkeypatch.setattr("pytest.main", lambda args: captured.append(args) or 0)
    with pytest.raises(SystemExit) as exc:
        Command().run_from_argv(["manage.py", "pytest", "tests/", "-k", "auth"])
    assert exc.value.code == 0
    assert captured == [["tests/", "-k", "auth"]]


def test_admin_patch_is_idempotent_and_registers_view() -> None:
    from django.contrib import admin

    from django_pytest.admin import patch_admin

    patch_admin()
    patch_admin()  # idempotent
    names = {getattr(u, "name", None) for u in admin.site.get_urls()}
    assert "django_pytest_report" in names


def test_admin_report_view_renders_html(monkeypatch: pytest.MonkeyPatch) -> None:
    from django_pytest import admin as dp_admin
    from django_pytest.analysis.models import Report

    monkeypatch.setattr(dp_admin, "analyze", lambda *_a, **_k: Report())
    request = RequestFactory().get("/admin/django-pytest/report/")
    request.user = SimpleNamespace(is_active=True, is_staff=True)  # type: ignore[attr-defined]
    response = dp_admin.report_view(request)
    assert response.status_code == 200
    assert b"<!doctype html>" in response.content
