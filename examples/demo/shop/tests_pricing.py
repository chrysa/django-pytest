"""Demo test suite with deliberate anti-patterns for `testcheck` to flag.

This suite is intentionally imperfect:

* ``test_apply_discount`` is a healthy test (covers ``apply_discount``).
* ``test_missing_assertion`` has no assertion   → HIGH anti-pattern.
* ``test_slow_with_sleep`` calls ``time.sleep`` → MEDIUM anti-pattern + slow test.
* ``test_uses_db_fixture`` shows the plugin's ``db`` fixture (healthy).

Run ``manage.py pytest`` then ``manage.py testcheck`` to see them reported.
"""

from __future__ import annotations

import time

from shop.pricing import apply_discount


def test_apply_discount() -> None:
    """Healthy test: clear arrange/act/assert covering apply_discount."""
    assert apply_discount(100.0, 25) == 75.0
    assert apply_discount(50.0, 0) == 50.0


def test_missing_assertion() -> None:
    """Anti-pattern: computes a value but never asserts anything."""
    apply_discount(100.0, 10)


def test_slow_with_sleep() -> None:
    """Anti-pattern: a real sleep makes the suite slow and flaky."""
    time.sleep(1.1)
    assert apply_discount(200.0, 50) == 100.0


def test_uses_db_fixture(db: None) -> None:
    """Healthy test using the plugin's transactional ``db`` fixture."""
    assert apply_discount(10.0, 100) == 0.0
