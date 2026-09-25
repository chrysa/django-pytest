# GLOSSARY — django-pytest

Terms as used in this repository (FACT unless noted).

- **Runner** — the runtime half: pytest plugin + `manage.py pytest` command +
  optional `PytestRunner` that wire Django up for pytest.
- **Doctor** — the analysis half: the engine + checks that inspect a suite and
  report optimizations.
- **Analysis engine** (`django_pytest.analysis`) — framework-agnostic orchestrator
  that runs a registry of `Check` objects over an `AnalysisContext` and produces a
  `Report`. Imports neither Django nor pytest (ADR-001 invariant).
- **AnalysisContext** — the assembled input to checks: parsed AST + runtime data +
  coverage (`analysis/context.py`, `build_context`).
- **Check** — a single analysis unit over the context; concrete checks:
  `slow_tests`, `anti_patterns`, `parallelization`, `coverage_gaps` (`analysis/checks/`).
- **Report** — the structured result rendered by a reporter (`analysis/models.py`).
- **Reporter** — renders a `Report` as `terminal`, `json`, or `html`
  (`reporters/`).
- **`db` fixture** — plugin-provided fixture wrapping each test in a transaction
  rolled back afterwards (`plugin.py`).
- **Runtime capture** — per-test duration, query count, and fixture usage recorded
  by the plugin to `.django_pytest/last-run.json` (`analysis/runtime.py`).
- **`testcheck`** — management command running the Doctor with `--fail-on <severity>`
  as a CI gate (`management/commands/testcheck.py`).
- **pytest11 entry point** — the packaging mechanism that auto-registers the plugin.
- **Admin report view** — optional staff-only HTML report at
  `/admin/django-pytest/report/`, opt out via `DJANGO_PYTEST_ADMIN = False`.
- **Hybrid package** — the app+plugin+engine packaging decision (ADR-001).
- **canon / shared-standards** — the chrysa ecosystem's authoritative rule set the
  repo defers to; canon wins over any annexe (CLAUDE.md).
- **Generated context files** — `handover.md`, `ai-instructions.md`,
  `context-map.json`, `llms-full.txt`: machine/agent context produced by
  `scripts/gen_context_files.py` (ADR D-0012); not hand-edited.
</content>
