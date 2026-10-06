# REVIEW — django-pytest documentation pass

Docs-only review. No source/tests/deps/CI/config were modified. Tags:
FACT / INFERENCE / UNKNOWN / PROPOSAL.

## Scope

Generated root docs: PRD, TRD, CONSTRAINTS, REQUIREMENTS, DECISIONS, TESTING,
SECURITY, GLOSSARY, REVIEW. Preserved existing: README.md, ARCHITECTURE.md,
CHANGELOG.md, CLAUDE.md, AGENTS.md, CONTRIBUTING.md, and generated context files.

## Contradictions & inconsistencies found (flagged, not fixed)

1. **Django version floor.** `README.md` states "Django ≥4.2" while
   `pyproject.toml` declares `django>=6.1` and `ARCHITECTURE.md` confirms
   `django>=6.1`. The packaged floor is 6.1; the README understates it. [FACT]
2. **pytest version floor.** README mentions pytest ≥8; `pyproject.toml` declares
   `pytest>=9.1.1`. [FACT]
3. **Python floor phrasing.** README/CLAUDE.md say "code runs on 3.11+" but the
   distribution `requires-python = ">=3.14"`. Consistent once read as
   "packaged floor 3.14, source compatible lower" — documented in CONSTRAINTS. [FACT]
4. **`DECISIONS.md` pointer.** `CLAUDE.md` directs readers to `DECISIONS.md` for
   ADR-001, but the ADR lives at `docs/adr/ADR-001-hybrid-app-and-plugin.md` and no
   `DECISIONS.md` previously existed. This pass adds a `DECISIONS.md` index that
   reconciles the pointer (does not move or alter the canonical ADR). [FACT]
5. **Missing Makefile targets referenced elsewhere.** `CHANGELOG.md` says
   "Run `make changelog`" and the generated context files say "Regenerate with
   `make gen-context-files`", but the current `Makefile` defines neither target
   (it has `install/dev/test/test-cov/lint/format/typecheck/docker-test/build/
   pre-commit/clean/ci`). Documentation references commands the Makefile does not
   expose. [FACT — owner to reconcile]
6. **Branch base.** `CONTRIBUTING.md` says branch from `main`; the chrysa canon /
   user memory treats `develop` as the workspace and `main` as production. Repo is
   currently on branch `chore/claude-config-drift-hook`. Possible policy drift —
   flagged for owner. [INFERENCE]

## fastapi-pytest relationship (task-asserted)

The task states django-pytest is the Django original that `fastapi-pytest` ports.
**This repository contains no reference to fastapi-pytest** (no mention in README,
ARCHITECTURE, ADRs, or config). The relationship is therefore **not verifiable
from this repo** — recorded as task context, not an in-repo FACT. A sibling repo
`fastapi-pytest` exists in the same fleet (per the skills listing), but no
cross-link or shared-lineage marker is present here to confirm the port. [UNKNOWN]

## Documentation debt

- README understates dependency floors (items 1–2) — a code-owner edit, out of
  docs-only scope for source but the README could be corrected in a follow-up.
- Dangling `make changelog` / `make gen-context-files` references (item 5).
- No OBSERVABILITY or ROADMAP content exists to document (see "Docs skipped").
- Notion links and repo profile/DDD level are "(not available)" in `handover.md` —
  ecosystem metadata gap. [FACT]

## Docs skipped (with reason)

- **OBSERVABILITY.md** — skipped: this is a dev-time library with no runtime
  service, logs, metrics, or tracing surface of its own (ARCHITECTURE.md: "No
  network services or external APIs"). Nothing to document.
- **ROADMAP.md** — skipped: no roadmap, backlog, TODO, or future-work statements
  found in-repo; CHANGELOG `[Unreleased]` is empty. Inventing one would violate the
  no-fabrication rule.

## Quality pass

- Every generated claim carries an in-repo evidence pointer or an explicit
  UNKNOWN/INFERENCE tag. No secrets encountered or copied. CLAUDE.md managed blocks
  and generated context files were not modified.
</content>
