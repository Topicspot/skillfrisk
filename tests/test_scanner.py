from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from skillscan.cli import app
from skillscan.report import result_to_json
from skillscan.scanner import scan_path

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
