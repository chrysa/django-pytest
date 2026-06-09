"""Minimal Django settings for the django-pytest demo project.

``TEST_RUNNER`` is pointed at django-pytest so ``manage.py test`` delegates to
pytest (and the django-pytest plugin). The plugin also auto-activates for a
plain ``pytest`` invocation because ``DJANGO_SETTINGS_MODULE`` is set in
``pytest.ini``.
"""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "demo-insecure-key-not-for-production"  # noqa: S105
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django_pytest",
    "shop",
]

ROOT_URLCONF = "demo_project.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

# Delegate `manage.py test` to pytest via django-pytest.
TEST_RUNNER = "django_pytest.runner.PytestRunner"

USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
