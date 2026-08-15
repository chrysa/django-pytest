# Deep-dive — chrysa/django-pytest

**Purpose (1 phrase).** A hybrid Python package that (a) wires Django up for native
`pytest` runs with zero conftest boilerplate (pytest plugin + optional `TEST_RUNNER`
+ `manage.py pytest` command) and (b) ships a framework-agnostic **analysis engine**
("Doctor") that inspects the suite for slow tests, anti-patterns, parallelization
opportunities and coverage gaps, emitting terminal/JSON/self-contained-HTML reports.

**Local shape (what already exists).**
- `src/django_pytest/plugin.py` (179 L) — `pytest11` entry point, Django autodetect
  (`DJANGO_SETTINGS_MODULE`), `setup_databases`, `db` fixture, runtime capture into
  `.django_pytest/last-run.json`.
- `analysis/` — `engine.py`, `runtime.py` (RunData/TestRecord), `checks/` (base +
  slow_tests, anti_patterns, parallelization, coverage_gaps). **MUST stay import-free
  of Django and pytest** (unit-testable).
- `reporters/` — terminal, json, html (78 L self-contained HTML).
- `runner.py` — `PytestRunner` translating Django CLI flags → pytest options.
- Python ≥3.14, Django ≥6, pytest ≥9. MIT. coverage `fail_under=80`.

The functionality (Django-native pytest bootstrap + a test-suite analyzer) maps
directly onto a handful of well-known OSS plugins. Below, each is torn down for the
one mechanism worth borrowing. Licenses flagged inline.

---

## 1. pytest-dev/pytest-django

- **owner/repo:** pytest-dev/pytest-django
- **stars:** ~1.5k
- **activity:** active (1,405 commits; tracks Django 5.2/6.1/main)
- **license:** **BSD-3-Clause — permissive, copiable** (attribution only)
- **pattern file/module:** `pytest_django/plugin.py` — `pytest_configure` /
  `pytest_load_initial_conftests`, the `django_db_setup` / `db` / `transactional_db`
  fixtures, and `DJANGO_SETTINGS_MODULE` / `--ds` / `--dc` resolution.
- **mechanism:** The plugin resolves settings from `--ds`/`--dc` CLI, ini
  (`DJANGO_SETTINGS_MODULE` in `[pytest]`), or the env var, calls `django.setup()`
  once, then lazily creates the test DB via a session-scoped `django_db_setup`
  fixture. Per-test isolation is a fixture that opens an `atomic()` block and rolls
  it back on teardown; `transactional_db` instead flushes. Crucially, DB access is
  **blocked by default** unless a test requests `db` (a `pytest_collection_modifyitems`
  guard), which prevents accidental DB hits.
- **portable snippet (~15 L) — the rollback-isolation fixture, the core idea:**
  ```python
  import pytest
  from django.test.utils import setup_databases, teardown_databases

  @pytest.fixture(scope="session")
  def django_db_setup(request, django_db_blocker):
      with django_db_blocker.unblock():
          cfg = setup_databases(verbosity=0, interactive=False)
      yield
      with django_db_blocker.unblock():
          teardown_databases(cfg, verbosity=0)

  @pytest.fixture
  def db(django_db_setup, django_db_blocker):
      from django.db import connections
      with django_db_blocker.unblock():
          atomics = {a: connections[a].atomic() for a in connections}  # simplified
          [a.__enter__() for a in atomics.values()]
          yield
          [a.__exit__(None, None, None) for a in atomics.values()]  # rollback
  ```
- **integration steps:** django-pytest already re-implements this in `plugin.py`
  (`_DB_CONFIG = setup_databases(...)`, a `db` fixture). Borrow two refinements it
  currently lacks: (1) a **`django_db_blocker`** so the analysis engine / non-db tests
  can't silently touch the DB, and (2) `--reuse-db` / `--create-db` to skip recreation
  between runs (huge local-dev speedup). Wire both into `pytest_addoption`.
