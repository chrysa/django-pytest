"""Core data structures shared across the analysis engine."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from dataclasses import field


class Severity(enum.IntEnum):
    """Ordered severity levels. Higher means more important."""

    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @property
    def label(self) -> str:
        return self.name.lower()


@dataclass(frozen=True, slots=True)
class Finding:
    """A single issue or suggestion produced by a check."""

    check_id: str
    severity: Severity
    message: str
    suggestion: str = ""
    path: str | None = None
    line: int | None = None
    test_id: str | None = None

    @property
    def location(self) -> str:
        if self.path is None:
            return ""
        if self.line is not None:
            return f"{self.path}:{self.line}"
        return self.path


@dataclass(slots=True)
class Report:
    """Aggregated result of an analysis run."""

    findings: list[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def extend(self, findings: list[Finding]) -> None:
        self.findings.extend(findings)

    @property
    def max_severity(self) -> Severity:
        if not self.findings:
            return Severity.INFO
        return max(f.severity for f in self.findings)

    def counts(self) -> dict[Severity, int]:
        result: dict[Severity, int] = dict.fromkeys(Severity, 0)
        for finding in self.findings:
            result[finding.severity] += 1
        return result

    def by_severity(self) -> list[Finding]:
        return sorted(self.findings, key=lambda f: (-f.severity, f.check_id))
