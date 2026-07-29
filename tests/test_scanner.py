from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from skillfrisk.cli import app
from skillfrisk.report import result_to_json, result_to_sarif
from skillfrisk.scanner import scan_path

FIXTURES = Path(__file__).parent / "fixtures"


def test_benign_skill_has_no_high_risk_findings() -> None:
    result = scan_path(FIXTURES / "benign_skill")
    assert result.files_scanned == 1
    assert not result.failed
    assert result.risk_score == 0


def test_malicious_skill_detects_prompt_injection_and_rce() -> None:
    result = scan_path(FIXTURES / "malicious_skill")
    rule_ids = {finding.rule_id for finding in result.findings}
    assert "PROMPT_INJECTION" in rule_ids
    assert "REMOTE_CODE_EXEC" in rule_ids
    assert "SECRET_ACCESS" in rule_ids
    assert "DESTRUCTIVE_COMMAND" in rule_ids


def test_python_ast_detects_dynamic_exec_and_shell_true() -> None:
    result = scan_path(FIXTURES / "malicious_skill")
    rule_ids = {finding.rule_id for finding in result.findings}
    assert "PY_DYNAMIC_EXEC" in rule_ids
    assert "PY_SHELL_TRUE" in rule_ids


def test_mcp_manifest_detects_dangerous_permissions() -> None:
    result = scan_path(FIXTURES / "mcp_server")
    rule_ids = {finding.rule_id for finding in result.findings}
    assert "MCP_DANGEROUS_TOOLS" in rule_ids
    assert "MCP_WILDCARD_PERMISSION" in rule_ids


def test_json_report_is_machine_readable() -> None:
    result = scan_path(FIXTURES / "mcp_server")
    payload = json.loads(result_to_json(result))
    assert payload["files_scanned"] == 1
    assert payload["failed"] is True
    assert payload["findings"]


def test_cli_returns_nonzero_for_high_risk_findings() -> None:
    runner = CliRunner()
    completed = runner.invoke(app, ["scan", str(FIXTURES / "malicious_skill"), "--json"])
    assert completed.exit_code == 2
    assert "PROMPT_INJECTION" in completed.output


def test_sarif_report_is_github_code_scanning_compatible() -> None:
    result = scan_path(FIXTURES / "malicious_skill")
    payload = json.loads(result_to_sarif(result))
    assert payload["version"] == "2.1.0"
    run = payload["runs"][0]
    assert run["tool"]["driver"]["name"] == "skillfrisk"
    assert any(item["ruleId"] == "REMOTE_CODE_EXEC" for item in run["results"])


def test_cli_version_option() -> None:
    runner = CliRunner()
    completed = runner.invoke(app, ["--version"])
    assert completed.exit_code == 0
    assert completed.output.startswith("skillfrisk ")


def test_cli_writes_sarif_report(tmp_path: Path) -> None:
    sarif_path = tmp_path / "skillfrisk.sarif"
    runner = CliRunner()
    completed = runner.invoke(
        app,
        [
            "scan",
            str(FIXTURES / "malicious_skill"),
            "--sarif",
            str(sarif_path),
            "--no-fail-on-high",
        ],
    )
    assert completed.exit_code == 0
    payload = json.loads(sarif_path.read_text(encoding="utf-8"))
    assert payload["runs"][0]["results"]


def test_clean_scan_prints_a_summary_line_not_an_empty_table() -> None:
    runner = CliRunner()
    completed = runner.invoke(app, ["scan", str(FIXTURES / "benign_skill")])
    assert completed.exit_code == 0
    assert "Severity" not in completed.output
    assert "0 findings" in completed.output
    assert "No high-risk findings detected." in completed.output


def test_findings_table_reports_the_file_count() -> None:
    runner = CliRunner()
    completed = runner.invoke(app, ["scan", str(FIXTURES / "malicious_skill")])
    assert completed.exit_code == 2
    assert "file(s)" in completed.output
    assert "PROMPT_INJECTION" in completed.output


def test_scanning_a_single_file_reports_its_findings() -> None:
    result = scan_path(FIXTURES / "malicious_skill" / "run.py")
    assert result.files_scanned == 1
    assert {finding.rule_id for finding in result.findings} >= {"PY_DYNAMIC_EXEC", "SECRET_ACCESS"}
    assert result.failed


def test_scanning_an_unsupported_file_scans_nothing() -> None:
    result = scan_path(FIXTURES / "malicious_skill" / "SKILL.md")
    assert result.files_scanned == 1
