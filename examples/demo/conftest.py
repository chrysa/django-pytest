"""Point pytest at the demo settings so the django-pytest plugin configures Django.

Setting the environment variable here (rather than in ``pytest.ini``) means both
``manage.py pytest`` and a plain ``pytest`` invocation work, with no
"Unknown config option" warning from pytest.
"""

from __future__ import annotations

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo_project.settings")
