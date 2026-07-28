"""False-positive regression tests on real, popular, benign skills.

The corpus is vendored unmodified from anthropics/skills (see tests/corpus/NOTICE.md).
skillscan must not raise high-severity findings on any of them.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from skillscan.scanner import scan_path

CORPUS = Path(__file__).parent / "corpus"
SKILLS = ["docx", "pdf", "mcp-builder"]


@pytest.mark.parametrize("skill", SKILLS)
def test_popular_clean_skill_has_no_high_findings(skill: str) -> None:
    result = scan_path(CORPUS / skill)
    high = [f for f in result.findings if f.severity == "high"]
    assert high == [], f"false positives on clean skill {skill}: {high}"
    assert not result.failed
