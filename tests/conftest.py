"""Configures a minimal Django environment for the integration tests.

The pure analysis-engine tests do not need this, but the command / runner / admin
tests do. Settings are configured once per session via ``settings.configure``.
"""

from __future__ import annotations

import django
from django.conf import settings


def pytest_configure() -> None:
    if settings.configured:
        return
    settings.configure(
        DEBUG=False,
        SECRET_KEY="django-pytest-tests",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.admin",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django_pytest",
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ]
                },
            }
        ],
        ROOT_URLCONF="tests.urls_for_admin",
        USE_TZ=True,
    )
    django.setup()
