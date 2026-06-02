"""Runtime data persistence round-trips."""

from __future__ import annotations

from pathlib import Path

from django_pytest.analysis.runtime import RunData
from django_pytest.analysis.runtime import TestRecord


def test_record_updates_total_duration() -> None:
    data = RunData()
    data.record(TestRecord(nodeid="t::a", duration=1.5))
    data.record(TestRecord(nodeid="t::b", duration=0.5))
    assert data.total_duration == 2.0
    assert set(data.tests) == {"t::a", "t::b"}


def test_json_round_trip() -> None:
    data = RunData(total_duration=3.0, xdist_workers=4)
    data.tests["t::a"] = TestRecord(nodeid="t::a", duration=3.0, query_count=7, uses_db=True, fixtures=["db"])
    restored = RunData.from_json(data.to_json())
    assert restored.total_duration == 3.0
    assert restored.xdist_workers == 4
    assert restored.tests["t::a"].query_count == 7
    assert restored.tests["t::a"].uses_db is True


def test_save_and_load(tmp_path: Path) -> None:
    data = RunData()
    data.record(TestRecord(nodeid="t::a", duration=2.0))
    saved = data.save(tmp_path)
    assert saved.is_file()

    loaded = RunData.load(tmp_path)
    assert loaded is not None
    assert loaded.tests["t::a"].duration == 2.0


def test_load_missing_returns_none(tmp_path: Path) -> None:
    assert RunData.load(tmp_path) is None
