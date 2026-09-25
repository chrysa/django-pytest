# TESTING — django-pytest

Tags: FACT / INFERENCE / UNKNOWN. Commands below are transcribed from `Makefile`
and `pyproject.toml`; they were **not executed** during this docs-only pass.

## Test suite (FACT)

- Location: `tests/` — files named `tests_*.py`, plus `conftest.py`,
  `urls_for_admin.py`, `__init__.py`.
- Test files: `tests_anti_patterns.py`, `tests_checks_runtime.py`,
  `tests_context.py`, `tests_django_integration.py`, `tests_engine_reporters.py`,
  `tests_html_reporter.py`, `tests_plugin.py`, `tests_runner.py`, `tests_runtime.py`.
- Test function count: **59** `def test...` functions across `tests/tests_*.py`
  (FACT — measured via `grep`). ADR-001 mentions "23 tests" for the engine in
  isolation; the full suite is larger — not a contradiction, different scope.
- The suite runs with the package's own plugin disabled: `addopts` includes
  `-p no:django_pytest -p no:query_optimizer --tb=short` (`pyproject.toml`).
- `pythonpath = [".", "src"]`, `testpaths = ["tests"]` (`pyproject.toml`).

## How to run (FACT — Makefile)

```bash
make install     # pip install -e ".[dev]" && pre-commit install
make test        # pytest tests/ --tb=short
make test-cov    # pytest tests/ --cov=django_pytest --cov-report=term-missing --cov-report=xml
make lint        # ruff check src/django_pytest tests
make typecheck   # mypy src/django_pytest
make ci          # lint + typecheck + test
make docker-test # build Dockerfile.test and run the suite in-container (CI path)
```

Note: chrysa convention (CONTRIBUTING.md) is to use `make` targets, not to invoke
`pytest`/`ruff`/`mypy` directly on the host.

## Coverage gate (FACT)

- `fail_under = 80` (`pyproject.toml`, CLAUDE.md).
- CI generates coverage in the Docker test job and uploads it as artifact
  `test-results-<python-version>` for a separate sonar job (`.github/workflows/ci.yml`).

## Demo project (FACT)

- `examples/demo/` is an illustrative Django project (`demo_project`, `shop` app,
  `conftest.py`, `pytest.ini`) used to exercise the plugin end-to-end. It is
  excluded from lint (`pyproject.toml extend-exclude`).

## Not covered / unknown

- [UNKNOWN] Actual last green run, pass/fail counts, and measured coverage % —
  not executed here and no committed report artifact was inspected.
- [UNKNOWN] Cross-version matrix results (multiple Python/Django/pytest versions).
</content>
