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

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **django-pytest** (558 symbols, 1010 relationships, 47 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/django-pytest/context` | Codebase overview, check index freshness |
| `gitnexus://repo/django-pytest/clusters` | All functional areas |
| `gitnexus://repo/django-pytest/processes` | All execution flows |
| `gitnexus://repo/django-pytest/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

<!-- ui-ux-skill: not-applicable -- reason: backend lib/scaffolder/gateway, no human-facing surface -->

## Skills

- `testing-pytest/SKILL.md` — pytest DDD + pytest-mock + constants (load when writing tests)

Shared skills from `shared-standards/.claude/skills/`:
- `dockerfile-multistage/SKILL.md` — 4-stage Python 3.14 containers (load when editing Dockerfile)

<!-- chrysa:standards-import:start -->
@.chrysa/STANDARDS.md
<!-- chrysa:standards-import:end -->
