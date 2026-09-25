# PRD — django-pytest

> Tags: FACT (verifiable in-repo), INFERENCE (reasoned from evidence),
> UNKNOWN (not determinable from the repo), PROPOSAL (suggested, not implemented).
> This document is descriptive of the repository as-is; it invents no requirements.

## Problem (FACT — README.md, ARCHITECTURE.md)

Running pytest under Django normally requires `conftest.py` / `pytest-django`
boilerplate, and Django test suites tend to accumulate slow tests, anti-patterns,
serial execution, and coverage gaps that are invisible without tooling.

## Product (FACT — README.md, docs/adr/ADR-001-hybrid-app-and-plugin.md)

`django-pytest` is a reusable Python package that ships two capabilities in one
distribution:

1. **Runner** — a pytest plugin (`pytest11` entry point) plus Django management
   commands that wire Django up for pytest (settings autodetection, test database
   lifecycle, a transactional `db` fixture) so pytest runs with no boilerplate.
2. **Doctor** — a framework-agnostic analysis engine that inspects a suite and
   reports slow tests, anti-patterns, parallelization opportunities, and coverage
   gaps, rendered as terminal / JSON / self-contained HTML (HTML also viewable in
   the Django admin).

## Target users (INFERENCE — README.md, CONTRIBUTING.md)

Django developers and CI maintainers who use pytest and want zero-config
integration plus automated test-suite health analysis. This is developer tooling
(a library / dev dependency), not an end-user application.

## Goals (FACT — README.md, ADR-001)

- G-1: Run pytest natively inside Django without per-project boilerplate.
- G-2: Stay inert (no-op) in non-Django projects where the plugin is installed.
- G-3: Let the analysis engine be adopted independently of the runtime plugin.
- G-4: Surface findings in multiple formats (terminal, JSON, HTML, admin view).
- G-5: Provide a CI gate (`testcheck --fail-on <severity>`).

## Non-goals (INFERENCE — ADR-001, ARCHITECTURE.md)

- No application database, network service, or external API of its own.
- No `[project.scripts]` console entry point (activation is via `pytest11` entry
  point and/or `INSTALLED_APPS`).

## Relationship to fastapi-pytest (FACT — task framing; see REVIEW.md)

Per the documenting task, `django-pytest` is the Django original that
`fastapi-pytest` ports. This repository contains no in-repo reference to
`fastapi-pytest`; the relationship is asserted by the task, not verifiable from
this repo's contents. See REVIEW.md → "Contradictions / relationship".

## Success signals (INFERENCE)

- Suite self-tests green (59 test functions across `tests/tests_*.py` — FACT).
- Coverage gate `fail_under = 80` (FACT — pyproject.toml / CLAUDE.md).
- CI (pre-commit, lint, mypy strict, test, sonar) passing (FACT — CONTRIBUTING.md,
  .github/workflows/).
</content>
</invoke>