- **gotchas:** BSD requires keeping their copyright notice on any copied code — you
  are re-implementing, so just don't paste files verbatim. Their `db` fixture uses
  savepoints for nested atomics; a naive single-`atomic()` breaks tests that themselves
  call `transaction.atomic()`. Session-scoped DB + `xdist` needs per-worker DB suffixes
  (`test_db_gw0`), which they handle in `fixtures.py` — check before you ship parallel.

---

## 2. pytest-dev/pytest-xdist

- **owner/repo:** pytest-dev/pytest-xdist
- **stars:** ~1.9k
- **activity:** very active (1,402 commits)
- **license:** **MIT — permissive, copiable**
- **pattern file/module:** `src/xdist/scheduler/loadscope.py` and `load.py` — the
  scheduling algorithms that assign test items to workers.
- **mechanism:** `-n auto` spawns N worker subprocesses; a scheduler distributes
  collected node IDs. `loadscope` groups tests by module/class so fixtures with
  module scope aren't rebuilt across workers; `load` distributes individually for
  max parallelism. Relevant to django-pytest's **`parallelization` check**: xdist is
  the *target recommendation* — the check should estimate wall-clock speedup and warn
  about ordering/shared-state hazards that break under `-n`.
- **portable snippet (~12 L) — a grouping heuristic for the parallelization check:**
  ```python
  from collections import defaultdict

  def group_by_scope(records):  # records: [(nodeid, duration_s), ...]
      groups = defaultdict(float)
      for nodeid, dur in records:
          module = nodeid.split("::", 1)[0]
          groups[module] += dur
      total = sum(groups.values())
      longest = max(groups.values(), default=0.0)
      ideal_workers = min(len(groups), 8)
      # Amdahl-ish floor: you can never beat the single slowest module
      est_parallel = max(longest, total / ideal_workers)
      return {"serial_s": total, "est_parallel_s": est_parallel,
              "speedup": round(total / est_parallel, 2) if est_parallel else 1.0}
  ```
- **integration steps:** feed `analysis/checks/parallelization.py` the per-module
  duration sums from `RunData`; if `speedup > ~1.5` and no ordering anti-patterns
  detected, emit a rec "install pytest-xdist, run `-n auto` (~Nx faster)". Cite the
  `loadscope` mode when module-scoped fixtures dominate.
- **gotchas:** xdist parallelism silently corrupts suites that share module-level
  mutable state or rely on test ordering — your `anti_patterns` check should gate the
  parallelization rec on absence of those. Also the "slowest single module" is the
  real floor (Amdahl); don't advertise linear speedup.

---

## 3. tarpas/pytest-testmon

- **owner/repo:** tarpas/pytest-testmon
- **stars:** ~1.0k
- **activity:** active
- **license:** **MIT (AGPL for the hosted testmon.org service — the plugin itself is
  permissive/copiable; the SaaS backend is not)**. Flag: verify the exact LICENSE in
  the repo root before copying, dual-licensing here is a trap.
- **pattern file/module:** `testmon/db.py` + `testmon/process_code.py` — coverage-to-
  test dependency mapping persisted in `.testmondata` (SQLite), keyed by file/block
  checksums.
- **mechanism:** Runs tests under `coverage.py`, records which source blocks each test
  executed, hashes those blocks (AST-level, so whitespace/comment edits don't
  invalidate), and on the next run selects only tests whose covered blocks changed.
  This is the durable-history idea django-pytest gestures at with
  `.django_pytest/last-run.json` but does per-test-selection instead of just timing.
- **portable snippet (~14 L) — checksum-keyed run history (SQLite), portable:**
  ```python
  import sqlite3, hashlib, json

  def save_run(records, path=".django_pytest/history.db"):
      con = sqlite3.connect(path)
      con.execute("CREATE TABLE IF NOT EXISTS runs("
                  "nodeid TEXT, dur REAL, queries INT, src_hash TEXT, ts REAL)")
      con.executemany("INSERT INTO runs VALUES(?,?,?,?,?)",
                      [(r.nodeid, r.duration, r.queries,
                        hashlib.sha256(r.source.encode()).hexdigest(), r.ts)
                       for r in records])
      con.commit(); con.close()
  ```
