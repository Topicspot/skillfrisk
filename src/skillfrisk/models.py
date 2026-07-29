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


@dataclass(frozen=True)
class SetDelta:
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.added or self.removed)


@dataclass
class DiffResult:
    old_root: Path
    new_root: Path
    new_findings: list[Finding] = field(default_factory=list)
    resolved_findings: list[Finding] = field(default_factory=list)
    carried_findings: list[Finding] = field(default_factory=list)
    allowed_tools: SetDelta = field(default_factory=SetDelta)
    shell_commands: SetDelta = field(default_factory=SetDelta)
    network_hosts: SetDelta = field(default_factory=SetDelta)
    files_added: list[str] = field(default_factory=list)
    files_removed: list[str] = field(default_factory=list)
    files_changed: list[str] = field(default_factory=list)

    @property
    def capabilities_grew(self) -> bool:
        return bool(
            self.allowed_tools.added or self.shell_commands.added or self.network_hosts.added
        )

    @property
    def verdict(self) -> str:
        if self.new_findings or self.capabilities_grew:
            return "risk_increased"
        if self.resolved_findings:
            return "risk_reduced"
        return "no_new_risk"
