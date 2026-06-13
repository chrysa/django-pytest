"""Static (AST) detection of common test anti-patterns."""

from __future__ import annotations

import ast

from django_pytest.analysis.checks.base import Check
from django_pytest.analysis.checks.base import call_names
from django_pytest.analysis.checks.base import decorator_names
from django_pytest.analysis.checks.base import iter_test_functions
from django_pytest.analysis.context import AnalysisContext
from django_pytest.analysis.models import Finding
from django_pytest.analysis.models import Severity
from django_pytest.analysis.runtime import RunData
from django_pytest.analysis.runtime import TestRecord


_DB_MARKERS = {"pytest.mark.django_db", "django_db"}


def _has_assertion(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for node in ast.walk(func):
        if isinstance(node, ast.Assert):
            return True
        if isinstance(node, ast.Call):
            target = node.func
            # self.assertX(...) / pytest.raises(...) / pytest.warns(...)
            if isinstance(target, ast.Attribute):
                if target.attr.startswith("assert"):
                    return True
                if target.attr in {"raises", "warns", "approx"}:
                    return True
    return False


def _uses_db(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    if _DB_MARKERS & decorator_names(func):
        return True
    args = {a.arg for a in func.args.args}
    return "db" in args or "transactional_db" in args


class AntiPatternCheck(Check):
    id = "anti-patterns"
    name = "Test anti-patterns"

    def analyze(self, ctx: AnalysisContext) -> list[Finding]:
        findings: list[Finding] = []
        runtime = ctx.runtime
        for module in ctx.modules:
            rel = str(module.path.relative_to(ctx.root)) if module.path.is_relative_to(ctx.root) else str(module.path)
            for func in iter_test_functions(module.tree):
                calls = call_names(func)

                if not _has_assertion(func):
                    findings.append(
                        Finding(
                            check_id=self.id,
                            severity=Severity.HIGH,
                            message=f"Test '{func.name}' has no assertion.",
                            suggestion="Add an assert, pytest.raises, or self.assertX so the test can actually fail.",
                            path=rel,
                            line=func.lineno,
                        )
                    )

                if "time.sleep" in calls or "sleep" in calls:
                    findings.append(
                        Finding(
                            check_id=self.id,
                            severity=Severity.MEDIUM,
                            message=f"Test '{func.name}' calls sleep().",
                            suggestion="Replace real sleeps with mocked clocks (freezegun) or event-based waits to avoid flaky, slow tests.",
                            path=rel,
                            line=func.lineno,
                        )
                    )

                if "print" in calls:
                    findings.append(
                        Finding(
                            check_id=self.id,
                            severity=Severity.LOW,
                            message=f"Test '{func.name}' contains a print() call.",
                            suggestion="Remove leftover debug prints or use the caplog/capsys fixtures.",
                            path=rel,
                            line=func.lineno,
                        )
                    )

                # Cross static + runtime: DB marker but the test issued zero queries.
                if _uses_db(func) and runtime is not None:
                    record = self._match_runtime(runtime, rel, func.name)
                    if record is not None and record.uses_db and record.query_count == 0:
                        findings.append(
                            Finding(
                                check_id=self.id,
                                severity=Severity.MEDIUM,
                                message=f"Test '{func.name}' requests the database but issues no queries.",
                                suggestion="Drop the db marker/fixture to skip transaction setup and speed the test up.",
                                path=rel,
                                line=func.lineno,
                                test_id=record.nodeid,
                            )
                        )
        return findings

    @staticmethod
    def _match_runtime(runtime: RunData, rel: str, func_name: str) -> TestRecord | None:
        filename = rel.split("/")[-1]
        for nodeid, record in runtime.tests.items():
            if nodeid.endswith(f"::{func_name}") and filename in nodeid:
                return record
        return None
