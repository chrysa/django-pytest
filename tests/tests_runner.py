"""Unit tests for the configurable PytestRunner (no live pytest session)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from django_pytest import runner as runner_mod
from django_pytest.runner import PytestRunner


def _capture(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    calls: list[list[str]] = []
    monkeypatch.setattr("pytest.main", lambda args, plugins=None: calls.append(args) or 0)  # noqa: ARG005
    return calls


def test_failfast_and_verbosity_translation(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _capture(monkeypatch)
    PytestRunner(verbosity=2, failfast=True).run_tests(["tests/"])
    argv = calls[0]
    assert "--exitfirst" in argv
    assert "-v" in argv
    assert "tests/" in argv


def test_quiet_verbosity_adds_no_header(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _capture(monkeypatch)
    PytestRunner(verbosity=0, failfast=False).run_tests([])
    argv = calls[0]
    assert "-qq" in argv
    assert "--no-header" in argv
    assert "--exitfirst" not in argv


def test_markers_join_into_single_expression(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _capture(monkeypatch)
    PytestRunner(failfast=False, markers=[["unit", "db"], ["slow"]]).run_tests([])
    argv = calls[0]
    assert "-m" in argv
    assert argv[argv.index("-m") + 1] == "unit or db or slow"


def test_coverage_flag_emits_cov_options(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _capture(monkeypatch)
    PytestRunner(failfast=False, coverage_xml=True).run_tests([])
    argv = calls[0]
    assert "--cov" in argv
    assert any(part.startswith("xml:") for part in argv)


def test_log_level_sets_env_and_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DJANGO_LOG_LEVEL", raising=False)
    calls = _capture(monkeypatch)
    PytestRunner(failfast=False, log_level="WARNING").run_tests([])
    import os

    assert os.environ["DJANGO_LOG_LEVEL"] == "WARNING"
    assert "WARNING" in calls[0]


def test_config_autodetect(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    argv: list[str] = []
    runner_mod._define_config(argv, None)
    assert argv == ["--config-file", "pytest.ini"]


def test_extra_tests_passed_as_plugins(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, Any] = {}
    monkeypatch.setattr("pytest.main", lambda args, plugins=None: seen.update(args=args, plugins=plugins) or 0)
    sentinel = object()
    PytestRunner(failfast=False).run_tests([], extra_tests=[sentinel])
    assert seen["plugins"] == [sentinel]


def test_add_arguments_builds_help_and_skips_existing() -> None:
    recorded: dict[str, dict[str, Any]] = {}

    class FakeParser:
        _option_string_actions = {"--failfast": object()}

        def add_argument(self, option: str, **kwargs: Any) -> None:
            recorded[option] = kwargs

    PytestRunner.add_arguments(FakeParser())  # type: ignore[arg-type]
    assert "--failfast" not in recorded  # already present, skipped
    assert "--verbosity" not in recorded  # no cli_params, skipped
    assert recorded["--coverage-xml"]["dest"] == "coverage_xml"
    assert "--benchmark" in recorded
    assert recorded["--log-level"]["help"].endswith("[Default: ERROR]")


def test_init_value_uses_defaults() -> None:
    runner = PytestRunner()
    assert runner.cache_clear is None  # no default declared
    assert runner.log_level == "ERROR"  # cli_params default
    assert runner.benchmark is False  # explicit default
