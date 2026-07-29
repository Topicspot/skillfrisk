"""Compare two versions of a skill and report what an update changes.

Findings are matched semantically (rule, file, normalized snippet), not by line
number, so reflowed or shifted text does not produce false "new" findings.
No network access: both versions are local paths.
"""

from __future__ import annotations

import re
from pathlib import Path

from .capabilities import extract_capabilities
from .models import DiffResult, Finding, SetDelta
from .scanner import scan_path

_WHITESPACE = re.compile(r"\s+")


def _finding_key(finding: Finding) -> tuple[str, str, str]:
    snippet = _WHITESPACE.sub(" ", finding.snippet).strip().lower()
    return (finding.rule_id, finding.path, snippet)


def _set_delta(old: set[str], new: set[str]) -> SetDelta:
    return SetDelta(added=sorted(new - old), removed=sorted(old - new))


def diff_paths(old_root: Path, new_root: Path) -> DiffResult:
    old_scan = scan_path(old_root)
    new_scan = scan_path(new_root)
    old_keys = {_finding_key(f) for f in old_scan.findings}
    new_keys = {_finding_key(f) for f in new_scan.findings}

    old_caps = extract_capabilities(old_root)
    new_caps = extract_capabilities(new_root)
    old_files = set(old_caps.file_hashes)
    new_files = set(new_caps.file_hashes)

    return DiffResult(
        old_root=old_root.resolve(),
        new_root=new_root.resolve(),
        new_findings=[f for f in new_scan.findings if _finding_key(f) not in old_keys],
        resolved_findings=[f for f in old_scan.findings if _finding_key(f) not in new_keys],
        carried_findings=[f for f in new_scan.findings if _finding_key(f) in old_keys],
        allowed_tools=_set_delta(old_caps.allowed_tools, new_caps.allowed_tools),
        shell_commands=_set_delta(old_caps.shell_commands, new_caps.shell_commands),
        network_hosts=_set_delta(old_caps.network_hosts, new_caps.network_hosts),
        files_added=sorted(new_files - old_files),
        files_removed=sorted(old_files - new_files),
        files_changed=sorted(
            name
            for name in old_files & new_files
            if old_caps.file_hashes[name] != new_caps.file_hashes[name]
        ),
    )