- **integration steps:** promote `last-run.json` to an append-only SQLite history so
  the `slow_tests` check can flag **regressions** ("test X went 0.2s→1.4s over 5 runs")
  rather than only absolute slowness. Keep it in `analysis/runtime.py`, still
  Django-free.
- **gotchas:** the AST-block-checksum selection is genuinely hard (import graphs,
  dynamic dispatch) — don't copy the *selection* engine, only the persistence idea.
  The AGPL/SaaS split means: safe to mirror the plugin's local storage concept,
  **do not** vendor anything from the hosted-service side.

---

## 4. CFMTech/pytest-monitor

- **owner/repo:** CFMTech/pytest-monitor
- **stars:** ~180
- **activity:** active (98 commits, 12 open issues)
- **license:** **MIT — permissive, copiable**
- **pattern file/module:** `pytest_monitor/pytest_monitor.py` — the
  `pytest_runtest_call` wrapper that samples resource usage, stored in a `.pymon`
  SQLite DB.
- **mechanism:** Wraps each test call, measures wall time + CPU + peak memory
  (`psutil` + `memory_profiler`) and persists a row per test per run so you can
  compare across environments/commits. This is the resource-capture layer django-pytest
  only partially has (it captures timing + query counts, not memory/CPU).
- **portable snippet (~12 L) — per-test resource capture hook:**
  ```python
  import time, resource, pytest

  @pytest.hookimpl(hookwrapper=True)
  def pytest_runtest_call(item):
      rss0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
      t0 = time.perf_counter()
      outcome = yield
      dur = time.perf_counter() - t0
      rss1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
      item.user_properties.append(("dpytest", {"dur": dur, "rss_kb": rss1 - rss0}))
  ```
- **integration steps:** django-pytest's `plugin.py` already times tests; add the
  `ru_maxrss` delta (stdlib `resource`, no psutil dep needed for a first cut) into
  `TestRecord` so `slow_tests`/`anti_patterns` can flag memory-heavy tests (e.g.
  fixtures loading huge datasets).
- **gotchas:** `ru_maxrss` is peak-since-process-start on Linux (KB) and doesn't reset
  between tests — you get a monotonic high-water mark, so deltas can be 0 or misleading
  under xdist. For true per-test memory use `tracemalloc` instead; psutil adds a heavy
  dep the project currently avoids.

---

## 5. tmarice/django-timed-tests

- **owner/repo:** tmarice/django-timed-tests
- **stars:** ~29
- **activity:** modest (61 commits; supports Django ≤4.2, older)
- **license:** **MIT — permissive, copiable**
- **pattern file/module:** `django_timed_tests/runner.py` — a `TimedTestRunner`
  subclassing Django's `DiscoverRunner`, overriding the result class to record
  per-test durations and print a "10 slowest" + per-module/case/method breakdown.
- **mechanism:** Hooks Django's own test runner (not pytest) via a custom
  `TestResult` that stamps start/stop around each test, then aggregates a tree
  (module → class → method). Directly parallels django-pytest's `runner.PytestRunner`
  and `slow_tests` check — same "what gets measured gets improved" framing.
- **portable snippet (~12 L) — hierarchical duration rollup for the report:**
  ```python
  from collections import defaultdict

  def rollup(records):  # records: [(nodeid, dur), ...]  nodeid = "mod::Class::test"
      tree = defaultdict(lambda: defaultdict(float))
      for nodeid, dur in records:
          parts = nodeid.split("::")
          module, klass = parts[0], (parts[1] if len(parts) > 2 else "<func>")
          tree[module][klass] += dur
      return {m: {"total": sum(cs.values()), "classes": dict(cs)}
              for m, cs in tree.items()}
  ```
