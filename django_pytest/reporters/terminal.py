"""Human-readable terminal reporter (ANSI colors when attached to a TTY)."""

from __future__ import annotations

import sys

from django_pytest.analysis.models import Report
from django_pytest.analysis.models import Severity


_COLORS = {
    Severity.HIGH: "\033[91m",
    Severity.MEDIUM: "\033[93m",
    Severity.LOW: "\033[94m",
    Severity.INFO: "\033[90m",
}
_RESET = "\033[0m"
_BOLD = "\033[1m"


def render_terminal(report: Report, *, color: bool | None = None) -> str:
    if color is None:
        color = sys.stdout.isatty()

    def paint(text: str, code: str) -> str:
        return f"{code}{text}{_RESET}" if color else text

    lines: list[str] = []
    lines.append(paint("django-pytest · test analysis", _BOLD))

    counts = report.counts()
    summary = " · ".join(f"{counts[s]} {s.label}" for s in reversed(Severity) if counts[s])
    lines.append(summary or "no findings")
    lines.append("")

    if not report.findings:
        lines.append(paint("Nothing to flag. Tests look healthy.", _COLORS[Severity.INFO]))
        return "\n".join(lines)

    for finding in report.by_severity():
        code = _COLORS[finding.severity]
        tag = paint(f"[{finding.severity.label.upper():<6}]", code)
        head = f"{tag} {paint(finding.check_id, _BOLD)}: {finding.message}"
        lines.append(head)
        if finding.location:
            lines.append(f"         {finding.location}")
        if finding.suggestion:
            lines.append(f"         -> {finding.suggestion}")
        lines.append("")

    return "\n".join(lines).rstrip()
