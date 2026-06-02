# django-pytest

Native pytest integration for Django **plus** a test analysis & optimization engine.

Two things in one package:

1. **Runner** — a pytest plugin + management command that wire Django up for you
   (settings, test database, transactional isolation), so you can run pytest
   without the usual boilerplate.
2. **Doctor** — an analysis engine that inspects your suite and proposes
   optimizations: slow tests, anti-patterns, parallelization, and coverage gaps.
   Output as terminal, JSON, or a self-contained **HTML report** (also viewable
   in the Django admin).

## Install

```bash
pip install django-pytest
```

Add the app to `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django_pytest",
]
```

The pytest plugin auto-activates whenever `DJANGO_SETTINGS_MODULE` is set, so no
`conftest.py` boilerplate is required. It stays inert in non-Django projects.

## Run tests

```bash
# via management command (Django already configured)
python manage.py pytest tests/ -k auth --cov

# or plain pytest, the plugin discovers Django on its own
DJANGO_SETTINGS_MODULE=myproj.settings pytest
```

The plugin provides a `db` fixture (per-test transaction rolled back afterwards)
and records timings, query counts and fixture usage to `.django_pytest/last-run.json`.

Optionally make `manage.py test` delegate to pytest:

```python
TEST_RUNNER = "django_pytest.runner.PytestRunner"
```

The runner adds flags that translate to pytest options, so the Django CLI stays
the entry point:

```bash
python manage.py test --coverage-xml --markers unit db   # -> --cov ... -m "unit or db"
python manage.py test --tests-html --verbosity 3         # HTML report, -vv
python manage.py test --no-input --benchmark             # opt-in pytest-benchmark
```

| Flag | pytest translation | Notes |
|---|---|---|
| `--failfast` | `--exitfirst` | on by default |
| `--markers a b` | `-m "a or b"` | repeatable; groups are OR-joined |
| `--coverage-html/-txt/-xml` | `--cov --cov-branch --cov-report ...` | needs `pytest-cov` |
| `--tests-html` / `--tests-xml` | `--html=...` / `--junitxml=...` | HTML needs `pytest-html` |
| `--benchmark` | `--benchmark-*` | off by default; needs `pytest-benchmark` |
| `--dependencies` | `--list-processed-dependencies` | needs `pytest-dependency` |
| `--cache-clear` | `--cache-clear` | |
| `--config PATH` | `--config-file PATH` | auto-detects `pytest.ini`/`pyproject.toml`/`setup.cfg` |
| `--log-level LEVEL` | `--log-level LEVEL` | also sets `DJANGO_LOG_LEVEL` |
| `--verbosity 0..3` | `-qq`/`-q`/`-v`/`-vv` + `--durations`/`--tb` | Django's own flag |

Reports default to `./reports`; override the root with the
`DJANGO_PYTEST_REPORTS_DIR` environment variable.

## Analyze (the "doctor")

```bash
# human-readable report
python manage.py testcheck

# right after a run, inline
pytest --dpytest-check

# machine-readable / HTML export
python manage.py testcheck --format json
python manage.py testcheck --format html --output report.html

# fail CI on serious findings
python manage.py testcheck --fail-on high
```

### Checks

| Check | What it flags | Source |
|---|---|---|
| `slow-tests` | tests above `--slow-threshold` (default 1s), with N+1 hints | runtime |
| `anti-patterns` | missing assertions, `sleep()`, leftover `print()`, db-marked tests issuing zero queries | AST + runtime |
| `parallelization` | serial suites that would benefit from `pytest-xdist`, db/unit split | runtime |
| `coverage-gaps` | files below `--coverage-threshold`, prioritized by untested lines | `coverage.xml` |

Slow-test, parallelization and coverage checks need data: run the suite once
(`manage.py pytest --cov --cov-report=xml`) before analyzing.

## Admin report

When `django.contrib.admin` is enabled, a staff-only report is served at
`/admin/django-pytest/report/` (rendered HTML). Disable with
`DJANGO_PYTEST_ADMIN = False` in settings.

## Compatibility

| | Minimum | Tested |
|---|---|---|
| Python | 3.14 (chrysa standard; code itself runs on 3.11+) | 3.14 |
| Django | 4.2 LTS | 6.0 |
| pytest | 8.0 | 9.0 |

## Development

```bash
make install     # editable install + pre-commit hooks
make test        # pytest
make lint        # ruff
make typecheck   # mypy (strict)
```
