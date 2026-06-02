"""Standalone HTML reporter (self-contained, inline CSS — no assets needed)."""

from __future__ import annotations

import html
from datetime import UTC
from datetime import datetime

from django_pytest.analysis.models import Report
from django_pytest.analysis.models import Severity


_SEVERITY_COLOR = {
    Severity.HIGH: "#e5484d",
    Severity.MEDIUM: "#f5a623",
    Severity.LOW: "#4a90e2",
    Severity.INFO: "#8a8f98",
}

_STYLE = """
:root { color-scheme: light dark; }
body { font-family: ui-monospace, "SF Mono", Menlo, monospace; margin: 0; padding: 2rem;
       background: #0f1115; color: #e6e6e6; }
h1 { font-size: 1.3rem; margin: 0 0 .25rem; }
.sub { color: #8a8f98; margin-bottom: 1.5rem; font-size: .85rem; }
.summary { display: flex; gap: .5rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.pill { padding: .25rem .7rem; border-radius: 999px; font-size: .8rem; font-weight: 600; color: #0f1115; }
table { width: 100%; border-collapse: collapse; font-size: .85rem; }
th { text-align: left; color: #8a8f98; font-weight: 600; padding: .5rem .6rem; border-bottom: 1px solid #262a31; }
td { padding: .6rem; border-bottom: 1px solid #1b1e24; vertical-align: top; }
.sev { font-weight: 700; white-space: nowrap; }
.loc { color: #8a8f98; font-size: .78rem; }
.suggestion { color: #b6c2cf; }
.empty { color: #3fb950; padding: 2rem 0; }
"""


def _pill(label: str, count: int, color: str) -> str:
    return f'<span class="pill" style="background:{color}">{count} {html.escape(label)}</span>'


def render_html(report: Report, *, title: str = "django-pytest · test analysis") -> str:
    counts = report.counts()
    generated = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")

    pills = "".join(_pill(sev.label, counts[sev], _SEVERITY_COLOR[sev]) for sev in reversed(Severity) if counts[sev])
    summary = pills or '<span class="loc">no findings</span>'

    if not report.findings:
        body = '<p class="empty">Nothing to flag. Tests look healthy.</p>'
    else:
        rows = []
        for f in report.by_severity():
            color = _SEVERITY_COLOR[f.severity]
            loc = f'<div class="loc">{html.escape(f.location)}</div>' if f.location else ""
            test = f'<div class="loc">{html.escape(f.test_id)}</div>' if f.test_id else ""
            suggestion = f'<div class="suggestion">→ {html.escape(f.suggestion)}</div>' if f.suggestion else ""
            rows.append(
                f"<tr>"
                f'<td class="sev" style="color:{color}">{f.severity.label.upper()}</td>'
                f"<td>{html.escape(f.check_id)}</td>"
                f"<td>{html.escape(f.message)}{loc}{test}{suggestion}</td>"
                f"</tr>"
            )
        body = (
            "<table><thead><tr><th>Severity</th><th>Check</th><th>Finding</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>"
        )

    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>{html.escape(title)}</title><style>{_STYLE}</style></head><body>"
        f"<h1>{html.escape(title)}</h1>"
        f'<div class="sub">Generated {generated}</div>'
        f'<div class="summary">{summary}</div>'
        f"{body}</body></html>"
    )
