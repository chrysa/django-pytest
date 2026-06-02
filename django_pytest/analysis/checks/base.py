"""Base class and shared AST helpers for checks."""

from __future__ import annotations

import ast
from abc import ABC
from abc import abstractmethod

from django_pytest.analysis.context import AnalysisContext
from django_pytest.analysis.models import Finding


class Check(ABC):
    """A single analysis rule. Subclasses implement :meth:`analyze`."""

    id: str
    name: str

    @abstractmethod
    def analyze(self, ctx: AnalysisContext) -> list[Finding]:
        """Inspect the context and return findings (possibly empty)."""
        raise NotImplementedError


def iter_test_functions(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Yield top-level and class-nested ``test_*`` functions."""

    functions: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            functions.append(node)
    return functions


def decorator_names(func: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    names: set[str] = set()
    for dec in func.decorator_list:
        target = dec.func if isinstance(dec, ast.Call) else dec
        names.add(_dotted_name(target))
    return names


def _dotted_name(node: ast.expr) -> str:
    parts: list[str] = []
    current: ast.expr | None = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def call_names(func: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """All dotted call targets invoked inside a function body."""

    names: set[str] = set()
    for node in ast.walk(func):
        if isinstance(node, ast.Call):
            names.add(_dotted_name(node.func))
    return names
