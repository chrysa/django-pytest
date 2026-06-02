# CLAUDE.md — django-pytest

Native pytest integration for Django + a test analysis/optimization engine.
Hybrid package: a **pytest plugin** (runtime) and a **Django app** (commands,
admin, runner), over a framework-agnostic **analysis engine**.

## Layout

```
django_pytest/
├── plugin.py            # pytest11 entry point: Django autodetect, db fixture, runtime capture
├── runner.py            # PytestRunner — optional Django TEST_RUNNER
├── apps.py              # AppConfig; wires the admin report in ready()
├── admin.py             # staff-only /admin/django-pytest/report/ view
├── management/commands/ # pytest, testcheck
├── analysis/            # engine + checks (no Django/pytest imports)
│   ├── engine.py · context.py · models.py · runtime.py
│   └── checks/          # slow_tests · anti_patterns · parallelization · coverage_gaps
└── reporters/           # terminal · json · html
tests/                   # tests_*.py (pure-Python, no settings needed)
```

## Commands (always `make <target>`)

- `make test` · `make lint` (ruff) · `make typecheck` (mypy strict) · `make test-cov`

## Conventions

- Python ≥3.14 (chrysa standard), Django ≥4.2, pytest ≥8. Tested on 3.14 / Django 6 / pytest 9.
- ruff (line 120, double quotes, isort single-line), mypy strict, coverage `fail_under = 80`.
- The analysis engine MUST stay import-free of Django and pytest (keeps it unit-testable).
- Test files: `tests_*.py`. Our own suite runs with `-p no:django_pytest` (don't self-activate).

## Decisions

See `DECISIONS.md` → ADR-001 (hybrid app + plugin).
