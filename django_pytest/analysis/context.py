"""Builds the analysis context: parsed test files, runtime data and coverage."""

from __future__ import annotations

import ast
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from django_pytest.analysis.runtime import RunData


TEST_FILE_GLOBS = ("test_*.py", "tests_*.py", "*_test.py")


@dataclass(slots=True)
class ParsedTestModule:
    """A test file together with its parsed AST."""

    path: Path
    tree: ast.Module
    source: str


@dataclass(slots=True)
class FileCoverage:
    """Coverage figures for a single source file."""

    filename: str
    line_rate: float
    missing_lines: int


@dataclass(slots=True)
class AnalysisContext:
    """Everything the checks need to inspect a test suite."""

    root: Path
    modules: list[ParsedTestModule] = field(default_factory=list)
    runtime: RunData | None = None
    coverage: list[FileCoverage] = field(default_factory=list)
    slow_threshold: float = 1.0
    coverage_threshold: float = 0.80


def discover_test_files(paths: list[Path]) -> list[Path]:
    found: set[Path] = set()
    for base in paths:
        if base.is_file() and base.suffix == ".py":
            found.add(base)
            continue
        if not base.is_dir():
            continue
        for pattern in TEST_FILE_GLOBS:
            found.update(base.rglob(pattern))
    return sorted(found)


def parse_modules(files: list[Path]) -> list[ParsedTestModule]:
    modules: list[ParsedTestModule] = []
    for path in files:
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except OSError:
            continue
        except SyntaxError:
            continue
        modules.append(ParsedTestModule(path=path, tree=tree, source=source))
    return modules


def load_coverage(coverage_xml: Path) -> list[FileCoverage]:
    if not coverage_xml.is_file():
        return []
    try:
        root = ET.parse(coverage_xml).getroot()  # noqa: S314 - local trusted file
    except ET.ParseError:
        return []
    results: list[FileCoverage] = []
    for klass in root.iter("class"):
        filename = klass.get("filename", "")
        line_rate = float(klass.get("line-rate", "0") or 0)
        missing = sum(1 for line in klass.iter("line") if line.get("hits") == "0")
        results.append(FileCoverage(filename=filename, line_rate=line_rate, missing_lines=missing))
    return results


def build_context(
    root: Path,
    test_paths: list[Path],
    *,
    slow_threshold: float = 1.0,
    coverage_threshold: float = 0.80,
) -> AnalysisContext:
    files = discover_test_files(test_paths)
    return AnalysisContext(
        root=root,
        modules=parse_modules(files),
        runtime=RunData.load(root),
        coverage=load_coverage(root / "coverage.xml"),
        slow_threshold=slow_threshold,
        coverage_threshold=coverage_threshold,
    )
