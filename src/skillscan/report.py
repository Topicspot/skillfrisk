from __future__ import annotations

import html
import json
from dataclasses import asdict

from rich.console import Console
from rich.table import Table

from .models import ScanResult


def result_to_json(result: ScanResult) -> str:
    payload = {
        "root": str(result.root),
        "files_scanned": result.files_scanned,
        "risk_score": result.risk_score,
        "failed": result.failed,
        "findings": [asdict(f) for f in result.findings],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def print_terminal(result: ScanResult) -> None:
    console = Console()
    table = Table(title=f"skillscan: {result.risk_score}/100 risk, {len(result.findings)} findings")
    for col in ["Severity", "Rule", "File", "Line", "Snippet"]:
        table.add_column(col)
    for finding in result.findings:
        table.add_row(finding.severity.value, finding.rule_id, finding.path, str(finding.line), finding.snippet)
    console.print(table)
    if result.failed:
        console.print("[bold red]High-risk findings detected.[/bold red]")
    else:
        console.print("[bold green]No high-risk findings detected.[/bold green]")


def result_to_html(result: ScanResult) -> str:
    rows = "\n".join(
        "<tr>" + "".join(
            f"<td>{html.escape(str(value))}</td>"
            for value in [f.severity.value, f.rule_id, f.path, f.line, f.snippet, f.recommendation]
        ) + "</tr>"
        for f in result.findings
    )
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><title>skillscan report</title>
<style>body{{font-family:Inter,system-ui,sans-serif;margin:2rem;background:#0f172a;color:#e2e8f0}}table{{border-collapse:collapse;width:100%;background:#111827}}td,th{{border:1px solid #334155;padding:.6rem;vertical-align:top}}th{{background:#1e293b}}.score{{font-size:2rem;font-weight:800}}</style></head>
<body><h1>skillscan report</h1><p class=\"score\">Risk score: {result.risk_score}/100</p><p>Files scanned: {result.files_scanned}. Findings: {len(result.findings)}.</p>
<table><thead><tr><th>Severity</th><th>Rule</th><th>File</th><th>Line</th><th>Snippet</th><th>Recommendation</th></tr></thead><tbody>{rows}</tbody></table>
</body></html>"""
