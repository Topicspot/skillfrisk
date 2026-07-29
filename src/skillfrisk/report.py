from __future__ import annotations

import html
import json
from dataclasses import asdict

from rich.console import Console
from rich.table import Table

from .models import DiffResult, Finding, ScanResult


def result_to_json(result: ScanResult) -> str:
    payload = {
        "root": str(result.root),
        "files_scanned": result.files_scanned,
        "risk_score": result.risk_score,
        "failed": result.failed,
        "findings": [asdict(f) for f in result.findings],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def result_to_sarif(result: ScanResult) -> str:
    rules_by_id = {}
    results = []
    severity_to_level = {
        "critical": "error",
        "high": "error",
        "medium": "warning",
        "low": "note",
    }
    for finding in result.findings:
        rules_by_id[finding.rule_id] = {
            "id": finding.rule_id,
            "name": finding.title,
            "shortDescription": {"text": finding.title},
            "help": {"text": finding.recommendation},
            "properties": {"severity": finding.severity.value},
        }
        results.append(
            {
                "ruleId": finding.rule_id,
                "level": severity_to_level[finding.severity.value],
                "message": {"text": f"{finding.title}: {finding.snippet}"},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": finding.path},
                            "region": {"startLine": finding.line},
                        }
                    }
                ],
                "properties": {
                    "severity": finding.severity.value,
                    "recommendation": finding.recommendation,
                },
            }
        )
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "skillfrisk",
                        "informationUri": "https://github.com/Topicspot/skillfrisk",
                        "rules": list(rules_by_id.values()),
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


SEVERITY_STYLE = {
    "critical": "bold red",
    "high": "red",
    "medium": "yellow",
    "low": "cyan",
}


def print_terminal(result: ScanResult) -> None:
    console = Console()
    files = result.files_scanned
    if not result.findings:
        console.print(
            f"skillfrisk: {files} file(s) scanned, 0 findings, risk {result.risk_score}/100",
            highlight=False,
        )
        console.print("[bold green]No high-risk findings detected.[/bold green]")
        return

    table = Table(
        title=f"skillfrisk: {result.risk_score}/100 risk, "
        f"{len(result.findings)} findings in {files} file(s)"
    )
    for col in ["Severity", "Rule", "File", "Line", "Snippet"]:
        table.add_column(col)
    for finding in result.findings:
        severity = finding.severity.value
        table.add_row(
            f"[{SEVERITY_STYLE[severity]}]{severity}[/]",
            finding.rule_id,
            finding.path,
            str(finding.line),
            finding.snippet,
        )
    console.print(table)
    if result.failed:
        console.print("[bold red]High-risk findings detected.[/bold red]")
    else:
        console.print("[bold green]No high-risk findings detected.[/bold green]")


