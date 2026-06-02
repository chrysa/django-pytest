"""A configurable Django ``TEST_RUNNER`` that delegates to pytest.

Set in settings::

    TEST_RUNNER = "django_pytest.runner.PytestRunner"

``manage.py test`` then runs the pytest suite (and the django-pytest plugin),
exposing extra flags (coverage / report generation, markers, verbosity, log
level...) that are translated into pytest options.

Report destinations default to ``./reports`` and can be relocated with the
``DJANGO_PYTEST_REPORTS_DIR`` environment variable.
"""

from __future__ import annotations

import argparse
import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

REPORTS_PATH = Path(os.environ.get("DJANGO_PYTEST_REPORTS_DIR", "reports"))
COVERAGE_REPORTS_PATH = REPORTS_PATH / "coverage"
TESTS_REPORTS_PATH = REPORTS_PATH / "tests"
COVERAGE_OPTIONS = ["--cov-config=pyproject.toml", "--cov", "--cov-branch"]


def _define_config(argv: list[str], value: Any) -> None:
    path = value
    if path is None:
        for candidate in ("pytest.ini", "pyproject.toml", "setup.cfg"):
            if Path(candidate).is_file():
                path = candidate
                break
    if path is not None:
        argv.extend(["--config-file", str(path)])


def _define_debug_state(argv: list[str], value: Any) -> None:  # noqa: ARG001
    os.environ["DJANGO_LOG_LEVEL"] = "DEBUG"


def _define_log_level(argv: list[str], value: Any) -> None:
    level = str(value)
    os.environ["DJANGO_LOG_LEVEL"] = level
    argv.extend(["--log-cli-level", "CRITICAL", "--log-level", level])


def _define_verbosity(argv: list[str], value: Any) -> None:
    index = max(0, min(int(value), 3))
    durations = ["0", "5", "10", "15"]
    flags = ["-qq", "-q", "-v", "-vv"]
    tb_levels = ["no", "line", "short", "long"]
    argv.extend(
        [
            flags[index],
            "--durations",
            durations[index],
            "--tb",
            tb_levels[index],
            "--verbosity",
            "0" if index < 2 else str(index),
        ]
    )
    if index < 2:
        argv.append("--no-header")


def _set_markers(argv: list[str], value: Any) -> None:
    markers = [marker for group in value for marker in group]
    if markers:
        argv.extend(["-m", " or ".join(markers)])


_FUNCTIONS: dict[str, Callable[[list[str], Any], None]] = {
    "_define_config": _define_config,
    "_define_debug_state": _define_debug_state,
    "_define_log_level": _define_log_level,
    "_define_verbosity": _define_verbosity,
    "_set_markers": _set_markers,
}


