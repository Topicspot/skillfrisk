# Changelog

## Unreleased

- Added SARIF output (`--sarif`) for GitHub code scanning integrations.
- Added `--version` to the CLI.

## 0.2.0 - 2026-07-28

- Renamed the project from skillscan to skillfrisk; the CLI command is now `skillfrisk`.
- First release on PyPI.
- Regression corpus expanded from 3 to 10 anthropics/skills skills (92 files); fixed the false positives this exposed in OBFUSCATION, PY_DYNAMIC_EXEC, and SECRET_ACCESS.
- Added a reproducible benchmark harness (`benchmarks/run.py`) with pinned versions of cisco-ai-skill-scanner and SkillSpector, plus recorded results.

## 0.1.0 - Unreleased

- Initial scanner for SKILL.md files and MCP manifests.
- Terminal, JSON, and HTML reports.
- CI with Ruff and Pytest.
