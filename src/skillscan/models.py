from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


SEVERITY_SCORE = {
    Severity.LOW: 1,
    Severity.MEDIUM: 3,
    Severity.HIGH: 7,
    Severity.CRITICAL: 10,
}


@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    severity: Severity
    path: str
    line: int
    snippet: str
    recommendation: str


@dataclass
class ScanResult:
    root: Path
    findings: list[Finding] = field(default_factory=list)
    files_scanned: int = 0

    @property
    def risk_score(self) -> int:
        raw = sum(SEVERITY_SCORE[f.severity] for f in self.findings)
        return min(100, raw * 5)

    @property
    def failed(self) -> bool:
        return any(f.severity in {Severity.HIGH, Severity.CRITICAL} for f in self.findings)
