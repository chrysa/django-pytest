"""`manage.py pytest` — run pytest with Django already wired up.

Any extra arguments are forwarded verbatim to pytest, e.g.::

    manage.py pytest tests/ -k auth --cov
"""

from __future__ import annotations

import sys
from typing import Any

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run pytest with the Django environment configured by django-pytest."

    def create_parser(self, prog_name: str, subcommand: str, **kwargs: Any) -> Any:
        parser = super().create_parser(prog_name, subcommand, **kwargs)
        parser.add_argument("pytest_args", nargs="*", help="Arguments forwarded to pytest.")
        return parser

    def run_from_argv(self, argv: list[str]) -> None:
        # Bypass Django's option parsing so pytest flags (e.g. -k, -x) pass through untouched.
        self._forward(argv[2:])

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ARG002 - Django command signature
        self._forward(list(options.get("pytest_args", [])))

    def _forward(self, pytest_args: list[str]) -> None:
        import pytest

        exit_code = pytest.main(pytest_args)
        sys.exit(int(exit_code))
