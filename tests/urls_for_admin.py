"""Minimal URLconf so the admin site (and its patched report view) can resolve."""

from __future__ import annotations

from django.contrib import admin
from django.urls import path


urlpatterns = [path("admin/", admin.site.urls)]
