"""Native pytest integration for Django plus a test analysis & optimization engine."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version


try:
    __version__ = version("django-pytest")
except PackageNotFoundError:  # editable install / not installed
    __version__ = "0.0.0+unknown"

default_app_config = "django_pytest.apps.DjangoPytestConfig"

__all__ = ["__version__"]
