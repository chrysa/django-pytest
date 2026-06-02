"""A Django TEST_RUNNER that delegates to pytest.

Set in settings::

    TEST_RUNNER = "django_pytest.runner.PytestRunner"

so that ``manage.py test`` runs the pytest suite (and the django-pytest plugin).
"""

from __future__ import annotations

from typing import Any


class PytestRunner:
    """Minimal Django test runner backed by pytest."""

    def __init__(
        self,
        *,
        verbosity: int = 1,
        failfast: bool = False,
        **kwargs: Any,
    ) -> None:
        self.verbosity = verbosity
        self.failfast = failfast
        self.kwargs = kwargs

    def run_tests(self, test_labels: list[str], **kwargs: Any) -> int:  # noqa: ARG002
        import pytest

        args: list[str] = list(test_labels)
        if self.failfast:
            args.append("-x")
        if self.verbosity > 1:
            args.append("-v")
        return int(pytest.main(args))