def result_to_html(result: ScanResult) -> str:
    rows = "\n".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(str(value))}</td>"
            for value in [f.severity.value, f.rule_id, f.path, f.line, f.snippet, f.recommendation]
        )
        + "</tr>"
        for f in result.findings
    )
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><title>skillfrisk report</title>
<style>body{{font-family:Inter,system-ui,sans-serif;margin:2rem;background:#0f172a;color:#e2e8f0}}table{{border-collapse:collapse;width:100%;background:#111827}}td,th{{border:1px solid #334155;padding:.6rem;vertical-align:top}}th{{background:#1e293b}}.score{{font-size:2rem;font-weight:800}}</style></head>
<body><h1>skillfrisk report</h1><p class=\"score\">Risk score: {result.risk_score}/100</p><p>Files scanned: {result.files_scanned}. Findings: {len(result.findings)}.</p>
<table><thead><tr><th>Severity</th><th>Rule</th><th>File</th><th>Line</th><th>Snippet</th><th>Recommendation</th></tr></thead><tbody>{rows}</tbody></table>
</body></html>"""


VERDICT_TEXT = {
    "risk_increased": "[bold red]VERDICT: RISK INCREASED.[/bold red]",
    "risk_reduced": "[bold green]VERDICT: RISK REDUCED.[/bold green]",
    "no_new_risk": "[bold green]VERDICT: NO NEW RISK.[/bold green]",
}
CAPABILITY_LABELS = [
    ("allowed_tools", "allowed-tools"),
    ("shell_commands", "shell commands"),
    ("network_hosts", "network hosts"),
]


def diff_to_json(diff: DiffResult) -> str:
    payload = {
        "old": str(diff.old_root),
        "new": str(diff.new_root),
        "verdict": diff.verdict,
        "new_findings": [asdict(f) for f in diff.new_findings],
        "resolved_findings": [asdict(f) for f in diff.resolved_findings],
        "carried_findings": [asdict(f) for f in diff.carried_findings],
        "capabilities": {
            key: {"added": delta.added, "removed": delta.removed}
            for key, _ in CAPABILITY_LABELS
            for delta in [getattr(diff, key)]
        },
        "files": {
            "added": diff.files_added,
            "removed": diff.files_removed,
            "changed": diff.files_changed,
        },
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _finding_table(title: str, findings: list[Finding]) -> Table:
    table = Table(title=title)
    for col in ["Severity", "Rule", "File", "Line", "Snippet"]:
        table.add_column(col)
    for finding in findings:
        severity = finding.severity.value
        table.add_row(
            f"[{SEVERITY_STYLE[severity]}]{severity}[/]",
            finding.rule_id,
            finding.path,
            str(finding.line),
            finding.snippet,
        )
    return table


def print_diff_terminal(diff: DiffResult, show_resolved: bool = False) -> None:
    console = Console()
    files_summary = (
        f"files: {len(diff.files_changed)} changed, "
        f"{len(diff.files_added)} added, {len(diff.files_removed)} removed"
    )
    console.print(
        f"skillfrisk diff  {diff.old_root.name} -> {diff.new_root.name}    {files_summary}",
        highlight=False,
    )
    if diff.new_findings:
        console.print(_finding_table(f"NEW FINDINGS ({len(diff.new_findings)})", diff.new_findings))
    else:
        console.print("No new findings.", highlight=False)
    for key, label in CAPABILITY_LABELS:
        delta = getattr(diff, key)
        if delta.changed:
            added = "".join(f" [red]+{item}[/red]" for item in delta.added)
            removed = "".join(f" [green]-{item}[/green]" for item in delta.removed)
            console.print(f"  {label}:{added}{removed}")
    if not diff.capabilities_grew:
        console.print("Capability surface did not grow.", highlight=False)
    if show_resolved and diff.resolved_findings:
        console.print(
            _finding_table(f"RESOLVED ({len(diff.resolved_findings)})", diff.resolved_findings)
        )
    summary = (
        f"resolved: {len(diff.resolved_findings)}, "
        f"carried over from the old version: {len(diff.carried_findings)}"
    )
    console.print(summary, highlight=False)
    console.print(VERDICT_TEXT[diff.verdict])


def diff_to_html(diff: DiffResult) -> str:
    def rows(findings: list[Finding]) -> str:
        return "\n".join(
            "<tr>"
            + "".join(
                f"<td>{html.escape(str(value))}</td>"
                for value in [f.severity.value, f.rule_id, f.path, f.line, f.snippet]
            )
            + "</tr>"
            for f in findings
        )

    caps = "".join(
        f"<li>{label}: added {', '.join(getattr(diff, key).added) or 'none'}; "
        f"removed {', '.join(getattr(diff, key).removed) or 'none'}</li>"
        for key, label in CAPABILITY_LABELS
    )
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><title>skillfrisk diff</title>
<style>body{{font-family:Inter,system-ui,sans-serif;margin:2rem;background:#0f172a;color:#e2e8f0}}table{{border-collapse:collapse;width:100%;background:#111827;margin-bottom:1.5rem}}td,th{{border:1px solid #334155;padding:.6rem;vertical-align:top}}th{{background:#1e293b}}</style></head>
<body><h1>skillfrisk diff</h1>
<p>{html.escape(str(diff.old_root))} &rarr; {html.escape(str(diff.new_root))}</p>
<p><strong>Verdict: {html.escape(diff.verdict.replace("_", " "))}</strong></p>
<h2>New findings ({len(diff.new_findings)})</h2>
<table><thead><tr><th>Severity</th><th>Rule</th><th>File</th><th>Line</th><th>Snippet</th></tr></thead><tbody>{rows(diff.new_findings)}</tbody></table>
<h2>Capability changes</h2><ul>{caps}</ul>
<h2>Resolved ({len(diff.resolved_findings)})</h2>
<table><thead><tr><th>Severity</th><th>Rule</th><th>File</th><th>Line</th><th>Snippet</th></tr></thead><tbody>{rows(diff.resolved_findings)}</tbody></table>
</body></html>"""
