from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from . import __version__
from .diff import diff_paths
from .models import SEVERITY_SCORE, Severity
from .report import (
    diff_to_html,
    diff_to_json,
    print_diff_terminal,
    print_terminal,
    result_to_html,
    result_to_json,
    result_to_sarif,
)
from .scanner import scan_path

app = typer.Typer(help="Static security scanner for AI-agent skills and MCP servers.")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"skillfrisk {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    _version: Annotated[
        bool | None,
        typer.Option("--version", callback=_version_callback, is_eager=True, help="Show version."),
    ] = None,
) -> None:
    """Static security scanner for AI-agent skills and MCP servers."""


@app.command()
def scan(
    path: Annotated[Path, typer.Argument(help="Skill/MCP directory to scan.")] = Path(),
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON report.")] = False,
    html_output: Annotated[Path | None, typer.Option("--html", help="Write HTML report.")] = None,
    sarif_output: Annotated[
        Path | None, typer.Option("--sarif", help="Write SARIF report.")
    ] = None,
    no_fail_on_high: Annotated[
        bool,
        typer.Option("--no-fail-on-high", help="Do not exit non-zero for high findings."),
    ] = False,
) -> None:
    result = scan_path(path)
    if html_output:
        html_output.parent.mkdir(parents=True, exist_ok=True)
        html_output.write_text(result_to_html(result), encoding="utf-8")
    if sarif_output:
        sarif_output.parent.mkdir(parents=True, exist_ok=True)
        sarif_output.write_text(result_to_sarif(result), encoding="utf-8")
    if json_output:
        typer.echo(result_to_json(result))
    else:
        print_terminal(result)
    if not no_fail_on_high and result.failed:
        raise typer.Exit(2)


@app.command()
def diff(
    old: Annotated[Path, typer.Argument(help="Old skill version: directory or SKILL.md.")],
    new: Annotated[Path, typer.Argument(help="New skill version: directory or SKILL.md.")],
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON report.")] = False,
    html_output: Annotated[Path | None, typer.Option("--html", help="Write HTML report.")] = None,
    fail_on: Annotated[
        str,
        typer.Option(
            "--fail-on",
            help="Exit non-zero for new findings at this severity or above: "
            "critical, high, medium, low, or any-change (also fails on grown capabilities).",
        ),
    ] = "high",
    no_fail: Annotated[bool, typer.Option("--no-fail", help="Report only, always exit 0.")] = False,
    show_resolved: Annotated[
        bool, typer.Option("--show-resolved", help="Also print findings the update resolved.")
    ] = False,
) -> None:
    """Compare two versions of a skill and report what the update changes."""
    levels = {level.value for level in Severity} | {"any-change"}
    if fail_on not in levels:
        typer.echo(f"invalid --fail-on value: {fail_on} (choose from {sorted(levels)})")
        raise typer.Exit(1)
    for path in (old, new):
        if not path.exists():
            typer.echo(f"path does not exist: {path}")
            raise typer.Exit(1)
    result = diff_paths(old, new)
    if html_output:
        html_output.parent.mkdir(parents=True, exist_ok=True)
        html_output.write_text(diff_to_html(result), encoding="utf-8")
    if json_output:
        typer.echo(diff_to_json(result))
    else:
        print_diff_terminal(result, show_resolved=show_resolved)
    if no_fail:
        return
    if fail_on == "any-change":
        if result.new_findings or result.capabilities_grew:
            raise typer.Exit(2)
        return
    threshold = SEVERITY_SCORE[Severity(fail_on)]
    if any(SEVERITY_SCORE[f.severity] >= threshold for f in result.new_findings):
        raise typer.Exit(2)


if __name__ == "__main__":
    app()
