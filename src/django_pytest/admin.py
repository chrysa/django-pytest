"""Optional Django admin integration.

Adds a staff-only ``django-pytest/report/`` view to the default admin site that
renders the live test-analysis report as HTML. Wired up from ``apps.ready()``;
opt out with ``DJANGO_PYTEST_ADMIN = False`` in settings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.urls import path

from django_pytest.analysis.engine import analyze
from django_pytest.reporters.html_reporter import render_html


_PATCHED = False


def _report_root() -> Path:
    """Anchor analysis to the project root, not the server's current directory.

    Prefer ``settings.BASE_DIR`` (the canonical project root) so the report is
    identical whatever directory the process was started from; fall back to the
    working directory only when the setting is unset.
    """

    base_dir = getattr(settings, "BASE_DIR", None)
    return Path(base_dir) if base_dir is not None else Path.cwd()


@staff_member_required
def report_view(request: HttpRequest) -> HttpResponse:  # noqa: ARG001
    root = _report_root()
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

    # Intentional monkey-patch of the admin site's bound method (zero-config
    # report view). mypy's [method-assign] is disabled for this module in
    # pyproject.toml rather than via an inline ignore.
    admin.site.get_urls = get_urls
