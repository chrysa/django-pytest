# django-pytest — GitHub Copilot Instructions

## Purpose

Native pytest integration for Django plus a test analysis/optimization engine.
Hybrid package: a pytest plugin (runtime), a Django app (commands, admin,
runner), over a framework-agnostic analysis engine.

## Conventions

- Python ≥3.14, Django ≥4.2, pytest ≥8. Flat layout (`django_pytest/`, `tests/`).
- ruff (line 120, double quotes), mypy strict, coverage `fail_under = 80`.
- The analysis engine MUST stay import-free of Django and pytest.
- Test files: `tests_*.py`. Suite runs with `-p no:django_pytest`.
- All tests/lint/build go through Docker or pre-commit — never on host.

## Commands

`make test` · `make lint` · `make typecheck` · `make test-cov` · `make docker-test`
