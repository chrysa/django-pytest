"""pytest plugin: native Django setup + runtime data collection.

Registered via the ``pytest11`` entry point. Activates only when Django is
discoverable (``DJANGO_SETTINGS_MODULE`` set or settings importable), so the
plugin is safe to keep installed in non-Django projects.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

import pytest

from django_pytest.analysis.runtime import RunData
from django_pytest.analysis.runtime import TestRecord


if TYPE_CHECKING:
    from collections.abc import Generator


_RUN_DATA = RunData()
_DJANGO_READY = False
_DB_CONFIG: Any = None


def _django_configured() -> bool:
    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        return False
    try:
        import django  # noqa: F401
    except ImportError:
        return False
    return True


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("django-pytest")
    group.addoption(
        "--dpytest-check",
        action="store_true",
        default=False,
        help="Run the test analysis engine after the session and print a report.",
    )
    group.addoption(
        "--dpytest-no-db",
        action="store_true",
        default=False,
        help="Skip test-database creation even if Django is configured.",
    )


def pytest_configure(config: pytest.Config) -> None:
    global _DJANGO_READY, _DB_CONFIG
    config.addinivalue_line("markers", "slow: marks a test as slow (see django-pytest analysis).")
    if not _django_configured():
        return

    import django
    from django.conf import settings

    django.setup()
    _DJANGO_READY = True

    if config.getoption("--dpytest-no-db") or not settings.DATABASES:
        return

    from django.test.utils import setup_test_environment

    setup_test_environment()
    config._dpytest_teardown_env = True  # type: ignore[attr-defined]


@pytest.hookimpl(trylast=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    if not _DJANGO_READY or session.config.getoption("--dpytest-no-db"):
        return
    global _DB_CONFIG
    from django.test.utils import setup_databases

    verbosity = session.config.option.verbose
    _DB_CONFIG = setup_databases(verbosity=verbosity, interactive=False)


@pytest.fixture
def db() -> Generator[None]:
    """Wrap a test in an atomic block that is rolled back afterwards."""

    if not _DJANGO_READY:
        pytest.skip("Django is not configured (set DJANGO_SETTINGS_MODULE).")
    from django.db import transaction

    atomic = transaction.atomic()
    atomic.__enter__()
    try:
        yield
    finally:
        transaction.set_rollback(True)
        atomic.__exit__(None, None, None)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None) -> Generator[None]:  # noqa: ARG001
    start = time.perf_counter()
    captures = _start_query_capture()
    outcome = yield
    duration = time.perf_counter() - start
    query_count = _stop_query_capture(captures)
    del outcome

    fixtures = sorted(getattr(item, "fixturenames", []))
    uses_db = "db" in fixtures or "transactional_db" in fixtures or item.get_closest_marker("django_db") is not None
    _RUN_DATA.record(
        TestRecord(
            nodeid=item.nodeid,
            duration=duration,
            query_count=query_count,
            uses_db=uses_db,
            fixtures=fixtures,
        )
    )


def _start_query_capture() -> Any:
    if not _DJANGO_READY:
        return None
    try:
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        ctx = CaptureQueriesContext(connection)
        ctx.__enter__()
        return ctx
    except Exception:  # noqa: BLE001 - DB may be unavailable; degrade gracefully
        return None


def _stop_query_capture(ctx: Any) -> int:
    if ctx is None:
        return 0
    try:
        ctx.__exit__(None, None, None)
        return len(ctx.captured_queries)
    except Exception:  # noqa: BLE001
        return 0


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # noqa: ARG001
    worker = os.environ.get("PYTEST_XDIST_WORKER")
    _RUN_DATA.xdist_workers = int(os.environ.get("PYTEST_XDIST_WORKER_COUNT", "0") or 0)

    # Only the controller (or a non-xdist run) persists, to avoid clobbering.
    if worker is None:
        root = Path(str(session.config.rootpath))
        _RUN_DATA.save(root)

    if _DB_CONFIG is not None:
        from django.test.utils import teardown_databases

        teardown_databases(_DB_CONFIG, verbosity=session.config.option.verbose)
    if getattr(session.config, "_dpytest_teardown_env", False):
        from django.test.utils import teardown_test_environment

        teardown_test_environment()

    if session.config.getoption("--dpytest-check"):
        _print_analysis(Path(str(session.config.rootpath)))


def _print_analysis(root: Path) -> None:
    from django_pytest.analysis.engine import analyze
    from django_pytest.reporters.terminal import render_terminal

    report = analyze(root, [root])
    print("\n" + render_terminal(report))  # noqa: T201 - intentional plugin output
