"""Test-file discovery: pruning, globbing and explicit-failure behaviour."""

from __future__ import annotations

from pathlib import Path

import pytest

from django_pytest.analysis.context import discover_test_files


def test_discovers_test_files_by_glob(tmp_path: Path) -> None:
    (tmp_path / "tests_a.py").write_text("", encoding="utf-8")
    (tmp_path / "b_test.py").write_text("", encoding="utf-8")
    (tmp_path / "helpers.py").write_text("", encoding="utf-8")
    found = {p.name for p in discover_test_files([tmp_path])}
    assert found == {"tests_a.py", "b_test.py"}


def test_prunes_vendored_directories(tmp_path: Path) -> None:
    (tmp_path / "tests_real.py").write_text("", encoding="utf-8")
    for pruned in (".venv", "node_modules", "__pycache__"):
        sub = tmp_path / pruned
        sub.mkdir()
        (sub / "tests_vendored.py").write_text("", encoding="utf-8")
    found = {p.name for p in discover_test_files([tmp_path])}
    assert found == {"tests_real.py"}


def test_explicit_python_file_is_discovered(tmp_path: Path) -> None:
    target = tmp_path / "anything.py"
    target.write_text("", encoding="utf-8")
    assert discover_test_files([target]) == [target]


def test_missing_path_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        discover_test_files([tmp_path / "does_not_exist"])
