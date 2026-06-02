"""Optional Django admin integration.

Adds a staff-only ``django-pytest/report/`` view to the default admin site that
renders the live test-analysis report as HTML. Wired up from ``apps.ready()``;
opt out with ``DJANGO_PYTEST_ADMIN = False`` in settings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.urls import path

from django_pytest.analysis.engine import analyze
from django_pytest.reporters.html_reporter import render_html


_PATCHED = False


@staff_member_required
def report_view(request: HttpRequest) -> HttpResponse:  # noqa: ARG001
    root = Path.cwd()
    report = analyze(root, [root])
    return HttpResponse(render_html(report))


def patch_admin() -> None:
    """Append the report view to the default admin site's URLs (idempotent)."""

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_get_urls = admin.site.get_urls

    def get_urls() -> list[Any]:
        extra: list[Any] = [
            path(
                "django-pytest/report/",
                admin.site.admin_view(report_view),
                name="django_pytest_report",
            )
        ]
        return extra + list(original_get_urls())

    admin.site.get_urls = get_urls
