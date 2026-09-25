# DECISIONS — django-pytest

Architecture Decision Records. The canonical ADR files live under `docs/adr/`.
This file is a consolidated index plus decisions inferable from repo config that
have no standalone ADR (tagged accordingly). Where a rationale is not recorded in
the repo it is marked UNKNOWN rather than invented.

> Note: `CLAUDE.md` points readers to a `DECISIONS.md` for "ADR-001 (hybrid app +
> plugin)". That target file did not previously exist; the ADR itself lives at
> `docs/adr/ADR-001-hybrid-app-and-plugin.md`. This index reconciles the pointer.

## ADR index (canonical, from docs/adr/)

| ADR | Title | Status | Date | Source |
|-----|-------|--------|------|--------|
| ADR-001 | Hybrid Django app + pytest plugin architecture | accepted | 2026-06-02 | `docs/adr/ADR-001-hybrid-app-and-plugin.md` |

### ADR-001 summary (FACT)

Ship one hybrid package: a `pytest11` plugin for the runtime (Django autodetect,
test-DB lifecycle, transactional `db` fixture, per-test capture to
`.django_pytest/last-run.json`), a Django app for the developer surface (`pytest`
/ `testcheck` commands, optional `TEST_RUNNER`, optional staff-only admin report),
and a framework-agnostic analysis engine that imports neither Django nor pytest.
Consequences: plugin no-ops in non-Django projects; runtime/static split lets
checks combine evidence and degrade gracefully; two activation paths must both be
documented and are independently adoptable.

## Implicit decisions (INFERENCE from config — no standalone ADR)

- **D-i1** Packaged Python floor 3.14 despite code running on 3.11+ — aligns to the
  chrysa standard (CLAUDE.md). Rationale beyond "chrysa standard": UNKNOWN.
- **D-i2** ruff `target-version` py313 as a temporary workaround for a py314 ruff
  formatting bug (`pyproject.toml` comment).
- **D-i3** Admin report injected by monkey-patching `admin.site.get_urls` rather
  than requiring users to swap `AdminSite`; mypy `[method-assign]` disabled for it
  (`pyproject.toml`, ADR-001).
- **D-i4** Self-suite disables the package's own plugin (`-p no:django_pytest`) so
  the library does not test itself through its own runtime hooks (CLAUDE.md).

## Referenced external ADRs (EXTERNAL — defined in shared-standards, not in this repo)

- **ADR D-0012** — generated context files (`handover.md`, `ai-instructions.md`,
  etc.). Referenced in generated file headers; full text lives in the canon.

## Unknowns

- Rationale for the `django>=6.1` / `pytest>=9.1.1` floors vs the README's
  "Django ≥4.2 / pytest ≥8" claim: UNKNOWN (contradiction, see REVIEW.md).
</content>
