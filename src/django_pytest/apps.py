"""Django application configuration."""

from __future__ import annotations

from django.apps import AppConfig


class DjangoPytestConfig(AppConfig):
    name = "django_pytest"
    verbose_name = "Django pytest integration"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from django.conf import settings

        if not getattr(settings, "DJANGO_PYTEST_ADMIN", True):
            return
        try:
            from django_pytest.admin import patch_admin

            patch_admin()
        except Exception:  # noqa: BLE001 - admin is optional; never block app startup
            pass
