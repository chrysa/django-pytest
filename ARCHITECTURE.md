# Architecture

## Purpose

`django-pytest` is a reusable Python package providing native pytest integration
for Django, plus a test analysis & optimization engine ("Doctor"). The runner
wires Django up for pytest (settings, test database, transactional isolation);
the engine inspects a suite and reports slow tests, anti-patterns, parallelization
opportunities, and coverage gaps as terminal, JSON, or a self-contained HTML
report (also viewable in the Django admin).

## Stack

- Python `>=3.14` (packaged via `setuptools` / `pyproject.toml`, `src/` layout).
- Runtime deps: `django>=6.1`, `pytest>=9.1.1`.
- Dev tooling: `pytest-cov`, `ruff`, `mypy`, `django-stubs`.
- Distributed as the importable package `django_pytest` (typed, ships `py.typed`).

## Layout

- `src/django_pytest/` — the installable package.
  - `plugin.py` — pytest plugin (registered via the `pytest11` entry point);
    Django setup + runtime data collection; provides a `db` fixture.
  - `runner.py` — `PytestRunner`, a Django `TEST_RUNNER` that delegates to pytest.
  - `apps.py` — `DjangoPytestConfig` AppConfig; wires admin from `ready()`.
  - `admin.py` — optional staff-only admin report view (opt out via
    `DJANGO_PYTEST_ADMIN = False`); monkey-patches `admin.site.get_urls`.
  - `analysis/` — the analysis engine: `engine.py` (orchestrates checks into a
    `Report`), `context.py` (`build_context`), `runtime.py`, `models.py`, and
    `checks/` (`base.py`, `slow_tests.py`, `anti_patterns.py`,
    `coverage_gaps.py`, `parallelization.py`).
  - `reporters/` — `terminal.py`, `json_reporter.py`, `html_reporter.py`.
  - `management/commands/` — `pytest.py` and `testcheck.py` management commands.
- `tests/` — the package's own pytest suite (with `conftest.py`).
- `examples/demo/` — an illustrative demo Django project (excluded from lint).
- `scripts/` — `quality_gate.py`, `gen_context_files.py`.
- `docs/` — `adr/`, `reference/`; `standards/` — shared rule set.

## Entrypoints

- pytest plugin: `django_pytest = "django_pytest.plugin"` (`pytest11` entry point);
  auto-activates when Django is discoverable, inert otherwise.
- Django test runner: `TEST_RUNNER = "django_pytest.runner.PytestRunner"`.
- Management commands: `python manage.py pytest ...` and
  `python manage.py testcheck --fail-on high`.
- No `[project.scripts]` console script is declared.

## Data / External deps

- No application database of its own: operates on the host Django project's
  settings and test database. The `db` fixture wraps each test in a transaction
  rolled back afterwards.
- Reads runtime test data collected by the plugin; consumes coverage output from
  `pytest-cov`. Reports default to `./reports`.
- No network services or external APIs.

## Build & test (real commands)

Real targets from `Makefile`:

```bash
make install     # pip install -e ".[dev]" && pre-commit install
make test        # pytest tests/ --tb=short
make coverage    # pytest tests/ --cov=django_pytest --cov-report=term-missing --cov-report=xml
make lint        # ruff check src/django_pytest tests
make format      # ruff format src/django_pytest tests
make typecheck   # mypy (strict; see pyproject)
make ci          # lint + typecheck + test
```

Note: `pyproject.toml` `addopts` includes `-p no:django_pytest` (the package
disables its own plugin when testing itself) and `-p no:query_optimizer`.
Docker-based run: `Dockerfile.test` (`make` builds/runs `django-pytest-test`).
