from __future__ import annotations

import ast
import re
from collections.abc import Iterable
from pathlib import Path

import yaml

from .models import Finding, Severity

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".py", ".js", ".ts", ".sh"}
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"disregard (all )?(previous|prior|above) instructions",
    r"reveal (your )?(system prompt|hidden instructions|secrets)",
    r"do not tell (the )?user",
]
SHELL_PIPE_PATTERN = re.compile(r"(curl|wget)\b[^\n|;]*(\||;|&&)\s*(sh|bash|python)", re.I)
SECRET_READ_PATTERN = re.compile(
    r"(~/(\.ssh|\.aws|\.config)|/etc/passwd"
    r"|(os\.environ|getenv|dotenv|\.env\b)[^\n]{0,80}(key|token|secret|passw|credential)"
    r"|(key|token|secret|passw|credential)[^\n]{0,80}(os\.environ|getenv)\b)",
    re.I,
)
DESTRUCTIVE_PATTERN = re.compile(
    r"\b(rm\s+-rf\s+(/|~|\$HOME)|chmod\s+777|dd\s+if=|mkfs\.|shutdown\b)", re.I
)
EXFIL_PATTERN = re.compile(
    r"(curl|wget|requests\.|fetch\()(.|\n){0,120}(token|secret|password|api[_-]?key|\.env)", re.I
)
UNICODE_PATTERN = re.compile(r"[\u200b\u200c\u200d\ufeff\u202a-\u202e]")
OBFUSCATION_PATTERN = re.compile(
    r"(base64\s+-d|fromCharCode|(?<![\w.])eval\(|(?<![\w.])exec\(|atob\(|b64decode)", re.I
)


def is_scannable(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"SKILL.md", "mcp.json"}


def iter_scannable_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        if is_scannable(root):
            yield root
        return
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", ".venv", "node_modules", "__pycache__"} for part in path.parts):
            continue
        if is_scannable(path):
            yield path


def _finding(
    rule_id: str, title: str, severity: Severity, path: Path, line: int, snippet: str, rec: str
) -> Finding:
    return Finding(rule_id, title, severity, str(path), line, snippet.strip()[:220], rec)


def scan_text(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for i, line in enumerate(text.splitlines(), start=1):
        lower = line.lower()
        if any(re.search(pattern, lower, re.I) for pattern in PROMPT_INJECTION_PATTERNS):
            findings.append(
                _finding(
                    "PROMPT_INJECTION",
                    "Prompt-injection instruction",
                    Severity.HIGH,
                    path,
                    i,
                    line,
                    "Remove hidden instructions and keep skills declarative.",
                )
            )
        if SHELL_PIPE_PATTERN.search(line):
            findings.append(
                _finding(
                    "REMOTE_CODE_EXEC",
                    "Remote script piped into interpreter",
                    Severity.CRITICAL,
                    path,
                    i,
                    line,
                    "Pin and inspect downloads; never pipe network output directly into shells.",
                )
            )
        if SECRET_READ_PATTERN.search(line):
            findings.append(
                _finding(
                    "SECRET_ACCESS",
                    "Reads secrets or sensitive local files",
                    Severity.HIGH,
                    path,
                    i,
                    line,
                    "Request explicit narrow inputs instead of reading global secret stores.",
                )
            )
        if DESTRUCTIVE_PATTERN.search(line):
            findings.append(
                _finding(
                    "DESTRUCTIVE_COMMAND",
                    "Potentially destructive shell command",
                    Severity.HIGH,
                    path,
                    i,
                    line,
                    "Gate irreversible operations behind explicit user confirmation.",
                )
            )
        if EXFIL_PATTERN.search(line):
            findings.append(
                _finding(
                    "SECRET_EXFIL",
                    "Possible secret exfiltration",
                    Severity.CRITICAL,
                    path,
                    i,
                    line,
                    "Do not transmit secrets; redact and keep scans local by default.",
                )
            )
        if UNICODE_PATTERN.search(line):
            findings.append(
                _finding(
                    "HIDDEN_UNICODE",
                    "Hidden or bidirectional Unicode control character",
                    Severity.MEDIUM,
                    path,
                    i,
                    line,
                    "Remove invisible characters that can hide malicious text.",
                )
            )
        if OBFUSCATION_PATTERN.search(line):
            findings.append(
                _finding(
                    "OBFUSCATION",
                    "Obfuscated dynamic code execution",
                    Severity.HIGH,
                    path,
                    i,
                    line,
                    "Avoid eval/exec/base64 loaders in skills and MCP server hooks.",
                )
            )
    return findings


class PythonDangerVisitor(ast.NodeVisitor):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.findings: list[Finding] = []
        self._source = ""

    def visit_Call(self, node: ast.Call) -> None:
        name = ""
        if isinstance(node.func, ast.Attribute):
            name = node.func.attr
        elif isinstance(node.func, ast.Name):
            name = node.func.id
        # Only bare calls: re.compile()/obj.eval() are attribute calls, not builtins.
        if isinstance(node.func, ast.Name) and name in {"eval", "exec", "compile"}:
            self.findings.append(
                _finding(
                    "PY_DYNAMIC_EXEC",
                    "Python dynamic execution",
                    Severity.HIGH,
                    self.path,
                    node.lineno,
                    name,
                    "Replace dynamic execution with explicit parsing or dispatch.",
                )
            )
        if name in {"system", "popen", "run", "call"}:
            rendered = ast.get_source_segment(self._source, node) or name
            if re.search(r"shell\s*=\s*True", rendered):
                self.findings.append(
                    _finding(
                        "PY_SHELL_TRUE",
                        "subprocess with shell=True",
                        Severity.HIGH,
                        self.path,
                        node.lineno,
                        rendered,
                        "Pass argv lists and avoid shell=True.",
                    )
                )
        self.generic_visit(node)

    def scan(self, source: str) -> list[Finding]:
        self._source = source
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        self.visit(tree)
        return self.findings


def scan_python_ast(path: Path, text: str) -> list[Finding]:
    return PythonDangerVisitor(path).scan(text)


def scan_mcp_manifest(path: Path, text: str) -> list[Finding]:
    if path.name not in {"mcp.json", "mcp.yaml", "mcp.yml"} and "mcp" not in path.name.lower():
        return []
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return []
    rendered = str(data).lower()
    findings: list[Finding] = []
    if any(word in rendered for word in ["delete", "write_file", "exec", "shell", "terminal"]):
        findings.append(
            _finding(
                "MCP_DANGEROUS_TOOLS",
                "MCP manifest exposes dangerous tools",
                Severity.MEDIUM,
                path,
                1,
                "manifest contains write/delete/exec-like tools",
                "Document permissions and require confirmation for destructive tools.",
            )
        )
    if "*" in rendered and any(word in rendered for word in ["scope", "permission", "allow"]):
        findings.append(
            _finding(
                "MCP_WILDCARD_PERMISSION",
                "MCP manifest uses wildcard permissions",
                Severity.HIGH,
                path,
                1,
                "wildcard permission",
                "Replace wildcard grants with least-privilege scopes.",
            )
        )
    return findings
