"""`manage.py testcheck` — analyze the test suite and report optimizations."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand
from django.core.management.base import CommandParser

from django_pytest.analysis.engine import analyze
from django_pytest.analysis.models import Severity
from django_pytest.reporters.html_reporter import render_html
from django_pytest.reporters.json_reporter import render_json
from django_pytest.reporters.terminal import render_terminal


_SEVERITY_BY_NAME = {s.label: s for s in Severity}


class Command(BaseCommand):
    help = "Analyze the test suite (slow tests, anti-patterns, parallelization, coverage gaps)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("paths", nargs="*", default=["."], help="Test paths to scan (default: project root).")
        parser.add_argument(
            "--format",
            choices=["terminal", "json", "html"],
            default="terminal",
            help="Output format (default: terminal).",
        )
        parser.add_argument("--output", default=None, help="Write the report to this file instead of stdout.")
        parser.add_argument("--slow-threshold", type=float, default=1.0, help="Seconds above which a test is slow.")
        parser.add_argument("--coverage-threshold", type=float, default=0.80, help="Minimum acceptable line rate.")
        parser.add_argument(
            "--fail-on",
            choices=list(_SEVERITY_BY_NAME),
            default=None,
            help="Exit non-zero if any finding meets or exceeds this severity.",
        )

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ARG002 - Django command signature
        root = Path.cwd()
        paths = [Path(p) for p in options["paths"]]
        report = analyze(
            root,
            paths,
            slow_threshold=options["slow_threshold"],
            coverage_threshold=options["coverage_threshold"],
        )

        fmt = options["format"]
        if fmt == "json":
            rendered = render_json(report)
        elif fmt == "html":
            rendered = render_html(report)
        else:
            rendered = render_terminal(report, color=options["output"] is None)

        output = options["output"]
        if output:
            Path(output).write_text(rendered, encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Report written to {output}"))
        else:
            self.stdout.write(rendered)

        fail_on = options["fail_on"]
        if fail_on is not None and report.max_severity >= _SEVERITY_BY_NAME[fail_on]:
            sys.exit(1)
