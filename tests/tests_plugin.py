"""Unit tests for the plugin's pure helpers (no live pytest session needed)."""

from __future__ import annotations

from pathlib import Path

import pytest

from django_pytest import plugin


def test_django_configured_false_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    assert plugin._django_configured() is False


def test_stop_query_capture_handles_none() -> None:
    assert plugin._stop_query_capture(None) == 0


def test_start_query_capture_returns_none_when_not_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(plugin, "_DJANGO_READY", False)
    assert plugin._start_query_capture() is None


def test_addoption_registers_flags() -> None:
    recorded: list[str] = []

    class FakeGroup:
        def addoption(self, name: str, **kwargs: object) -> None:  # noqa: ARG002
            recorded.append(name)

    class FakeParser:
        def getgroup(self, name: str) -> FakeGroup:  # noqa: ARG002
            return FakeGroup()

    plugin.pytest_addoption(FakeParser())  # type: ignore[arg-type]
    assert "--dpytest-check" in recorded
    assert "--dpytest-no-db" in recorded


def test_print_analysis_outputs_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "tests_sample.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    plugin._print_analysis(tmp_path)
    assert "test analysis" in capsys.readouterr().out
