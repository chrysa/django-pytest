# django-pytest — runnable demo

A minimal Django project showing the two halves of django-pytest:

1. running the suite through Django (`manage.py pytest` / `manage.py test`);
2. the **test doctor** (`manage.py testcheck`) reporting anti-patterns, slow
   tests, parallelization hints, and coverage gaps.

## What it shows

- `TEST_RUNNER = "django_pytest.runner.PytestRunner"` in
  `demo_project/settings.py` so `manage.py test` delegates to pytest.
- A `shop` app with a deliberately imperfect suite (`shop/tests_pricing.py`):
  a healthy test, one with no assertion, one calling `time.sleep`, and one
  using the plugin's transactional `db` fixture.
- A `pricing.bulk_price` function left untested to surface a coverage gap.

## Run it

From the repository root (use Docker or a virtualenv — never system Python):

```bash
pip install -e ".[dev]"
```

Then, from this directory (`examples/demo/`):

```bash
# 1. Run the suite via Django. The plugin records per-test timings and query
#    counts into .django_pytest/last-run.json and writes coverage.xml.
python manage.py pytest

# 2. Analyze the suite. Reads the parsed tests + the runtime data + coverage.
python manage.py testcheck

# 3. Same report as standalone HTML.
python manage.py testcheck --format html --output report.html
```

`manage.py test` works too — it routes through the same pytest runner.

## What testcheck reports here

- **HIGH** — `test_missing_assertion` has no assertion.
- **MEDIUM** — `test_slow_with_sleep` calls `sleep()`.
- **slow tests** — `test_slow_with_sleep` (≈1.1s, above the 1.0s threshold).
- **coverage gaps** — `shop/pricing.py` (`bulk_price` untested) and `shop/apps.py`.
