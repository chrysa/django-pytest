# SECURITY — django-pytest

Docs-only assessment. No code was modified. Findings are for the owner to action;
this pass does not fix code. Tags: FACT / INFERENCE / UNKNOWN.

## Secret scan (FACT)

A heuristic scan of `src/` and `examples/` for `password|secret|token|api key`
returned **no hardcoded secrets, keys, tokens, or credentials**. No `.env` file is
committed; `ai-instructions.md` and CONTRIBUTING.md both mandate env vars and a
kept-in-sync `.env.example`. No secrets to redact.

The repo ships a secret-scanning pre-commit hook (`.claude/hooks/secret-scanner.cjs`)
and a `.github/workflows/secret-scan.yml` workflow — security scanning is a
committed gate (aligns with the chrysa "security scanning is a gate" rule).

## Attack surface (INFERENCE)

This is developer tooling / a test library, not a deployed service. There is no
network listener, no application database, and no external API of its own
(ARCHITECTURE.md). The runtime executes inside the developer's / CI's test process.

Notable surfaces to keep in mind (no finding, informational):

- **Admin report view** (`admin.py`) — served at `/admin/django-pytest/report/`,
  documented as **staff-only** and opt-out via `DJANGO_PYTEST_ADMIN = False`. It is
  injected by monkey-patching `admin.site.get_urls`. INFERENCE: renders a suite
  HTML report; owner should confirm the staff-only guard and that report content
  (file paths, test names) is acceptable to expose to staff users. No verification
  of the guard was performed in this docs-only pass — [UNKNOWN], not a finding.
- **AST parsing of the host suite** by the analysis engine operates on the
  project's own source; no untrusted external input is ingested.

## Findings

- No HIGH/CRITICAL findings identified from documentation and a heuristic secret
  scan. A full `/security-review` of the diff/code was **out of scope** for this
  docs-only task and is **not** a substitute for one.

## Recommended follow-ups (PROPOSAL — for the owner, not done here)

1. Confirm the admin report view enforces `is_staff`/permission checks and that
   the monkey-patch cannot leak the view when `DJANGO_PYTEST_ADMIN` is unset.
2. Run the repo's own `/security-review` (or the Senior SecOps agent) on the code,
   per the global CLAUDE.md security rule, before any release/publish.
</content>
