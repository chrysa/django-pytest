"""Machine-readable JSON reporter."""

from __future__ import annotations

import json

from django_pytest.analysis.models import Report


def render_json(report: Report) -> str:
    payload = {
        "max_severity": report.max_severity.label,
        "counts": {sev.label: count for sev, count in report.counts().items()},
        "findings": [
            {
                "check_id": f.check_id,
                "severity": f.severity.label,
                "message": f.message,
                "suggestion": f.suggestion,
                "location": f.location or None,
                "test_id": f.test_id,
            }
            for f in report.by_severity()
        ],
    }
    return json.dumps(payload, indent=2)
