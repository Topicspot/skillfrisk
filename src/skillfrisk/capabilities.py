"""Extract the capability surface of a skill version.

Everything here is static and offline: frontmatter tool grants, shell commands
referenced in text, network hosts referenced in text, and a content hash per
file. Two surfaces are compared by ``skillfrisk diff`` to show what an update
adds or removes.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .rules import iter_scannable_files

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
URL_PATTERN = re.compile(r"https?://([a-zA-Z0-9.-]+)")
SHELL_COMMANDS = {
    "bash",
    "chmod",
    "chown",
    "curl",
    "dd",
    "docker",
    "git",
    "kubectl",
    "node",
    "npm",
    "npx",
    "osascript",
    "pip",
    "powershell",
    "python",
    "python3",
    "rm",
    "rsync",
    "scp",
    "sh",
    "ssh",
    "sudo",
    "uv",
    "uvx",
    "wget",
}
COMMAND_PATTERN = re.compile(
    r"(?:^|[|;&`$(]\s*|\b(?:sudo|exec)\s+)(" + "|".join(sorted(SHELL_COMMANDS)) + r")\b"
)


@dataclass
class Capabilities:
    allowed_tools: set[str] = field(default_factory=set)
    shell_commands: set[str] = field(default_factory=set)
    network_hosts: set[str] = field(default_factory=set)
    file_hashes: dict[str, str] = field(default_factory=dict)


def _frontmatter_tools(text: str) -> set[str]:
    match = FRONTMATTER.match(text)
    if not match:
        return set()
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return set()
    if not isinstance(data, dict):
        return set()
    raw = data.get("allowed-tools", data.get("allowed_tools"))
    if isinstance(raw, str):
        return {item.strip() for item in raw.split(",") if item.strip()}
    if isinstance(raw, list):
        return {str(item).strip() for item in raw if str(item).strip()}
    return set()


def extract_capabilities(root: Path) -> Capabilities:
    root = root.resolve()
    base = root.parent if root.is_file() else root
    caps = Capabilities()
    for path in iter_scannable_files(root):
        raw = path.read_bytes()
        rel = str(path.relative_to(base))
        caps.file_hashes[rel] = hashlib.sha256(raw).hexdigest()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if path.name == "SKILL.md":
            caps.allowed_tools |= _frontmatter_tools(text)
        for line in text.splitlines():
            caps.shell_commands.update(m.group(1) for m in COMMAND_PATTERN.finditer(line))
            caps.network_hosts.update(m.group(1) for m in URL_PATTERN.finditer(line))
    return caps