- **integration steps:** the HTML/terminal reporters can render this module→class
  rollup as a collapsible tree instead of a flat slowest-N list, giving users the
  "where is my suite time actually going" view. Pure-Python, drops straight into
  `analysis/` with no Django import.
- **gotchas:** it's a `unittest`/DiscoverRunner design — do not adopt its runner, only
  the aggregation shape. Django ≥ has native `--durations` (unittest) now, so position
  django-pytest's value as the *analysis on top of* timings, not the timing itself.

---

## 6. pytest-dev/pytest-html

- **owner/repo:** pytest-dev/pytest-html
- **stars:** ~775
- **activity:** active (671 commits)
- **license:** **MPL-2.0 — weak copyleft, FILE-LEVEL. Flag: not GPL-viral, but any
  MPL-licensed *file* you copy stays MPL and its source must be offered. Re-implement
  rather than vendor their files; your own from-scratch HTML template is unaffected.**
- **pattern file/module:** `src/pytest_html/report_data.py` + the bundled
  `resources/style.css` / `main.js` — a single self-contained HTML report with all
  CSS/JS inlined, sortable/filterable result table.
- **mechanism:** Collects per-test outcome/duration/logs into a data object, renders
  a Jinja-ish template with inlined assets so the report is one portable `.html`
  (works offline, emailable). Exactly django-pytest's `reporters/html_reporter.py`
  goal ("self-contained HTML report, also viewable in Django admin").
- **portable snippet (~10 L) — self-contained inlining pattern (write your own CSS):**
  ```python
  def render_html(rows, css: str, js: str) -> str:
      body = "\n".join(
          f"<tr class='{r.status}'><td>{r.nodeid}</td>"
          f"<td>{r.duration:.3f}s</td><td>{r.queries}</td></tr>" for r in rows)
      return (f"<!doctype html><meta charset=utf-8>"
              f"<style>{css}</style>"
              f"<table id=results><thead><tr><th>Test<th>Time<th>Queries"
              f"</thead><tbody>{body}</tbody></table>"
              f"<script>{js}</script>")  # sortable table, no external CDN
  ```
- **integration steps:** django-pytest already inlines (78-L `html_reporter.py`); the
  borrowable *idea* is client-side sort/filter JS so a large report stays navigable,
  and a stable `data-*` schema on rows so the Django-admin embed can re-use the same
  markup. Keep writing your own CSS/JS to avoid the MPL entanglement.
- **gotchas:** **MPL is per-file copyleft** — copying their `style.css`/`main.js`
  obliges you to disclose those files' source under MPL. Trivial to avoid: hand-write
  the ~30 lines of sort JS. Also self-contained reports bloat fast; cap embedded logs.

---

## Cross-cutting takeaways

1. **DB isolation** — adopt pytest-django's `django_db_blocker` + `--reuse-db` (BSD,
   copiable) to harden the existing `db` fixture and speed local runs.
2. **History/regression** — promote `last-run.json` → append-only SQLite (testmon idea,
   MIT plugin; avoid its AGPL SaaS side) so `slow_tests` flags regressions, not just
   absolute slowness.
3. **Report UX** — module→class duration rollup (django-timed-tests) + client-side
   sortable table (pytest-html *concept only*, MPL per-file — reimplement).

## License summary

| Source | License | Verdict |
| --- | --- | --- |
| pytest-django | BSD-3-Clause | permissive — copiable (keep notice) |
| pytest-xdist | MIT | permissive — copiable |
| pytest-testmon | MIT plugin / **AGPL SaaS** | plugin copiable; **do not** touch SaaS side |
| pytest-monitor | MIT | permissive — copiable |
| django-timed-tests | MIT | permissive — copiable |
| pytest-html | **MPL-2.0** | weak copyleft, per-file — **reimplement**, don't vendor files |