DEFAULT_ARGUMENTS: dict[str, dict[str, Any]] = {
    "benchmark": {
        "cli_params": {"action": "store_true", "help": "run benchmark tests"},
        "default": False,
        "pytest_options": [
            "--benchmark-enable",
            "--benchmark-compare",
            "--benchmark-histogram",
            "--benchmark-autosave",
            "--benchmark-verbose",
        ],
    },
    "cache_clear": {
        "cli_params": {"action": "store_true", "help": "clear pytest cache folder"},
        "pytest_options": "--cache-clear",
    },
    "config": {
        "cli_params": {"default": None, "help": "path to a pytest config file"},
        "function": "_define_config",
    },
    "coverage_html": {
        "cli_params": {
            "action": "store_true",
            "help": f"run coverage and write an HTML report to {COVERAGE_REPORTS_PATH.as_posix()}",
        },
        "pytest_options": [*COVERAGE_OPTIONS, "--cov-report", f"html:{COVERAGE_REPORTS_PATH}/html_report"],
    },
    "coverage_txt": {
        "cli_params": {
            "action": "store_true",
            "help": f"run coverage and write a text report to {COVERAGE_REPORTS_PATH.as_posix()}",
        },
        "pytest_options": [*COVERAGE_OPTIONS, "--cov-report", f"txt:{COVERAGE_REPORTS_PATH}/coverage.txt"],
    },
    "coverage_xml": {
        "cli_params": {
            "action": "store_true",
            "help": f"run coverage and write an XML report to {COVERAGE_REPORTS_PATH.as_posix()}",
        },
        "pytest_options": [*COVERAGE_OPTIONS, "--cov-report", f"xml:{COVERAGE_REPORTS_PATH}/coverage.xml"],
    },
    "dependencies": {
        "cli_params": {
            "action": "store_true",
            "help": "display test dependencies (requires pytest-dependency)",
        },
        "pytest_options": "--list-processed-dependencies",
    },
    "failfast": {
        "cli_params": {"action": "store_true", "help": "stop the run on the first failure"},
        "default": True,
        "pytest_options": "--exitfirst",
    },
    "log_level": {
        "cli_params": {"default": "ERROR", "action": "store", "help": "set DJANGO_LOG_LEVEL"},
        "function": "_define_log_level",
    },
    "markers": {
        "cli_params": {"action": "append", "nargs": "+", "help": "marker expression(s) to run"},
        "function": "_set_markers",
    },
    "no_debug": {
        "cli_params": {"action": "store_true", "help": "disable DEBUG log level"},
        "function": "_define_debug_state",
    },
    "tests_html": {
        "cli_params": {
            "action": "store_true",
            "help": f"write an HTML test report to {TESTS_REPORTS_PATH.as_posix()}/tests.html",
        },
        "pytest_options": f"--html={TESTS_REPORTS_PATH.as_posix()}/tests.html",
    },
    "tests_xml": {
        "cli_params": {
            "action": "store_true",
            "help": f"write a JUnit XML report to {TESTS_REPORTS_PATH.as_posix()}/tests.xml",
        },
        "pytest_options": f"--junitxml={TESTS_REPORTS_PATH}/tests.xml",
    },
    "verbosity": {"default": 2, "function": "_define_verbosity"},
}


class PytestRunner:
    """Translate Django ``manage.py test`` options into a pytest invocation."""

    def __init__(
        self,
        *,
        verbosity: int = 2,
        failfast: bool = True,
        keepdb: bool = False,
        **kwargs: Any,
    ) -> None:
        self.verbosity = verbosity
        self.failfast = failfast
        self.keepdb = keepdb
        self._init_value(kwargs)

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        for name, config in DEFAULT_ARGUMENTS.items():
            params = config.get("cli_params")
            if not params:
                continue
            option = f"--{name.replace('_', '-')}"
            if option in parser._option_string_actions:  # noqa: SLF001
                continue
            kwargs = dict(params)
            if "help" in kwargs and "default" in kwargs:
                kwargs["help"] = f"{kwargs['help']} [Default: {kwargs['default']}]"
            parser.add_argument(option, dest=name, **kwargs)

    @staticmethod
    def _add_pytest_options(config: dict[str, Any], argv: list[str]) -> None:
        options = config["pytest_options"]
        if isinstance(options, list):
            argv.extend(options)
        else:
            argv.append(options)

    def _init_value(self, kwargs: dict[str, Any]) -> None:
        for name, config in DEFAULT_ARGUMENTS.items():
            if hasattr(self, name):
                continue
            default = config.get("default", config.get("cli_params", {}).get("default"))
            setattr(self, name, kwargs.get(name, default))

    def _is_active_option(self, config: dict[str, Any], name: str, value: Any) -> bool:  # noqa: ARG002
        if value is None:
            return False
        action = config.get("cli_params", {}).get("action")
        if action == "store_true":
            return value is True
        if action == "store_false":
            return value is False
        if action == "append":
            return bool(value)
        # No action (e.g. verbosity/log_level): always active unless explicitly "False".
        return str(value) != "False"

    def run_tests(self, test_labels: list[str], extra_tests: Any = None, **kwargs: Any) -> int:  # noqa: ARG002
        """Run pytest and return its exit code (0 == success)."""
        import pytest

        argv: list[str] = ["-r", "EFSxX"] if int(self.verbosity) > 1 else []
        for name, config in DEFAULT_ARGUMENTS.items():
            value = getattr(self, name)
            if not self._is_active_option(config, name, value):
                continue
            if "pytest_options" in config:
                self._add_pytest_options(config, argv)
            elif "function" in config:
                _FUNCTIONS[config["function"]](argv, value)
            else:
                logger.error("%s is not a supported runner option", name)
        argv.extend(test_labels)
        if extra_tests:
            return int(pytest.main(argv, plugins=extra_tests))
        return int(pytest.main(argv))
