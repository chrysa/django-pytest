# ADR-001 — Hybrid Django app + pytest plugin architecture

- **Date:** 2026-06-02
- **Status:** accepted

## Context

We want a single package that (a) runs pytest natively inside Django without the
usual `conftest.py`/`pytest-django` boilerplate, and (b) analyzes the test suite
to propose optimizations (slow tests, anti-patterns, parallelization, coverage
gaps). These two concerns live at different layers: the analysis engine is pure
Python, the runner needs pytest hooks, and the report surfacing benefits from
Django management commands and an admin view.

## Decision

Ship a **hybrid** package:

- **pytest plugin** (`pytest11` entry point → `django_pytest.plugin`) handles the
  runtime: Django autodetection (`DJANGO_SETTINGS_MODULE`), test-DB lifecycle, a
  transactional `db` fixture, and per-test data collection (duration, query
  count, fixtures) persisted to `.django_pytest/last-run.json`.
- **Django app** (`INSTALLED_APPS`) handles the developer surface: `pytest` and
  `testcheck` management commands, an optional `TEST_RUNNER`, and an optional
  staff-only admin report view wired from `AppConfig.ready()`.
- **Analysis engine** (`django_pytest.analysis`) is framework-agnostic: a
  registry of `Check` objects over an `AnalysisContext` (parsed AST + runtime +
  coverage). Reporters render terminal / JSON / HTML.

The engine never imports Django or pytest, so it stays unit-testable in isolation
(23 tests, no Django settings required).

## Consequences

- The plugin is safe to keep installed in non-Django projects: it no-ops unless
  Django is configured.
- The runtime/static split lets checks combine evidence (e.g. "db-marked test
  issues zero queries") while degrading gracefully when no run data exists.
- Two activation paths (entry point for pytest, `INSTALLED_APPS` for Django) must
  both be documented; users can adopt either half independently.
