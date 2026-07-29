from __future__ import annotations

from pathlib import Path

from .models import ScanResult
from .rules import iter_scannable_files, scan_mcp_manifest, scan_python_ast, scan_text


def scan_path(root: Path) -> ScanResult:
    root = root.resolve()
    base = root.parent if root.is_file() else root
    result = ScanResult(root=root)
    for path in iter_scannable_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(base)
        result.files_scanned += 1
        result.findings.extend(scan_text(rel, text))
        if path.suffix == ".py":
            result.findings.extend(scan_python_ast(rel, text))
        result.findings.extend(scan_mcp_manifest(rel, text))
    return result
