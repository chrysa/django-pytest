# REQUIREMENTS — django-pytest

Tags: FACT / INFERENCE / UNKNOWN / PROPOSAL. A requirement is marked **IMPLEMENTED**
only where an in-repo evidence pointer verifies it. Evidence pointers are file paths.

## Functional requirements

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| REQ-RUN-001 | pytest plugin registered via `pytest11` entry point | IMPLEMENTED | `pyproject.toml` entry point; `src/django_pytest/plugin.py` |
| REQ-RUN-002 | Plugin auto-activates when `DJANGO_SETTINGS_MODULE` is set; inert otherwise | IMPLEMENTED (INFERENCE on inert path) | `src/django_pytest/plugin.py`; README.md; ADR-001 |
| REQ-RUN-003 | Transactional `db` fixture (per-test transaction rolled back) | IMPLEMENTED | `src/django_pytest/plugin.py`; README.md; ADR-001 |
| REQ-RUN-004 | Per-test runtime capture (duration, query count, fixtures) persisted | IMPLEMENTED | `src/django_pytest/analysis/runtime.py`; ADR-001 (`.django_pytest/last-run.json`) |
| REQ-RUN-005 | `manage.py pytest` command translating Django flags to pytest options | IMPLEMENTED | `src/django_pytest/management/commands/pytest.py`; README.md flag table |
| REQ-RUN-006 | Optional `PytestRunner` as Django `TEST_RUNNER` | IMPLEMENTED | `src/django_pytest/runner.py` |
| REQ-DOC-001 | Analysis engine orchestrates a registry of checks into a `Report` | IMPLEMENTED | `src/django_pytest/analysis/engine.py`, `models.py`, `context.py` |
| REQ-DOC-002 | Check: slow tests (threshold, N+1 hints) | IMPLEMENTED | `src/django_pytest/analysis/checks/slow_tests.py` |
| REQ-DOC-003 | Check: anti-patterns | IMPLEMENTED | `src/django_pytest/analysis/checks/anti_patterns.py` |
| REQ-DOC-004 | Check: parallelization (xdist / db-unit split) | IMPLEMENTED | `src/django_pytest/analysis/checks/parallelization.py` |
| REQ-DOC-005 | Check: coverage gaps (consumes `coverage.xml`) | IMPLEMENTED | `src/django_pytest/analysis/checks/coverage_gaps.py` |
| REQ-DOC-006 | `manage.py testcheck --fail-on <severity>` CI gate | IMPLEMENTED | `src/django_pytest/management/commands/testcheck.py`; README.md |
| REQ-REP-001 | Terminal reporter | IMPLEMENTED | `src/django_pytest/reporters/terminal.py` |
| REQ-REP-002 | JSON reporter | IMPLEMENTED | `src/django_pytest/reporters/json_reporter.py` |
| REQ-REP-003 | Self-contained HTML reporter | IMPLEMENTED | `src/django_pytest/reporters/html_reporter.py` |
| REQ-REP-004 | Staff-only admin report at `/admin/django-pytest/report/` (opt-out via `DJANGO_PYTEST_ADMIN = False`) | IMPLEMENTED | `src/django_pytest/admin.py`, `apps.py`; README.md |

## Non-functional requirements

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| REQ-NFR-001 | Analysis engine imports neither Django nor pytest (unit-testable in isolation) | IMPLEMENTED (INFERENCE — enforced by convention, not a test) | ADR-001; CLAUDE.md convention; `analysis/` layout |
| REQ-NFR-002 | Typed distribution shipping `py.typed`; mypy strict | IMPLEMENTED | `src/django_pytest/py.typed`; pyproject `[tool.mypy]`; Makefile `typecheck` |
| REQ-NFR-003 | Coverage gate `fail_under = 80` | IMPLEMENTED | `pyproject.toml`; CLAUDE.md |
| REQ-NFR-004 | Lint via ruff (line 120, double quotes, single-line isort) | IMPLEMENTED | `pyproject.toml [tool.ruff]`; Makefile `lint` |
| REQ-NFR-005 | Runs in a container for CI (`Dockerfile.test`) | IMPLEMENTED | `Dockerfile.test`; Makefile `docker-test`; `.github/workflows/ci.yml` |
| REQ-NFR-006 | Self-suite must not self-activate the plugin | IMPLEMENTED | `pyproject.toml addopts` `-p no:django_pytest`; CLAUDE.md |

## Version / compatibility requirements

See CONSTRAINTS.md — the declared version floors are **contradictory across docs**
(README says Django ≥4.2; pyproject and ARCHITECTURE say `django>=6.1`). Flagged,
not resolved (docs-only).
</content>
