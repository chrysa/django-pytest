"""Runtime data captured by the pytest plugin and persisted between runs."""

from __future__ import annotations

import json
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path


CACHE_DIR = ".django_pytest"
CACHE_FILE = "last-run.json"


@dataclass(slots=True)
class TestRecord:
    """Runtime measurements for a single test node."""

    __test__ = False  # not a pytest test class

    nodeid: str
    duration: float = 0.0
    query_count: int = 0
    uses_db: bool = False
    fixtures: list[str] = field(default_factory=list)
    outcome: str = "passed"


@dataclass(slots=True)
class RunData:
    """Collection of per-test runtime records plus session-level totals."""

    tests: dict[str, TestRecord] = field(default_factory=dict)
    total_duration: float = 0.0
    xdist_workers: int = 0

    def record(self, record: TestRecord) -> None:
        self.tests[record.nodeid] = record
        self.total_duration += record.duration

    def to_json(self) -> str:
        payload = {
            "total_duration": self.total_duration,
            "xdist_workers": self.xdist_workers,
            "tests": {nodeid: asdict(rec) for nodeid, rec in self.tests.items()},
        }
        return json.dumps(payload, indent=2, sort_keys=True)

    @classmethod
    def from_json(cls, raw: str) -> RunData:
        payload = json.loads(raw)
        data = cls(
            total_duration=float(payload.get("total_duration", 0.0)),
            xdist_workers=int(payload.get("xdist_workers", 0)),
        )
        for nodeid, rec in payload.get("tests", {}).items():
            data.tests[nodeid] = TestRecord(**rec)
        return data

    def save(self, root: Path) -> Path:
        cache_dir = root / CACHE_DIR
        cache_dir.mkdir(parents=True, exist_ok=True)
        target = cache_dir / CACHE_FILE
        target.write_text(self.to_json(), encoding="utf-8")
        return target

    @classmethod
    def load(cls, root: Path) -> RunData | None:
        target = root / CACHE_DIR / CACHE_FILE
        if not target.is_file():
            return None
        return cls.from_json(target.read_text(encoding="utf-8"))
