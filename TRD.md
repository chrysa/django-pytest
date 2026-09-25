# TRD — django-pytest

Tags: FACT / INFERENCE / UNKNOWN / PROPOSAL. Evidence pointers are in-repo paths.
Architecture detail lives in the existing `ARCHITECTURE.md` (preserved, not
duplicated here); this TRD covers the technical contract, entrypoints, and
data flow.

## Language & packaging (FACT)

- Python `>=3.14` declared (`pyproject.toml`); CLAUDE.md notes the code itself
  runs on 3.11+ and README states the same — the *packaged* floor is 3.14.
- Build backend: `setuptools>=84` / `wheel`, `src/` layout, package `django_pytest`.
- Typed: ships `src/django_pytest/py.typed`.

## Entrypoints (FACT — ARCHITECTURE.md, pyproject.toml)

| Entrypoint | Mechanism | Evidence |
|-----------|-----------|----------|
| pytest plugin | `pytest11` entry point → `django_pytest.plugin` | `pyproject.toml`, `plugin.py` |
| Django test runner | `TEST_RUNNER = "django_pytest.runner.PytestRunner"` | `runner.py` |
| `manage.py pytest` | Django management command | `management/commands/pytest.py` |
| `manage.py testcheck` | Django management command, `--fail-on <severity>` | `management/commands/testcheck.py` |
| Admin report view | monkey-patch of `admin.site.get_urls` from `AppConfig.ready()` | `apps.py`, `admin.py` |

No `[project.scripts]` console script is declared (FACT — ARCHITECTURE.md).

## Component contract (FACT)

- **plugin.py** — Django autodetection via `DJANGO_SETTINGS_MODULE`, test-DB
  lifecycle, transactional `db` fixture, per-test runtime capture.
- **analysis/** — `engine.py` orchestrates a registry of `Check` objects over an
  `AnalysisContext` (`context.py`) composed of parsed AST + runtime (`runtime.py`)
  + coverage; `models.py` holds `Report`/finding types; `checks/` implements
  `slow_tests`, `anti_patterns`, `parallelization`, `coverage_gaps` over `base.py`.
  Hard invariant: this package imports neither Django nor pytest (ADR-001).
- **reporters/** — `terminal`, `json_reporter`, `html_reporter` render a `Report`.

## Data flow (FACT — ADR-001, ARCHITECTURE.md, README.md)

1. Plugin collects per-test data (duration, query count, fixtures) during a run,
   persisting to `.django_pytest/last-run.json`.
2. `pytest-cov` produces `coverage.xml` when coverage flags are passed.
3. `testcheck` builds an `AnalysisContext` from AST + runtime JSON + coverage,
   runs the check registry, and renders via a reporter (default output root
   `./reports`, overridable).
4. Slow-test, parallelization, and coverage checks require a prior run with data
   (README.md).

## External dependencies & services (FACT — ARCHITECTURE.md)

- Runtime deps: `django>=6.1`, `pytest>=9.1.1` (`pyproject.toml`). Note the
  README's "Django ≥4.2" is inconsistent with this floor — see CONSTRAINTS.md.
- Dev deps: `pytest-cov>=7.1.0`, `ruff>=0.16.3`, `mypy>=2.3.0`, `django-stubs>=6.1.0`.
- No application DB, no network service, no external API. Operates on the host
  project's Django settings and test DB.

## Configuration surface (FACT)

- `DJANGO_SETTINGS_MODULE` — drives plugin activation.
- `DJANGO_PYTEST_ADMIN = False` — disables the admin report view.
- pytest `addopts` in host may pass through the runner's translated flags.
- Reports root overridable (README.md).

## Build & CI (FACT — Makefile, .github/workflows/ci.yml, Dockerfile.test)

- Local: `make install|test|test-cov|lint|format|typecheck|ci|docker-test|build`.
- CI runs tests via Docker (`make docker-test`) and uploads a
  `test-results-<python-version>` coverage artifact consumed by a separate sonar job.
</content>
