from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from .report import print_terminal, result_to_html, result_to_json
from .scanner import scan_path

app = typer.Typer(help="Static security scanner for AI-agent skills and MCP servers.")


@app.callback()
def main() -> None:
    """Static security scanner for AI-agent skills and MCP servers."""


@app.command()
def scan(
    path: Annotated[Path, typer.Argument(help="Skill/MCP directory to scan.")] = Path("."),
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON report.")] = False,
    html_output: Annotated[Path | None, typer.Option("--html", help="Write HTML report.")] = None,
    no_fail_on_high: Annotated[
        bool,
        typer.Option("--no-fail-on-high", help="Do not exit non-zero for high findings."),
    ] = False,
) -> None:
    result = scan_path(path)
    if html_output:
        html_output.parent.mkdir(parents=True, exist_ok=True)
        html_output.write_text(result_to_html(result), encoding="utf-8")
    if json_output:
        typer.echo(result_to_json(result))
    else:
        print_terminal(result)
    if not no_fail_on_high and result.failed:
        raise typer.Exit(2)


if __name__ == "__main__":
    app()
